"""Headless single-worker orchestration of observation, cache and pinned reads."""
from pathlib import Path
from contextlib import ExitStack
import copy,hashlib,json,os,sqlite3,sys,time
import runtime,attempts
sys.path.insert(0,str(runtime.ROOT/'EXPERIMENTS/draft_authoring'))
import authoring_presenter as p
im=p.a.im

def observe(root,context):
    c=None;start=time.monotonic()
    try:
        with im.Store(root) as store:
            c=store._connect(False,_allow_recovery=False)
            try:
                steps=[0]
                def progress():
                    steps[0]+=1000;return int(steps[0]>200000 or time.monotonic()-start>1)
                c.set_progress_handler(progress,1000);c.execute('BEGIN')
                row=c.execute('SELECT commit_sequence,commit_id FROM commits ORDER BY commit_sequence DESC LIMIT 1').fetchone()
                token=[row[0],row[1]] if row else [0,None]
                p.a.need(type(token[0])is int and 0<=token[0]<=9007199254740991 and (token[1] is None or p.a.reader.UUID.fullmatch(token[1])),'INVALID_BANK_SIGNAL')
                st=store.db.stat();identity=[st.st_dev,st.st_ino,str(store.root)]
                return {'status':'OK','code':'BANK_OBSERVED','context':context,'token':token,'identity':identity}
            finally:c.close();c=None
    except sqlite3.Error as e:return {'status':'ERROR','code':'BANK_BUSY' if (getattr(e,'sqlite_errorcode',0) or 0)&255 in [5,6] else 'BANK_DISCONNECTED','context':context}
    except Exception:return {'status':'ERROR','code':'BANK_DISCONNECTED','context':context}

def cache_ready(roots,token):
    search=p.base.commands.search
    try:
        with search.Cache(roots['cache'],roots['bank'],search.SearchAPI(roots['bank'],roots['cache']).limits) as cache:
            c=cache.connect(search.Budget(cache.limits),recovery=False)
            try:return cache.metadata(c)[0]==token[0]
            finally:c.close()
    except Exception:return False

class Backend(p.Backend):
    def __init__(self,roots,*,context='configured-bank',**kw):
        super().__init__(roots,**kw);self.context=context;self.roots={k:Path(v) for k,v in roots.items()}
        self.identity=hashlib.sha256(im.encoded({k:str(v) for k,v in sorted(self.roots.items())})).hexdigest()
    def dispatch(self,action,args):
        if action=='observe':
            out=observe(self.roots['bank'],self.context)
            if out['status']=='OK':out['cache_ready']=cache_ready(self.roots,out['token'])
            out['root_generation']=self.identity;return out
        if action=='attempts':return attempts.query(self.roots['bank'],{'protocol':attempts.QUERY,'operation':'attempt.get','transaction_id':args['transaction_id'],'before_rowid':args.get('before_rowid')})
        if action=='safeguard':return runtime.safeguard(self.roots,portable=self.workspace.portable)
        return super().dispatch(action,args)

class Flow:
    """Coalesced work only; the existing Bridge owns the one active worker."""
    def __init__(self,context,root_generation):
        self.context=context;self.root_generation=root_generation;self.token=None;self.identity=None;self.refresh_pending=True;self.rebuild_pending=True;self.search_pending=None;self.index_ready=False;self._index_notice='';self.notice='';self.disconnected=False;self.closing=False
    @property
    def notice(self):return ' '.join(x for x in [self._bank_notice,self._index_notice] if x)
    @notice.setter
    def notice(self,value):self._bank_notice=value
    def apply(self,action,result):
        if self.closing:return
        if action=='observe':
            if result.get('context')!=self.context or result.get('root_generation')!=self.root_generation:return
            if result['status']!='OK':self.disconnected=True;self.notice='Bank недоступен; показаны прежние данные / '+result['code'];return
            if self.disconnected:self.notice='Соединение с Bank восстановлено';self.disconnected=False
            changed=(result['token']!=self.token or result['identity']!=self.identity)
            if changed:
                self.refresh_pending=True;self.notice='Bank обновился. Открытый материал и выбранная запись истории сохранены.' if self.token is not None else ''
                self.token=copy.deepcopy(result['token']);self.identity=copy.deepcopy(result['identity'])
            self.index_ready=result['cache_ready']
            if self.index_ready:self._index_notice=''
            if changed and not self.index_ready:self.rebuild_pending=True
        elif action in ['save','author_save','object_save','continue_save'] and result['status'] in ['ACCEPTED','REPLAY']:
            self.refresh_pending=True;self.rebuild_pending=True;self.index_ready=False
        elif action=='rebuild':
            self.index_ready=result['status']=='BUILT'
            self._index_notice='' if self.index_ready else 'Поиск пока недоступен / '+result.get('code','INDEX_UNAVAILABLE')
    def search(self,args):self.search_pending=copy.deepcopy(args)
    def next(self):
        if self.closing:return None
        if self.refresh_pending:self.refresh_pending=False;return ('list',{'protocol':p.base.discovery.PROTOCOL,'object_types':p.base.TYPES,'snapshot_sequence':None,'after_object_id':None,'limit':10},'Bank')
        if self.rebuild_pending:self.rebuild_pending=False;return ('rebuild',{},None)
        if self.search_pending is not None:
            args=self.search_pending;self.search_pending=None;return ('search',args,'Search')
        return None
    def close(self):self.closing=True;self.search_pending=None;self.refresh_pending=False;self.rebuild_pending=False
