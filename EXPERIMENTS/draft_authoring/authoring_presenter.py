"""Creation composition; accepted six-root Backend and publisher stay unchanged."""
from pathlib import Path
import copy,sys,threading
import authoring as a
sys.path.insert(0,str(a.ROOT/'EXPERIMENTS/local_ui'))
import presenter as base

class SealedPublisher(a.producer.Publisher):
    def __init__(self,*args,expected,**kw):super().__init__(*args,**kw);self.expected=expected
    def _prepare(self,stack,tx,budget):
        prepared=super()._prepare(stack,tx,budget)
        a.producer.need(a.sha(prepared['manifest'])==self.expected,'SEALED_MANIFEST_MISMATCH')
        return prepared

class Backend:
    def __init__(self,roots,*,_portable_fixture=False,_limits=None,_hook=None,_controller_kwargs=None,_publisher_kwargs=None):
        self.workspace=a.Workspace(roots,_portable_fixture=_portable_fixture,_limits=_limits,_hook=_hook)
        self.base=base.Backend({k:v for k,v in roots.items() if k!='authoring'},_controller_kwargs=_controller_kwargs,_publisher_kwargs=_publisher_kwargs)
        self.cancel=threading.Event()
    def config(self):
        self.base.config()
        with self.workspace.session():pass
    def dispatch(self,action,args):
        w=self.workspace;tx=args.get('transaction_id')
        if action=='author_prepare':return w.prepare(args['fields'],cancel=self.cancel.is_set)
        if action=='author_load':return w.inspect(tx)
        if action=='author_finish':return w.inspect(tx,finish=True)
        if action=='author_list':return w.listing(args.get('after'))
        try:
            if action not in ['publish','resume','inspect','save','receipt']:return self.base.dispatch(action,args)
            a.need(type(tx) is str and a.reader.UUID.fullmatch(tx),'INVALID_TRANSACTION_ID')
            with w.session() as stack:
                if action in ['publish','resume']:
                    stack.enter_context(a.io.Directory(w.roots['authoring']/tx,write=True))
                    budget=a.Budget(w);intent,raw=w.read_intent(tx,budget);seal=w.read_seal(tx,budget)
                    draft=w.verify_source(intent,seal,raw,'DRAFT.json',budget);expected=w.prepared_result(intent,seal,draft)['manifest_sha256']
                    return SealedPublisher(w.roots['intake'],w.roots['source'],expected=expected,**self.base.pkw).execute(action,tx)
                # Receipt/save inspect the actual package/Bank even if journal or
                # prepared copy is damaged. A local journal is never a receipt.
                return self.base.dispatch(action,args)
        except Exception as e:
            result=w.failure(tx,e)
            return {k:result[k] for k in ['status','code','transaction_id']}

class Model(base.Model):
    def __init__(self):
        super().__init__();self.transaction_id=None;self.generation=0;self.active_generation=None;self.preparation=None;self.intents=[];self.intent_page={};self.outcomes={}
    def clear_transaction(self):
        self.preparation=None;self.publication=None;self.save=None;self.last_receipt=None;self.result=None
    def select_transaction(self,tx):
        if self.busy or self.closing or not(type(tx) is str and a.reader.UUID.fullmatch(tx)):return False
        self.transaction_id=tx;self.generation+=1;self.clear_transaction();return True
    def begin(self,action,args,tab):
        if self.busy or self.closing or self.closed:return False
        if action in ['author_load','author_finish','publish','resume','inspect','save','receipt'] and args.get('transaction_id')!=self.transaction_id:return False
        if action=='author_prepare':self.transaction_id=None;self.generation+=1;self.clear_transaction()
        if not super().begin(action,args,tab):return False
        self.active_generation=self.generation;return True
    def finish(self,result):
        action,args,tab=self.active;epoch=self.active_generation;tx=args.get('transaction_id')
        self.active_generation=None
        if action in ['author_load','author_finish','publish','resume','inspect','save','receipt']:
            actual=result.get('transaction_id') or result.get('data',{}).get('receipt',{}).get('transaction_id')
            if epoch!=self.generation or tx!=self.transaction_id or actual is not None and actual!=tx:
                return self.finish_mismatch()
            if tx not in self.outcomes and len(self.outcomes)>=128:self.outcomes.pop(next(iter(self.outcomes)))
            self.outcomes.setdefault(tx,{})[action]=copy.deepcopy(result)
        refresh=super().finish(result)
        if action=='author_prepare' and result.get('transaction_id'):
            self.transaction_id=result['transaction_id'];self.generation+=1;self.clear_transaction();self.result=copy.deepcopy(result);self.preparation=copy.deepcopy(result)
        if action in ['author_load','author_finish']:self.preparation=copy.deepcopy(result)
        if action=='author_list' and result.get('status')=='OK':self.intents=copy.deepcopy(result['items']);self.intent_page={k:result[k] for k in ['has_more','next_after']}
        return refresh
    def finish_mismatch(self):
        self.busy=False;self.active=None;self.result={'status':'ERROR','code':'TRANSACTION_CONTEXT_MISMATCH'};self.status='Результат относится к другой записи; проверь квитанцию'
        if self.closing:self.closed=True
        return False
    def receipt_args(self,tx):
        args=super().receipt_args(tx)
        if args['expected_manifest_sha256'] is None and self.preparation and self.preparation.get('transaction_id')==tx:args['expected_manifest_sha256']=self.preparation.get('manifest_sha256')
        return args

def display(result,*,technical=False,labels=None):
    if technical or result.get('result_kind')!='local_bank_authoring':return base.display(result,technical=technical,labels=labels)
    state=result['status'];code=result['code'];labels={'PREPARED':'Материал подготовлен. Опубликуй пакет и сохрани его в Bank.','SEALED':'Копия проверена. Заверши подготовку этой же записи.','INCOMPLETE':'Подготовка прервана. Сохранённые части оставлены для проверки.','RETRYABLE_BUSY':'Другая операция использует рабочую папку. Повтори после её завершения.','CANCELLED':'Подготовка отменена до создания записи.','REJECTED':'Материал не подготовлен. Проверь поля и указанный лимит.'}
    lines=[labels.get(state,state)+'\n'+code]
    preview=result.get('preview',{});v=preview.get('values',{})
    if v:lines.append('\n'.join(str(v[k]) for k in ['title','filename','uri','body'] if k in v))
    if v.get('kind')=='url':lines.append('Ссылка сохранена без скачивания содержимого.')
    if preview.get('truncated_fields'):lines.append('Предпросмотр сокращён; сохранённый материал не изменён.')
    if code in ['INPUT_NOT_SEALED','INTENT_NOT_PUBLISHED']:lines.append('Эта запись не возобновляется из исходника. Новый ввод требует явного создания новой записи.')
    if result.get('sealed_input_may_exist'):lines.append('Полная копия могла сохраниться. Открой и проверь эту же запись.')
    lines.append('Подготовка ещё не подтверждает сохранение в Bank.')
    raw=''.join(c if ord(c)>=32 or c in '\n\t' else '�' for c in '\n\n'.join(lines)).encode('utf-8')
    return raw[:65536].decode('utf-8','ignore')
