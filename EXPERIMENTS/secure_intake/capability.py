"""Actual Windows capability checks in owned temporary fixtures, no user configuration edits."""
import json,os,subprocess,tempfile,uuid,shutil
from pathlib import Path
import win32_io as n

def capabilities():
    parent=Path(tempfile.mkdtemp(prefix='bank-intake-cap-'));root=parent/'private'
    report={}
    try:
        n.private_directory(root)
        with n.configured_root(root) as h:report['private_acl']=n.security_sddl(h)
        raw=root/'test.bin';raw.write_bytes(b'fixture')
        with n.Handle(raw) as h:
            report['read_exact']=h.read(64)==b'fixture'
            try:raw.write_bytes(b'changed');report['write_blocked']=False
            except OSError as e:report['write_blocked']=True;report['write_error']=getattr(e,'winerror',None)
            try:os.replace(raw,root/'moved.bin');report['rename_blocked']=False
            except OSError as e:report['rename_blocked']=True;report['rename_error']=getattr(e,'winerror',None)
        hard=root/'hard.bin';os.link(raw,hard)
        try:n.Handle(hard).close();report['hardlink_rejected']=False
        except n.SafetyError as e:report['hardlink_rejected']=str(e)=='HARDLINK'
        os.unlink(hard)
        target=root/'target';target.mkdir();junction=root/'junction'
        p=subprocess.run(['cmd','/d','/c','mklink','/J',str(junction),str(target)],capture_output=True,timeout=5)
        report['junction_create_exit']=p.returncode
        if p.returncode==0:
            try:n.Handle(junction,directory=True).close();report['junction_rejected']=False
            except n.SafetyError as e:report['junction_rejected']=str(e)=='REPARSE_POINT'
            os.rmdir(junction)
        for directory in [False,True]:
            label='directory_symlink' if directory else 'file_symlink'
            link=root/label
            try:
                os.symlink(target if directory else raw,link,target_is_directory=directory)
                report[label+'_created']=True
                try:n.Handle(link,directory=directory).close();report[label+'_rejected']=False
                except n.SafetyError as e:report[label+'_rejected']=str(e)=='REPARSE_POINT'
                os.rmdir(link) if directory else os.unlink(link)
            except OSError as e:report[label+'_created']=False;report[label+'_error']=getattr(e,'winerror',None)
        return report
    finally:shutil.rmtree(parent)
if __name__=='__main__':print(json.dumps(capabilities(),ensure_ascii=True))
