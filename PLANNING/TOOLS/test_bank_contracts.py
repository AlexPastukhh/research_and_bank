"""Meaningful negative conformance cases; synthetic temporary copies, no Bank writes."""
import copy,json,unittest,tempfile,shutil,uuid,hashlib
from pathlib import Path
import check_bank_contracts as c
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  idx=c.load(c.CONTRACTS/'BANK_TYPE_EXAMPLES/INDEX.json')['examples'];cls.idx=idx
  cls.create=c.validate_package(c.ROOT/idx['create']['path']);cls.source=c.validate_package(c.ROOT/idx['source_boundary']['path'],'R0_SOURCE_BOUNDARY')
 def bad(self,docs,profile='R1',accepted=()):
  with self.assertRaises(c.ContractError):c.validate_documents(docs,profile,accepted)
 def test_valid_history_and_independent_forms(self):
  self.assertEqual(c.check_all(),{'create':4,'continuation':1,'source_boundary':4})
  note=copy.deepcopy(next(d for d in self.create if d['object_type']=='Annotation'));note['data']['targets']=[];c.validate_documents([note])
  asset=copy.deepcopy(next(d for d in self.create if d['object_type']=='Asset'));asset['data']['storage']={'mode':'locator','uri':'https://example.org/reference','label':None};c.validate_documents([asset])
  archive=next(d for d in self.source if d['object_type']=='Source' and d['data']['subject_entity_ref'] is None);c.validate_documents([archive],'R0_SOURCE_BOUNDARY')
  self.bad([archive])
  self.bad(c.validate_package(c.ROOT/self.idx['continuation']['path'],accepted=self.create))
 def test_schema_failures(self):
  asset=next(d for d in self.create if d['object_type']=='Asset');note=next(d for d in self.create if d['object_type']=='Annotation');entity=next(d for d in self.create if d['object_type']=='Entity')
  mutations=[('unknown field',asset,lambda d:d.update(unknown=1)),('schema version',asset,lambda d:d.update(schema='bank-asset/2')),('wrong object type',asset,lambda d:d.update(object_type='Source')),('wrong UUID',asset,lambda d:d.update(object_id='legacy-1')),('UUID newline',asset,lambda d:d.update(object_id=d['object_id']+'\n')),('date',asset,lambda d:d.update(revision_created_at='2026-10-06')),('date offset',asset,lambda d:d.update(revision_created_at='2026-10-06T05:00:00+01:00')),('numeric title',asset,lambda d:d.update(title=4)),('missing provenance',asset,lambda d:d.pop('provenance')),('external origin missing locator',asset,lambda d:d['provenance'].update(origin_kind='external_capture')),('derived missing inputs',asset,lambda d:d['provenance'].update(origin_kind='derived')),('asset negative size',asset,lambda d:d['data']['storage'].update(byte_length=-1)),('invalid media',asset,lambda d:d['data']['storage'].update(media_type='invalid')),('entity-as-source',entity,lambda d:d['data'].update(entity_kind='source')),('AI origin mismatch',note,lambda d:d['provenance'].update(origin_kind='user_authored')),('invalid author',note,lambda d:d['data']['author'].update(kind='invented')),('empty note',note,lambda d:d['data'].update(body=''))]
  for label,original,mutate in mutations:
   with self.subTest(label=label):
    docs=copy.deepcopy(self.create);d=next(d for d in docs if d['object_id']==original['object_id']);mutate(d);self.bad(docs)
 def test_reference_identity_and_cycles(self):
  for label in ['unresolved','wrong type','duplicate member','duplicate object','duplicate revision','source reference','cycle','object type change']:
   with self.subTest(label=label):
    docs=copy.deepcopy(self.create);a,e,n,col=docs
    if label=='unresolved':n['data']['targets'][0]['revision_id']=str(uuid.uuid4())
    if label=='wrong type':n['data']['targets'][0]['object_type']='Entity'
    if label=='duplicate member':col['data']['members'].append(copy.deepcopy(col['data']['members'][0]))
    if label=='duplicate object':docs.append(copy.deepcopy(a));docs[-1]['revision_id']=str(uuid.uuid4())
    if label=='duplicate revision':n['revision_id']=a['revision_id']
    if label=='source reference':a['provenance']['source_ref']={k:self.source[0][k] for k in ['object_type','object_id','revision_id']}
    if label=='cycle':
     a['provenance']['derived_from']=[{k:n[k] for k in ['object_type','object_id','revision_id']}];n['provenance']['derived_from']=[{k:a[k] for k in ['object_type','object_id','revision_id']}]
    if label=='object type change':
     docs=[copy.deepcopy(n)];docs[0]['object_id']=a['object_id'];docs[0]['revision_id']=str(uuid.uuid4());self.bad(docs,accepted=[a]);continue
    self.bad(docs)
  old=copy.deepcopy(self.create[0]);new=copy.deepcopy(self.create[2]);new['revision_id']=old['revision_id'];new['data']['targets']=[];self.bad([new],accepted=[old])
  sources=copy.deepcopy(self.source);sources[2]['data']['subject_entity_ref']={k:sources[0][k] for k in ['object_type','object_id','revision_id']};self.bad(sources,'R0_SOURCE_BOUNDARY')
 def test_strict_json_and_receipts(self):
  for raw in [b'{"a":1,"a":2}',b'{"a":NaN}',b'\xef\xbb\xbf{}',b'{']:
   with self.subTest(raw=raw),self.assertRaises(c.ContractError):c.strict_json(raw)
  receipt={'protocol':'local-bank-intake/1','attempt_id':str(uuid.uuid4()),'transaction_id':str(uuid.uuid4()),'manifest_sha256':'0'*64,'recorded_at':'2026-10-06T05:40:00Z','status':'ACCEPTED','code':'OK','diagnostics':[],'commit_id':str(uuid.uuid4()),'commit_sequence':1,'committed':[{'object_id':str(uuid.uuid4()),'revision_id':str(uuid.uuid4())}]};c.validate_envelope(receipt)
  for label in ['missing commit','error with commit','wrong success code','unknown state']:
   r=copy.deepcopy(receipt)
   if label=='missing commit':r.pop('commit_id')
   if label=='error with commit':r.update(status='CONFLICT',code='BASE_REVISION_MISMATCH')
   if label=='wrong success code':r['code']='UNKNOWN'
   if label=='unknown state':r['status']='UNKNOWN'
   with self.subTest(label=label),self.assertRaises(c.ContractError):c.validate_envelope(r)
 def test_package_integrity(self):
  for label in ['tampered','missing','extra','operation mismatch','descriptor mismatch','manifest mismatch','duplicate operation']:
   with self.subTest(label=label),tempfile.TemporaryDirectory() as tmp:
    original=c.ROOT/self.idx['create']['path'];folder=Path(tmp)/original.name;shutil.copytree(original,folder)
    m=c.load(folder/'manifest.json');op=m['operations'][0];docpath=folder/op['document_path']
    if label=='tampered':(folder/'files/report.md').write_text('changed')
    if label=='missing':(folder/'files/report.md').unlink()
    if label=='extra':(folder/'extra.txt').write_text('unlisted')
    if label=='operation mismatch':op['revision_id']=str(uuid.uuid4())
    if label=='descriptor mismatch':
     doc=c.load(docpath);doc['data']['storage']['byte_length']+=1;docpath.write_text(json.dumps(doc),encoding='utf8');f=next(f for f in m['files'] if f['path']==op['document_path']);f.update(byte_length=docpath.stat().st_size,sha256=hashlib.sha256(docpath.read_bytes()).hexdigest())
    if label=='duplicate operation':m['operations'].append(copy.deepcopy(op))
    raw=json.dumps(m).encode();(folder/'manifest.json').write_bytes(raw);ready=c.load(folder/'READY.json');ready.update(manifest_byte_length=len(raw),manifest_sha256=hashlib.sha256(raw).hexdigest())
    if label=='manifest mismatch':ready['manifest_sha256']='0'*64
    (folder/'READY.json').write_text(json.dumps(ready),encoding='utf8')
    with self.assertRaises(c.ContractError):c.validate_package(folder)
if __name__=='__main__':unittest.main()
