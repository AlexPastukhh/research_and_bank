from pathlib import Path
import sys,json,copy,uuid,tempfile,shutil,hashlib,sqlite3,datetime
ROOT=Path(r'C:\Users\alexa\research_and_bank');sys.path.insert(0,str(ROOT/'PLANNING/TOOLS'));import check_bank_contracts as v
index=v.load(ROOT/'PLANNING/CONTRACTS/BANK_TYPE_EXAMPLES/INDEX.json');fixture=ROOT/index['examples']['create']['path'];docs=v.validate_package(fixture)
results={}
# Full current validate_documents with an already accepted identical command is not a replay validator.
try:v.validate_documents(docs,accepted=docs)
except v.ContractError as e:results['replay_naive_fresh_domain_before_lookup']={'observed':str(e),'expected':'DUPLICATE_REVISION','confirmed':str(e)=='DUPLICATE_REVISION'}
else:results['replay_naive_fresh_domain_before_lookup']={'confirmed':False}
# Full type/ref pure checks do not bind Asset storage metadata to its manifest descriptor.
changed=copy.deepcopy(docs);asset=next(d for d in changed if d['object_type']=='Asset');asset['data']['storage']['sha256']='0'*64
v.validate_documents(changed);results['asset_binding_missing_from_pure_helper']={'pure_domain_observed':'PASS','actual_retained_hash':next(d for d in docs if d['object_type']=='Asset')['data']['storage']['sha256'],'mutant_asset_hash':asset['data']['storage']['sha256']}
with tempfile.TemporaryDirectory(prefix='bank-card-review-') as t:
 package=Path(t)/fixture.name;shutil.copytree(fixture,package);manifest=v.load(package/'manifest.json');op=next(o for o in manifest['operations'] if o['object_id']==asset['object_id']);p=package/op['document_path'];raw=(json.dumps(asset,indent=2)+'\n').encode();p.write_bytes(raw)
 for f in manifest['files']:
  if f['path']==op['document_path']:f.update(byte_length=len(raw),sha256=hashlib.sha256(raw).hexdigest())
 raw=(json.dumps(manifest,indent=2)+'\n').encode();(package/'manifest.json').write_bytes(raw);ready=v.load(package/'READY.json');ready.update(manifest_byte_length=len(raw),manifest_sha256=hashlib.sha256(raw).hexdigest());(package/'READY.json').write_text(json.dumps(ready),encoding='utf-8')
 try:v.validate_package(package)
 except v.ContractError as e:results['asset_binding_missing_from_pure_helper'].update(full_reference_observed=str(e),confirmed=str(e)=='ASSET_DESCRIPTOR_MISMATCH')
 else:results['asset_binding_missing_from_pure_helper']['confirmed']=False
# R1 independent-save scope is narrower than transport's intent enum.
with tempfile.TemporaryDirectory(prefix='bank-card-intent-review-') as t:
 package=Path(t)/fixture.name;shutil.copytree(fixture,package);manifest=v.load(package/'manifest.json');manifest['intent']='tracked_research';raw=(json.dumps(manifest)+'\n').encode();(package/'manifest.json').write_bytes(raw);ready=v.load(package/'READY.json');ready.update(manifest_byte_length=len(raw),manifest_sha256=hashlib.sha256(raw).hexdigest());(package/'READY.json').write_text(json.dumps(ready),encoding='utf-8')
 observed=v.validate_package(package,profile='R1');results['r1_intent_not_checked_by_static_helper']={'manifest_intent':'tracked_research','static_R1_observed':'PASS','documents':len(observed),'confirmed':bool(observed),'scope_requirement':'LOCAL_WRITE_CONTRACT.md: R1 independent save; R2 tracked research; importer must gate intent separately.'}

# Incoming cap does not cap total accepted history. Valid 1100-revision causal chain, newest-first.
entity=next(d for d in docs if d['object_type']=='Entity');history=[]
for i in range(sys.getrecursionlimit()+100):
 d=copy.deepcopy(entity);d['object_id']=str(uuid.uuid4());d['revision_id']=str(uuid.uuid4());d['data']['asset_refs']=[];d['provenance']['derived_from']=[] if not history else [{'object_type':'Entity','object_id':history[-1]['object_id'],'revision_id':history[-1]['revision_id']}];history.append(d)
fresh=copy.deepcopy(history[0]);fresh['object_id']=str(uuid.uuid4());fresh['revision_id']=str(uuid.uuid4())
try:v.validate_documents([fresh],accepted=list(reversed(history)))
except RecursionError:results['unbounded_history_recursive_helper']={'accepted_documents':len(history),'incoming_documents':1,'observed':'RecursionError','confirmed':True}
except Exception as e:results['unbounded_history_recursive_helper']={'observed':type(e).__name__+':'+str(e),'confirmed':False}
else:results['unbounded_history_recursive_helper']={'observed':'PASS','confirmed':False}
# SQL triggers are not the authority for incremental BLOB writes: writer must scope row IDs itself.
c=sqlite3.connect(':memory:',isolation_level=None);c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA trusted_schema=OFF');has_defensive=hasattr(c,'setconfig') and hasattr(sqlite3,'SQLITE_DBCONFIG_DEFENSIVE')
if has_defensive:c.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE,True)
c.executescript((ROOT/'PLANNING/CONTRACTS/LOCAL_STORAGE_SCHEMA.sql').read_text(encoding='utf-8-sig'));c.execute('BEGIN IMMEDIATE');c.execute("INSERT INTO commits(transaction_id,commit_id,manifest_sha256,manifest_blob,ready_blob,accepted_at,policy_version,policy_blob) VALUES(?,?,?,?,?,?,?,?)",('tx','commit','0'*64,b'{}',b'{}','2026-10-06T00:00:00Z','synthetic',b'{}'));seq=c.execute('SELECT commit_sequence FROM commits').fetchone()[0];c.execute('INSERT INTO files(commit_sequence,path,byte_length,sha256,file_blob) VALUES(?,?,?,?,?)',(seq,'fixture.bin',5,hashlib.sha256(b'hello').hexdigest(),b'hello'));fid=c.execute('SELECT file_id FROM files').fetchone()[0];c.execute('INSERT INTO accepted_receipts VALUES(?,?)',(seq,b'{}'));c.execute('COMMIT')
try:c.execute('UPDATE files SET file_blob=? WHERE file_id=?',(b'jello',fid))
except sqlite3.IntegrityError as e:sql_update=str(e)
else:sql_update='UNEXPECTED_ALLOWED'
with c.blobopen('files','file_blob',fid,readonly=False) as b:b.write(b'jello')
value=c.execute('SELECT file_blob FROM files WHERE file_id=?',(fid,)).fetchone()[0]
results['incremental_blob_authority']={'sql_update_observed':sql_update,'blob_write_existing_row_observed':value.decode(),'defensive_enabled':has_defensive,'confirmed':sql_update=='immutable_original' and value==b'jello','scope':'Deliberate trusted-connection primitive probe, not incoming exploitable SQL or installed Bank defect'};c.close()
assert all(x.get('confirmed',False) for x in results.values()),results
report={'record_kind':'sqlite_importer_card_native_counterexamples','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'sqlite_version':sqlite3.sqlite_version,'scope':'Read existing contracts/fixtures; mutate owned temporary fixture and in-memory SQLite only; no Bank/importer acceptance','results':results,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'PLANNING/TOOLS/check_bank_contracts.py',ROOT/'PLANNING/CONTRACTS/LOCAL_STORAGE_SCHEMA.sql',ROOT/'PLANNING/WORK_ITEMS/R1_SQLITE_IMPORTER.json']}}
print('DBCOUNTER='+json.dumps(report),flush=True)
