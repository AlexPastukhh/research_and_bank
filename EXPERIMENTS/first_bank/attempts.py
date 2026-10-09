"""Private diagnostic ledger. Canonical acceptance and absence remain separate."""
from pathlib import Path
import copy,json,re,sqlite3,sys,time,uuid
from contextlib import contextmanager
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'EXPERIMENTS/sqlite_importer'))
import importer as im
PROTOCOL='local-bank-attempt/1'
QUERY='local-bank-attempt-query/1'
STATES=['ACCEPTED','REPLAY','CONFLICT','REJECTED','INCOMPLETE','INTEGRITY_ERROR','IO_ERROR','RETRYABLE_BUSY','UNKNOWN','CANCELLED','READY_NOT_PUBLISHED']
CAP=65536;SCAN=4096;PAGE=20;MS=1000
CODE=re.compile(r'^[A-Z][A-Z0-9_]{0,63}$');HASH=re.compile(r'^[0-9a-f]{64}$')
def valid_tx(v):return type(v)is str and im.reader.UUID.fullmatch(v) is not None
def digest(v):return type(v)is str and HASH.fullmatch(v) is not None
SCHEMA=json.loads((Path(__file__).parent/'attempt.schema.json').read_text())
validator=Draft202012Validator(SCHEMA,format_checker=FormatChecker())
result_validator=Draft202012Validator(json.loads((Path(__file__).parent/'attempt_result.schema.json').read_text()),format_checker=FormatChecker())

def validate(d,contracts,row=None):
    im.need(next(validator.iter_errors(d),None)is None,'ATTEMPT_FORMAT','INTEGRITY_ERROR')
    receipt=d['canonical_receipt']
    if receipt is not None:
        contracts.envelope(receipt)
        im.need(all(receipt[k]==d[k] for k in ['transaction_id','manifest_sha256','status','code']),'ATTEMPT_CORRELATION','INTEGRITY_ERROR')
    if row is not None:
        im.need(tuple(d[k] for k in ['attempt_id','transaction_id','manifest_sha256','recorded_at'])==tuple(row),'ATTEMPT_ROW_INTEGRITY','INTEGRITY_ERROR')
    return d

@contextmanager
def connection(root,write=False):
    with im.Store(root) as store:
        c=store._connect(write,_allow_recovery=False)
        try:yield store,c
        finally:
            try:
                if c.in_transaction:c.execute('ROLLBACK')
            finally:c.close()

def record(root,result,*,_hook=None):
    """Called only after all canonical writer/rollback/snapshot resources close."""
    d={'protocol':PROTOCOL,'attempt_id':str(uuid.uuid4()),'transaction_id':result.get('transaction_id') if valid_tx(result.get('transaction_id')) else None,'manifest_sha256':result.get('manifest_sha256') if digest(result.get('manifest_sha256')) else None,'recorded_at':im.now(),'status':result['status'],'code':result['code'],'canonical_receipt':copy.deepcopy(result.get('receipt'))}
    c=None;committed=False
    try:
        with connection(root,True) as (store,c):
            validate(d,store.contracts);raw=im.encoded(d);im.need(len(raw)<=CAP,'ATTEMPT_SIZE_LIMIT','IO_ERROR')
            c.execute('PRAGMA busy_timeout=1000');c.execute('BEGIN IMMEDIATE')
            if _hook:_hook('before_attempt_append',d)
            c.execute('INSERT INTO attempt_receipts(attempt_id,transaction_id,manifest_sha256,recorded_at,receipt_blob) VALUES(?,?,?,?,?)',(*[d[k] for k in ['attempt_id','transaction_id','manifest_sha256','recorded_at']],raw))
            c.execute('COMMIT');committed=True
            if _hook:_hook('after_attempt_append',d)
            c=None
        return {'availability':'available','attempt_id':d['attempt_id']}
    except BaseException as e:
        if not isinstance(e,(Exception,KeyboardInterrupt)):raise
        if committed:return {'availability':'available','attempt_id':d['attempt_id']}
        return {'availability':'unavailable','code':'ATTEMPT_NOT_RECORDED'}

def scan(c,contracts,tx,*,before=None,latest=False,scan_limit=SCAN):
    """Insertion order cursor; bounded metadata and blobs, never false absence."""
    im.need(valid_tx(tx),'INVALID_TRANSACTION_ID')
    im.need(before is None or type(before)is int and before>0,'INVALID_ATTEMPT_CURSOR')
    start=time.monotonic();steps=0;rows=[];cursor=before
    def progress():
        nonlocal steps
        steps+=1000
        return int(steps>200000 or (time.monotonic()-start)*1000>MS)
    c.set_progress_handler(progress,1000)
    try:
        lengths=c.execute('SELECT rowid,length(attempt_id),length(transaction_id),length(manifest_sha256),length(recorded_at),length(receipt_blob) FROM attempt_receipts WHERE rowid<? ORDER BY rowid DESC LIMIT ?', (before or 9223372036854775807,scan_limit+1)).fetchall()
        exhausted=len(lengths)<=scan_limit
        for rid,aid_n,tx_n,hash_n,time_n,n in lengths[:scan_limit]:
            if (time.monotonic()-start)*1000>MS:return {'availability':'incomplete_scan','items':rows,'next_before_rowid':cursor}
            im.need(aid_n==36 and tx_n in (None,36) and hash_n in (None,64) and type(time_n)is int and 1<=time_n<=64 and type(n)is int and 0<n<=CAP,'ATTEMPT_ROW_INTEGRITY','INTEGRITY_ERROR')
            row=c.execute('SELECT attempt_id,transaction_id,manifest_sha256,recorded_at FROM attempt_receipts WHERE rowid=?',(rid,)).fetchone()
            raw=c.execute('SELECT receipt_blob FROM attempt_receipts WHERE rowid=?',(rid,)).fetchone()[0]
            d=im.reader.strict_json(raw,CAP,64)
            if d.get('protocol')==PROTOCOL:validate(d,contracts,row)
            else:
                # Known legacy canonical envelope is accepted only after validation.
                contracts.envelope(d);im.need(all(d[k]==row[i] for i,k in enumerate(['attempt_id','transaction_id','manifest_sha256','recorded_at'])),'ATTEMPT_ROW_INTEGRITY','INTEGRITY_ERROR')
                d={'protocol':PROTOCOL,'attempt_id':row[0],'transaction_id':row[1],'manifest_sha256':row[2],'recorded_at':row[3],'status':d['status'],'code':d['code'],'canonical_receipt':d}
                validate(d,contracts,row)
            cursor=rid
            if row[1]==tx:
                rows.append(d)
                if latest:return {'availability':'available','attempt':d}
                if len(rows)==PAGE:return {'availability':'available','items':rows,'next_before_rowid':cursor}
        if not exhausted:return {'availability':'incomplete_scan','items':rows,'next_before_rowid':cursor}
        return {'availability':'available','items':rows,'next_before_rowid':None} if rows else {'availability':'not_recorded','items':[],'next_before_rowid':None}
    except sqlite3.Error:
        if steps>200000 or (time.monotonic()-start)*1000>MS:return {'availability':'incomplete_scan','items':rows,'next_before_rowid':cursor}
        return {'availability':'unavailable','code':'ATTEMPT_READ_UNAVAILABLE'}
    except (im.Problem,im.reader.Rejected,ValueError,TypeError,KeyError):
        return {'availability':'unavailable','code':'ATTEMPT_READ_UNAVAILABLE'}
    finally:c.set_progress_handler(None,0)

def latest(c,contracts,tx):return scan(c,contracts,tx,latest=True)

def query(root,q):
    c=None
    result={'protocol':QUERY,'operation':'attempt.get','transaction_id':q.get('transaction_id') if valid_tx(q.get('transaction_id')) else None,'status':'ERROR','data':{'availability':'unavailable','code':'INVALID_ATTEMPT_QUERY'}}
    try:
        im.need(set(q)<= {'protocol','operation','transaction_id','before_rowid'} and q.get('protocol')==QUERY and q.get('operation')=='attempt.get' and valid_tx(q.get('transaction_id')),'INVALID_ATTEMPT_QUERY')
        with connection(root) as (store,c):
            c.execute('BEGIN')
            result['data']=scan(c,store.contracts,q['transaction_id'],before=q.get('before_rowid'));result['status']='OK'
            c=None
    except Exception:pass
    if next(result_validator.iter_errors(result),None)is not None or len(im.encoded(result))>PAGE*CAP+4096:
        result.update(status='ERROR',data={'availability':'unavailable','code':'ATTEMPT_READ_UNAVAILABLE'})
    return result
