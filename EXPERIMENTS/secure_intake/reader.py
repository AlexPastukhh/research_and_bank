"""Transport-only Windows secure reader. VERIFIED_TRANSPORT is NOT Bank acceptance."""
from pathlib import Path
from contextlib import ExitStack
from types import MappingProxyType
import errno, hashlib, json, math, os, re, threading, uuid
from jsonschema import Draft202012Validator, FormatChecker
import win32_io as native

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = 'local-bank-intake/1'
UUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}')
PATH = re.compile(r'(?:[a-z0-9][a-z0-9_-]*/)*[a-z0-9][a-z0-9_-]*(?:\.[a-z0-9]+)?')
RESERVED = {'manifest.json','ready.json','ready.pending','manifest.pending'}
class Rejected(ValueError): pass
class Cancelled(Exception): pass
class ConfigurationError(ValueError): pass
def configured_policy(raw):
    try:return Policy(raw)
    except Rejected as exc:raise ConfigurationError('INVALID_POLICY') from exc
def need(ok, code):
    if not ok: raise Rejected(code)
def valid_path(value):
    need(isinstance(value,str) and len(value)<=180 and bool(PATH.fullmatch(value)), 'INVALID_PATH')
    for segment in value.split('/'):
        stem = segment.split('.')[0].upper()
        need(stem not in ['CON','PRN','AUX','NUL'] and not re.fullmatch(r'(COM|LPT)[1-9]',stem), 'RESERVED_DEVICE')
        need(segment.casefold() not in RESERVED, 'RESERVED_NAME')
    return value
def strict_json(raw, cap, depth):
    need(len(raw)<=cap,'LIMIT_EXCEEDED')
    need(not raw.startswith(b'\xef\xbb\xbf'),'JSON_BOM')
    level=0; string=False; escaped=False
    for byte in raw:
        if string:
            if escaped: escaped=False
            elif byte==92: escaped=True
            elif byte==34: string=False
        elif byte==34: string=True
        elif byte in [91,123]:
            level+=1; need(level<=depth,'JSON_DEPTH')
        elif byte in [93,125]: level-=1
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,'DUPLICATE_JSON_KEY'); result[key]=value
        return result
    try:
        data=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,
                        parse_constant=lambda _: (_ for _ in ()).throw(Rejected('NONFINITE_JSON')))
        # Reject lone surrogate values/keys before later UTF-8 sizing or diagnostics.
        def unicode_values(value):
            if isinstance(value,str): value.encode('utf-8')
            elif isinstance(value,float): need(math.isfinite(value),'NONFINITE_JSON')
            elif isinstance(value,dict):
                for k,v in value.items(): k.encode('utf-8'); unicode_values(v)
            elif isinstance(value,list):
                for x in value: unicode_values(x)
        unicode_values(data); return data
    except Rejected:raise
    except (UnicodeError,ValueError,RecursionError) as exc: raise Rejected('INVALID_JSON') from exc

class Policy:
    def __init__(self, raw):
        obj=strict_json(raw,524288,64)
        need(isinstance(obj,dict) and isinstance(obj.get('limits'),dict),'INVALID_POLICY')
        expected={'file_bytes','package_bytes','files','operations','manifest_bytes','ready_bytes','object_json_bytes',
                  'json_container_depth','annotation_body_bytes','title_bytes','locator_bytes','diagnostic_bytes','blob_chunk_bytes','writer_busy_timeout_ms'}
        need(set(obj['limits'])==expected and isinstance(obj.get('policy_version'),str),'INVALID_POLICY')
        for value in obj['limits'].values(): need(type(value) is int and 0<value<=9007199254740991,'INVALID_POLICY')
        # Do not permit unchecked parser depth/chunk/count increases in this prototype.
        limits=obj['limits'];need(limits['json_container_depth']<=64 and limits['blob_chunk_bytes']<=1048576 and limits['files']<=128 and limits['operations']<=128,'UNSUPPORTED_POLICY')
        need(limits['manifest_bytes']<=524288 and limits['ready_bytes']<=16384 and limits['object_json_bytes']<=2097152,'UNSUPPORTED_POLICY')
        need(limits['file_bytes']<=67108864 and limits['package_bytes']<=268435456 and limits['diagnostic_bytes']<=8192,'UNSUPPORTED_POLICY')
        self.raw=bytes(raw);self.version=obj['policy_version'];self.limits=MappingProxyType(dict(limits))
    def __getitem__(self,key): return self.limits[key]

class Snapshot:
    """Lifetime-bound opaque snapshot; consumer never reopens source or staged filenames."""
    status='VERIFIED_TRANSPORT'
    def __init__(self, directory, owned, handles, stack, metadata, manifest, ready, policy):
        self._directory=directory; self._owned=owned; self._handles=handles; self._stack=stack
        self._closed=False;self._lock=threading.RLock();self._chunk=policy['blob_chunk_bytes']
        self.files=MappingProxyType(dict(metadata));self.manifest_bytes=bytes(manifest);self.ready_bytes=bytes(ready)
        self.policy_bytes=policy.raw;self.policy_version=policy.version
        self.transaction_id=json.loads(ready.decode('utf-8'))['transaction_id']
        self.manifest_sha256=hashlib.sha256(manifest).hexdigest()
    def iter_bytes(self,name):
        with self._lock:
            if self._closed: raise Rejected('SNAPSHOT_CLOSED')
            need(name in self._handles,'UNKNOWN_SNAPSHOT_FILE')
            handle=self._handles[name];length,digest=self.files[name]
            need(handle.size()==length and handle.info().links==1,'SNAPSHOT_INTEGRITY')
            # Full bounded integrity pass BEFORE exposing any consumer bytes.
            handle.seek();actual=hashlib.sha256();count=0
            while raw:=handle.read(self._chunk): actual.update(raw);count+=len(raw);need(count<=length,'SNAPSHOT_INTEGRITY')
            need(count==length and actual.hexdigest()==digest,'SNAPSHOT_INTEGRITY')
            handle.seek();count=0
            while raw:=handle.read(self._chunk):
                count+=len(raw);need(count<=length,'SNAPSHOT_INTEGRITY');yield raw
            need(count==length,'SNAPSHOT_INTEGRITY')
    def close(self):
        with self._lock:
            if self._closed: return
            self._closed=True
            # Release file handles while directory/root leases still prevent redirects.
            errors=[]
            for h in self._handles.values():
                try:h.close()
                except OSError:errors.append('HANDLE_CLOSE_FAILED')
            self._handles.clear()
            for p in self._owned:
                try:os.unlink(p)
                except FileNotFoundError:pass
                except OSError:errors.append('STAGING_RECLAIM_FAILED')
            self._stack.close()
            try:os.rmdir(self._directory)
            except OSError:errors.append('STAGING_QUARANTINED')
            if errors:raise OSError(','.join(errors))
    def __enter__(self): return self
    def __exit__(self,*_): self.close()

class Result:
    def __init__(self,status,code,snapshot=None,diagnostic=None):
        self.status=status;self.code=code;self.snapshot=snapshot;self.diagnostic=diagnostic or code

def read_package(intake_root, transaction_id, staging_root, *, policy_bytes=None, schema=None, cancel=None, _hook=None):
    """All roots/policy/schema/hooks are trusted configuration, never package-supplied paths."""
    if policy_bytes is None: policy_bytes=(ROOT/'PLANNING/CONTRACTS/LOCAL_INTAKE_LIMITS.json').read_bytes()
    policy=configured_policy(policy_bytes)
    if schema is None: schema=json.loads((ROOT/'PLANNING/CONTRACTS/LOCAL_WRITE_ENVELOPE.schema.json').read_text(encoding='utf-8'))
    validator=Draft202012Validator(schema,format_checker=FormatChecker())
    source=ExitStack();stage=ExitStack();owned=[];staged_handles={};directory=None
    def outcome(status, code, *, snapshot=None, diagnostic=None):
        message=(diagnostic if diagnostic is not None else code).encode('utf-8')
        message=message[:policy['diagnostic_bytes']].decode('utf-8','ignore')
        result=Result(status,code,snapshot)
        result.diagnostic=message
        return result
    def event(name,value=None):
        if cancel and cancel(): raise Cancelled()
        if _hook:_hook(name,value)
        if cancel and cancel(): raise Cancelled()
    def bounded(handle,cap):
        need(handle.size()<=cap,'LIMIT_EXCEEDED');handle.seek();chunks=[];total=0
        while raw:=handle.read(min(policy['blob_chunk_bytes'],cap+1-total)):
            total+=len(raw);need(total<=cap,'LIMIT_EXCEEDED');chunks.append(raw);event('read_chunk',total)
        return b''.join(chunks)
    def cleanup():
        errors=[]
        for h in staged_handles.values():
            try:h.close()
            except OSError:errors.append('HANDLE_CLOSE_FAILED')
        for p in owned:
            try:os.unlink(p)
            except FileNotFoundError:pass
            except OSError:errors.append('STAGING_RECLAIM_FAILED')
        stage.close()
        if directory is not None:
            try:os.rmdir(directory)
            except FileNotFoundError:pass
            except OSError:errors.append('STAGING_QUARANTINED')
        return errors
    try:
        need(isinstance(transaction_id,str) and bool(UUID.fullmatch(transaction_id)),'INVALID_TRANSACTION_ID')
        event('begin')
        ir=Path(intake_root);sr=Path(staging_root)
        need(ir!=sr and not ir.is_relative_to(sr) and not sr.is_relative_to(ir),'ROOT_OVERLAP')
        root_handle=source.enter_context(native.configured_root(ir));stage.enter_context(native.configured_root(sr))
        package=ir/transaction_id;directory_handles={}
        package_handle=source.enter_context(native.Handle(package,directory=True))
        native.verify_private_acl(package_handle);directory_handles['']=package_handle
        try:ready_handle=source.enter_context(native.Handle(package/'READY.json'))
        except OSError as exc:
            if getattr(exc,'winerror',None)==2:source.close();stage.close();return outcome('INCOMPLETE','READY_NOT_PUBLISHED')
            raise
        native.verify_private_acl(ready_handle)
        ready_identity=ready_handle.identity();ready_raw=bounded(ready_handle,policy['ready_bytes'])
        ready=strict_json(ready_raw,policy['ready_bytes'],policy['json_container_depth'])
        need(not list(validator.iter_errors(ready)),'READY_SCHEMA')
        need(ready.get('protocol')==PROTOCOL and ready.get('transaction_id')==transaction_id,'TRANSACTION_ID_MISMATCH')
        try:manifest_handle=source.enter_context(native.Handle(package/'manifest.json'))
        except OSError as exc:
            if getattr(exc,'winerror',None)==2:raise Rejected('MISSING_MANIFEST') from exc
            raise
        native.verify_private_acl(manifest_handle)
        manifest_identity=manifest_handle.identity();manifest_raw=bounded(manifest_handle,policy['manifest_bytes'])
        need(len(manifest_raw)==ready['manifest_byte_length'] and hashlib.sha256(manifest_raw).hexdigest()==ready['manifest_sha256'],'MANIFEST_INTEGRITY')
        manifest=strict_json(manifest_raw,policy['manifest_bytes'],policy['json_container_depth'])
        need(isinstance(manifest,dict) and isinstance(manifest.get('files'),list) and isinstance(manifest.get('operations'),list),'MANIFEST_SCHEMA')
        need(len(manifest['files'])<=policy['files'] and len(manifest['operations'])<=policy['operations'],'LIMIT_EXCEEDED')
        need(not list(validator.iter_errors(manifest)),'MANIFEST_SCHEMA')
        need(manifest.get('protocol')==PROTOCOL and manifest.get('transaction_id')==transaction_id,'TRANSACTION_ID_MISMATCH')
        files=manifest['files'];operations=manifest['operations']
        need(len(files)<=policy['files'] and len(operations)<=policy['operations'],'LIMIT_EXCEEDED')
        descriptors={};parents=set()
        for f in files:
            name=valid_path(f['path']);need(name not in descriptors,'DUPLICATE_FILE')
            need(f['byte_length']<=policy['file_bytes'],'LIMIT_EXCEEDED');descriptors[name]=f
            parts=name.split('/')
            for i in range(1,len(parts)): parents.add('/'.join(parts[:i]))
        need(not set(descriptors)&parents,'FILE_DIRECTORY_COLLISION')
        document_paths=set();object_ids=set();revision_ids=set()
        for operation in operations:
            name=valid_path(operation['document_path'])
            need(name in descriptors,'UNLISTED_DOCUMENT');need(name not in document_paths,'DUPLICATE_DOCUMENT')
            need(operation['object_id'] not in object_ids and operation['revision_id'] not in revision_ids,'DUPLICATE_OPERATION_ID')
            document_paths.add(name);object_ids.add(operation['object_id']);revision_ids.add(operation['revision_id'])
            need(descriptors[name]['byte_length']<=policy['object_json_bytes'],'LIMIT_EXCEEDED')
        expected_bytes=len(ready_raw)+len(manifest_raw)+sum(f['byte_length'] for f in files)
        need(expected_bytes<=policy['package_bytes'],'LIMIT_EXCEEDED')
        # Lock each allowed directory before descending; OPEN_REPARSE_POINT sees link itself.
        for name in sorted(parents,key=lambda x:(x.count('/'),x)):
            h=source.enter_context(native.Handle(package/name,directory=True));native.verify_private_acl(h);directory_handles[name]=h
        def inventory():
            seen_files=set();seen_dirs=set();entry_count=0
            for name in ['',*sorted(parents)]:
                path=package/name
                with os.scandir(path) as entries:
                    for entry in entries:
                        entry_count+=1;need(entry_count<=len(descriptors)+len(parents)+2,'EXTRA_ENTRY')
                        rel=(name+'/' if name else '')+entry.name
                        if rel in ['READY.json','manifest.json'] and name=='': seen_files.add(rel);continue
                        valid_path(rel)
                        # Do not follow redirects, including unknown/unlisted directories.
                        info=entry.stat(follow_symlinks=False)
                        need(not getattr(info,'st_file_attributes',0)&0x400,'REPARSE_POINT')
                        if entry.is_dir(follow_symlinks=False):need(rel in parents,'EXTRA_DIRECTORY');seen_dirs.add(rel)
                        else:need(rel in descriptors,'EXTRA_FILE');seen_files.add(rel)
            need(seen_dirs==parents and seen_files==set(descriptors)|{'READY.json','manifest.json'},'INVENTORY_MISMATCH')
        inventory();event('inventory_checked')
        directory=sr/('attempt-'+str(uuid.uuid4()));native.private_directory(directory)
        stage.enter_context(native.Handle(directory,directory=True))
        metadata={};measured=len(ready_raw)+len(manifest_raw);source_files=[]
        for index,name in enumerate(sorted(descriptors)):
            f=descriptors[name]
            try:h=source.enter_context(native.Handle(package/name))
            except OSError as exc:
                if getattr(exc,'winerror',None)==2:raise Rejected('MISSING_FILE') from exc
                raise
            native.verify_private_acl(h);initial=h.identity()
            cap=policy['object_json_bytes'] if name in document_paths else policy['file_bytes']
            need(h.size()<=cap,'LIMIT_EXCEEDED');need(h.size()==f['byte_length'],'FILE_INTEGRITY')
            path=directory/(str(index)+'.blob');out=native.Handle(path,new=True);staged_handles[name]=out;owned.append(path);native.verify_private_acl(out)
            digest=hashlib.sha256();length=0;json_chunks=[];event('file_opened',name)
            while raw:=h.read(policy['blob_chunk_bytes']):
                length+=len(raw);measured+=len(raw)
                need(length<=cap and measured<=policy['package_bytes'],'LIMIT_EXCEEDED')
                event('before_stage_write',name);out.write(raw);digest.update(raw)
                if name in document_paths:json_chunks.append(raw)
                event('payload_chunk',name)
            need(length==f['byte_length'] and digest.hexdigest()==f['sha256'],'FILE_INTEGRITY')
            need(h.identity()==initial,'SOURCE_CHANGED')
            if name in document_paths:strict_json(b''.join(json_chunks),cap,policy['json_container_depth'])
            out.seek();saved=hashlib.sha256();saved_length=0
            while raw:=out.read(policy['blob_chunk_bytes']):saved.update(raw);saved_length+=len(raw)
            need(saved_length==length and saved.hexdigest()==digest.hexdigest(),'STAGING_INTEGRITY')
            metadata[name]=(length,digest.hexdigest());source_files.append((h,initial));event('file_staged',name)
        event('before_final_check');inventory()
        need(ready_handle.identity()==ready_identity and manifest_handle.identity()==manifest_identity,'SOURCE_CHANGED')
        need(bounded(ready_handle,policy['ready_bytes'])==ready_raw and bounded(manifest_handle,policy['manifest_bytes'])==manifest_raw,'SOURCE_CHANGED')
        for h,identity in source_files:native.verify_private_acl(h);need(h.identity()==identity,'SOURCE_CHANGED')
        for h in [ready_handle,manifest_handle,*directory_handles.values(),*staged_handles.values()]:native.verify_private_acl(h)
        need(measured==expected_bytes,'PACKAGE_INTEGRITY');event('before_success')
        snapshot=Snapshot(directory,owned,staged_handles,stage,metadata,manifest_raw,ready_raw,policy)
        source.close();return outcome('VERIFIED_TRANSPORT','OK',snapshot=snapshot)
    except Cancelled:
        source.close();errors=cleanup();return outcome('CANCELLED','CANCELLED',diagnostic='CANCELLED'+(':'+','.join(errors) if errors else ''))
    except (Rejected,native.SafetyError) as exc:
        source.close();errors=cleanup();message=str(exc).encode('utf-8')[:policy['diagnostic_bytes']].decode('utf-8','ignore')
        return outcome('REJECTED',str(exc),diagnostic=message+(':'+','.join(errors) if errors else ''))
    except OSError as exc:
        source.close();errors=cleanup();code='IO_ERROR_'+str(getattr(exc,'winerror',None) or exc.errno or 'UNKNOWN')
        return outcome('IO_ERROR',code,diagnostic=code+(':'+','.join(errors) if errors else ''))
    except BaseException:
        source.close();cleanup();raise
