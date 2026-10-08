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
                return c.query(im.encoded(q))
        except KeyboardInterrupt:return {'status':'UNKNOWN' if action=='save' else 'CANCELLED','code':'OPERATION_OUTCOME_UNCERTAIN'}
        except Exception:return {'status':'UNKNOWN' if action=='save' else 'ERROR','code':'UI_OPERATION_ERROR'}
class Model:
    def __init__(self):
        self.busy=False;self.closing=False;self.closed=False;self.selected=None;self.rows={k:[] for k in ['Bank','Collections','History','Search']};self.pages={k:{} for k in self.rows};self.result=None;self.publication=None;self.save=None;self.last_receipt=None;self.status='Готов';self.active=None
    def begin(self,action,args,tab):
        if self.busy or self.closed or self.closing:return False
        self.busy=True;self.active=(action,copy.deepcopy(args),tab);self.status='Выполняется: '+action;return True
    def close_request(self):
        self.closing=True;self.status='Закрытие: ожидаем результат текущей операции' if self.busy else 'Закрыто'
        if not self.busy:self.closed=True
    def finish(self,result):
        action,args,tab=self.active;self.busy=False;self.active=None;self.result=copy.deepcopy(result);state=result.get('status','ERROR');self.status=state+' / '+result.get('code','')
        if action in ['publish','inspect','resume']:self.publication=copy.deepcopy(result)
        if action=='save':self.save=copy.deepcopy(result)
        if action=='receipt' and state=='OK':self.last_receipt=copy.deepcopy(result['data']['receipt'])
        if state=='OK':
            if action=='list':self.rows[tab]=copy.deepcopy(result['items']);self.pages[tab]={'snapshot_sequence':result['snapshot_sequence'],'after_object_id':result['next_after_object_id'],'has_more':result['has_more']}
            if action=='history':self.rows['History']=copy.deepcopy(result['data']['revisions']);self.pages['History']={'snapshot_sequence':result['snapshot_sequence'],'offset':result['data']['next_offset'],'has_more':result['data']['has_more'],'ref':args['ref']}
            if action=='search':self.rows['Search']=copy.deepcopy(result['data']['hits']);self.pages['Search']={'snapshot_sequence':result['snapshot_sequence'],'offset':args.get('offset',0)+10,'has_more':result['data']['has_more'],'query_args':args}
        elif action in ['list','history','search']:self.status+='; показаны прежние данные'
        if self.closing:self.closed=True
        return action=='save' and state in ['ACCEPTED','REPLAY'] and not self.closing
    def select(self,tab,index):
        if self.busy or self.closing:return False
        if not(0<=index<len(self.rows[tab])):return False
        self.selected=copy.deepcopy(self.rows[tab][index]['ref']);return True
    def receipt_args(self,tx):
        expected=self.publication.get('manifest_sha256') if self.publication and self.publication.get('transaction_id')==tx else None
        return {'transaction_id':tx,'expected_manifest_sha256':expected}
def render(result):
    state=result.get('status','ERROR');code=result.get('code','');lines=[state+' / '+code]
    if state=='OK' and 'document' in result.get('data',{}):
        d=result['data']['document'];lines += [d.get('title') or '(без названия)',d['object_type'],'Revision: '+d['revision_id'],'Object: '+d['object_id'],'Принято: '+result['data']['accepted_at'],json.dumps(d['data'],ensure_ascii=False,indent=2),'Происхождение: '+json.dumps(d['provenance'],ensure_ascii=False,indent=2)]
        if 'member_statuses' in result['data']:lines.append('Доступность членов: '+json.dumps(result['data']['member_statuses'],ensure_ascii=False,indent=2))
    elif state=='OK' and 'original' in result.get('data',{}):
        data=result['data'];original=data['original'];lines += ['Оригинал экспортирован без запуска/просмотра активного содержимого.',original['path'],'SHA-256: '+original['sha256'],'Размер: '+str(original['byte_length'])+' bytes','Приватный файл сохраняется после закрытия; перед следующим чтением нужно проверить hash.']
    elif state=='OK' and result.get('data',{}).get('availability')=='locator_only':lines+=['Сохранённый URL (без загрузки): '+result['data']['uri']]
    elif result.get('protocol')==discovery.PROTOCOL and state=='OK':lines += ['Срез: '+str(result['snapshot_sequence']),'Объектов на странице: '+str(len(result['items'])),'Выбери строку и открой сохранённую revision.']
    elif state=='OK' and 'hits' in result.get('data',{}):lines += ['Совпадений: '+str(result['data']['total_matches']),'Поддержка извлечения: '+json.dumps(result['data']['coverage'],ensure_ascii=False,indent=2)]
    elif state=='OK' and 'revisions' in result.get('data',{}):lines += ['История на срезе '+str(result['snapshot_sequence'])+'; revisions: '+str(len(result['data']['revisions'])),'Выбери revision для открытия.']
    else:
        for key in ['transaction_id','manifest_sha256','file_count','cleanup_status']:
            if result.get(key) is not None:lines.append(key+': '+str(result[key]))
        receipt=result.get('receipt') or result.get('data',{}).get('receipt')
        if receipt:lines.append('Квитанция: '+json.dumps(receipt,ensure_ascii=False,indent=2))
        if result.get('Bank_accepted') is False:lines.append('Пакет готовится отдельно; запись в Bank подтверждается квитанцией сохранения.')
        if state=='UNKNOWN':lines.append('Исход неизвестен. Проверь тот же пакет и квитанцию перед повтором; ID не менять.')
        if code=='RECEIPT_NOT_FOUND':lines.append('Квитанция не найдена; это не доказывает, что предыдущая запись не была принята.')
        if code in ['INDEX_UNAVAILABLE','INDEX_NOT_READY','INDEX_PROFILE_MISMATCH']:lines.append('Для поиска требуется явное перестроение индекса.')
    return '\n\n'.join(lines)
def display(result,cap=65536):
    raw=render(result).encode('utf-8');truncated=len(raw)>cap;value=raw[:cap].decode('utf-8',errors='ignore');value=''.join(c if ord(c)>=32 or c in '\n\t' else '�' for c in value)
    return value+('\n\n[Текст сокращён для просмотра; исходные данные и ID не изменены.]' if truncated else '')
class Bridge:
    def __init__(self,backend):self.backend=backend;self.results=queue.Queue(maxsize=1);self.thread=None
    def submit(self,action,args):
        if self.thread is not None:return False
        args=copy.deepcopy(args)
        def work():
            try:r=self.backend.dispatch(action,args)
            except BaseException:r={'status':'UNKNOWN' if action=='save' else 'ERROR','code':'UI_WORKER_ERROR'}
            self.results.put(r)
        self.thread=threading.Thread(target=work,name='bank-ui-operation',daemon=False);self.thread.start();return True
    def poll(self):
        try:r=self.results.get_nowait()
        except queue.Empty:return None
        self.thread.join();self.thread=None;return r
