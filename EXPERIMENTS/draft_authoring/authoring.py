"""Bounded immutable new-intent preparation, separate from Bank acceptance."""
from pathlib import Path
from contextlib import ExitStack,contextmanager
import copy,datetime,hashlib,json,os,sys,time,uuid
from jsonschema import Draft202012Validator,FormatChecker
import authoring_io as io
ROOT=io.ROOT
sys.path.insert(0,str(ROOT/'EXPERIMENTS/package_producer'))
import producer
im=producer.im;reader=im.reader
encoded=producer.encoded
sha=lambda b:hashlib.sha256(b).hexdigest()
ROLES={'bank','intake','stage','cache','output','source','authoring'}
VERSION='r1-authoring/1'
PRODUCER={'name':'research-bank-authoring','version':'1'}

class Problem(ValueError):
    def __init__(self,code):self.code=code;super().__init__(code)

class Cancelled(Exception):pass

def need(ok,code):
    if not ok:raise Problem(code)

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')

def text(value,cap,*,optional=False):
    if optional and value is None:return None
    need(type(value) is str,'INVALID_INPUT')
    try:raw=value.encode('utf-8')
    except UnicodeError as e:raise Problem('INVALID_INPUT') from e
    need(len(raw)<=cap,'AUTHORING_INPUT_LIMIT')
    need(bool(value.strip()),'EMPTY_INPUT')
    return value

class Budget:
    def __init__(self,workspace,cancel=None):self.w=workspace;self.cancel=cancel;self.start=time.monotonic();self.bytes=0
    def tick(self,cancellable=True):
        if cancellable and self.cancel and self.cancel():raise Cancelled()
        need((time.monotonic()-self.start)*1000<=self.w.limits['capture_elapsed_ms'],'AUTHORING_WORK_LIMIT')
    def charge(self,size,cancellable=True):
        self.tick(cancellable);self.bytes+=size;need(self.bytes<=self.w.limits['work_bytes'],'AUTHORING_WORK_LIMIT')

class Workspace:
    def __init__(self,roots,*,_portable_fixture=False,_limits=None,_hook=None):
        self.roots={k:Path(v) for k,v in roots.items()};self.portable=_portable_fixture;self.hook=_hook
        raw=(Path(__file__).parent/'LIMITS.json').read_bytes()
        self.limits=reader.strict_json(raw,32768,16);self.limits.update(_limits or {});self._validate_limits(self.limits)
        self.contracts=im.Contracts();self.dv=Draft202012Validator(json.loads((ROOT/'EXPERIMENTS/package_producer/draft.schema.json').read_bytes()),format_checker=FormatChecker())
    @staticmethod
    def _validate_limits(limits):
        need(limits.get('policy_version')==VERSION,'UNSUPPORTED_AUTHORING_PROFILE')
        required={'intents','workspace_bytes_including_managed_source','intent_record_bytes','seal_record_bytes','source_path_utf8_bytes','title_utf8_bytes','filename_utf8_bytes','locator_utf8_bytes','identity_or_model_utf8_bytes','body_utf8_bytes','document_bytes','chunk_bytes','capture_elapsed_ms','page_items','workspace_scan_entries','per_request_output_bytes','work_bytes'}
        need(required<=set(limits),'INVALID_AUTHORING_PROFILE')
        need(all(type(limits[k]) is int and limits[k]>=0 for k in required),'INVALID_AUTHORING_PROFILE')
        need(limits['chunk_bytes']>0 and limits['page_items']>0,'INVALID_AUTHORING_PROFILE')
    def event(self,name,value=None):
        if self.hook:self.hook(name,value)
    @contextmanager
    def session(self):
        need(os.name=='nt' or self.portable,'UNSUPPORTED_PLATFORM');need(set(self.roots)==ROLES,'INVALID_ROOT_CONFIGURATION')
        paths=list(self.roots.values());need(all(p.is_absolute() and '..' not in p.parts for p in paths),'INVALID_ROOT_CONFIGURATION')
        need(all(not(a.is_relative_to(b) or b.is_relative_to(a)) for i,a in enumerate(paths) for b in paths[i+1:]),'ROOT_OVERLAP')
        with ExitStack() as stack:
            for p in paths:stack.enter_context(io.Directory(p,write=True,root=True))
            stack.enter_context(io.WorkspaceLock(self.roots['authoring']/'LOCK'))
            yield stack
    def usage(self):
        entries=0;size=0;intents=0
        def walk(path):
            nonlocal entries,size
            with os.scandir(path) as it:
                for e in it:
                    # The OS lease deliberately denies other opens of LOCK.
                    # Windows DirEntry.stat may open a file handle; account for
                    # the verified empty lock separately instead of probing it.
                    if path==self.roots['authoring'] and e.name=='LOCK':continue
                    entries+=1;need(entries<=self.limits['workspace_scan_entries'],'AUTHORING_SCAN_LIMIT')
                    s=e.stat(follow_symlinks=False);need(not e.is_symlink() and not getattr(s,'st_file_attributes',0)&0x400,'UNTRUSTED_WORKSPACE_ENTRY')
                    if e.is_dir(follow_symlinks=False):walk(Path(e.path))
                    else:
                        need(e.is_file(follow_symlinks=False),'UNTRUSTED_WORKSPACE_ENTRY')
                        # Windows FindFirstFile metadata has st_nlink=0. The
                        # unchanged private File adapter verifies actual links,
                        # identity, ACL and final path through a pinned handle.
                        with io.File(Path(e.path)) as f:size+=f.size();f.check()
        with os.scandir(self.roots['authoring']) as it:
            for e in it:
                if e.name=='LOCK':continue
                need(reader.UUID.fullmatch(e.name) is not None and e.is_dir(follow_symlinks=False) and not e.is_symlink(),'UNTRUSTED_WORKSPACE_ENTRY');intents+=1
        walk(self.roots['authoring']);walk(self.roots['source']);return size,intents
    def fields(self,data):
        need(type(data) is dict and data.get('kind') in ['file','url','note'],'INVALID_INPUT')
        kind=data['kind'];allowed={'kind','title'}|({'path'} if kind=='file' else {'uri'} if kind=='url' else {'body','author_kind','identity','model','content_format'})
        need(set(data)<=allowed and {'kind','title'}<=set(data),'INVALID_INPUT');v=copy.deepcopy(data)
        text(v['title'],min(self.limits['title_utf8_bytes'],self.contracts.policy['title_bytes']))
        if kind=='file':
            text(v.get('path'),self.limits['source_path_utf8_bytes']);need('\x00' not in v['path'],'INVALID_SOURCE_PATH');text(Path(v['path']).name,self.limits['filename_utf8_bytes'])
        elif kind=='url':
            text(v.get('uri'),min(self.limits['locator_utf8_bytes'],self.contracts.policy['locator_bytes']));need(v['uri'].startswith(('http://','https://','file://')) and FormatChecker().conforms(v['uri'],'uri'),'INVALID_URI')
        else:
            text(v.get('body'),min(self.limits['body_utf8_bytes'],self.contracts.policy['annotation_body_bytes']));v.setdefault('author_kind','unknown');v.setdefault('identity',None);v.setdefault('model',None);v.setdefault('content_format','plain_text')
            need(v['author_kind'] in ['user','ai','unknown'] and v['content_format'] in ['plain_text','markdown'],'INVALID_INPUT')
            for k in ['identity','model']:text(v[k],self.limits['identity_or_model_utf8_bytes'],optional=True)
        return v
    def doc(self,intent,original=None):
        f=intent['fields'];kind=f['kind'];typ='Annotation' if kind=='note' else 'Asset';origin={'user':'user_authored','ai':'ai_authored','unknown':'unknown'}.get(f.get('author_kind'),'unknown') if kind=='note' else ('user_capture' if kind=='url' else 'unknown')
        provenance={'origin_kind':origin,'producer':PRODUCER,'source_locator':f['uri'] if kind=='url' else None,'captured_at':intent['created_at'] if kind!='note' else None,'source_ref':None,'derived_from':[]}
        if kind=='file':data={'storage':{'mode':'bytes','file_path':'payload/original.bin','byte_length':original[0],'sha256':original[1],'media_type':'application/octet-stream','original_filename':Path(f['path']).name}}
        elif kind=='url':data={'storage':{'mode':'locator','uri':f['uri'],'label':None}}
        else:data={'kind':'note','content_format':f['content_format'],'body':f['body'],'author':{'kind':f['author_kind'],'identity':f['identity'],'model':f['model']},'targets':[]}
        return {'schema':'bank-annotation/1' if typ=='Annotation' else 'bank-asset/1','object_type':typ,'object_id':intent['object_id'],'revision_id':intent['revision_id'],'revision_created_at':intent['created_at'],'title':f['title'],'provenance':provenance,'data':data}
    def draft(self,intent,doc,files):
        return {'protocol':'local-bank-draft/1','transaction_id':intent['transaction_id'],'command':'commit_revisions','intent':'independent_save','created_at':intent['created_at'],'producer':PRODUCER,'operations':[{'object_id':doc['object_id'],'revision_id':doc['revision_id'],'base_revision_id':None,'type':doc['object_type'],'schema_ref':doc['schema'],'document_path':'docs/object.json'}],'files':sorted(files)}
    def small(self,path,cap,budget):
        with io.File(path) as f:
            need(f.size()<=cap,'AUTHORING_WORK_LIMIT');parts=[];count=0
            while b:=f.read(self.limits['chunk_bytes']):count+=len(b);need(count<=cap,'AUTHORING_WORK_LIMIT');budget.charge(len(b),False);parts.append(b)
            f.check();need(count==f.size(),'CONTROL_CHANGED');return b''.join(parts)
    def parse(self,raw,cap):return reader.strict_json(raw,cap,self.contracts.policy['json_container_depth'])
    def write(self,path,raw,budget,phase):
        budget.charge(len(raw))
        with io.File(path,new=True) as f:f.write(raw);f.flush()
        need(self.small(path,len(raw),budget)==raw,'WRITE_READBACK');self.event(phase,path)
    def control(self,parent,name,raw,budget,phase):
        pending=parent/(name+'.pending');self.write(pending,raw,budget,phase+'_pending');io.move_no_replace(pending,parent/(name+'.json'));self.event(phase,parent/(name+'.json'))
    def result(self,tx,status,code,**kw):
        value={'result_kind':'local_bank_authoring','result_version':1,'transaction_id':tx,'status':status,'code':code,'Bank_accepted':False,**kw}
        if len(encoded(value))>self.limits['per_request_output_bytes']:return {'result_kind':'local_bank_authoring','result_version':1,'transaction_id':tx,'status':'ERROR','code':'AUTHORING_RESULT_LIMIT','Bank_accepted':False}
        return value
    def display_fields(self,f):
        v={};truncated=[]
        for k,x in f.items():
            if k=='path':x=Path(x).name;k='filename'
            if isinstance(x,str):
                cap=4096 if k=='body' else 512;raw=x.encode('utf-8');v[k]=raw[:cap].decode('utf-8','ignore')
                if len(raw)>cap:truncated.append(k)
            else:v[k]=x
        return {'values':v,'truncated_fields':truncated,'preview_only':True}
    def prepare(self,data,*,cancel=None):
        tx=None;budget=Budget(self,cancel);sealed=False
        try:
            fields=self.fields(data)
            with self.session() as stack:
                original=None
                if fields['kind']=='file':
                    original=stack.enter_context(io.SelectedOriginal(fields['path'],self.roots.values(),portable_fixture=self.portable));need(original.size()<=self.contracts.policy['file_bytes'],'AUTHORING_INPUT_LIMIT')
                ids=[str(uuid.uuid4()) for _ in range(3)];intent={'protocol':'local-bank-authoring-intent/1','transaction_id':ids[0],'object_id':ids[1],'revision_id':ids[2],'created_at':utc(),'fields':fields,'profile':copy.deepcopy(self.limits)}
                sample=self.doc(intent,(original.size(),'0'*64) if original else None);self.contracts.schema(sample);raw_sample=encoded(sample);need(len(raw_sample)<=min(self.limits['document_bytes'],self.contracts.policy['object_json_bytes']),'AUTHORING_INPUT_LIMIT')
                raw_intent=encoded(intent);need(len(raw_intent)<=self.limits['intent_record_bytes'],'AUTHORING_INPUT_LIMIT')
                size,count=self.usage();reserve=len(raw_intent)+len(raw_sample)+self.limits['seal_record_bytes']+self.contracts.policy['manifest_bytes']+(original.size() if original else 0)
                work_reserve=2*len(raw_intent)+4*len(raw_sample)+2*self.limits['seal_record_bytes']+3*self.contracts.policy['manifest_bytes']+2*(original.size() if original else 0)
                need(work_reserve<=self.limits['work_bytes'],'AUTHORING_WORK_LIMIT')
                need(count<self.limits['intents'] and size+reserve<=self.limits['workspace_bytes_including_managed_source'],'AUTHORING_WORKSPACE_LIMIT');budget.tick()
                journal=self.roots['authoring']/ids[0];source=self.roots['source']/ids[0];need(not io.present(journal) and not io.present(source),'INTENT_COLLISION')
                tx=ids[0];io.mkdir(journal);stack.enter_context(io.Directory(journal,write=True));self.control(journal,'INTENT',raw_intent,budget,'intent_published')
                io.mkdir(source);stack.enter_context(io.Directory(source,write=True));self.event('source_created',source);io.mkdir(source/'docs');descriptors=[]
                if original:
                    io.mkdir(source/'payload');digest=hashlib.sha256();count=0
                    with io.File(source/'payload/original.bin',new=True) as f:
                        while b:=original.read(self.limits['chunk_bytes']):
                            count+=len(b);need(count<=self.contracts.policy['file_bytes'],'AUTHORING_INPUT_LIMIT');budget.charge(len(b));digest.update(b);f.write(b);self.event('capture_chunk',tx)
                        need(count==original.size(),'SOURCE_CHANGED');original.check();f.flush()
                    original_descriptor=(count,digest.hexdigest());descriptors.append({'path':'payload/original.bin','byte_length':count,'sha256':digest.hexdigest()});self.event('original_flushed',tx)
                else:original_descriptor=None
                doc=self.doc(intent,original_descriptor);self.contracts.schema(doc);raw_doc=encoded(doc);need(len(raw_doc)<=min(self.limits['document_bytes'],self.contracts.policy['object_json_bytes']),'AUTHORING_INPUT_LIMIT');self.write(source/'docs/object.json',raw_doc,budget,'document_flushed');descriptors.append({'path':'docs/object.json','byte_length':len(raw_doc),'sha256':sha(raw_doc)});descriptors.sort(key=lambda f:f['path'])
                draft=self.draft(intent,doc,[f['path'] for f in descriptors]);need(next(self.dv.iter_errors(draft),None) is None,'INVALID_DRAFT');raw_draft=encoded(draft);need(len(raw_draft)<=self.contracts.policy['manifest_bytes'],'AUTHORING_INPUT_LIMIT');self.write(source/'DRAFT.pending',raw_draft,budget,'draft_flushed')
                seal={'protocol':'local-bank-authoring-seal/1','transaction_id':tx,'intent_sha256':sha(raw_intent),'draft_sha256':sha(raw_draft),'files':descriptors};raw_seal=encoded(seal);need(len(raw_seal)<=self.limits['seal_record_bytes'],'AUTHORING_INPUT_LIMIT')
                budget.tick();self.write(journal/'SEAL.pending',raw_seal,budget,'seal_published_pending');io.move_no_replace(journal/'SEAL.pending',journal/'SEAL.json');sealed=True;self.event('seal_published',journal/'SEAL.json')
                self.verify_source(intent,seal,raw_intent,'DRAFT.pending',budget);io.move_no_replace(source/'DRAFT.pending',source/'DRAFT.json');self.event('draft_published',tx)
                return self.prepared_result(intent,seal,draft)
        except Cancelled:return self.result(tx,'INCOMPLETE' if tx else 'CANCELLED','SEALED_VERIFY_REQUIRED' if sealed else 'PREPARATION_CANCELLED')
        except BaseException as e:
            if not isinstance(e,Exception) and not isinstance(e,KeyboardInterrupt):raise
            return self.failure(tx,e,sealed)
    def failure(self,tx,e,sealed=False):
        code=getattr(e,'code',str(e) if isinstance(e,reader.Rejected) else 'AUTHORING_IO_ERROR')
        if isinstance(e,KeyboardInterrupt):code='INTERRUPTED'
        if isinstance(e,OSError) and (getattr(e,'winerror',None) in (32,33) or e.errno in (16,11)):code='AUTHORING_BUSY'
        if isinstance(e,io.n.SafetyError):code=str(e)
        if isinstance(e,io.private_io.Refused):code=str(e)
        code=producer.commands.code_text(code,'AUTHORING_IO_ERROR')
        status='RETRYABLE_BUSY' if code=='AUTHORING_BUSY' else ('INCOMPLETE' if tx else 'REJECTED')
        return self.result(tx,status,code,sealed_input_may_exist=bool(sealed))
    def read_intent(self,tx,budget):
        raw=self.small(self.roots['authoring']/tx/'INTENT.json',self.limits['intent_record_bytes'],budget);d=self.parse(raw,self.limits['intent_record_bytes'])
        need(type(d) is dict and set(d)=={'protocol','transaction_id','object_id','revision_id','created_at','fields','profile'},'INVALID_INTENT');need(d['protocol']=='local-bank-authoring-intent/1' and d['transaction_id']==tx,'INVALID_INTENT')
        need(all(type(d[k]) is str and reader.UUID.fullmatch(d[k]) for k in ['transaction_id','object_id','revision_id']),'INVALID_INTENT');need(len({d[k] for k in ['transaction_id','object_id','revision_id']})==3,'INVALID_INTENT')
        self._validate_limits(d['profile']);need(type(d['created_at']) is str and d['created_at'].endswith('Z') and FormatChecker().conforms(d['created_at'],'date-time'),'INVALID_INTENT');need(self.fields(d['fields'])==d['fields'] and raw==encoded(d),'INVALID_INTENT');return d,raw
    def read_seal(self,tx,budget):
        raw=self.small(self.roots['authoring']/tx/'SEAL.json',self.limits['seal_record_bytes'],budget);d=self.parse(raw,self.limits['seal_record_bytes']);need(type(d) is dict and set(d)=={'protocol','transaction_id','intent_sha256','draft_sha256','files'},'INVALID_SEAL');need(d['protocol']=='local-bank-authoring-seal/1' and d['transaction_id']==tx,'INVALID_SEAL');need(all(type(d[k]) is str and len(d[k])==64 and all(c in '0123456789abcdef' for c in d[k]) for k in ['intent_sha256','draft_sha256']),'INVALID_SEAL');need(type(d['files']) is list and 1<=len(d['files'])<=2,'INVALID_SEAL')
        for f in d['files']:need(type(f) is dict and set(f)=={'path','byte_length','sha256'} and type(f['path']) is str and type(f['byte_length']) is int and f['byte_length']>=0 and type(f['sha256']) is str and len(f['sha256'])==64 and all(c in '0123456789abcdef' for c in f['sha256']),'INVALID_SEAL')
        need(raw==encoded(d),'INVALID_SEAL');return d
    def verify_source(self,intent,seal,intent_raw,draft_name,budget):
        tx=intent['transaction_id'];need(seal['intent_sha256']==sha(intent_raw),'INTENT_INTEGRITY');source=self.roots['source']/tx
        names=['docs/object.json']+(['payload/original.bin'] if intent['fields']['kind']=='file' else []);need([f['path'] for f in seal['files']]==sorted(names),'SEAL_INVENTORY')
        with ExitStack() as stack:
            stack.enter_context(io.Directory(source,write=True));pub=producer.Publisher(self.roots['intake'],self.roots['source'],_portable_fixture=self.portable);parents=pub._parts(names)
            for p in parents:stack.enter_context(io.Directory(source/p,write=True))
            pub._inventory(source,names,parents,[draft_name]);raw=self.small(source/draft_name,self.contracts.policy['manifest_bytes'],budget);need(sha(raw)==seal['draft_sha256'],'DRAFT_INTEGRITY');draft=self.parse(raw,self.contracts.policy['manifest_bytes']);need(next(self.dv.iter_errors(draft),None) is None,'INVALID_DRAFT');descriptors={}
            for f in seal['files']:
                cap=min(self.limits['document_bytes'],self.contracts.policy['object_json_bytes']) if f['path']=='docs/object.json' else self.contracts.policy['file_bytes'];need(f['byte_length']<=cap,'AUTHORING_WORK_LIMIT');digest=hashlib.sha256();count=0
                with io.File(source/f['path']) as handle:
                    need(handle.size()==f['byte_length'],'PREPARED_FILE_INTEGRITY')
                    while b:=handle.read(self.limits['chunk_bytes']):count+=len(b);budget.charge(len(b),False);need(count<=cap,'AUTHORING_WORK_LIMIT');digest.update(b)
                    handle.check();need(count==handle.size() and digest.hexdigest()==f['sha256'],'PREPARED_FILE_INTEGRITY')
                descriptors[f['path']]=(f['byte_length'],f['sha256'])
            raw_doc=self.small(source/'docs/object.json',min(self.limits['document_bytes'],self.contracts.policy['object_json_bytes']),budget);doc=self.parse(raw_doc,self.contracts.policy['object_json_bytes']);expected=self.doc(intent,descriptors.get('payload/original.bin'));need(doc==expected,'PREPARED_DOCUMENT_MISMATCH');expected_draft=self.draft(intent,expected,names);need(draft==expected_draft,'PREPARED_DRAFT_MISMATCH');im.Store._doc_check(self,doc,draft['operations'][0],descriptors,self.contracts.policy);return draft
    def prepared_result(self,intent,seal,draft,status='PREPARED'):
        manifest={**draft,'protocol':reader.PROTOCOL,'files':seal['files']};raw=encoded(manifest);need(len(raw)<=self.contracts.policy['manifest_bytes'] and len(raw)+sum(f['byte_length'] for f in seal['files'])+self.contracts.policy['ready_bytes']<=self.contracts.policy['package_bytes'],'AUTHORING_INPUT_LIMIT')
        return self.result(intent['transaction_id'],status,'INPUT_VERIFIED' if status=='PREPARED' else 'FINISH_PREPARATION_REQUIRED',ref={'object_type':'Annotation' if intent['fields']['kind']=='note' else 'Asset','object_id':intent['object_id'],'revision_id':intent['revision_id']},manifest_sha256=sha(raw),preview=self.display_fields(intent['fields']))
    def inspect(self,tx,*,finish=False):
        budget=Budget(self)
        try:
            need(type(tx) is str and reader.UUID.fullmatch(tx),'INVALID_TRANSACTION_ID')
            with self.session() as stack:
                journal=self.roots['authoring']/tx
                if not io.present(journal):return self.result(tx,'NOT_FOUND','INTENT_NOT_FOUND')
                stack.enter_context(io.Directory(journal,write=True))
                if not io.present(journal/'INTENT.json'):return self.result(tx,'INCOMPLETE','INTENT_NOT_PUBLISHED')
                intent,raw=self.read_intent(tx,budget)
                if not io.present(journal/'SEAL.json'):return self.result(tx,'INCOMPLETE','INPUT_NOT_SEALED',preview=self.display_fields(intent['fields']))
                seal=self.read_seal(tx,budget);source=self.roots['source']/tx;marker='DRAFT.json' if io.present(source/'DRAFT.json') else 'DRAFT.pending';draft=self.verify_source(intent,seal,raw,marker,budget)
                if marker=='DRAFT.pending':
                    if not finish:return self.prepared_result(intent,seal,draft,'SEALED')
                    with io.Directory(source,write=True):io.move_no_replace(source/'DRAFT.pending',source/'DRAFT.json');self.event('draft_published',tx)
                return self.prepared_result(intent,seal,draft)
        except Exception as e:return self.failure(tx if type(tx) is str and reader.UUID.fullmatch(tx) else None,e)
    def listing(self,after=None):
        budget=Budget(self)
        try:
            need(after is None or type(after) is str and reader.UUID.fullmatch(after),'INVALID_CURSOR')
            with self.session():
                _,count=self.usage();need(count<=self.limits['intents'],'AUTHORING_SCAN_LIMIT');ids=[]
                with os.scandir(self.roots['authoring']) as entries:
                    for e in entries:
                        if e.name!='LOCK':ids.append(e.name)
                ids=sorted(n for n in ids if after is None or n>after);selected=ids[:self.limits['page_items']];items=[]
                for tx in selected:
                    with io.Directory(self.roots['authoring']/tx,write=True):
                        if not io.present(self.roots['authoring']/tx/'INTENT.json'):items.append({'transaction_id':tx,'title':'Прерванная подготовка','kind':None,'state':'INCOMPLETE'});continue
                        intent,_=self.read_intent(tx,budget);items.append({'transaction_id':tx,'title':self.display_fields(intent['fields'])['values']['title'],'kind':intent['fields']['kind'],'state':'UNVERIFIED'})
                return self.result(None,'OK','INTENT_PAGE',items=items,has_more=len(ids)>len(selected),next_after=selected[-1] if len(ids)>len(selected) else None)
        except Exception as e:return self.failure(None,e)
