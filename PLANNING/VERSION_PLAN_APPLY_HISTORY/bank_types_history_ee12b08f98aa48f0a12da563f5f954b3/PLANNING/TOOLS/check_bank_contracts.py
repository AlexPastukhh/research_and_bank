"""Read-only static schema/fixture conformance; NOT a production importer/security boundary."""
from pathlib import Path
import json,hashlib,re
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[2]
CONTRACTS=ROOT/'PLANNING/CONTRACTS'
class ContractError(ValueError):pass
def need(condition,code):
 if not condition:raise ContractError(code)
def strict_json(raw):
 def pairs(xs):
  out={}
  for k,v in xs:
   need(k not in out,'DUPLICATE_JSON_KEY');out[k]=v
  return out
 try:return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ContractError('NONFINITE_JSON')))
 except (UnicodeError,json.JSONDecodeError) as exc:raise ContractError('INVALID_JSON') from exc
def load(p):return strict_json(p.read_bytes())
def validators():
 bank=load(CONTRACTS/'BANK_TYPES.schema.json');env=load(CONTRACTS/'LOCAL_WRITE_ENVELOPE.schema.json')
 for s in [bank,env]:Draft202012Validator.check_schema(s)
 return Draft202012Validator(bank,format_checker=FormatChecker()),Draft202012Validator(env,format_checker=FormatChecker())
def validate_envelope(data):
 _,v=validators();need(not list(v.iter_errors(data)),'ENVELOPE_SCHEMA')
def refs(doc):
 yield from doc['provenance']['derived_from']
 if doc['provenance']['source_ref'] is not None:yield doc['provenance']['source_ref']
 data=doc['data'];kind=doc['object_type']
 if kind=='Entity':yield from data['asset_refs']
 if kind=='Annotation':yield from data['targets']
 if kind=='Collection':yield from data['members']
 if kind=='Source' and data['subject_entity_ref'] is not None:yield data['subject_entity_ref']
def validate_documents(docs,profile='R1',accepted=()):
 v,_=validators();reg=load(CONTRACTS/'BANK_SCHEMA_COMPATIBILITY.json');need(profile in reg['profiles'],'UNSUPPORTED_PROFILE')
 caps=reg['profiles'][profile];allowed={(x['object_type'],x['schema_ref']) for x in reg['schemas']}
 index={};object_ids=set();revision_ids=set()
 for doc in [*accepted,*docs]:
  need(not list(v.iter_errors(doc)),'OBJECT_SCHEMA')
  need((doc['object_type'],doc['schema']) in allowed,'UNSUPPORTED_SCHEMA')
  key=(doc['object_id'],doc['revision_id']);need(key not in index,'DUPLICATE_REVISION');index[key]=doc
 for doc in docs:
  oid=doc['object_id'];rid=doc['revision_id'];need(oid not in object_ids,'DUPLICATE_OBJECT');need(rid not in revision_ids,'DUPLICATE_REVISION_ID')
  object_ids.add(oid);revision_ids.add(rid)
  need(doc['object_type'] in caps['write_types'],'UNSUPPORTED_WRITE_TYPE')
  need(profile!='R1' or doc['provenance']['source_ref'] is None,'SOURCE_REF_OUTSIDE_R1')
  for old in accepted:
   if old['object_id']==oid:need(old['object_type']==doc['object_type'],'OBJECT_TYPE_CHANGED')
  for ref in refs(doc):
   need(ref['object_type'] in caps['read_types'],'UNSUPPORTED_REFERENCE_TYPE')
   target=index.get((ref['object_id'],ref['revision_id']));need(target is not None,'UNRESOLVED_REFERENCE')
   need(target['object_type']==ref['object_type'],'REFERENCE_TYPE_MISMATCH')
 # All causal references, including supplied accepted history, participate in cycle check.
 visited=set();active=set()
 def visit(key):
  need(key not in active,'DERIVATION_CYCLE')
  if key in visited:return
  active.add(key)
  for ref in index[key]['provenance']['derived_from']:
   dep=(ref['object_id'],ref['revision_id']);need(dep in index,'UNRESOLVED_REFERENCE');visit(dep)
  active.remove(key);visited.add(key)
 for key in index:visit(key)
 return docs
PATH=re.compile(r'(?:[a-z0-9][a-z0-9_-]*/)*[a-z0-9][a-z0-9_-]*(?:\.[a-z0-9]+)?')
def file_path(root,name):
 need(len(name)<=180 and bool(PATH.fullmatch(name)),'INVALID_FIXTURE_PATH')
 for part in name.split('/'):
  stem=part.split('.')[0].upper();need(stem not in ['CON','PRN','AUX','NUL'] and not re.fullmatch(r'(COM|LPT)[1-9]',stem),'RESERVED_PATH')
 q=root/name;need(q.resolve().is_relative_to(root.resolve()),'OUTSIDE_FIXTURE');need(not q.is_symlink(),'FIXTURE_SYMLINK');return q
def validate_package(folder,profile='R1',accepted=()):
 _,v=validators();raw=(folder/'manifest.json').read_bytes();m=strict_json(raw);ready=load(folder/'READY.json')
 for x in [m,ready]:need(not list(v.iter_errors(x)),'ENVELOPE_SCHEMA')
 need(m['transaction_id']==ready['transaction_id']==folder.name,'PACKAGE_ID_MISMATCH')
 need(ready['manifest_byte_length']==len(raw) and ready['manifest_sha256']==hashlib.sha256(raw).hexdigest(),'MANIFEST_INTEGRITY')
 desc={}
 for f in m['files']:
  name=f['path'];need(name not in desc,'DUPLICATE_FILE');need(name.split('/')[-1] not in ['manifest.json','ready.json','ready.pending'],'RESERVED_PATH')
  q=file_path(folder,name);need(q.is_file(),'MISSING_FILE');b=q.read_bytes();need(len(b)==f['byte_length'] and hashlib.sha256(b).hexdigest()==f['sha256'],'FILE_INTEGRITY');desc[name]=f
 expected={'manifest.json','READY.json'}|set(desc)
 need({p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}==expected,'UNLISTED_FILE')
 docs=[];op_ids=set();op_revs=set();document_paths=set()
 for op in m['operations']:
  need(op['object_id'] not in op_ids,'DUPLICATE_OBJECT');need(op['revision_id'] not in op_revs,'DUPLICATE_REVISION_ID');need(op['document_path'] not in document_paths,'DUPLICATE_DOCUMENT')
  op_ids.add(op['object_id']);op_revs.add(op['revision_id']);document_paths.add(op['document_path'])
  need(op['document_path'] in desc,'UNLISTED_DOCUMENT');doc=load(file_path(folder,op['document_path']))
  need(all(doc.get(k)==op[v] for k,v in [('object_id','object_id'),('revision_id','revision_id'),('object_type','type'),('schema','schema_ref')]),'OPERATION_DOCUMENT_MISMATCH')
  docs.append(doc)
 validate_documents(docs,profile,accepted)
 for doc in docs:
  if doc['object_type']=='Asset' and doc['data']['storage']['mode']=='bytes':
   storage=doc['data']['storage'];need(storage['file_path'] in desc,'UNLISTED_ASSET')
   f=desc[storage['file_path']];need(f['byte_length']==storage['byte_length'] and f['sha256']==storage['sha256'],'ASSET_DESCRIPTOR_MISMATCH')
 return docs
def check_all():
 index=load(CONTRACTS/'BANK_TYPE_EXAMPLES/INDEX.json');results={}
 for label in ['create','continuation','source_boundary']:
  e=index['examples'][label];history=[d for prior in e['accepted_inputs'] for d in results[prior]]
  results[label]=validate_package(ROOT/e['path'],e['profile'],history)
 # Older transport fixtures are synthetic ExampleItem, not production domain objects.
 for marker in (CONTRACTS/'LOCAL_WRITE_EXAMPLES').glob('*/READY.json'):
  m=load(marker.parent/'manifest.json');mark=load(marker);validate_envelope(m);validate_envelope(mark)
  raw=(marker.parent/'manifest.json').read_bytes();need(mark['manifest_sha256']==hashlib.sha256(raw).hexdigest() and mark['manifest_byte_length']==len(raw),'LEGACY_FIXTURE_MANIFEST')
 return {k:len(v) for k,v in results.items()}
if __name__=='__main__':print(json.dumps({'status':'PASS_STATIC_CONFORMANCE','examples':check_all(),'scope':'JSON Schema/bytes/identity/refs only; no runtime import/confinement/durable acceptance.'}))
