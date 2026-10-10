"""Headless UI state/backend; Tk is imported only in desktop.py's window factory."""
from pathlib import Path
from contextlib import ExitStack
import copy,json,os,queue,sys,threading,uuid
import discovery
commands=discovery.commands;im=commands.im;read=commands.read
sys.path.insert(0,str(discovery.ROOT/'EXPERIMENTS/package_producer'))
import producer
TYPES=sorted(read.TYPES)
class Backend:
    def __init__(self,roots,*,_controller_kwargs=None,_publisher_kwargs=None):self.roots={k:Path(v) for k,v in roots.items()};self.ckw=_controller_kwargs or {};self.pkw=_publisher_kwargs or {}
    def config(self):
        if set(self.roots)!={'bank','intake','stage','cache','output','source'}:raise commands.ConfigurationError('INVALID_CONFIGURATION')
        paths=list(self.roots.values())
        if any(not p.is_absolute() or '..' in p.parts for p in paths) or any(a.is_relative_to(b) or b.is_relative_to(a) for i,a in enumerate(paths) for b in paths[i+1:]):raise commands.ConfigurationError('INVALID_CONFIGURATION')
        with ExitStack() as guards:
            for p in paths:guards.enter_context(producer.io.Directory(p,root=True))
    def controller(self):return commands.Controller(self.roots['bank'],**{k+'_root':self.roots[k] for k in ['intake','stage','cache','output']},**self.ckw)
    def query(self,operation,**kw):return {'protocol':read.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':operation,**kw}
    def dispatch(self,action,args):
        try:
            self.config()
            if action=='list':return discovery.Discovery(self.roots['bank']).execute(args)
            if action in ['publish','inspect','resume']:return producer.Publisher(self.roots['intake'],self.roots['source'],**self.pkw).execute(action,args['transaction_id'])
            with self.controller() as c:
                if action=='save':return c.save('bank.save',args['transaction_id'])
                if action=='rebuild':return c.rebuild()
                if action=='receipt':q=self.query('receipt.get',transaction_id=args['transaction_id'],expected_manifest_sha256=args.get('expected_manifest_sha256'))
                elif action=='search':q=self.query('bank.search',object_types=args['object_types'],fields=args['fields'],query=args['query'],revisions_mode=args['revisions_mode'],snapshot_sequence=args.get('snapshot_sequence'),limit=10,offset=args.get('offset',0))
                else:
                    ref=args['ref'];base={'object_type':ref['object_type'],'object_id':ref['object_id']}
                    if action=='detail':q=self.query('collection.get' if ref['object_type']=='Collection' else 'bank.get',**base,selector={'mode':'pinned','revision_id':ref['revision_id']})
                    elif action=='history':q=self.query('bank.history',**base,snapshot_sequence=args.get('snapshot_sequence'),limit=10,offset=args.get('offset',0))
                    elif action=='export':q=self.query('bank.original',**base,revision_id=ref['revision_id'])
                    else:return {'status':'ERROR','code':'INVALID_ACTION'}
                result=c.query(im.encoded(q))
                # UI-only metadata, resolved on the existing worker from each exact pin.
                # The read/search protocol and stored documents are unchanged.
                rows=result.get('data',{}).get('hits' if action=='search' else 'revisions',[]) if action in ['search','history'] else []
                for row in rows[:10]:
                    ref=row['ref'];label=c.query(im.encoded(self.query('bank.get',object_type=ref['object_type'],object_id=ref['object_id'],selector={'mode':'pinned','revision_id':ref['revision_id']})))
                    if label.get('status')=='OK':
                        row['title']=label['data']['document']['title'];row['accepted_at']=label['data']['accepted_at']
                    else:row['title_unavailable']=True
                return result
        except KeyboardInterrupt:return {'status':'UNKNOWN' if action=='save' else 'CANCELLED','code':'OPERATION_OUTCOME_UNCERTAIN'}
        except Exception:return {'status':'UNKNOWN' if action in ['save','author_save','object_save','continue_save'] else 'ERROR','code':'UI_OPERATION_ERROR'}
class Model:
    def __init__(self):
        self.busy=False;self.closing=False;self.closed=False;self.selected=None;self.rows={k:[] for k in ['Bank','Collections','History','Search']};self.pages={k:{} for k in self.rows};self.result=None;self.publication=None;self.save=None;self.last_receipt=None;self.status='Готов';self.active=None;self.labels={}
    def begin(self,action,args,tab):
        if self.busy or self.closed or self.closing:return False
        self.busy=True;self.active=(action,copy.deepcopy(args),tab);self.status=action_label(action);return True
    def close_request(self):
        self.closing=True;self.status='Закрытие: ожидаем результат текущей операции' if self.busy else 'Закрыто'
        if not self.busy:self.closed=True
    def finish(self,result):
        action,args,tab=self.active;self.busy=False;self.active=None;self.result=copy.deepcopy(result);state=result.get('status','ERROR');self.status=outcome_label(result)
        if action in ['publish','inspect','resume']:self.publication=copy.deepcopy(result)
        if action=='save':self.save=copy.deepcopy(result)
        if action=='receipt' and state=='OK':self.last_receipt=copy.deepcopy(result['data']['receipt'])
        if state=='OK':
            if action=='list':self.rows[tab]=copy.deepcopy(result['items']);self.pages[tab]={'snapshot_sequence':result['snapshot_sequence'],'after_object_id':result['next_after_object_id'],'has_more':result['has_more']}
            if action=='history':self.rows['History']=copy.deepcopy(result['data']['revisions']);self.pages['History']={'snapshot_sequence':result['snapshot_sequence'],'offset':result['data']['next_offset'],'has_more':result['data']['has_more'],'ref':args['ref']}
            if action=='search':self.rows['Search']=copy.deepcopy(result['data']['hits']);self.pages['Search']={'snapshot_sequence':result['snapshot_sequence'],'offset':args.get('offset',0)+10,'has_more':result['data']['has_more'],'query_args':args}
        elif action in ['list','history','search']:self.status+='; показаны прежние данные'
        for rows in self.rows.values():
            for row in rows:self.remember(row)
        data=result.get('data',{})
        if 'document' in data:self.remember({'ref':{k:data['document'][k] for k in ['object_type','object_id','revision_id']},'title':data['document']['title'],'accepted_at':data.get('accepted_at','')})
        if self.closing:self.closed=True
        return action=='save' and state in ['ACCEPTED','REPLAY'] and not self.closing
    def select(self,tab,index):
        if self.busy or self.closing:return False
        if not(0<=index<len(self.rows[tab])):return False
        self.remember(self.rows[tab][index]);self.selected=copy.deepcopy(self.rows[tab][index]['ref']);return True
    def remember(self,row):
        if 'title' not in row:return
        key=ref_key(row['ref'])
        if key not in self.labels and len(self.labels)>=512:self.labels.pop(next(iter(self.labels)))
        self.labels[key]={'title':row['title'],'accepted_at':row.get('accepted_at','')}
    def ref_label(self,ref):
        info=self.labels.get(ref_key(ref),{})
        text=material_label(ref,info.get('title'))
        return text+(' — '+info['accepted_at'] if info.get('accepted_at') else '')
    def receipt_args(self,tx):
        expected=self.publication.get('manifest_sha256') if self.publication and self.publication.get('transaction_id')==tx else None
        return {'transaction_id':tx,'expected_manifest_sha256':expected}
VALUE_LABELS={'note':'Заметка','file':'Файл','url':'Ссылка','unknown':'Не указан','user':'Человек','ai':'ИИ','system':'Приложение','plain_text':'Обычный текст','markdown':'Markdown','auto':'Определить автоматически','utf8_text':'Текст UTF-8','binary':'Без преобразования','tag':'Метка','comment':'Комментарий','interpretation':'Интерпретация','user_capture':'Добавлено пользователем','external_capture':'Получено из внешнего источника','user_authored':'Создано человеком','ai_authored':'Создано ИИ','derived':'На основе других материалов'}
def value_label(value):return VALUE_LABELS.get(value,value)
def action_label(action):
    return {'author_save':'Сохраняем материал…','object_save':'Сохраняем изменения…','continue_save':'Повторяем сохранение…','author_prepare':'Проверяем материал…','object_prepare':'Проверяем изменения…','save':'Сохраняем…','list':'Обновляем список…','rebuild':'Обновляем поиск…','search':'Ищем…','detail':'Открываем материал…','history':'Открываем историю…','object_base':'Открываем редактор…','publish':'Проверяем данные для сохранения…','receipt':'Проверяем результат сохранения…'}.get(action,'Выполняем действие…')
def outcome_label(result):
    code=result.get('code','');state=result.get('status','ERROR')
    if code=='UNTRUSTED_OWNER':return 'Не удалось сохранить: служебный файл имеет неподходящего владельца Windows. Проверь рабочую папку приложения; введённые данные менять не нужно.'
    if code=='STALE_BASE':return 'Материал уже изменён. Открой его заново перед редактированием.'
    if code=='EMPTY_INPUT':return 'Заполни обязательные поля.'
    if state=='UNKNOWN':return 'Подтверждение сохранения не получено. Повтори сохранение этой же записи.'
    if state=='CANCELLED':return 'Действие отменено. Материал не сохранён.'
    return {'OK':'Готово','ACCEPTED':'Сохранено','REPLAY':'Уже сохранено','PREPARED':'Данные проверены; сохранение ещё не завершено','PUBLISHED':'Данные готовы к сохранению','ALREADY_PUBLISHED':'Данные готовы к сохранению','BUILT':'Поиск обновлён','SEALED':'Данные проверены; сохранение можно продолжить','INCOMPLETE':'Сохранение не завершено. Повтори действие для этой же записи.','REJECTED':'Не удалось сохранить. Проверь введённые данные.','RETRYABLE_BUSY':'Рабочая папка занята. Повтори после завершения другой операции.'}.get(state,'Не удалось выполнить действие. Подробности — в дополнительных инструментах.')
TYPE_LABELS={'Asset':'Материал','Annotation':'Заметка','Entity':'Сущность','Collection':'Коллекция'}
FIELD_LABELS={'title':'название','filename':'имя файла','uri':'ссылка','aliases':'альтернативные названия','body':'текст заметки','content':'содержимое файла'}
def type_label(typ):return TYPE_LABELS.get(typ,typ)
def chosen_types(choice):return TYPES if choice=='Все типы' else [next((k for k,v in TYPE_LABELS.items() if v==choice),choice)]
def ref_key(ref):return tuple(ref[k] for k in ['object_type','object_id','revision_id'])
def material_label(ref,title=None):
    text=title or (type_label(ref['object_type'])+' — название не загружено' if title is None else type_label(ref['object_type'])+' без названия')
    return ''.join(c if ord(c)>=32 else ' ' for c in text)[:160]
def row_values(row):
    return (type_label(row['ref']['object_type']),material_label(row['ref'],row.get('title')),row.get('accepted_at',''))
def intent_labels(items):
    # Index maps to the full transaction in Model; labels never become identities.
    return [str(n+1)+'. '+(x.get('title') or 'Без названия')[:64] for n,x in enumerate(items)]
def render(result,technical=False,labels=None):
    if technical:return json.dumps(result,ensure_ascii=False,indent=2)
    state=result.get('status','ERROR');code=result.get('code','')
    messages={'OK':'Готово','ACCEPTED':'Сохранено в Bank','REPLAY':'Сохранение уже подтверждено','PUBLISHED':'Пакет опубликован; теперь сохрани его в Bank','ALREADY_PUBLISHED':'Пакет уже опубликован','BUILT':'Поиск обновлён','PREPARED':'Подготовлено; опубликуй пакет и сохрани его в Bank'}
    lines=[outcome_label(result)]
    labels=labels or {}
    def refs(values):
        return '\n'.join(str(n+1)+'. '+material_label(ref,labels.get(ref_key(ref),{}).get('title')) for n,ref in enumerate(values)) or 'Не указаны'
    data=result.get('data',{})
    if state=='OK' and 'document' in data:
        d=data['document'];v=d['data'];typ=d['object_type'];lines += [d.get('title') or 'Без названия',type_label(typ)]
        if data.get('accepted_at'):lines.append('Сохранено: '+data['accepted_at'])
        if typ=='Annotation':
            lines += [v['body'],'Формат: '+value_label(v['content_format']),'Автор: '+(v['author'].get('identity') or value_label(v['author']['kind']))]
            if v['author'].get('model'):lines.append('Модель ИИ: '+v['author']['model'])
            lines.append('Относится к:\n'+refs(v.get('targets',[])))
        elif typ=='Entity':
            lines += ['Вид: '+v['entity_kind'],'Другие названия: '+(', '.join(v['aliases']) or 'Не указаны')]
            if v['external_ids']:lines.append('Внешние идентификаторы:\n'+'\n'.join(x['namespace']+': '+x['value'] for x in v['external_ids']))
            lines.append('Связанные материалы:\n'+refs(v['asset_refs']))
        elif typ=='Collection':lines.append('Состав коллекции:\n'+refs(v['members']))
        elif typ=='Asset':
            storage=v['storage']
            if storage['mode']=='locator':lines += ['Ссылка: '+storage['uri'],storage.get('label') or '','Содержимое ссылки не скачивается.']
            else:lines += ['Файл: '+storage['original_filename'],'Тип файла: '+storage['media_type'],'Размер: '+str(storage['byte_length'])+' байт']
        pv=d['provenance'];lines.append('Происхождение: '+value_label(pv['origin_kind']))
        if pv.get('source_locator'):lines.append('Источник: '+pv['source_locator'])
        if pv.get('derived_from'):lines.append('Основано на:\n'+refs(pv['derived_from']))
        if 'member_statuses' in data:
            unavailable=[n+1 for n,x in enumerate(data['member_statuses']) if x.get('availability')!='available']
            if unavailable:lines.append('Недоступные материалы в коллекции (номера в списке): '+', '.join(map(str,unavailable))+'. Подробности — в технических деталях.')
    elif state=='OK' and 'original' in data:
        original=data['original'];lines += ['Файл выгружен без запуска его содержимого.',original['path'],'Размер: '+str(original['byte_length'])+' байт','Файл сохраняется после закрытия приложения. При следующем чтении его целостность нужно проверить.']
    elif state=='OK' and data.get('availability')=='locator_only':lines+=['Сохранённая ссылка (без загрузки): '+data['uri']]
    elif result.get('protocol')==discovery.PROTOCOL and state=='OK':lines += ['Материалов на странице: '+str(len(result['items'])),'Выбери материал и нажми «Открыть».']
    elif state=='OK' and 'hits' in data:
        lines.append('Совпадений: '+str(data['total_matches']))
        coverage_labels={'indexed':'содержимое проиндексировано','locator_only':'ссылки без скачивания','unsupported_media':'формат не поддерживает поиск по содержимому','size_limit':'содержимое превышает лимит поиска','invalid_utf8':'содержимое не является UTF-8'}
        lines.extend(label+': '+str(data.get('coverage',{}).get(key,0)) for key,label in coverage_labels.items() if data.get('coverage',{}).get(key,0))
    elif state=='OK' and 'revisions' in data:lines += ['Записей в истории на странице: '+str(len(data['revisions'])),'Выбери запись по названию и времени сохранения.']
    else:
        receipt=result.get('receipt') or data.get('receipt')
        if receipt:lines.append('Сохранение подтверждено.')
        if result.get('Bank_accepted') is False:lines.append('Материал ещё не сохранён в банке.')
        if state=='UNKNOWN':lines.append('Подтверждение сохранения не получено. Повтори сохранение этой же записи; новая копия не будет создана.')
        if code=='RETAINED_WORK_LIMIT':
            lines.append('Достигнут рабочий лимит проверки истории. Пакет сохранён для повтора.')
            if state=='IO_ERROR':lines.append('Проверка уже принятого сохранения не завершена. Это не означает, что данные не сохранены; проверь квитанцию после изменения рабочего лимита.')
        if code=='RECEIPT_NOT_FOUND':lines.append('Квитанция не найдена; это не доказывает, что предыдущая запись не была принята.')
        if code in ['INDEX_UNAVAILABLE','INDEX_NOT_READY','INDEX_PROFILE_MISMATCH']:lines.append('Для поиска требуется явное обновление индекса.')
        if code=='STALE_BASE':lines.append('Материал уже изменён другим сохранением. Эта подготовка сохранена; для новой правки открой актуальный материал в Bank.')
    return '\n\n'.join(lines)
def display(result,cap=65536,*,technical=False,labels=None):
    raw=render(result,technical=technical,labels=labels).encode('utf-8');truncated=len(raw)>cap;value=raw[:cap].decode('utf-8',errors='ignore');value=''.join(c if ord(c)>=32 or c in '\n\t' else '�' for c in value)
    return value+('\n\n[Текст сокращён для просмотра; сохранённые данные не изменены.]' if truncated else '')
class Bridge:
    def __init__(self,backend):self.backend=backend;self.results=queue.Queue(maxsize=1);self.thread=None
    def submit(self,action,args):
        if self.thread is not None:return False
        args=copy.deepcopy(args)
        def work():
            try:r=self.backend.dispatch(action,args)
            except BaseException:r={'status':'UNKNOWN' if action in ['save','author_save','object_save','continue_save'] else 'ERROR','code':'UI_WORKER_ERROR'}
            self.results.put(r)
        self.thread=threading.Thread(target=work,name='bank-ui-operation',daemon=False);self.thread.start();return True
    def poll(self):
        try:r=self.results.get_nowait()
        except queue.Empty:return None
        self.thread.join();self.thread=None;return r
