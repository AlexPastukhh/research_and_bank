"""Bounded synthetic R1 read adapter/CLI; never initializes or imports a Bank.

Operator root configuration, app code and current owner are trusted. No live
deployment, search/UI or release acceptance follows from this component.
"""
from pathlib import Path
from contextlib import ExitStack
from collections import OrderedDict
import argparse,copy,hashlib,json,os,sqlite3,stat,sys,time,uuid
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'EXPERIMENTS/sqlite_importer'))
import importer as im
PROTOCOL='local-bank-query/1'
OPS={'bank.get','collection.get','bank.original','bank.history','receipt.get','bank.search'}
TYPES={'Asset','Entity','Annotation','Collection'}

class ReadError(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)
def need(ok,code='INTEGRITY_ERROR'):
    if not ok:raise ReadError(code)
def ref(d):return {k:d[k] for k in ['object_type','object_id','revision_id']}

class Budget:
    def __init__(self,limits):self.limits=limits;self.metadata=0;self.bytes=0;self.steps=0;self.start=time.monotonic();self.exceeded=False
    def tick(self):
        if (time.monotonic()-self.start)*1000>self.limits['elapsed_ms']:self.exceeded=True;raise ReadError('LIMIT_EXCEEDED')
    def charge(self,n,metadata=False):
        self.tick();self.bytes+=n
        if metadata:self.metadata+=n
        need(self.bytes<=self.limits['stored_bytes_per_request'] and self.metadata<=self.limits['stored_metadata_bytes_per_request'],'LIMIT_EXCEEDED')
    def progress(self):
        self.steps+=1000
        if self.steps>self.limits['sqlite_vm_steps'] or (time.monotonic()-self.start)*1000>self.limits['elapsed_ms']:self.exceeded=True;return 1
        return 0

class Exporter:
    """Own random filenames only; protect accepted outputs until API.close()."""
    def __init__(self,root,bank_root,hook=None):
        self.root=Path(root).absolute();bank_root=Path(bank_root).absolute();self.stack=ExitStack();self.outputs={};self.hook=hook
        need(not self.root.is_relative_to(bank_root) and not bank_root.is_relative_to(self.root),'BANK_UNAVAILABLE')
        try:
            if os.name=='nt':self.stack.enter_context(im.native.configured_root(self.root))
            else:
                info=self.root.lstat();need(stat.S_ISDIR(info.st_mode) and not self.root.is_symlink() and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)&0o077==0,'BANK_UNAVAILABLE')
                need(not any(p.is_symlink() for p in self.root.parents),'BANK_UNAVAILABLE')
        except BaseException:self.stack.close();raise
    def close(self):
        for folder,h in self.outputs.values():
            if h:h.close()
        self.outputs.clear();self.stack.close()
    def discard(self,export_id):
        folder,h=self.outputs.pop(export_id)
        if h:h.close()
        (folder/'original.bin').unlink();folder.rmdir()
    def create(self,chunks,length,digest,budget):
        export_id=str(uuid.uuid4());folder=self.root/export_id;path=folder/'original.bin';h=None
        if os.name=='nt':im.native.private_directory(folder)
        else:folder.mkdir(mode=0o700)
        try:
            count=0;actual=hashlib.sha256()
            if os.name=='nt':
                h=im.native.Handle(path,new=True)
                for raw in chunks:
                    budget.tick();need(len(raw)<=budget.limits['export_chunk_bytes']);h.write(raw);count+=len(raw);actual.update(raw)
                    if self.hook:self.hook('export_chunk',path)
                im.native.checked(im.native.flush_file(h.h));need(h.size()==length)
                h.seek();rhash=hashlib.sha256();total=0
                while raw:=h.read(budget.limits['export_chunk_bytes']):budget.tick();total+=len(raw);rhash.update(raw)
                need(total==length and rhash.hexdigest()==digest);h.close();h=None
                h=im.native.Handle(path);im.native.verify_private_acl(h)
            else:
                with path.open('xb') as f:
                    os.chmod(path,0o600)
                    for raw in chunks:
                        budget.tick();need(len(raw)<=budget.limits['export_chunk_bytes']);f.write(raw);count+=len(raw);actual.update(raw)
                        if self.hook:self.hook('export_chunk',path)
                    f.flush();os.fsync(f.fileno())
                rhash=hashlib.sha256();total=0
                with path.open('rb') as f:
                    while raw:=f.read(budget.limits['export_chunk_bytes']):budget.tick();total+=len(raw);rhash.update(raw)
                need(total==length and rhash.hexdigest()==digest)
            need(count==length and actual.hexdigest()==digest)
            self.outputs[export_id]=(folder,h)
            return {'export_id':export_id,'path':str(path),'byte_length':length,'sha256':digest,'lifetime':'private_persistent_export_verify_hash_on_later_read','rendering':'opaque_bytes_no_execution'}
        except BaseException:
            if h:h.close()
            if path.exists():path.unlink()
            folder.rmdir();raise
        finally:
            # Close a suspended BLOB generator before its read transaction ends,
            # including exporter I/O/cancellation faults.
            close=getattr(chunks,'close',None)
            if close:close()

class ReadSession:
    def __init__(self,store,budget,hook=None):self.store=store;self.budget=budget;self.hook=hook;self.c=None;self.cache=OrderedDict();self.snapshot=None
    def __enter__(self):
        self.c=self.store._connect(False)
        try:
            self.c.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE,True)
            self.c.set_progress_handler(self.budget.progress,1000)
            allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_TRANSACTION,sqlite3.SQLITE_RECURSIVE}
            self.c.set_authorizer(lambda action,*_:sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
            self.c.execute('BEGIN');maximum=self.c.execute('SELECT commit_sequence FROM commits ORDER BY commit_sequence DESC LIMIT 1').fetchone();self.snapshot=maximum[0] if maximum else 0
            need(type(self.snapshot) is int and 0<=self.snapshot<=9007199254740991)
            if self.hook:self.hook('snapshot_selected',self.snapshot)
            return self
        except BaseException:self.c.close();self.c=None;raise
    def __exit__(self,*_):
        if self.c:self.c.close();self.c=None
    def commit(self,seq):
        if seq in self.cache:return self.cache[seq]
        c=self.c;store=self.store
        sizes=c.execute('SELECT length(manifest_blob),length(ready_blob),length(policy_blob) FROM commits WHERE commit_sequence=?',(seq,)).fetchone();need(sizes and all(type(n)is int and n>=0 for n in sizes));self.budget.charge(sum(sizes),True)
        row,m,policy=store._commit_metadata(c,seq)
        files=c.execute('SELECT file_id,path,byte_length,sha256,length(file_blob) FROM files WHERE commit_sequence=? ORDER BY path',(seq,)).fetchmany(policy['files']+1)
        expected={f['path']:(f['byte_length'],f['sha256']) for f in m['files']}
        need(len(expected)==len(m['files'])==len(files))
        for f in files:need(expected.get(f[1])==(f[2],f[3]) and type(f[2])is int and f[2]>=0 and f[4]==f[2])
        revs=c.execute('SELECT revision_id,object_id,object_type,schema_ref,base_revision_id,operation_index,document_path FROM revisions WHERE commit_sequence=? ORDER BY operation_index',(seq,)).fetchmany(policy['operations']+1)
        need(revs==[(o['revision_id'],o['object_id'],o['type'],o['schema_ref'],o['base_revision_id'],i,o['document_path']) for i,o in enumerate(m['operations'])])
        length=c.execute('SELECT length(receipt_blob) FROM accepted_receipts WHERE commit_sequence=?',(seq,)).fetchone();need(length and type(length[0])is int and 0<=length[0]<=65536);self.budget.charge(length[0],True)
        receipt=im.reader.strict_json(store._small_column(c,'accepted_receipts','receipt_blob','commit_sequence',seq,65536),65536,64);store.contracts.envelope(receipt)
        need(receipt['status']=='ACCEPTED' and receipt['code']=='OK' and receipt['transaction_id']==row[0] and receipt['manifest_sha256']==row[2] and receipt['commit_id']==row[1] and receipt['commit_sequence']==seq and receipt['recorded_at']==row[3] and receipt['committed']==[{'object_id':o['object_id'],'revision_id':o['revision_id']} for o in m['operations']])
        value={'row':row,'manifest':m,'policy':policy,'files':{f[1]:f for f in files},'receipt':receipt,'documents':{}}
        self.cache[seq]=value
        if len(self.cache)>4:self.cache.popitem(last=False)
        return value
    def file_chunks(self,f,cap,metadata=False):
        need(type(f[2])is int and 0<=f[2]<=cap and f[4]==f[2]);self.budget.charge(f[2],metadata);total=0;h=hashlib.sha256()
        with self.c.blobopen('files','file_blob',f[0],readonly=True) as blob:
            while raw:=blob.read(self.budget.limits['export_chunk_bytes']):
                self.budget.tick();total+=len(raw);need(total<=f[2]);h.update(raw);yield raw
        need(total==f[2] and h.hexdigest()==f[3])
    def document(self,row):
        rid,oid,kind,seq,path=row;commit=self.commit(seq)
        if rid in commit['documents']:return commit['documents'][rid],commit
        op=next((o for o in commit['manifest']['operations'] if o['revision_id']==rid),None);need(op and (op['object_id'],op['type'],op['document_path'])==(oid,kind,path))
        f=commit['files'].get(path);need(f);raw=b''.join(self.file_chunks(f,commit['policy']['object_json_bytes'],True));d=im.reader.strict_json(raw,commit['policy']['object_json_bytes'],64)
        need(isinstance(d,dict));need((d.get('object_type'),d.get('schema')) in self.store.contracts.allowed,'UNSUPPORTED_SCHEMA')
        self.store._doc_check(d,op,{n:(f[2],f[3]) for n,f in commit['files'].items()},commit['policy'])
        commit['documents'][rid]=d;return d,commit
    def select(self,q):
        oid=q['object_id'];kind=q['object_type']
        head=self.c.execute('SELECT revision_id,object_id,object_type,commit_sequence,document_path FROM revisions WHERE object_id=? AND commit_sequence<=? ORDER BY commit_sequence DESC LIMIT 1',(oid,self.snapshot)).fetchone()
        need(head is not None,'OBJECT_NOT_FOUND');need(head[2]==kind,'TYPE_MISMATCH')
        rid=q.get('revision_id') or (q.get('selector',{}).get('revision_id'))
        if rid is None:row=head
        else:
            row=self.c.execute('SELECT revision_id,object_id,object_type,commit_sequence,document_path FROM revisions WHERE revision_id=? AND commit_sequence<=?',(rid,self.snapshot)).fetchone()
            need(row is not None and row[1]==oid,'REVISION_NOT_FOUND');need(row[2]==kind,'TYPE_MISMATCH')
        d,commit=self.document(row);return d,row,commit
    def detail(self,q):
        d,row,commit=self.select(q);data={'document':d,'ref':ref(d),'commit_sequence':row[3],'accepted_at':commit['row'][3]}
        if q['operation']=='collection.get':
            members=d['data']['members'];need(len(members)<=self.budget.limits['member_count'],'LIMIT_EXCEEDED');states=[]
            for member in members:
                found=self.c.execute('SELECT revision_id,object_id,object_type,commit_sequence,document_path FROM revisions WHERE revision_id=? AND commit_sequence<=?',(member['revision_id'],self.snapshot)).fetchone()
                if not found or found[1]!=member['object_id']:availability='revision_not_found'
                elif found[2]!=member['object_type']:availability='type_mismatch'
                else:
                    try:self.document(found);availability='available'
                    except (im.Problem,im.reader.Rejected,ReadError) as e:
                        if getattr(e,'code',None)=='LIMIT_EXCEEDED':raise
                        availability='integrity_error'
                states.append({'ref':member,'availability':availability})
            data['member_statuses']=states
        return data
    def history(self,q):
        selected=q['snapshot_sequence'];seq=self.snapshot if selected is None else selected
        need(seq<=self.snapshot,'SNAPSHOT_NOT_AVAILABLE')
        if seq>0:need(self.c.execute('SELECT 1 FROM commits WHERE commit_sequence=?',(seq,)).fetchone() is not None,'SNAPSHOT_NOT_AVAILABLE')
        head=self.c.execute('SELECT object_type FROM revisions WHERE object_id=? AND commit_sequence<=? ORDER BY commit_sequence DESC LIMIT 1',(q['object_id'],seq)).fetchone()
        need(head is not None,'OBJECT_NOT_FOUND');need(head[0]==q['object_type'],'TYPE_MISMATCH')
        rows=self.c.execute('SELECT revision_id,object_id,object_type,commit_sequence,document_path FROM revisions WHERE object_id=? AND commit_sequence<=? ORDER BY commit_sequence DESC LIMIT ? OFFSET ?',(q['object_id'],seq,q['limit']+1,q['offset'])).fetchall();items=[]
        for row in rows[:q['limit']]:
            d,commit=self.document(row);items.append({'ref':ref(d),'commit_sequence':row[3],'accepted_at':commit['row'][3]})
        self.snapshot=seq
        return {'revisions':items,'limit':q['limit'],'offset':q['offset'],'has_more':len(rows)>q['limit'],'next_offset':q['offset']+len(items) if len(rows)>q['limit'] else None}
    def receipt(self,q):
        row=self.c.execute('SELECT commit_sequence,manifest_sha256 FROM commits WHERE transaction_id=?',(q['transaction_id'],)).fetchone();need(row is not None,'RECEIPT_NOT_FOUND')
        need(q['expected_manifest_sha256'] is None or row[1]==q['expected_manifest_sha256'],'TRANSACTION_HASH_MISMATCH')
        commit=self.commit(row[0]);ops={o['document_path']:o for o in commit['manifest']['operations']}
        for path,f in commit['files'].items():
            if path in ops:
                op=ops[path];self.document((op['revision_id'],op['object_id'],op['type'],row[0],path))
            else:
                for _ in self.file_chunks(f,commit['policy']['file_bytes']):pass
        sys.path.insert(0,str(ROOT/'EXPERIMENTS/first_bank'))
        import attempts
        latest=attempts.latest(self.c,self.store.contracts,q['transaction_id'])
        self.c.set_progress_handler(self.budget.progress,1000)
        return {'receipt':commit['receipt'],'manifest_sha256':row[1],'latest_diagnostic_attempt':latest}

class ReadAPI:
    def __init__(self,bank_root,output_root=None,*,contracts=None,_hook=None,_limits=None):
        self.root=Path(bank_root).absolute();self.output_root=output_root;self.contracts=contracts or im.Contracts();self.hook=_hook;self.exporter=None;self.closed=False
        folder=Path(__file__).parent;self.limits=json.loads((folder/'LIMITS.json').read_text());self.limits.update(_limits or {})
        self.request_validator=Draft202012Validator(json.loads((ROOT/'PLANNING/CONTRACTS/BANK_QUERY.schema.json').read_text(encoding='utf-8-sig')))
        self.result_validator=Draft202012Validator(json.loads((folder/'result.schema.json').read_text()))
    def close(self):
        self.closed=True
        if self.exporter:self.exporter.close();self.exporter=None
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
    def parse(self,raw):
        need(type(raw)is bytes,'INVALID_REQUEST')
        try:q=im.reader.strict_json(raw,self.limits['request_bytes'],self.limits['request_depth'])
        except im.reader.Rejected as e:raise ReadError('LIMIT_EXCEEDED' if str(e) in ['LIMIT_EXCEEDED','JSON_DEPTH'] else 'INVALID_REQUEST') from e
        need(isinstance(q,dict),'INVALID_REQUEST');return q
    def validate(self,q):
        need(q.get('protocol')==PROTOCOL,'UNSUPPORTED_PROTOCOL')
        need(isinstance(q.get('operation'),str) and q['operation'] in OPS,'UNSUPPORTED_MODE')
        if 'object_type'in q:need(isinstance(q['object_type'],str) and q['object_type'] in TYPES,'UNSUPPORTED_TYPE')
        for key in ['limit','offset','snapshot_sequence']:
            if key in q and q[key]is not None:need(type(q[key])is int,'INVALID_REQUEST')
        need(next(self.request_validator.iter_errors(q),None)is None,'INVALID_REQUEST')
        need(q['operation']!='bank.search','UNSUPPORTED_MODE')
    def error(self,q,code,seq=None):
        rid=q.get('request_id') if isinstance(q,dict) else None;rid=rid if isinstance(rid,str) and im.reader.UUID.fullmatch(rid) else None
        op=q.get('operation') if isinstance(q,dict) else None;op=op if isinstance(op,str) and op in OPS else None
        result={'protocol':PROTOCOL,'request_id':rid,'operation':op,'status':'ERROR','snapshot_sequence':seq,'code':code,'message':code}
        need(next(self.result_validator.iter_errors(result),None)is None,'RESULT_CONFORMANCE');return result
    def execute(self,raw):
        q={};session=None;created=None;budget=Budget(self.limits)
        try:
            q=self.parse(raw);self.validate(q);need(not self.closed,'BANK_UNAVAILABLE')
            with im.Store(self.root,contracts=self.contracts) as store:
                with ReadSession(store,budget,self.hook) as session:
                    op=q['operation']
                    if op in ['bank.get','collection.get']:data=session.detail(q)
                    elif op=='bank.history':data=session.history(q)
                    elif op=='receipt.get':data=session.receipt(q)
                    else:
                        d,row,commit=session.select(q);storage=d['data']['storage'];data={'ref':ref(d),'commit_sequence':row[3],'accepted_at':commit['row'][3]}
                        if storage['mode']=='locator':data.update(availability='locator_only',uri=storage['uri'])
                        else:
                            need(self.output_root is not None,'BANK_UNAVAILABLE')
                            if self.exporter is None:self.exporter=Exporter(self.output_root,self.root,self.hook)
                            f=commit['files'][storage['file_path']]
                            output=self.exporter.create(session.file_chunks(f,commit['policy']['file_bytes']),storage['byte_length'],storage['sha256'],budget);created=output['export_id']
                            data.update(availability='bytes',original=output,media_type=storage['media_type'],display_filename=storage['original_filename'])
                    result={'protocol':PROTOCOL,'request_id':q['request_id'],'operation':op,'status':'OK','snapshot_sequence':session.snapshot,'data':data}
                    need(next(self.result_validator.iter_errors(result),None)is None,'RESULT_CONFORMANCE');need(len(im.encoded(result))<=self.limits['response_bytes'],'LIMIT_EXCEEDED');budget.tick();return result
        except ReadError as e:code=e.code
        except im.WorkLimit:code='LIMIT_EXCEEDED'
        except im.Problem as e:code='UNSUPPORTED_SCHEMA' if e.code=='UNSUPPORTED_SCHEMA' else ('BANK_UNAVAILABLE' if e.code in ['STORE_CLOSED','UNTRUSTED_TEST_ROOT','UNTRUSTED_TEST_PARENT'] else 'INTEGRITY_ERROR')
        except im.native.SafetyError:code='BANK_UNAVAILABLE'
        except (im.reader.Rejected,UnicodeError,ValueError,KeyError,TypeError):code='INTEGRITY_ERROR'
        except sqlite3.Error as e:
            n=getattr(e,'sqlite_errorcode',0) or 0;code='LIMIT_EXCEEDED' if budget.exceeded else ('BANK_BUSY' if n&255 in [sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED] else 'INTEGRITY_ERROR')
        except OSError:code='BANK_UNAVAILABLE'
        if created:self.exporter.discard(created)
        return self.error(q,code,session.snapshot if session else None)

def main():
    parser=argparse.ArgumentParser(description='Synthetic existing-Bank R1 read CLI; operator paths are trusted app configuration.')
    parser.add_argument('--bank-root',required=True);parser.add_argument('--output-root');args=parser.parse_args()
    with ReadAPI(args.bank_root,args.output_root) as api:
        raw=sys.stdin.buffer.read(api.limits['request_bytes']+1);result=api.execute(raw);sys.stdout.buffer.write(im.encoded(result)+b'\n');sys.stdout.buffer.flush()
    return 0 if result['status']=='OK' else 2
if __name__=='__main__':sys.exit(main())
