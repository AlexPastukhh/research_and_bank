"""Synthetic local whole-command Bank importer. No installed Bank/UI/release claim.

App code/configuration/root parents and current owner are trusted. Public APIs expose
no SQL, connections, BLOB handles or producer-selected storage destinations.
"""
from pathlib import Path
from contextlib import ExitStack
from dataclasses import dataclass
from collections import OrderedDict
import copy, datetime, errno, hashlib, json, os, re, sqlite3, stat, sys, uuid, time
from contextlib import contextmanager
from contextvars import ContextVar
from jsonschema import Draft202012Validator, FormatChecker
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'EXPERIMENTS/secure_intake'))
import reader
import win32_io as native

class Problem(Exception):
    def __init__(self,code,state='REJECTED'):self.code=code;self.state=state;super().__init__(code)
class Cancelled(Exception):pass
def need(ok,code,state='REJECTED'):
    if not ok:raise Problem(code,state)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(obj):return json.dumps(obj,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
def normalized(sql):return ' '.join(sql.split()).lower() if sql else None
@dataclass(frozen=True)
class Outcome:
    state:str
    code:str
    receipt:dict|None=None
    diagnostic:str=''

class Contracts:
    def __init__(self,path=None):
        path=Path(path or ROOT/'PLANNING/CONTRACTS')
        self.policy=reader.configured_policy((path/'LOCAL_INTAKE_LIMITS.json').read_bytes())
        self.ddl=(path/'LOCAL_STORAGE_SCHEMA.sql').read_text(encoding='utf-8-sig')
        self.bank=json.loads((path/'BANK_TYPES.schema.json').read_text(encoding='utf-8-sig'))
        self.env=json.loads((path/'LOCAL_WRITE_ENVELOPE.schema.json').read_text(encoding='utf-8-sig'))
        self.registry=json.loads((path/'BANK_SCHEMA_COMPATIBILITY.json').read_text(encoding='utf-8-sig'))
        self.bank_validator=Draft202012Validator(self.bank,format_checker=FormatChecker())
        self.envelope_validator=Draft202012Validator(self.env,format_checker=FormatChecker())
        for s in [self.bank,self.env]:Draft202012Validator.check_schema(s)
        self.allowed={(x['object_type'],x['schema_ref']) for x in self.registry['schemas'] if x['object_type'] in self.registry['profiles']['R1']['write_types']}
        ref=sqlite3.connect(':memory:',isolation_level=None)
        try:ref.executescript(self.ddl);self.catalog=self.catalog_of(ref)
        finally:ref.close()
    @staticmethod
    def catalog_of(c):
        rows=c.execute("SELECT type,name,tbl_name,sql FROM sqlite_schema ORDER BY type,name").fetchmany(64)
        need(len(rows)<64,'UNKNOWN_DB_FORMAT','INTEGRITY_ERROR')
        return [(t,n,tbl,normalized(sql)) for t,n,tbl,sql in rows]
    def schema(self,value):need(next(self.bank_validator.iter_errors(value),None) is None,'OBJECT_SCHEMA')
    def envelope(self,value):need(next(self.envelope_validator.iter_errors(value),None) is None,'ENVELOPE_SCHEMA')

class WorkLimit(Problem):
    def __init__(self):super().__init__('RETAINED_WORK_LIMIT','IO_ERROR')

class WorkBudget:
    def __init__(self,limits,event):
        self.limits=limits;self.event=event;self.start=time.monotonic();self.bytes=0;self.metadata=0;self.commits=0;self.summary=0
    def tick(self):
        self.event('retained_work_checkpoint')
        if (time.monotonic()-self.start)*1000>self.limits['elapsed_ms']:raise WorkLimit()
    def charge(self,n,metadata=False):
        self.tick()
        if self.bytes+n>self.limits['retained_bytes'] or (metadata and self.metadata+n>self.limits['metadata_bytes']):raise WorkLimit()
        self.bytes+=n
        if metadata:self.metadata+=n
    def read_size(self,size,metadata=False):
        self.tick();remaining=self.limits['retained_bytes']-self.bytes
        if metadata:remaining=min(remaining,self.limits['metadata_bytes']-self.metadata)
        if remaining<=0:raise WorkLimit()
        return min(size,remaining)
    def commit(self,seq):
        self.tick()
        if self.commits>=self.limits['commits']:raise WorkLimit()
        self.commits+=1;self.event('retained_commit_verification',seq)
    def summary_charge(self,docs):
        # Conservative accounting of the actual compact Python representation.
        n=sys.getsizeof(docs)+sum(sys.getsizeof(k)+sys.getsizeof(v)+sum(sys.getsizeof(x)+sys.getsizeof(y) for x,y in v.items()) for k,v in docs.items())
        if self.summary+n>self.limits['summary_bytes']:raise WorkLimit()
        self.summary+=n

class GuardedConnection(sqlite3.Connection):
    """Release the native identity lease after SQLite closes its own handle."""
    guard=None
    def close(self):
        try:super().close()
        finally:
            if self.guard is not None:self.guard.close();self.guard=None

def sqlite_guard(path):
    return native.SQLiteGuard(path) if os.name=='nt' else ExitStack()

def connect_guarded(path,*,uri=None,timeout=0):
    guard=sqlite_guard(path);c=None
    try:
        c=sqlite3.connect(uri or path,uri=uri is not None,isolation_level=None,timeout=timeout,factory=GuardedConnection)
        c.guard=guard
        if os.name=='nt':guard.check()
        return c
    except BaseException:
        if c is not None:c.close()
        else:guard.close()
        raise

class _WriteSession:
    """Private capability for only newly inserted file rows in this active command."""
    def __init__(self,c,seq,policy,event):self._c=c;self._seq=seq;self._new_ids=set();self._policy=policy;self._event=event
    def insert_and_copy(self,path,length,digest,chunks):
        need(self._c.in_transaction,'WRITER_NOT_ACTIVE','IO_ERROR')
        cur=self._c.execute('INSERT INTO files(commit_sequence,path,byte_length,sha256,file_blob) VALUES(?,?,?,?,zeroblob(?))',(self._seq,path,length,digest,length))
        fid=cur.lastrowid;self._new_ids.add(fid);self.write(fid,chunks,length,digest,path);return fid
    def write(self,fid,chunks,length,digest,path='fixture'):
        need(fid in self._new_ids and self._c.in_transaction,'OLD_BLOB_WRITE_FORBIDDEN','IO_ERROR')
        row=self._c.execute('SELECT commit_sequence,byte_length FROM files WHERE file_id=?',(fid,)).fetchone()
        need(row==(self._seq,length),'BLOB_SCOPE_MISMATCH','IO_ERROR');count=0;actual=hashlib.sha256()
        with self._c.blobopen('files','file_blob',fid,readonly=False) as blob:
            for raw in chunks:
                need(type(raw) is bytes and len(raw)<=self._policy['blob_chunk_bytes'],'SNAPSHOT_CHUNK_INVALID')
                count+=len(raw);need(count<=length,'SNAPSHOT_CHANGED');self._event('before_blob_write',path)
                blob.write(raw);actual.update(raw);self._event('blob_chunk',path)
        need(count==length and actual.hexdigest()==digest,'SNAPSHOT_CHANGED')

class Store:
    """Owned synthetic fixed-root store. Connection details never returned to producers."""
    def __init__(self,root,*,contracts=None,_snapshot_type=None,_hook=None,_cancel=None,_work_limits=None):
        self.root=Path(root).absolute();self.db=self.root/'bank.sqlite';self.contracts=contracts or Contracts()
        self._snapshot_type=_snapshot_type or reader.Snapshot;self._hook=_hook;self._cancel=_cancel;self._leases=ExitStack();self._closed=False
        profile=json.loads((Path(__file__).parent/'WORK_LIMITS.json').read_text(encoding='utf-8'));self.work_limits=dict(profile['limits']);self.work_limits.update(_work_limits or {})
        need(set(self.work_limits)=={'retained_bytes','metadata_bytes','commits','summary_bytes','elapsed_ms'} and all(type(x)is int and x>0 for x in self.work_limits.values()),'INVALID_WORK_POLICY','IO_ERROR')
        self._work=ContextVar('bank_retained_work',default=None)
        need(sqlite3.sqlite_version_info>=(3,37,0),'SQLITE_VERSION_UNSUPPORTED','IO_ERROR')
        need(hasattr(sqlite3.Connection,'setconfig') and hasattr(sqlite3,'SQLITE_DBCONFIG_DEFENSIVE'),'DEFENSIVE_UNAVAILABLE','IO_ERROR')
        if os.name=='nt':self._leases.enter_context(native.configured_root(self.root))
        else:
            # Portable test root only. This does not establish Windows confinement.
            need(self.root.is_dir() and not self.root.is_symlink(),'UNTRUSTED_TEST_ROOT','IO_ERROR')
            info=self.root.stat();need(info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)&0o077==0,'UNTRUSTED_TEST_ROOT','IO_ERROR')
            need(not any(p.is_symlink() for p in self.root.parents),'UNTRUSTED_TEST_PARENT','IO_ERROR')
    def close(self):self._closed=True;self._leases.close()
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
    def _event(self,name,value=None):
        if self._cancel and self._cancel():raise Cancelled()
        if self._hook:self._hook(name,value)
        if self._cancel and self._cancel():raise Cancelled()
    @contextmanager
    def _work_scope(self):
        if self._work.get() is not None:yield self._work.get();return
        budget=WorkBudget(self.work_limits,self._event);token=self._work.set(budget)
        try:yield budget
        finally:self._work.reset(token)
    def _path_check(self):
        need(not self._closed,'STORE_CLOSED','IO_ERROR')
        info=self.db.lstat();need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and not getattr(info,'st_file_attributes',0)&0x400,'UNTRUSTED_DB_FILE','INTEGRITY_ERROR')
        with sqlite_guard(self.db):
            with self.db.open('rb') as f:header=f.read(100)
        need(len(header)==100 and header[:16]==b'SQLite format 3\x00' and int.from_bytes(header[60:64],'big')==1 and int.from_bytes(header[68:72],'big')==1380076337,'UNKNOWN_DB_FORMAT','INTEGRITY_ERROR')
    def _catalog_check(self,c):
        need(c.execute('PRAGMA application_id').fetchone()[0]==1380076337 and c.execute('PRAGMA user_version').fetchone()[0]==1,'UNKNOWN_DB_FORMAT','INTEGRITY_ERROR')
        need(Contracts.catalog_of(c)==self.contracts.catalog,'UNKNOWN_DB_FORMAT','INTEGRITY_ERROR')
    def _configure(self,c):
        # Query journal before setting connection-local options; unknown DB is never reconfigured.
        need(c.execute('PRAGMA journal_mode').fetchone()[0]=='delete','UNSUPPORTED_JOURNAL','IO_ERROR')
        c.execute('PRAGMA synchronous=EXTRA');c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA trusted_schema=OFF');c.execute('PRAGMA cache_size=-1024')
        c.execute('PRAGMA busy_timeout='+str(self.contracts.policy['writer_busy_timeout_ms']))
        c.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE,True)
        need(c.getconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE),'DEFENSIVE_DISABLED','IO_ERROR')
        for pragma,value in [('synchronous',3),('foreign_keys',1),('trusted_schema',0),('read_uncommitted',0)]:need(c.execute('PRAGMA '+pragma).fetchone()[0]==value,'CONFIGURATION_MISMATCH','IO_ERROR')
    def initialize(self):
        need(not self._closed,'STORE_CLOSED','IO_ERROR');need(not self.db.exists(),'DATABASE_ALREADY_EXISTS','IO_ERROR')
        if os.name=='nt':
            with native.Handle(self.db,new=True) as handle:native.verify_private_acl(handle)
        else:
            fd=os.open(self.db,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
        c=None
        try:
            c=connect_guarded(self.db);self._configure(c)
            current=''
            for line in self.contracts.ddl.splitlines(keepends=True):
                current+=line
                if sqlite3.complete_statement(current):
                    if current.strip().upper()=='COMMIT;':
                        self._event('init_before_commit')
                        if os.name=='nt':c.guard.check()
                    c.execute(current);current=''
            need(not current.strip(),'INCOMPLETE_SCHEMA_SQL','IO_ERROR');self._catalog_check(c)
        except BaseException:
            if c and c.in_transaction:c.execute('ROLLBACK')
            raise
        finally:
            if c:c.close()
    def _connect(self,write=False,*,_allow_recovery=True):
        self._path_check();uri=self.db.as_uri()+'?mode='+('rw' if write else 'ro')
        c=connect_guarded(self.db,uri=uri,timeout=self.contracts.policy['writer_busy_timeout_ms']/1000)
        try:
            self._catalog_check(c)
            if write:self._configure(c)
            else:c.execute('PRAGMA query_only=ON');c.execute('PRAGMA trusted_schema=OFF');c.execute('PRAGMA foreign_keys=ON')
            return c
        except sqlite3.Error as e:
            c.close()
            if not write and _allow_recovery and getattr(e,'sqlite_errorcode',None)==sqlite3.SQLITE_READONLY_ROLLBACK:
                # A private known-header app DB needs SQLite's own journal rollback before a readonly view can be read.
                # No CREATE, schema reset, user import or manual journal removal. Only one bounded recovery/retry.
                recovered=Store._connect(self,True);recovered.close()
                return Store._connect(self,False,_allow_recovery=False)
            raise
        except BaseException:c.close();raise
    def _snapshot_header(self,s):
        need(isinstance(s,self._snapshot_type) and s.status=='VERIFIED_TRANSPORT','UNVERIFIED_SNAPSHOT')
        policy=reader.Policy(s.policy_bytes);m=reader.strict_json(s.manifest_bytes,policy['manifest_bytes'],policy['json_container_depth']);ready=reader.strict_json(s.ready_bytes,policy['ready_bytes'],policy['json_container_depth'])
        self.contracts.envelope(m);self.contracts.envelope(ready)
        need(m['intent']=='independent_save','UNSUPPORTED_INTENT')
        need(m['transaction_id']==ready['transaction_id']==s.transaction_id and sha(s.manifest_bytes)==s.manifest_sha256==ready['manifest_sha256'] and len(s.manifest_bytes)==ready['manifest_byte_length'],'SNAPSHOT_HEADER_INTEGRITY')
        need(len(m['files'])<=policy['files'] and len(m['operations'])<=policy['operations'],'LIMIT_EXCEEDED')
        files={}
        for f in m['files']:
            name=reader.valid_path(f['path']);need(name not in files,'DUPLICATE_FILE');need(f['byte_length']<=policy['file_bytes'],'LIMIT_EXCEEDED');files[name]=(f['byte_length'],f['sha256'])
        need(dict(s.files)==files,'SNAPSHOT_INVENTORY_MISMATCH')
        need(len(s.ready_bytes)+len(s.manifest_bytes)+sum(x[0] for x in files.values())<=policy['package_bytes'],'LIMIT_EXCEEDED')
        return m,policy,files
    def _read_snapshot_doc(self,s,path,policy):
        need(path in s.files and s.files[path][0]<=policy['object_json_bytes'],'DOCUMENT_LIMIT');parts=[];count=0
        for b in s.iter_bytes(path):
            need(type(b) is bytes and len(b)<=policy['blob_chunk_bytes'],'SNAPSHOT_CHUNK_INVALID');count+=len(b);need(count<=policy['object_json_bytes'],'DOCUMENT_LIMIT');parts.append(b)
        raw=b''.join(parts);need(len(raw)==s.files[path][0] and sha(raw)==s.files[path][1],'SNAPSHOT_CHANGED')
        return reader.strict_json(raw,policy['object_json_bytes'],policy['json_container_depth'])
    @staticmethod
    def _refs(d):
        yield from d['provenance']['derived_from']
        if d['provenance']['source_ref']:yield d['provenance']['source_ref']
        field={'Entity':'asset_refs','Annotation':'targets','Collection':'members'}.get(d['object_type'])
        if field:yield from d['data'][field]
    def _doc_check(self,d,op,files,policy):
        self.contracts.schema(d);need((d['object_type'],d['schema']) in self.contracts.allowed,'UNSUPPORTED_SCHEMA')
        need(all(d[k]==op[v] for k,v in [('object_id','object_id'),('revision_id','revision_id'),('object_type','type'),('schema','schema_ref')]),'OPERATION_DOCUMENT_MISMATCH')
        need(d['provenance']['source_ref'] is None,'SOURCE_REF_OUTSIDE_R1')
        for value,key in [(d['title'],'title_bytes'),(d['provenance']['source_locator'],'locator_bytes')]:
            if value is not None:need(len(value.encode('utf-8'))<=policy[key],'TEXT_LIMIT')
        if d['object_type']=='Annotation':need(len(d['data']['body'].encode('utf-8'))<=policy['annotation_body_bytes'],'TEXT_LIMIT')
        if d['object_type']=='Asset':
            storage=d['data']['storage']
            if storage['mode']=='bytes':
                path=reader.valid_path(storage['file_path']);need(files.get(path)==(storage['byte_length'],storage['sha256']),'ASSET_DESCRIPTOR_MISMATCH')
            else:need(len(storage['uri'].encode('utf-8'))<=policy['locator_bytes'],'TEXT_LIMIT')
    def _incoming_docs(self,s,m,policy,files):
        docs={};paths=set();rids=set()
        for op in m['operations']:
            need(op['object_id'] not in docs and op['revision_id'] not in rids and op['document_path'] not in paths,'DUPLICATE_OPERATION')
            d=self._read_snapshot_doc(s,op['document_path'],policy);self._doc_check(d,op,files,policy)
            docs[op['object_id']]=d;paths.add(op['document_path']);rids.add(op['revision_id'])
        return docs
    def _small_column(self,c,table,column,key,value,cap):
        # Only fixed internal table/column/key identifiers reach this helper.
        row=c.execute('SELECT length('+column+') FROM '+table+' WHERE '+key+'=?',(value,)).fetchone();need(row is not None and type(row[0]) is int and row[0]<=cap,'RETAINED_METADATA_LIMIT','INTEGRITY_ERROR')
        budget=self._work.get()
        if budget:budget.charge(row[0],metadata=True)
        return c.execute('SELECT '+column+' FROM '+table+' WHERE '+key+'=?',(value,)).fetchone()[0]
    def _commit_metadata(self,c,seq):
        p=self.contracts.policy;manifest=self._small_column(c,'commits','manifest_blob','commit_sequence',seq,524288);ready=self._small_column(c,'commits','ready_blob','commit_sequence',seq,16384);policy_raw=self._small_column(c,'commits','policy_blob','commit_sequence',seq,524288)
        policy=reader.Policy(policy_raw);m=reader.strict_json(manifest,policy['manifest_bytes'],policy['json_container_depth']);mark=reader.strict_json(ready,policy['ready_bytes'],policy['json_container_depth']);self.contracts.envelope(m);self.contracts.envelope(mark)
        row=c.execute('SELECT transaction_id,commit_id,manifest_sha256,accepted_at,policy_version FROM commits WHERE commit_sequence=?',(seq,)).fetchone()
        need(row and m['transaction_id']==mark['transaction_id']==row[0] and mark['manifest_byte_length']==len(manifest) and mark['manifest_sha256']==row[2]==sha(manifest) and policy.version==row[4],'RETAINED_COMMIT_INTEGRITY','INTEGRITY_ERROR')
        need(len(m['files'])<=policy['files'] and len(m['operations'])<=policy['operations'] and len(manifest)+len(ready)+sum(x['byte_length'] for x in m['files'])<=policy['package_bytes'],'RETAINED_COMMIT_LIMIT','INTEGRITY_ERROR')
        return row,m,policy
    def _verify_blob(self,c,row,cap,collect=False):
        fid,path,length,digest,actual_length=row;need(type(length) is int and 0<=length<=cap and actual_length==length,'RETAINED_BLOB_SIZE','INTEGRITY_ERROR');count=0;h=hashlib.sha256();parts=[]
        with c.blobopen('files','file_blob',fid,readonly=True) as b:
            while count<length:
                size=min(length-count,1048576,self.contracts.policy['blob_chunk_bytes']);budget=self._work.get()
                if budget:size=budget.read_size(size,collect)
                raw=b.read(size);need(bool(raw),'RETAINED_BLOB_SIZE','INTEGRITY_ERROR')
                if budget:budget.charge(len(raw),metadata=collect)
                count+=len(raw);need(count<=length,'RETAINED_BLOB_SIZE','INTEGRITY_ERROR');h.update(raw)
                if collect:parts.append(raw)
        need(count==length and h.hexdigest()==digest,'RETAINED_BLOB_HASH','INTEGRITY_ERROR');return b''.join(parts) if collect else None
    def _verify_commit(self,c,seq,*,_compact=False):
        try:
            budget=self._work.get()
            if budget:budget.commit(seq)
            return self._verify_commit_unchecked(c,seq,_compact=_compact)
        except WorkLimit:raise
        except Problem as e:raise Problem(e.code,'INTEGRITY_ERROR') from e
        except (reader.Rejected,native.SafetyError) as e:raise Problem('RETAINED_METADATA_INVALID','INTEGRITY_ERROR') from e
    def _verify_commit_unchecked(self,c,seq,*,_compact=False):
        row,m,policy=self._commit_metadata(c,seq);expected={f['path']:(f['byte_length'],f['sha256']) for f in m['files']};need(len(expected)==len(m['files']),'RETAINED_INVENTORY','INTEGRITY_ERROR')
        rows=c.execute('SELECT file_id,path,byte_length,sha256,length(file_blob) FROM files WHERE commit_sequence=? ORDER BY path',(seq,)).fetchmany(policy['files']+1)
        need(len(rows)==len(expected),'RETAINED_INVENTORY','INTEGRITY_ERROR');operations=m['operations'];op_by_path={o['document_path']:o for o in operations};docs={}
        for f in rows:
            need(expected.get(f[1])==(f[2],f[3]),'RETAINED_INVENTORY','INTEGRITY_ERROR');raw=self._verify_blob(c,f,policy['object_json_bytes'] if f[1] in op_by_path else policy['file_bytes'],f[1] in op_by_path)
            if raw is not None:
                d=reader.strict_json(raw,policy['object_json_bytes'],policy['json_container_depth']);self._doc_check(d,op_by_path[f[1]],expected,policy);docs[d['object_id']]={k:d[k] for k in ['revision_id','object_type']} if _compact else d
        revs=c.execute('SELECT revision_id,object_id,object_type,schema_ref,base_revision_id,operation_index,document_path FROM revisions WHERE commit_sequence=? ORDER BY operation_index',(seq,)).fetchmany(policy['operations']+1)
        need(revs==[(o['revision_id'],o['object_id'],o['type'],o['schema_ref'],o['base_revision_id'],i,o['document_path']) for i,o in enumerate(operations)],'RETAINED_REVISIONS','INTEGRITY_ERROR')
        b=self._small_column(c,'accepted_receipts','receipt_blob','commit_sequence',seq,65536);receipt=reader.strict_json(b,65536,64);self.contracts.envelope(receipt)
        need(receipt['status']=='ACCEPTED' and receipt['code']=='OK' and receipt['transaction_id']==row[0] and receipt['manifest_sha256']==row[2] and receipt['commit_id']==row[1] and receipt['commit_sequence']==seq and receipt['recorded_at']==row[3] and receipt['committed']==[{'object_id':o['object_id'],'revision_id':o['revision_id']} for o in operations],'RETAINED_RECEIPT_INTEGRITY','INTEGRITY_ERROR')
        return receipt,docs
    def _lookup_ref(self,c,ref,cache):
        budget=self._work.get()
        if budget:budget.tick()
        row=c.execute('SELECT object_id,object_type,commit_sequence FROM revisions WHERE revision_id=?',(ref['revision_id'],)).fetchone()
        need(row and row[0]==ref['object_id'],'UNRESOLVED_REFERENCE');need(row[1]==ref['object_type'],'REFERENCE_TYPE_MISMATCH')
        seq=row[2]
        if seq not in cache:
            _,docs=self._verify_commit(c,seq,_compact=True)
            budget=self._work.get()
            if budget:budget.summary_charge(docs)
            cache[seq]=docs
        d=cache[seq].get(ref['object_id']);need(d and d['revision_id']==ref['revision_id'],'RETAINED_REFERENCE_INTEGRITY','INTEGRITY_ERROR');return d
    def _new_command_checks(self,c,m,docs):
        cache=OrderedDict();edges={oid:set() for oid in docs}
        for op in m['operations']:
            need(c.execute('SELECT 1 FROM revisions WHERE revision_id=?',(op['revision_id'],)).fetchone() is None,'REVISION_ID_REUSED','CONFLICT')
            head=c.execute('SELECT object_type,revision_id FROM revisions WHERE object_id=? ORDER BY commit_sequence DESC LIMIT 1',(op['object_id'],)).fetchone()
            if head:
                need(head[0]==op['type'],'OBJECT_TYPE_CHANGED','CONFLICT');need(op['base_revision_id']==head[1],'STALE_BASE','CONFLICT')
            else:need(op['base_revision_id'] is None,'BASE_NOT_FOUND','CONFLICT')
        # Existing accepted DAG cannot depend on not-yet-accepted new UUIDs (reuse rejected above).
        for oid,d in docs.items():
            for ref in self._refs(d):
                need(ref['object_type'] in self.contracts.registry['profiles']['R1']['read_types'],'UNSUPPORTED_REFERENCE_TYPE')
                target=docs.get(ref['object_id'])
                if target and target['revision_id']==ref['revision_id']:need(target['object_type']==ref['object_type'],'REFERENCE_TYPE_MISMATCH')
                else:self._lookup_ref(c,ref,cache)
            for ref in d['provenance']['derived_from']:
                if ref['object_id'] in docs and docs[ref['object_id']]['revision_id']==ref['revision_id']:edges[oid].add(ref['object_id'])
        indegree={oid:len(deps) for oid,deps in edges.items()};reverse={oid:set() for oid in docs}
        for oid,deps in edges.items():
            for dep in deps:reverse[dep].add(oid)
        todo=[oid for oid,n in indegree.items() if n==0];visited=0
        while todo:
            oid=todo.pop();visited+=1
            for child in reverse[oid]:
                indegree[child]-=1
                if indegree[child]==0:todo.append(child)
        need(visited==len(docs),'DERIVATION_CYCLE')
    def _receipt(self,status,code,attempt,tx=None,digest=None,**kw):
        receipt={'protocol':reader.PROTOCOL,'attempt_id':attempt,'transaction_id':tx,'manifest_sha256':digest,'recorded_at':now(),'status':status,'code':code,'diagnostics':[]};receipt.update(kw);self.contracts.envelope(receipt);return receipt
    def _out(self,state,code,receipt=None):
        text=code.encode()[:self.contracts.policy['diagnostic_bytes']].decode('utf-8','ignore');return Outcome(state,code,receipt,text)
    def _commit(self,c):c.execute('COMMIT')
    def import_snapshot(self,s):
        with self._work_scope():return self._import_snapshot(s)
    def _import_snapshot(self,s):
        prior=None
        attempt=str(uuid.uuid4());tx=None;digest=None;c=None;commit_started=False;success=False
        try:
            if isinstance(s,self._snapshot_type):
                tx=s.transaction_id;digest=s.manifest_sha256
            self._event('start');m,policy,files=self._snapshot_header(s);tx=m['transaction_id'];digest=s.manifest_sha256;docs=self._incoming_docs(s,m,policy,files);self._event('incoming_validated')
            c=self._connect(True);c.execute('BEGIN IMMEDIATE');self._event('writer_locked')
            prior=c.execute('SELECT commit_sequence,manifest_sha256 FROM commits WHERE transaction_id=?',(tx,)).fetchone()
            if prior:
                need(prior[1]==digest,'TRANSACTION_ID_REUSED','CONFLICT');original,_=self._verify_commit(c,prior[0]);c.execute('ROLLBACK')
                replay=copy.deepcopy(original);replay.update(attempt_id=attempt,recorded_at=now(),status='REPLAY',code='ALREADY_ACCEPTED');self.contracts.envelope(replay);return self._out('REPLAY','ALREADY_ACCEPTED',replay)
            self._new_command_checks(c,m,docs);self._event('domain_validated');commit_id=str(uuid.uuid4());accepted_at=now()
            cur=c.execute('INSERT INTO commits(transaction_id,commit_id,manifest_sha256,manifest_blob,ready_blob,accepted_at,policy_version,policy_blob) VALUES(?,?,?,?,?,?,?,?)',(tx,commit_id,digest,s.manifest_bytes,s.ready_bytes,accepted_at,policy.version,s.policy_bytes));seq=cur.lastrowid
            need(seq<=9007199254740991,'COMMIT_SEQUENCE_LIMIT');writer=_WriteSession(c,seq,policy,self._event)
            for name,(length,h) in files.items():writer.insert_and_copy(name,length,h,s.iter_bytes(name));self._event('file_copied',name)
            for i,op in enumerate(m['operations']):c.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?)',(op['revision_id'],op['object_id'],op['type'],op['schema_ref'],op['base_revision_id'],seq,i,op['document_path']))
            receipt=self._receipt('ACCEPTED','OK',attempt,tx,digest,commit_id=commit_id,commit_sequence=seq,committed=[{'object_id':o['object_id'],'revision_id':o['revision_id']} for o in m['operations']]);receipt['recorded_at']=accepted_at;self.contracts.envelope(receipt)
            c.execute('INSERT INTO accepted_receipts VALUES(?,?)',(seq,encoded(receipt)));self._event('before_commit')
            if os.name=='nt':c.guard.check()
            commit_started=True;self._commit(c);success=True;self._event('after_commit');return self._out('ACCEPTED','OK',receipt)
        except Cancelled:
            if success:return self._out('ACCEPTED','OK',receipt)
            return self._out('UNKNOWN','COMMIT_OUTCOME_UNKNOWN') if commit_started else self._out('CANCELLED','CANCELLED')
        except WorkLimit:
            if commit_started:return self._out('UNKNOWN','COMMIT_OUTCOME_UNKNOWN')
            if prior:return self._out('IO_ERROR','RETAINED_WORK_LIMIT')
            return self._out('REJECTED','RETAINED_WORK_LIMIT',self._receipt('REJECTED','RETAINED_WORK_LIMIT',attempt,tx,digest))
        except (reader.Rejected,native.SafetyError) as e:
            if commit_started:return self._out('UNKNOWN','COMMIT_OUTCOME_UNKNOWN')
            return self._out('REJECTED',str(e),self._receipt('REJECTED',str(e),attempt,tx,digest))
        except Problem as e:
            if commit_started:return self._out('UNKNOWN','COMMIT_OUTCOME_UNKNOWN')
            state=e.state;receipt=self._receipt(state,e.code,attempt,tx,digest) if state in ['REJECTED','CONFLICT','INTEGRITY_ERROR'] else None
            return self._out(state,e.code,receipt)
        except (sqlite3.Error,OSError) as e:
            code=getattr(e,'sqlite_errorcode',None)
            if not commit_started and code and code&255 in [sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED]:return self._out('RETRYABLE_BUSY','WRITER_BUSY')
            if commit_started:
                if c:
                    try:c.close()
                    except sqlite3.Error:pass
                    c=None
                try:
                    recovered=self.get_receipt(tx,digest)
                    if recovered:return self._out('ACCEPTED','OK',recovered)
                    if code and code&255 in [sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED]:return self._out('RETRYABLE_BUSY','WRITER_BUSY')
                    return self._out('IO_ERROR','COMMIT_NOT_RETAINED')
                except Exception:return self._out('UNKNOWN','COMMIT_OUTCOME_UNKNOWN')
            error_name=getattr(e,'sqlite_errorname',None)
            return self._out('IO_ERROR',error_name if error_name else ('STORAGE_ENOSPC' if getattr(e,'errno',None)==errno.ENOSPC else 'STORAGE_IO_ERROR'))
        finally:
            if c:
                try:
                    if c.in_transaction:c.execute('ROLLBACK')
                finally:c.close()
    def get_receipt(self,tx,digest=None):
        with self._work_scope():return self._get_receipt(tx,digest)
    def _get_receipt(self,tx,digest=None):
        need(isinstance(tx,str) and bool(reader.UUID.fullmatch(tx)),'INVALID_TRANSACTION_ID');c=self._connect(False)
        try:
            c.execute('BEGIN');row=c.execute('SELECT commit_sequence,manifest_sha256 FROM commits WHERE transaction_id=?',(tx,)).fetchone()
            if not row:return None
            need(digest is None or digest==row[1],'TRANSACTION_HASH_MISMATCH','INTEGRITY_ERROR');receipt,_=self._verify_commit(c,row[0]);return receipt
        finally:c.close()
    def read_original(self,tx,path):
        with self._work_scope():yield from self._read_original(tx,path)
    def _read_original(self,tx,path):
        """Read exact retained logical file in a SQLite read snapshot; no intake access."""
        reader.valid_path(path);need(isinstance(tx,str) and bool(reader.UUID.fullmatch(tx)),'INVALID_TRANSACTION_ID');c=self._connect(False)
        try:
            c.execute('BEGIN');row=c.execute('SELECT commit_sequence FROM commits WHERE transaction_id=?',(tx,)).fetchone();need(row is not None,'RECEIPT_NOT_FOUND','INTEGRITY_ERROR');self._verify_commit(c,row[0])
            f=c.execute('SELECT file_id,path,byte_length,sha256,length(file_blob) FROM files WHERE commit_sequence=? AND path=?',(row[0],path)).fetchone();need(f,'ORIGINAL_NOT_FOUND','INTEGRITY_ERROR')
            budget=self._work.get()
            if budget:budget.charge(f[2]) # Reserve export reads before exposing bytes.
            with c.blobopen('files','file_blob',f[0],readonly=True) as b:
                while raw:=b.read(self.contracts.policy['blob_chunk_bytes']):
                    if budget:budget.tick()
                    yield raw
        finally:c.close()
    def import_package(self,intake,tx,stage):
        result=reader.read_package(intake,tx,stage)
        if result.snapshot:
            with result.snapshot:return self.import_snapshot(result.snapshot)
        if result.status in ['INCOMPLETE','REJECTED']:
            attempt=str(uuid.uuid4());valid_tx=tx if isinstance(tx,str) and reader.UUID.fullmatch(tx) else None
            return self._out(result.status,result.code,self._receipt(result.status,result.code,attempt,valid_tx))
        return self._out(result.status,result.code)
