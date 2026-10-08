"""Bounded prepared-draft publisher; package publication is never Bank acceptance."""
from pathlib import Path
from contextlib import ExitStack
import argparse,errno,hashlib,json,os,sys,time
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'EXPERIMENTS/local_command_adapter'))
import commands
im=commands.im;reader=im.reader
import producer_io as io
class Problem(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)
def need(ok,code):
    if not ok:raise Problem(code)
def encoded(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
class Budget:
    def __init__(self,limits):self.limits=limits;self.start=time.monotonic();self.bytes=0;self.metadata=0
    def tick(self):need((time.monotonic()-self.start)*1000<=self.limits['elapsed_ms'],'LIMIT_EXCEEDED')
    def charge(self,size,metadata=False):
        self.bytes+=size
        if metadata:self.metadata+=size
        need(self.bytes<=self.limits['work_bytes'] and self.metadata<=self.limits['metadata_bytes'],'LIMIT_EXCEEDED');self.tick()
class Publisher:
    def __init__(self,intake_root,source_root=None,*,_hook=None,_limits=None,_portable_fixture=False):
        self.intake=Path(intake_root);self.source=Path(source_root) if source_root is not None else None;self.hook=_hook;self.portable=_portable_fixture;self.contracts=im.Contracts();folder=Path(__file__).parent;self.limits=json.loads((folder/'LIMITS.json').read_text());self.limits.update(_limits or {});self.draft_validator=Draft202012Validator(json.loads((folder/'draft.schema.json').read_text()),format_checker=FormatChecker());self.result_validator=Draft202012Validator(json.loads((folder/'result.schema.json').read_text()))
    def _event(self,name,value=None):
        if self.hook:self.hook(name,value)
    def _config(self,source):
        need(os.name=='nt' or self.portable,'UNSUPPORTED_PLATFORM');paths=[self.intake]+([self.source] if self.source is not None else [])
        need(all(p.is_absolute() and '..' not in p.parts for p in paths),'INVALID_ROOT_CONFIGURATION')
        need(not source or self.source is not None,'SOURCE_NOT_CONFIGURED')
        if self.source is not None:need(not self.source.is_relative_to(self.intake) and not self.intake.is_relative_to(self.source),'ROOT_OVERLAP')
    def _parts(self,names):
        need(len(names)==len(set(names)),'DUPLICATE_FILE');parents=set()
        for name in names:
            reader.valid_path(name);need(name!='draft.json','RESERVED_DRAFT_CONTROL')
            pieces=name.split('/')
            for i in range(1,len(pieces)):parents.add('/'.join(pieces[:i]))
        need(not set(names)&parents,'FILE_DIRECTORY_COLLISION');need(len(parents)<=self.limits['directories'],'LIMIT_EXCEEDED');return sorted(parents,key=lambda x:(x.count('/'),x))
    def _inventory(self,base,names,parents,controls):
        seen=set();dirs=set();cap=len(names)+len(parents)+len(controls);count=0
        for parent in ['',*parents]:
            with os.scandir(base/parent) as entries:
                for entry in entries:
                    count+=1;need(count<=cap,'EXTRA_ENTRY');name=(parent+'/' if parent else '')+entry.name;s=entry.stat(follow_symlinks=False);need(not entry.is_symlink() and not getattr(s,'st_file_attributes',0)&0x400,'REPARSE_POINT')
                    if entry.is_dir(follow_symlinks=False):need(name in parents,'EXTRA_DIRECTORY');dirs.add(name)
                    else:need(name in set(names)|set(controls),'EXTRA_FILE');seen.add(name)
        need(seen==set(names)|set(controls) and dirs==set(parents),'INVENTORY_MISMATCH')
    def _chunks(self,f,cap,budget,metadata=False):
        need(f.size()<=cap,'LIMIT_EXCEEDED');f.seek();count=0
        while raw:=f.read(self.contracts.policy['blob_chunk_bytes']):
            count+=len(raw);need(count<=cap,'LIMIT_EXCEEDED');budget.charge(len(raw),metadata);yield raw
        need(count==f.size(),'FILE_CHANGED');f.check()
    def _small(self,f,cap,budget):return b''.join(self._chunks(f,cap,budget,True))
    def _hash(self,f,cap,budget):
        h=hashlib.sha256();count=0
        for raw in self._chunks(f,cap,budget):h.update(raw);count+=len(raw)
        return count,h.hexdigest()
    def _documents(self,ops,files,handles,budget):
        need(len(ops)<=self.contracts.policy['operations'],'LIMIT_EXCEEDED');oids=set();rids=set();paths=set();docs={}
        for op in ops:
            need(op['object_id'] not in oids and op['revision_id'] not in rids and op['document_path'] not in paths,'DUPLICATE_OPERATION');oids.add(op['object_id']);rids.add(op['revision_id']);paths.add(op['document_path']);need(op['document_path'] in handles,'UNLISTED_DOCUMENT')
            raw=self._small(handles[op['document_path']],self.contracts.policy['object_json_bytes'],budget);d=reader.strict_json(raw,self.contracts.policy['object_json_bytes'],self.contracts.policy['json_container_depth'])
            # Reuse unchanged pure validation; no Store construction/connection.
            im.Store._doc_check(self,d,op,files,self.contracts.policy);docs[d['object_id']]=d
        for d in docs.values():
            for ref in im.Store._refs(d):
                if ref['object_id'] in docs and ref['revision_id']==docs[ref['object_id']]['revision_id']:
                    target=docs[ref['object_id']];need(ref['object_type']==target['object_type'] and ref['revision_id']==target['revision_id'],'INTERNAL_REFERENCE_MISMATCH')
    def _header(self,m,tx):
        self.contracts.envelope(m);need(m.get('transaction_id')==tx and m.get('intent')=='independent_save','UNSUPPORTED_COMMAND');need(len(m['files'])<=self.contracts.policy['files'] and len(m['operations'])<=self.contracts.policy['operations'],'LIMIT_EXCEEDED')
        names=[f['path'] for f in m['files']];parents=self._parts(names);files={f['path']:(f['byte_length'],f['sha256']) for f in m['files']}
        for op in m['operations']:need(op['document_path'] in files,'UNLISTED_DOCUMENT')
        for name,(size,_) in files.items():need(size<=self.contracts.policy['file_bytes'],'LIMIT_EXCEEDED')
        return names,parents,files
    def _prepare(self,stack,tx,budget):
        stack.enter_context(io.Directory(self.source,root=True));base=self.source/tx;stack.enter_context(io.Directory(base));draft_file=stack.enter_context(io.File(base/'DRAFT.json'));identity=draft_file.identity();raw=self._small(draft_file,self.limits['draft_bytes'],budget);d=reader.strict_json(raw,self.limits['draft_bytes'],self.contracts.policy['json_container_depth']);need(next(self.draft_validator.iter_errors(d),None)is None,'INVALID_DRAFT');need(d['transaction_id']==tx and d['intent']=='independent_save','UNSUPPORTED_COMMAND');names=d['files'];need(len(names)<=self.contracts.policy['files'] and len(d['operations'])<=self.contracts.policy['operations'],'LIMIT_EXCEEDED');parents=self._parts(names)
        for parent in parents:stack.enter_context(io.Directory(base/parent))
        self._inventory(base,names,parents,['DRAFT.json']);handles={};identities={};files={};total=0
        for name in sorted(names):
            f=stack.enter_context(io.File(base/name));handles[name]=f;identities[name]=f.identity();cap=self.contracts.policy['object_json_bytes'] if any(o['document_path']==name for o in d['operations']) else self.contracts.policy['file_bytes'];size,digest=self._hash(f,cap,budget);files[name]=(size,digest);total+=size;need(total<=self.contracts.policy['package_bytes'],'LIMIT_EXCEEDED')
        m={**d,'protocol':reader.PROTOCOL,'files':[{'path':n,'byte_length':v[0],'sha256':v[1]} for n,v in files.items()]};self._header(m,tx);self._documents(m['operations'],files,handles,budget);manifest=encoded(m);need(len(manifest)<=self.contracts.policy['manifest_bytes'],'LIMIT_EXCEEDED');ready=encoded({'protocol':reader.PROTOCOL,'transaction_id':tx,'manifest_byte_length':len(manifest),'manifest_sha256':im.sha(manifest)});need(total+len(manifest)+len(ready)<=self.contracts.policy['package_bytes'],'LIMIT_EXCEEDED');self._event('source_validated',base)
        return {'base':base,'draft_file':draft_file,'draft_identity':identity,'draft_raw':raw,'files':files,'handles':handles,'identities':identities,'parents':parents,'manifest':manifest,'ready':ready}
    def _source_check(self,p,budget):
        need(p['draft_file'].identity()==p['draft_identity'] and self._small(p['draft_file'],self.limits['draft_bytes'],budget)==p['draft_raw'],'SOURCE_CHANGED');self._inventory(p['base'],list(p['files']),p['parents'],['DRAFT.json'])
        for name,f in p['handles'].items():f.check();need(f.identity()==p['identities'][name],'SOURCE_CHANGED')
    def _write(self,path,chunks,budget,name):
        with io.File(path,new=True) as f:
            for raw in chunks:f.write(raw);self._event('copy_chunk',name)
            f.flush();self._event('file_flushed',name)
    def _audit(self,stack,base,tx,budget,pending=False,expected=None):
        stack.enter_context(io.Directory(base,write=True));marker=stack.enter_context(io.File(base/('READY.pending' if pending else 'READY.json')));markraw=self._small(marker,self.contracts.policy['ready_bytes'],budget);mark=reader.strict_json(markraw,self.contracts.policy['ready_bytes'],self.contracts.policy['json_container_depth']);self.contracts.envelope(mark);need(mark.get('transaction_id')==tx and 'manifest_sha256' in mark,'MARKER_INVALID')
        mf=stack.enter_context(io.File(base/'manifest.json'));raw=self._small(mf,self.contracts.policy['manifest_bytes'],budget);need(mark['manifest_byte_length']==len(raw) and mark['manifest_sha256']==im.sha(raw),'MANIFEST_INTEGRITY');m=reader.strict_json(raw,self.contracts.policy['manifest_bytes'],self.contracts.policy['json_container_depth']);names,parents,files=self._header(m,tx);need(sum(f[0] for f in files.values())+len(raw)+len(markraw)<=self.contracts.policy['package_bytes'],'LIMIT_EXCEEDED')
        if expected is not None:need(raw==expected['manifest'] and markraw==expected['ready'],'PACKAGE_CONTENT_CONFLICT')
        for parent in parents:stack.enter_context(io.Directory(base/parent,write=True))
        self._inventory(base,names,parents,['manifest.json','READY.pending' if pending else 'READY.json']);handles={}
        for name in names:
            f=stack.enter_context(io.File(base/name));handles[name]=f;need(self._hash(f,self.contracts.policy['file_bytes'],budget)==files[name],'FILE_INTEGRITY')
        self._documents(m['operations'],files,handles,budget);budget.tick();return im.sha(raw),len(files)
    def _result(self,tx,status,code,digest=None,published=None,count=None,*,_fallback=False):
        r={'result_kind':'local_bank_package_publication','result_version':1,'transaction_id':tx if isinstance(tx,str) and reader.UUID.fullmatch(tx) else None,'status':status,'code':commands.code_text(code,'PRODUCER_ERROR'),'manifest_sha256':digest,'published':published,'file_count':count,'Bank_accepted':False,'validation_scope':'prepared_R1_package_app_refs_CAS_pending'}
        need(next(self.result_validator.iter_errors(r),None)is None and len(encoded(r))<=(8192 if _fallback else self.limits['response_bytes']),'RESULT_CONFORMANCE');return r
    def execute(self,action,tx):
        budget=Budget(self.limits);digest=None;count=None;move_started=False;base=self.intake/tx if isinstance(tx,str) else self.intake
        try:
            need(action in ['publish','inspect','resume'] and isinstance(tx,str) and reader.UUID.fullmatch(tx),'INVALID_REQUEST');self._config(action!='inspect')
            with ExitStack() as stack:
                root=stack.enter_context(io.Directory(self.intake,write=True,root=True))
                if action=='inspect':
                    if not io.present(base):return self._result(tx,'NOT_FOUND','PACKAGE_NOT_FOUND',published=False)
                    stack.enter_context(io.Directory(base,write=True))
                    if not io.present(base/'READY.json'):return self._result(tx,'INCOMPLETE','READY_NOT_PUBLISHED',published=False)
                    digest,count=self._audit(stack,base,tx,budget);return self._result(tx,'PUBLISHED','PACKAGE_VERIFIED',digest,True,count)
                p=self._prepare(stack,tx,budget);digest=im.sha(p['manifest']);count=len(p['files']);exists=io.present(base)
                if not exists:
                    if action=='resume':return self._result(tx,'NOT_FOUND','PACKAGE_NOT_FOUND',digest,False,count)
                    try:io.mkdir(base)
                    except OSError as e:
                        if (getattr(e,'winerror',None) or e.errno) not in [17,80,183]:raise
                        exists=True
                if exists:
                    stack.enter_context(io.Directory(base,write=True))
                    if io.present(base/'READY.json'):
                        self._audit(stack,base,tx,budget,expected=p);return self._result(tx,'ALREADY_PUBLISHED','PACKAGE_UNCHANGED',digest,True,count)
                    if action!='resume':return self._result(tx,'INCOMPLETE','EXISTING_PACKAGE_INCOMPLETE',digest,False,count)
                    need(io.present(base/'READY.pending'),'PENDING_NOT_COMPLETE')
                else:
                    stack.enter_context(io.Directory(base,write=True));self._event('directory_created',base)
                    for parent in p['parents']:io.mkdir(base/parent);stack.enter_context(io.Directory(base/parent,write=True))
                    for name,f in p['handles'].items():self._write(base/name,self._chunks(f,self.contracts.policy['file_bytes'],budget),budget,name)
                    self._source_check(p,budget);self._write(base/'manifest.json',[p['manifest']],budget,'manifest.json');self._write(base/'READY.pending',[p['ready']],budget,'READY.pending')
                self._event('before_publish',base);self._source_check(p,budget);root.check();self._event('before_move',base)
                # Audit context closes its pending marker handle before rename;
                # directory leases remain held with write sharing/no delete.
                with ExitStack() as audit:self._audit(audit,base,tx,budget,pending=True,expected=p)
                for context in [root]:context.check()
                move_started=True;io.move_no_replace(base/'READY.pending',base/'READY.json');self._event('after_move',base)
                with ExitStack() as audit:self._audit(audit,base,tx,budget,expected=p)
                return self._result(tx,'PUBLISHED','READY_PUBLISHED',digest,True,count)
        except (Problem,im.Problem,reader.Rejected,io.Refused,im.native.SafetyError) as e:
            code=getattr(e,'code',str(e));status='UNKNOWN' if move_started else ('CONFLICT' if code=='PACKAGE_CONTENT_CONFLICT' else 'REJECTED')
        except KeyboardInterrupt:status='UNKNOWN' if move_started else 'CANCELLED';code='PUBLICATION_OUTCOME_UNKNOWN' if move_started else 'CANCELLED'
        except OSError as e:
            error=getattr(e,'winerror',None) or e.errno
            if move_started and error in [17,80,183]:status='CONFLICT';code='READY_ALREADY_EXISTS'
            elif move_started and error in [32,33,errno.EBUSY]:status='RETRYABLE_BUSY';code='PUBLICATION_BUSY'
            else:status='UNKNOWN' if move_started else 'IO_ERROR';code='PUBLICATION_OUTCOME_UNKNOWN' if move_started else 'PACKAGE_IO_ERROR'
        except Exception:status='UNKNOWN' if move_started else 'IO_ERROR';code='PUBLICATION_OUTCOME_UNKNOWN' if move_started else 'PRODUCER_ERROR'
        if move_started and status=='UNKNOWN':code='PUBLICATION_OUTCOME_UNKNOWN'
        return self._result(tx,status,code,digest,None,count,_fallback=True)
def main(argv=None,*,_portable_fixture=False):
    p=commands.Parser(description='Synthetic prepared-draft publisher; published package is not Bank acceptance.');p.add_argument('action',choices=['publish','inspect','resume']);p.add_argument('--intake-root',required=True);p.add_argument('--source-root');p.add_argument('--transaction-id',required=True)
    try:
        a=p.parse_args(argv);result=Publisher(a.intake_root,a.source_root,_portable_fixture=_portable_fixture).execute(a.action,a.transaction_id)
    except commands.ConfigurationError:result={'status':'REJECTED','code':'INVALID_CLI','Bank_accepted':False}
    except Exception:result={'status':'IO_ERROR','code':'INVALID_CONFIGURATION','Bank_accepted':False}
    try:sys.stdout.buffer.write(encoded(result)+b'\n');sys.stdout.buffer.flush()
    except (OSError,KeyboardInterrupt):
        try:sys.stdout.close()
        except OSError:pass
        return 4
    return 0 if result['status'] in ['PUBLISHED','ALREADY_PUBLISHED'] else (3 if result['status']=='RETRYABLE_BUSY' else (4 if result['status']=='UNKNOWN' else (130 if result['status']=='CANCELLED' else 2)))
if __name__=='__main__':sys.exit(main())
