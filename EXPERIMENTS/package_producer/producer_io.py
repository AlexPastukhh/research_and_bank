"""Own publisher I/O; accepted secure reader adapter is unchanged."""
from pathlib import Path
import ctypes as C,errno,os,stat
import win32_io as n
class Refused(ValueError):pass
class Directory:
    def __init__(self,path,write=False,root=False):
        self.path=Path(path);self.handle=None;self.fd=None
        if os.name=='nt':
            guard=n.configured_root(self.path) if root else n.Handle(self.path,directory=True)
            try:
                if write:
                    h=n.create(n.extended(self.path),n.READ,3,None,3,n.FLAGS,None)
                    if h==n.INVALID:raise C.WinError(C.get_last_error())
                    self.handle=n.Handle.__new__(n.Handle);self.handle.path=self.path;self.handle.h=h;self.handle.directory=True
                    info=self.handle.info()
                    if n.get_type(h)!=1 or info.attrs&0x400 or not info.attrs&0x10:raise Refused('DIRECTORY_INVALID')
                    n.verify_private_acl(self.handle);self.check()
                else:n.verify_private_acl(guard);self.handle=guard;guard=None
            except BaseException:self.close();raise
            finally:
                if guard:guard.close()
        else:
            st=self.path.lstat()
            if not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)&0o077 or any(p.is_symlink() for p in [self.path,*self.path.parents]):raise Refused('UNTRUSTED_FIXTURE_ROOT')
            self.fd=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);self.identity=(st.st_dev,st.st_ino)
    def check(self):
        if self.handle:
            if self.handle.final_name().casefold()!=str(self.path).casefold() or self.handle.info().attrs&0x400:raise Refused('DIRECTORY_CHANGED')
        else:
            st=self.path.lstat()
            if not stat.S_ISDIR(st.st_mode) or (st.st_dev,st.st_ino)!=self.identity:raise Refused('DIRECTORY_CHANGED')
    def close(self):
        if self.handle:self.handle.close();self.handle=None
        if self.fd is not None:os.close(self.fd);self.fd=None
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
class File:
    def __init__(self,path,new=False):
        self.path=Path(path);self.handle=None;self.f=None
        if os.name=='nt':
            self.handle=n.Handle(self.path,new=new)
            try:n.verify_private_acl(self.handle)
            except BaseException:self.close();raise
        else:
            flags=os.O_RDWR|os.O_CREAT|os.O_EXCL if new else os.O_RDONLY
            fd=os.open(self.path,flags|os.O_NOFOLLOW,0o600);self.f=os.fdopen(fd,'r+b' if new else 'rb');s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)&0o077:self.close();raise Refused('FILE_INVALID')
    def identity(self):
        if self.handle:return self.handle.identity()
        s=os.fstat(self.f.fileno());return (s.st_dev,s.st_ino,s.st_nlink,s.st_mode,s.st_size,s.st_mtime_ns)
    def check(self):
        if self.handle:
            if self.handle.info().links!=1 or self.handle.info().attrs&0x400 or self.handle.final_name().casefold()!=str(self.path).casefold():raise Refused('FILE_CHANGED')
        else:
            s=self.path.lstat();i=self.identity()
            if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or (s.st_dev,s.st_ino)!=i[:2]:raise Refused('FILE_CHANGED')
    def size(self):return self.handle.size() if self.handle else os.fstat(self.f.fileno()).st_size
    def seek(self):self.handle.seek() if self.handle else self.f.seek(0)
    def read(self,size):return self.handle.read(size) if self.handle else self.f.read(size)
    def write(self,raw):
        if self.handle:self.handle.write(raw)
        elif self.f.write(raw)!=len(raw):raise OSError('SHORT_WRITE')
    def flush(self):
        if self.handle:n.checked(n.flush_file(self.handle.h))
        else:self.f.flush();os.fsync(self.f.fileno())
    def close(self):
        if self.handle:self.handle.close();self.handle=None
        if self.f:self.f.close();self.f=None
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
def mkdir(path):
    if os.name=='nt':n.private_directory(path)
    else:Path(path).mkdir(mode=0o700)
def move_no_replace(source,destination):
    if Path(source).parent!=Path(destination).parent:raise Refused('MOVE_OUTSIDE_DIRECTORY')
    if os.name=='nt':
        move=n.api(n.K,'MoveFileExW',[n.W.LPCWSTR,n.W.LPCWSTR,n.W.DWORD],n.W.BOOL)
        n.checked(move(n.extended(source),n.extended(destination),8))
    else:
        libc=C.CDLL(None,use_errno=True)
        try:rename=libc.renameat2
        except AttributeError:raise Refused('FIXTURE_RENAME_UNAVAILABLE')
        rename.argtypes=[C.c_int,C.c_char_p,C.c_int,C.c_char_p,C.c_uint];rename.restype=C.c_int
        if rename(-100,os.fsencode(source),-100,os.fsencode(destination),1)!=0:raise OSError(C.get_errno(),'RENAME_NOREPLACE')
def present(path):
    try:Path(path).lstat();return True
    except FileNotFoundError:return False
