"""Synthetic direct-SQL storage experiment. NOT a production Bank importer."""
from pathlib import Path
import sqlite3,json,hashlib,uuid,unittest,tempfile,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
DDL=ROOT/'PLANNING/CONTRACTS/LOCAL_STORAGE_SCHEMA.sql'
POLICY=ROOT/'PLANNING/CONTRACTS/LOCAL_INTAKE_LIMITS.json'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def connection(db):
 c=sqlite3.connect(str(db),isolation_level=None,timeout=0.1)
 c.execute('PRAGMA journal_mode=DELETE');c.execute('PRAGMA synchronous=EXTRA');c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA trusted_schema=OFF');c.execute('PRAGMA cache_size=16')
 c.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE,True)
 need(c.getconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE),'defensive disabled')
 need(c.execute('PRAGMA journal_mode').fetchone()[0]=='delete','wrong journal')
 need(c.execute('PRAGMA synchronous').fetchone()[0]==3,'wrong sync')
 need(c.execute('PRAGMA foreign_keys').fetchone()[0]==1,'FK disabled')
 return c
def initialize(db):
 c=connection(db);c.executescript(DDL.read_text(encoding='utf-8'));c.close()
def payload(tx):return b'p'*(2*1024*1024)+tx.encode()
def stage(c,tx,object_id=None,base=None,receipt=True):
 oid=object_id or str(uuid.uuid4());rid=str(uuid.uuid4());blob=payload(tx)
 m=json.dumps({'synthetic_storage_probe':tx}).encode();cur=c.execute('INSERT INTO commits(transaction_id,commit_id,manifest_sha256,manifest_blob,ready_blob,accepted_at,policy_version,policy_blob) VALUES (?,?,?,?,?,?,?,?)',(tx,str(uuid.uuid4()),hashlib.sha256(m).hexdigest(),m,b'synthetic-ready','2026-10-06T05:45:00Z','r1-local-limits/1',POLICY.read_bytes()));seq=cur.lastrowid
 doc=json.dumps({'synthetic_storage_probe':True,'object_id':oid,'revision_id':rid}).encode()
 for name,b in [('files/raw.bin',blob),('objects/item.json',doc)]:c.execute('INSERT INTO files(commit_sequence,path,byte_length,sha256,file_blob) VALUES(?,?,?,?,?)',(seq,name,len(b),hashlib.sha256(b).hexdigest(),b))
 c.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?)',(rid,oid,'Asset','bank-asset/1',base,seq,0,'objects/item.json'))
 raw=json.dumps({'synthetic_receipt':True,'transaction_id':tx,'commit_sequence':seq,'revision_id':rid}).encode()
 if receipt:c.execute('INSERT INTO accepted_receipts VALUES(?,?)',(seq,raw))
 return oid,rid,raw
def save(c,tx,oid=None,base=None):
 c.execute('BEGIN IMMEDIATE')
 try:
  if oid:
   head=c.execute('SELECT revision_id FROM object_heads WHERE object_id=?',(oid,)).fetchone();need(head and head[0]==base,'stale base')
  result=stage(c,tx,oid,base);c.execute('COMMIT');return result
 except Exception:
  if c.in_transaction:c.execute('ROLLBACK')
  raise
def count(c):return tuple(c.execute('SELECT count(*) FROM '+name).fetchone()[0] for name in ['commits','files','revisions','accepted_receipts'])
def integrity(c):
 need(c.execute('PRAGMA integrity_check').fetchone()[0]=='ok','database corrupt');need(not c.execute('PRAGMA foreign_key_check').fetchall(),'broken FK')
 for size,h,b in c.execute('SELECT byte_length,sha256,file_blob FROM files'):need(len(b)==size and hashlib.sha256(b).hexdigest()==h,'original corrupt')
def budget(manifest_bytes,ready_bytes,files,operations):
 p=json.loads(POLICY.read_text())['limits']
 values=[manifest_bytes,ready_bytes,operations,*[n for n,is_doc in files]]
 need(all(type(n) is int and n>=0 for n in values),'invalid numeric input')
 need(manifest_bytes<=p['manifest_bytes'] and ready_bytes<=p['ready_bytes'],'header cap')
 need(len(files)<=p['files'] and operations<=p['operations'],'count cap')
 need(all(n<=p['file_bytes'] and (not is_doc or n<=p['object_json_bytes']) for n,is_doc in files),'file cap')
 need(manifest_bytes+ready_bytes+sum(n for n,is_doc in files)<=p['package_bytes'],'package cap')
def parsed_depth(value):
 limit=json.loads(POLICY.read_text())['limits']['json_container_depth'];stack=[(value,0)];max_depth=0
 while stack:
  item,d=stack.pop()
  if isinstance(item,(dict,list)):
   d+=1;need(d<=limit,'depth cap');max_depth=max(d,max_depth);stack.extend((v,d) for v in (item.values() if isinstance(item,dict) else item))
 return max_depth
def string_budget(value,key):
 limit=json.loads(POLICY.read_text())['limits'][key];need(isinstance(value,str) and len(value.encode('utf-8'))<=limit,'text cap')
class StorageTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='bank-storage-probe-');self.db=Path(self.temp.name)/'probe.sqlite';initialize(self.db);self.c=connection(self.db)
 def tearDown(self):self.c.close();self.temp.cleanup()
 def test_commit_and_reopen(self):
  tx=str(uuid.uuid4());oid,rid,receipt=save(self.c,tx);self.c.close();self.c=connection(self.db);integrity(self.c)
  self.assertEqual(count(self.c),(1,2,1,1));self.assertEqual(self.c.execute('SELECT receipt_blob FROM accepted_receipts').fetchone()[0],receipt);self.assertEqual(self.c.execute("SELECT file_blob FROM files WHERE path='files/raw.bin'").fetchone()[0],payload(tx))
 def test_atomic_rollback_and_missing_receipt(self):
  self.c.execute('BEGIN IMMEDIATE');stage(self.c,str(uuid.uuid4()),receipt=False)
  with self.assertRaises(sqlite3.IntegrityError):self.c.execute('COMMIT')
  self.c.execute('ROLLBACK');self.assertEqual(count(self.c),(0,0,0,0))
  self.c.execute('BEGIN IMMEDIATE');stage(self.c,str(uuid.uuid4()))
  with self.assertRaises(sqlite3.IntegrityError):self.c.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),str(uuid.uuid4()),'Asset','bank-asset/1',None,1,1,'missing.json'))
  self.c.execute('ROLLBACK');self.assertEqual(count(self.c),(0,0,0,0));integrity(self.c)
 def test_unique_and_immutable(self):
  tx=str(uuid.uuid4());save(self.c,tx);before=count(self.c)
  with self.assertRaises(sqlite3.IntegrityError):save(self.c,tx)
  self.assertEqual(count(self.c),before)
  for table,col,value in [('commits','transaction_id','changed'),('files','path','changed'),('revisions','object_type','Entity'),('accepted_receipts','receipt_blob',b'changed')]:
   for sql,args in [('UPDATE '+table+' SET '+col+'=?',(value,)),('DELETE FROM '+table,())]:
    with self.subTest(sql=sql),self.assertRaises(sqlite3.IntegrityError):self.c.execute(sql,args)
  integrity(self.c);self.assertEqual(count(self.c),before)
 def test_writer_lock_and_stale_base(self):
  oid,rid,receipt=save(self.c,str(uuid.uuid4()));other=connection(self.db)
  try:
   self.c.execute('BEGIN IMMEDIATE')
   with self.assertRaises(sqlite3.OperationalError):other.execute('BEGIN IMMEDIATE')
   self.c.execute('ROLLBACK');save(other,str(uuid.uuid4()),oid,rid);before=count(other)
   with self.assertRaises(ValueError):save(self.c,str(uuid.uuid4()),oid,rid)
   self.assertEqual(count(other),before);integrity(other)
  finally:other.close()
 def test_process_death_precommit(self):self.death('before',17,(0,0,0,0))
 def test_process_death_postcommit(self):self.death('after',18,(1,2,1,1))
 def death(self,phase,exit_code,expected):
  self.c.close();tx=str(uuid.uuid4());q=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',str(self.db),phase,tx],capture_output=True,text=True,timeout=10)
  self.assertEqual(q.returncode,exit_code,q.stdout+q.stderr);self.c=connection(self.db);integrity(self.c);self.assertEqual(count(self.c),expected)
  if phase=='after':
   raw=self.c.execute('SELECT receipt_blob FROM accepted_receipts').fetchone()[0];self.assertEqual(json.loads(raw)['transaction_id'],tx)
   self.assertEqual(self.c.execute("SELECT file_blob FROM files WHERE path='files/raw.bin'").fetchone()[0],payload(tx))
   with self.assertRaises(sqlite3.IntegrityError):save(self.c,tx)
   self.assertEqual(count(self.c),expected)
 def test_projection_and_backup(self):
  oid,rid,_=save(self.c,str(uuid.uuid4()));save(self.c,str(uuid.uuid4()),oid,rid);heads=self.c.execute('SELECT * FROM object_heads').fetchall();original=count(self.c)
  view='CREATE VIEW '+DDL.read_text().split('CREATE VIEW ',1)[1].split('-- Canonical',1)[0]
  self.c.executescript('DROP VIEW object_heads;'+view);self.assertEqual(self.c.execute('SELECT * FROM object_heads').fetchall(),heads);self.assertEqual(count(self.c),original)
  backup=connection(Path(self.temp.name)/'snapshot.sqlite')
  try:self.c.backup(backup);integrity(backup);self.assertEqual(count(backup),original);self.assertEqual(backup.execute('SELECT * FROM object_heads').fetchall(),heads);self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0],1)
  finally:backup.close()
 def test_policy_boundaries(self):
  p=json.loads(POLICY.read_text())['limits'];budget(p['manifest_bytes'],p['ready_bytes'],[(p['file_bytes'],False)],p['operations'])
  cases=[(p['manifest_bytes']+1,0,[],0),(0,p['ready_bytes']+1,[],0),(0,0,[],p['operations']+1),(0,0,[(0,False)]*(p['files']+1),0),(0,0,[(p['file_bytes']+1,False)],0),(0,0,[(p['object_json_bytes']+1,True)],0),(1,0,[(p['file_bytes'],False)]*4,0),(False,0,[],0),(-1,0,[],0),(1.5,0,[],0)]
  for args in cases:
   with self.subTest(args=args),self.assertRaises(ValueError):budget(*args)
  budget(0,0,[(p['file_bytes'],False)]*4,0);budget(0,0,[(0,False)]*p['files'],0);budget(0,0,[(p['object_json_bytes'],True)],0)
  value=0
  for _ in range(p['json_container_depth']):value=[value]
  self.assertEqual(parsed_depth(value),p['json_container_depth'])
  with self.assertRaises(ValueError):parsed_depth([value])
  for key in ['annotation_body_bytes','title_bytes','locator_bytes','diagnostic_bytes']:
   string_budget('x'*p[key],key);string_budget('é'*(p[key]//2),key)
   with self.subTest(key=key),self.assertRaises(ValueError):string_budget('é'*(p[key]//2)+'x',key)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--child':
  c=connection(Path(sys.argv[2]));c.execute('BEGIN IMMEDIATE');stage(c,sys.argv[4])
  if sys.argv[3]=='after':c.execute('COMMIT');os._exit(18)
  os._exit(17)
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(StorageTests);result=unittest.TextTestRunner(verbosity=2).run(suite)
 print(json.dumps({'status':'PASS' if result.wasSuccessful() else 'FAIL','sqlite_version':sqlite3.sqlite_version,'python':sys.version,'tests_run':result.testsRun,'scope':'Synthetic direct-SQL + numeric/parsed policy probe; no power loss/production importer/Windows confinement accepted.'}))
 raise SystemExit(0 if result.wasSuccessful() else 1)
