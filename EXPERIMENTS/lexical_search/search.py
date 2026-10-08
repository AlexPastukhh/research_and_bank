"""Synthetic bounded R1 SQLite postings/search; no real deployment/release.

Current owner, operator roots and app code are trusted. Cache is disposable;
canonical Store/typed-read sources and formats are not modified.
"""
from pathlib import Path
from contextlib import ExitStack
import argparse,hashlib,json,os,sqlite3,stat,sys,unicodedata,uuid
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'EXPERIMENTS/bank_read_api'))
import bank_read as read
im=read.im
FIELDS=['title','filename','uri','aliases','body','content']
STATES=['indexed','locator_only','unsupported_media','invalid_utf8','size_limit','not_applicable']
PROFILE='r1-lexical/1';NORMALIZATION=1;APP_ID=0x52425331

class SearchError(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)
def need(ok,code='INDEX_UNAVAILABLE'):
    if not ok:raise SearchError(code)
def fingerprint(h,kind,row):h.update(im.encoded([kind,*row])+b'\n')
class Budget(read.Budget):
    def progress(self):
        # Count short statements too; coarse per-statement callbacks can miss
        # thousands of small indexed lookups in a complete generation audit.
        self.steps+=1
        if self.steps>self.limits['sqlite_vm_steps'] or (self.steps%128==0 and (read.time.monotonic()-self.start)*1000>self.limits['elapsed_ms']):self.exceeded=True;return 1
        return 0
class Session(read.ReadSession):
    def __enter__(self):
        super().__enter__()
        try:self.c.set_progress_handler(self.budget.progress,1);self.budget.tick();return self
        except BaseException:self.c.close();self.c=None;raise
def tokens(value,budget):
    value=unicodedata.normalize('NFC',unicodedata.normalize('NFC',value).casefold());result=set();word=[]
    for i,char in enumerate(value):
        if i%4096==0:budget.tick()
        category=unicodedata.category(char)[0]
        if category in 'LN' or (category=='M' and word):word.append(char)
        else:
            if word:result.add(''.join(word));word=[]
    if word:result.add(''.join(word))
    for term in result:need(len(term.encode('utf-8'))<=budget.limits['term_bytes'],'LIMIT_EXCEEDED')
    return result

class Cache:
    def __init__(self,root,bank_root,limits,hook=None):
        self.root=Path(root).absolute();bank=Path(bank_root).absolute();self.path=self.root/'search-cache.sqlite3';self.limits=limits;self.hook=hook;self.stack=ExitStack()
        need(not self.root.is_relative_to(bank) and not bank.is_relative_to(self.root))
        self.ddl=(Path(__file__).parent/'cache_schema.sql').read_text(encoding='utf-8')
        c=sqlite3.connect(':memory:')
        try:c.executescript(self.ddl);self.catalog=im.Contracts.catalog_of(c)
        finally:c.close()
    def __enter__(self):
        try:
            if os.name=='nt':self.stack.enter_context(im.native.configured_root(self.root))
            else:
                st=self.root.lstat();need(stat.S_ISDIR(st.st_mode) and not self.root.is_symlink() and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)&0o077==0)
                need(not any(p.is_symlink() for p in self.root.parents))
            return self
        except BaseException:self.stack.close();raise
    def __exit__(self,*_):self.stack.close()
    def _event(self,name,value=None):
        if self.hook:self.hook(name,value)
    def _path_check(self):
        st=self.path.lstat();need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and not getattr(st,'st_file_attributes',0)&0x400)
        need(st.st_size<=self.limits['cache_file_bytes'],'LIMIT_EXCEEDED')
        with im.sqlite_guard(self.path):
            with self.path.open('rb') as f:header=f.read(100)
        need(len(header)==100 and header[:16]==b'SQLite format 3\x00' and int.from_bytes(header[60:64],'big')==1 and int.from_bytes(header[68:72],'big')==APP_ID)
    def _catalog_check(self,c):
        need(c.execute('PRAGMA application_id').fetchone()[0]==APP_ID and c.execute('PRAGMA user_version').fetchone()[0]==1)
        try:need(im.Contracts.catalog_of(c)==self.catalog)
        except im.Problem as e:raise SearchError('INDEX_UNAVAILABLE') from e
    def configure(self,c,write):
        need(c.execute('PRAGMA journal_mode').fetchone()[0]=='delete')
        c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA trusted_schema=OFF');c.execute('PRAGMA busy_timeout=1000');c.execute('PRAGMA cache_size=-1024');c.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE,True)
        if write:
            c.execute('PRAGMA synchronous=EXTRA');c.execute('PRAGMA max_page_count='+str(self.limits['cache_file_bytes']//c.execute('PRAGMA page_size').fetchone()[0]))
        else:c.execute('PRAGMA query_only=ON')
    def initialize(self):
        need(not self.path.exists());fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd);c=im.connect_guarded(self.path)
        try:
            self.configure(c,True);part=''
            for line in self.ddl.splitlines(keepends=True):
                part+=line
                if sqlite3.complete_statement(part):
                    if part.strip().upper()=='COMMIT;':
                        self._event('init_before_commit')
                        if os.name=='nt':c.guard.check()
                    c.execute(part);part=''
            need(not part.strip());self._catalog_check(c)
        finally:c.close()
    def connect(self,budget,write=False,recovery=True):
        self._path_check();c=im.connect_guarded(self.path,uri=self.path.as_uri()+'?mode='+('rw' if write else 'ro'),timeout=1)
        try:self._catalog_check(c);self.configure(c,write)
        except sqlite3.Error as e:
            c.close()
            if not write and recovery and getattr(e,'sqlite_errorcode',None)==sqlite3.SQLITE_READONLY_ROLLBACK:
                restored=self.connect(budget,True);restored.close();return self.connect(budget,False,False)
            raise
        except BaseException:c.close();raise
        c.set_progress_handler(budget.progress,1)
        if not write:
            allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_TRANSACTION,sqlite3.SQLITE_RECURSIVE}
            c.set_authorizer(lambda a,*_:sqlite3.SQLITE_OK if a in allowed else sqlite3.SQLITE_DENY)
        return c
    def metadata(self,c):
        sizes=c.execute('SELECT length(profile_id),length(unicode_version),length(digest) FROM generation WHERE id=1').fetchone();need(sizes is not None,'INDEX_NOT_READY');need(all(type(n)is int and 0<=n<=64 for n in sizes))
        row=c.execute('SELECT watermark,profile_id,unicode_version,normalization,digest,revision_count,posting_count FROM generation WHERE id=1').fetchone()
        need(type(row[0])is int and 0<=row[0]<=9007199254740991 and type(row[5])is int and type(row[6])is int and 0<=row[5]<=self.limits['corpus_revisions'] and 0<=row[6]<=self.limits['postings'])
        need(row[1:4]==(PROFILE,unicodedata.unidata_version,NORMALIZATION),'INDEX_PROFILE_MISMATCH');return row

class SearchAPI:
    def __init__(self,bank_root,cache_root,*,_limits=None,_hook=None):
        self.bank_root=Path(bank_root).absolute();self.cache_root=Path(cache_root).absolute();self.hook=_hook
        folder=Path(__file__).parent;self.limits=json.loads((folder/'LIMITS.json').read_text());self.limits.update(_limits or {})
        self.reader=read.ReadAPI(self.bank_root,_limits=self.limits)
        self.result_validator=Draft202012Validator(json.loads((folder/'result.schema.json').read_text()))
    def close(self):self.reader.close()
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
    def _event(self,name,value=None):
        if self.hook:self.hook(name,value)
    def validate(self,raw,budget):
        q=self.reader.parse(raw);read.need(q.get('protocol')==read.PROTOCOL,'UNSUPPORTED_PROTOCOL');read.need(q.get('operation')=='bank.search','UNSUPPORTED_MODE')
        for key in ['limit','offset','snapshot_sequence']:
            if key in q and q[key]is not None:read.need(type(q[key])is int,'INVALID_REQUEST')
        read.need(next(self.reader.request_validator.iter_errors(q),None)is None,'INVALID_REQUEST')
        read.need(len(q['query'].encode('utf-8'))<=self.limits['query_bytes'],'LIMIT_EXCEEDED');terms=tokens(q['query'],budget);read.need(bool(terms),'INVALID_REQUEST');read.need(len(terms)<=self.limits['query_terms'],'LIMIT_EXCEEDED');return q,sorted(terms)
    def records(self,session,watermark,budget):
        count=0;postings=0
        cursor=session.c.execute('SELECT revision_id,object_id,object_type,commit_sequence,document_path FROM revisions WHERE commit_sequence<=? ORDER BY revision_id',(watermark,))
        for row in cursor:
            count+=1;need(count<=self.limits['corpus_revisions'],'LIMIT_EXCEEDED');budget.tick();d,commit=session.document(row);values={f:[] for f in FIELDS};values['title']=[d['title']];kind=d['object_type'];coverage='not_applicable'
            if kind=='Entity':values['aliases']=d['data']['aliases']
            if kind=='Annotation':values['body']=[d['data']['body']]
            if kind=='Asset':
                storage=d['data']['storage']
                if storage['mode']=='locator':coverage='locator_only';values['uri']=[storage['uri']]
                else:
                    if storage['original_filename']is not None:values['filename']=[storage['original_filename']]
                    collect=storage['media_type']=='text/plain' and storage['byte_length']<=self.limits['content_bytes'];parts=[]
                    chunks=session.file_chunks(commit['files'][storage['file_path']],commit['policy']['file_bytes'])
                    try:
                        for raw in chunks:
                            if collect:parts.append(raw)
                    finally:chunks.close()
                    if storage['media_type']!='text/plain':coverage='unsupported_media'
                    elif not collect:coverage='size_limit'
                    else:
                        try:values['content']=[b''.join(parts).decode('utf-8')];coverage='indexed'
                        except UnicodeDecodeError:coverage='invalid_utf8'
            entry=(row[0],row[1],kind,row[3],coverage,commit['row'][1],commit['files'][row[4]][3]);yield 'e',entry
            for field_id,field in enumerate(FIELDS):
                terms=set()
                for value in values[field]:terms.update(tokens(value,budget))
                for term in sorted(terms):
                    postings+=1;need(postings<=self.limits['postings'],'LIMIT_EXCEEDED');budget.charge(len(term.encode('utf-8'))+64);yield 't',(row[0],field_id,term)
    def canonical_digest(self,session,watermark,budget):
        h=hashlib.sha256();n=p=0
        for kind,row in self.records(session,watermark,budget):fingerprint(h,kind,row);n+=kind=='e';p+=kind=='t'
        return h.hexdigest(),n,p
    def cache_digest(self,c,budget):
        counts=c.execute('SELECT (SELECT count(*) FROM corpus),(SELECT count(*) FROM terms)').fetchone();need(counts[0]<=self.limits['corpus_revisions'] and counts[1]<=self.limits['postings'],'LIMIT_EXCEEDED')
        bad=c.execute("SELECT 1 FROM corpus WHERE length(CAST(rid AS BLOB))!=36 OR length(CAST(oid AS BLOB))!=36 OR length(CAST(commit_id AS BLOB))!=36 OR length(CAST(document_sha256 AS BLOB))!=64 OR object_type NOT IN ('Asset','Entity','Annotation','Collection') OR coverage NOT IN ('indexed','locator_only','unsupported_media','invalid_utf8','size_limit','not_applicable') LIMIT 1").fetchone();need(bad is None)
        h=hashlib.sha256();n=p=0
        for entry in c.execute('SELECT rid,oid,object_type,seq,coverage,commit_id,document_sha256 FROM corpus ORDER BY rid'):
            budget.tick();budget.charge(256,True);n+=1;fingerprint(h,'e',entry)
            for field,term in c.execute('SELECT field_id,CASE WHEN length(CAST(term AS BLOB))<=? THEN term ELSE NULL END FROM terms WHERE rid=? ORDER BY field_id,term',(self.limits['term_bytes'],entry[0])):
                need(type(field)is int and 0<=field<len(FIELDS) and isinstance(term,str) and bool(term));budget.charge(len(term.encode('utf-8'))+64);p+=1;fingerprint(h,'t',(entry[0],field,term))
        need((n,p)==counts);return h.hexdigest(),n,p
    def rebuild(self):
        budget=Budget(self.limits);c=None;committed=False;phase='bank'
        try:
            with im.Store(self.bank_root) as store:
                with Session(store,budget,self.hook) as session:
                    watermark=session.snapshot;phase='cache'
                    with Cache(self.cache_root,self.bank_root,self.limits,self.hook) as cache:
                        if not cache.path.exists():cache.initialize()
                        c=cache.connect(budget,True);c.execute('BEGIN IMMEDIATE');c.execute('DELETE FROM terms');c.execute('DELETE FROM corpus');c.execute('DELETE FROM generation');h=hashlib.sha256();n=p=0
                        for kind,row in self.records(session,watermark,budget):
                            fingerprint(h,kind,row)
                            if kind=='e':c.execute('INSERT INTO corpus VALUES(?,?,?,?,?,?,?)',row);n+=1;self._event('entry_written',n)
                            else:c.execute('INSERT INTO terms VALUES(?,?,?)',row);p+=1
                        c.execute('INSERT INTO generation VALUES(1,?,?,?,?,?,?,?)',(watermark,PROFILE,unicodedata.unidata_version,NORMALIZATION,h.hexdigest(),n,p));budget.tick();self._event('before_publish',watermark)
                        if os.name=='nt':c.guard.check()
                        c.execute('COMMIT');committed=True;self._event('after_publish',watermark)
                        return {'status':'BUILT','snapshot_sequence':watermark,'revision_count':n,'posting_count':p,'profile_id':PROFILE,'normalization_version':NORMALIZATION,'unicode_data_version':unicodedata.unidata_version,'fingerprint':h.hexdigest()}
        except (SearchError,read.ReadError) as e:code=e.code
        except im.WorkLimit:code='LIMIT_EXCEEDED'
        except (im.Problem,im.reader.Rejected) as e:code='BANK_UNAVAILABLE' if getattr(e,'code',None) in ['UNTRUSTED_TEST_ROOT','UNTRUSTED_TEST_PARENT','STORE_CLOSED','SQLITE_VERSION_UNSUPPORTED','DEFENSIVE_UNAVAILABLE'] else 'INTEGRITY_ERROR'
        except (sqlite3.Error,OSError,im.native.SafetyError,UnicodeError,ValueError,KeyError,TypeError) as e:
            n=getattr(e,'sqlite_errorcode',0)or 0;code='LIMIT_EXCEEDED' if budget.exceeded else ('BANK_BUSY' if n&255 in [sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED] else ('BANK_UNAVAILABLE' if phase=='bank' else 'INDEX_UNAVAILABLE'))
        finally:
            if c:
                try:
                    if c.in_transaction:c.execute('ROLLBACK')
                finally:c.close()
        if committed:return {'status':'UNKNOWN','code':'BUILD_OUTCOME_UNKNOWN'}
        return {'status':'ERROR','code':code}
    def execute(self,raw):
        budget=Budget(self.limits);q={};session=None;c=None;phase='bank'
        try:
            # Keep valid request identity even when later validation fails.
            q=self.reader.parse(raw);q,terms=self.validate(raw,budget)
            with im.Store(self.bank_root) as store:
                with Session(store,budget,self.hook) as session:
                    snapshot=session.snapshot if q['snapshot_sequence']is None else q['snapshot_sequence'];need(snapshot<=session.snapshot,'SNAPSHOT_NOT_AVAILABLE')
                    if snapshot>0:need(session.c.execute('SELECT 1 FROM commits WHERE commit_sequence=?',(snapshot,)).fetchone()is not None,'SNAPSHOT_NOT_AVAILABLE')
                    phase='cache'
                    with Cache(self.cache_root,self.bank_root,self.limits,self.hook) as cache:
                        c=cache.connect(budget);c.execute('BEGIN');meta=cache.metadata(c);need(meta[0]>=snapshot,'INDEX_NOT_READY');need(meta[0]<=session.snapshot)
                        actual=self.cache_digest(c,budget);need(actual==(meta[4],meta[5],meta[6]));phase='canonical_integrity';expected=self.canonical_digest(session,meta[0],budget);need(actual==expected);self._event('query_verified',snapshot);phase='cache'
                        type_slots=','.join('?' for _ in q['object_types']);field_ids=[FIELDS.index(f) for f in q['fields']];field_slots=','.join('?' for _ in field_ids);term_slots=','.join('?' for _ in terms);head_cache={}
                        def visible(rid,oid):
                            if q['revisions_mode']=='all_revisions':return True
                            if oid not in head_cache:
                                row=session.c.execute('SELECT revision_id FROM revisions WHERE object_id=? AND commit_sequence<=? ORDER BY commit_sequence DESC LIMIT 1',(oid,snapshot)).fetchone();head_cache[oid]=row[0] if row else None
                            return head_cache[oid]==rid
                        coverage={s:0 for s in STATES}
                        for rid,oid,state in c.execute('SELECT rid,oid,coverage FROM corpus WHERE object_type IN ('+type_slots+') AND seq<=?',(*q['object_types'],snapshot)):
                            budget.tick()
                            if visible(rid,oid):coverage[state]+=1
                        sql='SELECT e.rid,e.oid,e.object_type,e.seq,e.coverage FROM corpus e WHERE e.object_type IN ('+type_slots+') AND e.seq<=? AND (SELECT count(DISTINCT term) FROM terms WHERE rid=e.rid AND field_id IN ('+field_slots+') AND term IN ('+term_slots+'))=? ORDER BY e.seq DESC,e.oid,e.rid'
                        hits=[];total=0
                        for rid,oid,kind,seq,state in c.execute(sql,(*q['object_types'],snapshot,*field_ids,*terms,len(terms))):
                            budget.tick()
                            if not visible(rid,oid):continue
                            if q['offset']<=total<q['offset']+q['limit']:
                                matched=[FIELDS[x[0]] for x in c.execute('SELECT DISTINCT field_id FROM terms WHERE rid=? AND field_id IN ('+field_slots+') AND term IN ('+term_slots+') ORDER BY field_id',(rid,*field_ids,*terms))]
                                hits.append({'ref':{'object_type':kind,'object_id':oid,'revision_id':rid},'commit_sequence':seq,'matched_fields':matched,'extraction_state':state})
                            total+=1
                        data={'hits':hits,'total_matches':total,'has_more':q['offset']+q['limit']<total,'coverage':coverage,'profile_id':PROFILE,'normalization_version':NORMALIZATION,'unicode_data_version':unicodedata.unidata_version}
                        result={'protocol':read.PROTOCOL,'request_id':q['request_id'],'operation':'bank.search','status':'OK','snapshot_sequence':snapshot,'data':data};need(next(self.result_validator.iter_errors(result),None)is None,'RESULT_CONFORMANCE');need(len(im.encoded(result))<=self.limits['response_bytes'],'LIMIT_EXCEEDED');budget.tick();return result
        except (SearchError,read.ReadError) as e:code=e.code
        except im.WorkLimit:code='LIMIT_EXCEEDED'
        except (im.Problem,im.reader.Rejected) as e:code='BANK_UNAVAILABLE' if getattr(e,'code',None) in ['UNTRUSTED_TEST_ROOT','UNTRUSTED_TEST_PARENT','STORE_CLOSED','SQLITE_VERSION_UNSUPPORTED','DEFENSIVE_UNAVAILABLE'] else ('INTEGRITY_ERROR' if phase!='cache' else 'INDEX_UNAVAILABLE')
        except (sqlite3.Error,OSError,im.native.SafetyError,UnicodeError,ValueError,KeyError,TypeError) as e:
            n=getattr(e,'sqlite_errorcode',0)or 0;code='LIMIT_EXCEEDED' if budget.exceeded else ('BANK_BUSY' if n&255 in [sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED] else ('BANK_UNAVAILABLE' if phase=='bank' else ('INTEGRITY_ERROR' if phase=='canonical_integrity' else 'INDEX_UNAVAILABLE')))
        finally:
            if c:c.close()
        return self.reader.error(q,code,session.snapshot if session else None)

def main():
    p=argparse.ArgumentParser(description='Synthetic R1 lexical cache maintenance/query; operator roots are trusted configuration.');p.add_argument('action',choices=['rebuild','query']);p.add_argument('--bank-root',required=True);p.add_argument('--cache-root',required=True);a=p.parse_args()
    with SearchAPI(a.bank_root,a.cache_root) as app:
        result=app.rebuild() if a.action=='rebuild' else app.execute(sys.stdin.buffer.read(app.limits['request_bytes']+1));sys.stdout.buffer.write(im.encoded(result)+b'\n');sys.stdout.buffer.flush()
    return 0 if result['status']in ['OK','BUILT'] else 2
if __name__=='__main__':sys.exit(main())
