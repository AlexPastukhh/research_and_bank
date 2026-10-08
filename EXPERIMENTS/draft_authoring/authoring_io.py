"""Owned preparation I/O; external selected originals are read-only input.

Windows uses real leases; POSIX exists only as an explicitly selected test fixture.
The accepted reader/publisher sources are imported unchanged.
"""
from pathlib import Path
from contextlib import ExitStack
import ctypes as C,errno,os,stat,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'EXPERIMENTS/secure_intake'))
import win32_io as n
sys.path.insert(0,str(ROOT/'EXPERIMENTS/package_producer'))
import producer_io as private_io

class Refused(ValueError):
    def __init__(self,code):self.code=code;super().__init__(code)

def require(ok,code):
    if not ok:raise Refused(code)

Directory=private_io.Directory
File=private_io.File
mkdir=private_io.mkdir
present=private_io.present
move_no_replace=private_io.move_no_replace

class WorkspaceLock:
    """Persistent private file; the OS handle lock, never existence, owns a lease."""
    def __init__(self,path):self.path=Path(path);self.handle=None;self.fd=None
    def __enter__(self):
        if os.name=='nt':
            try:self.handle=n.Handle(self.path,new=True)
            except FileExistsError:
                self.handle=n.Handle(self.path,_share=0)
            except OSError as e:
                if getattr(e,'winerror',None) in (80,183):self.handle=n.Handle(self.path,_share=0)
                elif getattr(e,'winerror',None) in (32,33):raise Refused('AUTHORING_BUSY') from e
                else:raise
            try:n.verify_private_acl(self.handle);require(self.handle.size()==0,'INVALID_WORKSPACE_LOCK')
            except BaseException:self.__exit__();raise
        else:
            import fcntl
            self.fd=os.open(self.path,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
            s=os.fstat(self.fd)
            try:
                require(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size==0 and s.st_uid==os.getuid() and not stat.S_IMODE(s.st_mode)&0o077,'UNTRUSTED_LOCK')
                try:fcntl.flock(self.fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError as e:raise Refused('AUTHORING_BUSY') from e
            except BaseException:self.__exit__();raise
        return self
    def __exit__(self,*_):
        if self.handle:self.handle.close();self.handle=None
        if self.fd is not None:os.close(self.fd);self.fd=None

class SelectedOriginal:
    """Lease the selected source; filenames and broad read ACLs are not authority."""
    def __init__(self,path,excluded_roots,*,portable_fixture=False):
        self.path=Path(path);self.excluded=[Path(p) for p in excluded_roots];self.portable=portable_fixture;self.stack=ExitStack();self.handle=None;self.file=None;self.parents=[];self.key=None
    def __enter__(self):
        p=self.path
        require(p.is_absolute() and '..' not in p.parts,'INVALID_SOURCE_PATH')
        require(not any(p.is_relative_to(root) for root in self.excluded),'SOURCE_OVERLAPS_APP_ROOT')
        try:
            if os.name=='nt':
                raw=str(p)
                require(len(p.drive)==2 and p.drive[1]==':' and ':' not in raw[2:] and not raw.startswith('\\\\') and not any(x.endswith((' ','.')) for x in p.parts[1:]),'UNSUPPORTED_SOURCE_PATH')
                require(n.drive_type(p.drive+'\\')==3,'UNSUPPORTED_SOURCE_VOLUME')
                fs=C.create_unicode_buffer(64);flags=n.W.DWORD();n.checked(n.volume_info(p.drive+'\\',None,0,None,None,C.byref(flags),fs,len(fs)))
                require(fs.value=='NTFS','UNSUPPORTED_SOURCE_FILESYSTEM')
                # Directory write sharing allows unrelated app preparation under a
                # common ancestor. No DELETE sharing pins their names/identity.
                for parent in reversed(p.parents):
                    h=self.stack.enter_context(n.Handle(parent,directory=True,_share=3));self.parents.append((parent,h,h.identity()[:3]))
                self.handle=self.stack.enter_context(n.Handle(p));self.key=self.handle.identity()
            else:
                require(self.portable,'UNSUPPORTED_PLATFORM')
                for parent in reversed(p.parents):
                    s=parent.lstat();require(stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode),'REPARSE_SOURCE_PARENT');self.parents.append((parent,None,(s.st_dev,s.st_ino)))
                fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW);self.file=self.stack.enter_context(os.fdopen(fd,'rb'));s=os.fstat(fd)
                require(stat.S_ISREG(s.st_mode) and s.st_nlink==1,'SOURCE_LINK_OR_KIND');self.key=self.identity()
            self.check();return self
        except BaseException:self.stack.close();raise
    def identity(self):
        if self.handle:return self.handle.identity()
        s=os.fstat(self.file.fileno());return (s.st_dev,s.st_ino,s.st_nlink,s.st_mode,s.st_size,s.st_mtime_ns)
    def size(self):return self.handle.size() if self.handle else os.fstat(self.file.fileno()).st_size
    def read(self,size):return self.handle.read(size) if self.handle else self.file.read(size)
    def check(self):
        require(self.identity()==self.key,'SOURCE_CHANGED')
        if self.handle:
            require(self.handle.final_name().casefold()==str(self.path).casefold() and self.handle.info().links==1 and not self.handle.info().attrs&0x400,'SOURCE_CHANGED')
            for path,h,key in self.parents:
                require(h.identity()[:3]==key and h.final_name().casefold()==str(path).casefold() and not h.info().attrs&0x400,'SOURCE_PARENT_CHANGED')
        else:
            s=self.path.lstat();require((s.st_dev,s.st_ino)==self.key[:2] and s.st_nlink==1 and not stat.S_ISLNK(s.st_mode),'SOURCE_CHANGED')
            for path,_,key in self.parents:
                s=path.lstat();require((s.st_dev,s.st_ino)==key and stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode),'SOURCE_PARENT_CHANGED')
    def __exit__(self,*_):self.stack.close()
