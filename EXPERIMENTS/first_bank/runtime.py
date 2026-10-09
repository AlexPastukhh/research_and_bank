"""Explicit setup/launch and manual verified snapshot; no read-side creation."""
from pathlib import Path
from contextlib import ExitStack,contextmanager
import argparse,json,os,sqlite3,sys,time,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'EXPERIMENTS/draft_authoring'))
try:import authoring as a
except ImportError:
    if __name__=='__main__':
        print(json.dumps({'status':'ERROR','code':'PYTHON_DEPENDENCY_UNAVAILABLE','message':'Use the validated project .venv\\Scripts\\python.exe environment.'}));sys.exit(2)
    raise
im=a.im;io=a.io
PROFILE='research-bank-config/1'
def default_base():
    a.need(os.name=='nt','UNSUPPORTED_PLATFORM')
    return Path(os.environ['LOCALAPPDATA'])/'ResearchAndBank'
def roots_for(base):return {k:base/k for k in sorted(a.ROLES)}
def validate_roots(roots,portable=False):
    a.need(set(roots)==a.ROLES,'INVALID_ROOT_CONFIGURATION');paths=[Path(v) for v in roots.values()]
    a.need(os.name=='nt' or portable,'UNSUPPORTED_PLATFORM')
    a.need(all(p.is_absolute() and '..' not in p.parts for p in paths),'INVALID_ROOT_CONFIGURATION')
    a.need(all(not(x.is_relative_to(y) or y.is_relative_to(x)) for i,x in enumerate(paths) for y in paths[i+1:]),'ROOT_OVERLAP')
    with ExitStack() as s:
        for p in paths:s.enter_context(io.Directory(p,root=True))

def preflight(portable=False):
    a.need(sqlite3.sqlite_version_info>=(3,37,0) and hasattr(sqlite3.Connection,'setconfig'),'PYTHON_SQLITE_UNAVAILABLE')
    if portable:return {'python':sys.version.split()[0],'sqlite':sqlite3.sqlite_version,'tk':'not_checked_portable_fixture'}
    import tkinter
    return {'python':sys.version.split()[0],'sqlite':sqlite3.sqlite_version,'tk':tkinter.TkVersion}

def load(base,*,portable=False):
    base=Path(base);preflight(portable)
    with io.Directory(base,root=True):
        with io.File(base/'config.json') as f:
            a.need(f.size()<=16384,'CONFIG_LIMIT');raw=f.read(16385);f.check()
        d=im.reader.strict_json(raw,16384,16)
        a.need(set(d)=={'profile','config_id','roots'} and d['profile']==PROFILE and a.reader.UUID.fullmatch(d['config_id']),'INVALID_CONFIGURATION')
        roots={k:Path(v) for k,v in d['roots'].items()};a.need(roots==roots_for(base),'CONFIG_ROOT_MISMATCH');validate_roots(roots,portable)
        with im.Store(roots['bank']) as store:
            c=store._connect(False,_allow_recovery=False);c.close()
        return d

def setup(base,*,portable=False,hook=None):
    base=Path(base);a.need(base.is_absolute() and '..' not in base.parts,'INVALID_ROOT_CONFIGURATION');a.need(os.name=='nt' or portable,'UNSUPPORTED_PLATFORM');versions=preflight(portable)
    if io.present(base/'config.json'):return {'status':'READY','code':'CONFIG_REOPENED','config':load(base,portable=portable),'runtime':versions}
    if not io.present(base):io.mkdir(base)
    with io.Directory(base,root=True,write=True):
        roots=roots_for(base)
        for role,p in roots.items():
            if not io.present(p):io.mkdir(p)
            with io.Directory(p,root=True):pass
            if hook:hook('root_created',role)
        validate_roots(roots,portable)
        with im.Store(roots['bank'],_hook=(lambda n,v:hook(n,v)) if hook else None) as store:
            if not io.present(store.db):store.initialize()
            c=store._connect(False,_allow_recovery=False);c.close()
        if hook:hook('db_verified',None)
        d={'profile':PROFILE,'config_id':str(uuid.uuid4()),'roots':{k:str(v) for k,v in roots.items()}}
        pending=base/('config-'+uuid.uuid4().hex+'.pending');raw=im.encoded(d)
        with io.File(pending,new=True) as f:f.write(raw);f.flush()
        with io.File(pending) as f:a.need(f.read(16385)==raw,'CONFIG_READBACK');f.check()
        if hook:hook('config_pending',pending)
        io.move_no_replace(pending,base/'config.json')
        if hook:hook('config_published',base/'config.json')
    return {'status':'READY','code':'CONFIG_CREATED','config':load(base,portable=portable),'runtime':versions}

def safeguard(roots,*,portable=False,hook=None):
    validate_roots(roots,portable);roots={k:Path(v) for k,v in roots.items()};start=time.monotonic();folder=roots['output']/str(uuid.uuid4());source=None;dest=None
    with io.Directory(roots['output'],root=True):
        io.mkdir(folder)
        with io.Directory(folder,root=True):
            path=folder/'bank.sqlite'
            with io.File(path,new=True) as f:f.flush()
            try:
                with im.Store(roots['bank']) as store:
                    source=store._connect(False,_allow_recovery=False)
                    try:
                        dest=im.connect_guarded(path);page_size=source.execute('PRAGMA page_size').fetchone()[0]
                        def progress(status,remaining,total):
                            a.need(total*page_size<=1073741824 and time.monotonic()-start<60,'BACKUP_WORK_LIMIT')
                            if hook:hook('backup_page',remaining)
                        source.backup(dest,pages=256,progress=progress,sleep=.05)
                        dest.close();dest=None
                    finally:source.close();source=None
                with im.Store(folder) as copy:
                    c=copy._connect(False,_allow_recovery=False)
                    try:
                        c.execute('BEGIN');c.set_progress_handler(lambda:int(time.monotonic()-start>=60),1000)
                        a.need(c.execute('PRAGMA integrity_check(1)').fetchone()==('ok',),'BACKUP_SQLITE_INTEGRITY')
                        a.need(c.execute('PRAGMA foreign_key_check').fetchone() is None,'BACKUP_FOREIGN_KEYS')
                        verified=0;limitation=None
                        with copy._work_scope():
                            rows=c.execute('SELECT commit_sequence FROM commits ORDER BY commit_sequence').fetchmany(copy.work_limits['commits']+1)
                            try:
                                a.need(len(rows)<=copy.work_limits['commits'],'BACKUP_CONTENT_LIMIT')
                                for (seq,) in rows:copy._verify_commit(c,seq);verified+=1
                            except im.WorkLimit:limitation='RETAINED_WORK_LIMIT'
                            except a.Problem as e:
                                if e.code!='BACKUP_CONTENT_LIMIT':raise
                                limitation=e.code
                        watermark=c.execute('SELECT coalesce(max(commit_sequence),0) FROM commits').fetchone()[0]
                    finally:c.close()
                digest=__import__('hashlib').sha256();count=0
                with io.File(path) as f:
                    while raw:=f.read(1048576):
                        a.need(time.monotonic()-start<60,'BACKUP_WORK_LIMIT');count+=len(raw);digest.update(raw)
                    f.check()
                return {'status':'OK' if limitation is None else 'PARTIALLY_VERIFIED','code':'VERIFIED_SQLITE_BACKUP' if limitation is None else limitation,'path':str(path),'sha256':digest.hexdigest(),'byte_length':count,'snapshot_sequence':watermark,'verified_commits':verified,'diagnostic_verification':'not_verified','content_verification':'all_retained_canonical' if limitation is None else 'bounded_incomplete','restore_accepted':False}
            except Exception:
                return {'status':'ERROR','code':'BACKUP_NOT_VERIFIED','path':str(path),'restore_accepted':False}
            finally:
                if dest:dest.close()
                if source:source.close()

def main(argv=None):
    parser=argparse.ArgumentParser(description='Research Bank: explicit first-use setup and launch')
    parser.add_argument('action',choices=['setup','check','launch','backup']);parser.add_argument('--base',type=Path)
    args=parser.parse_args(argv)
    try:
        base=args.base or default_base()
        if args.action=='setup':result=setup(base)
        else:
            cfg=load(base);roots={k:Path(v) for k,v in cfg['roots'].items()}
            if args.action=='check':result={'status':'READY','code':'CONFIG_VERIFIED','config':cfg,'runtime':preflight()}
            elif args.action=='backup':result=safeguard(roots)
            else:
                from app import launch
                return launch(roots,cfg['config_id'])
    except Exception as e:result={'status':'ERROR','code':getattr(e,'code','SETUP_OR_RUNTIME_UNAVAILABLE')}
    print(json.dumps(result,ensure_ascii=False));return 0 if result['status'] in ['OK','READY'] else 2
if __name__=='__main__':sys.exit(main())
