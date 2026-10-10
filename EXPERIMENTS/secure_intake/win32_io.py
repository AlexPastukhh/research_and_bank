"""Narrow Windows/NTFS handle adapter for the synthetic secure-intake prototype.

Trusted root parents and authorized owner/SYSTEM are part of the threat boundary.
No admin resistance, remote/removable filesystem or live Bank support is claimed.
"""
import ctypes as C
from ctypes import wintypes as W
import os
from pathlib import Path

class SafetyError(ValueError): pass

if os.name == 'nt':
    K = C.WinDLL('kernel32', use_last_error=True)
    A = C.WinDLL('advapi32', use_last_error=True)
else:
    K = A = None

class FileInfo(C.Structure):
    _fields_ = [('attrs', W.DWORD), ('created', W.FILETIME), ('accessed', W.FILETIME),
                ('written', W.FILETIME), ('volume', W.DWORD), ('size_hi', W.DWORD),
                ('size_lo', W.DWORD), ('links', W.DWORD), ('index_hi', W.DWORD), ('index_lo', W.DWORD)]
class SecurityAttributes(C.Structure):
    _fields_ = [('length', W.DWORD), ('descriptor', C.c_void_p), ('inherit', W.BOOL)]

def api(dll, name, args, result):
    f = getattr(dll, name); f.argtypes = args; f.restype = result
    return f

if K:
    create = api(K,'CreateFileW',[W.LPCWSTR,W.DWORD,W.DWORD,C.c_void_p,W.DWORD,W.DWORD,W.HANDLE],W.HANDLE)
    close_handle = api(K,'CloseHandle',[W.HANDLE],W.BOOL)
    get_info = api(K,'GetFileInformationByHandle',[W.HANDLE,C.POINTER(FileInfo)],W.BOOL)
    get_type = api(K,'GetFileType',[W.HANDLE],W.DWORD)
    read_file = api(K,'ReadFile',[W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p],W.BOOL)
    write_file = api(K,'WriteFile',[W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p],W.BOOL)
    seek_file = api(K,'SetFilePointerEx',[W.HANDLE,C.c_longlong,C.POINTER(C.c_longlong),W.DWORD],W.BOOL)
    flush_file = api(K,'FlushFileBuffers',[W.HANDLE],W.BOOL)
    final_path = api(K,'GetFinalPathNameByHandleW',[W.HANDLE,W.LPWSTR,W.DWORD,W.DWORD],W.DWORD)
    drive_type = api(K,'GetDriveTypeW',[W.LPCWSTR],W.UINT)
    volume_info = api(K,'GetVolumeInformationW',[W.LPCWSTR,W.LPWSTR,W.DWORD,C.POINTER(W.DWORD),C.POINTER(W.DWORD),C.POINTER(W.DWORD),W.LPWSTR,W.DWORD],W.BOOL)
    attributes = api(K,'GetFileAttributesW',[W.LPCWSTR],W.DWORD)
    mkdir_native = api(K,'CreateDirectoryW',[W.LPCWSTR,C.POINTER(SecurityAttributes)],W.BOOL)
    local_free = api(K,'LocalFree',[C.c_void_p],C.c_void_p)
    process = api(K,'GetCurrentProcess',[],W.HANDLE)
    open_token = api(A,'OpenProcessToken',[W.HANDLE,W.DWORD,C.POINTER(W.HANDLE)],W.BOOL)
    token_info = api(A,'GetTokenInformation',[W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.POINTER(W.DWORD)],W.BOOL)
    sid_string = api(A,'ConvertSidToStringSidW',[C.c_void_p,C.POINTER(W.LPWSTR)],W.BOOL)
    sddl_sd = api(A,'ConvertStringSecurityDescriptorToSecurityDescriptorW',[W.LPCWSTR,W.DWORD,C.POINTER(C.c_void_p),C.POINTER(W.DWORD)],W.BOOL)
    security_info = api(A,'GetSecurityInfo',[W.HANDLE,C.c_int,W.DWORD,C.POINTER(C.c_void_p),C.c_void_p,C.POINTER(C.c_void_p),C.c_void_p,C.POINTER(C.c_void_p)],W.DWORD)
    sd_string = api(A,'ConvertSecurityDescriptorToStringSecurityDescriptorW',[C.c_void_p,W.DWORD,W.DWORD,C.POINTER(W.LPWSTR),C.POINTER(W.DWORD)],W.BOOL)

INVALID = C.c_void_p(-1).value
READ = 0x80000000
WRITE = 0x40000000
FLAGS = 0x02000000 | 0x00200000  # BACKUP_SEMANTICS | OPEN_REPARSE_POINT

def checked(ok):
    if not ok: raise C.WinError(C.get_last_error())
def ensure_windows():
    if K is None: raise SafetyError('UNSUPPORTED_PLATFORM')
def extended(path):
    return '\\\\?\\' + str(path)
def time_int(value): return (value.dwHighDateTime << 32) | value.dwLowDateTime

class Handle:
    """Non-inheritable handle; filenames are metadata, not future read authority."""
    def __init__(self, path, *, directory=False, new=False, _share=None):
        ensure_windows(); self.path = Path(path); self.h = None; self.directory = directory
        # New private files must have the same explicit owner as their directory.
        # In an elevated process the token's default owner may be Administrators.
        # Never change the descriptor of an existing file or weaken its check.
        descriptor = C.c_void_p(); attributes = None
        if new:
            sid = current_sid()
            checked(sddl_sd('O:'+sid+'D:P(A;;FA;;;SY)(A;;FA;;;'+sid+')',
                            1,C.byref(descriptor),None))
            attributes = SecurityAttributes(C.sizeof(SecurityAttributes),descriptor,False)
        try:
            h = create(extended(self.path), READ | (WRITE if new else 0), (0 if new else 1) if _share is None else _share,
                       C.byref(attributes) if attributes is not None else None, 1 if new else 3, FLAGS, None)
            error = C.get_last_error()
        finally:
            if descriptor.value: local_free(descriptor)
        if h == INVALID: raise C.WinError(error)
        self.h = h
        try:
            info = self.info()
            if get_type(h) != 1: raise SafetyError('NOT_DISK_FILE')
            if info.attrs & 0x400: raise SafetyError('REPARSE_POINT')
            if bool(info.attrs & 0x10) != directory: raise SafetyError('FILE_KIND_MISMATCH')
            if not directory and info.links != 1: raise SafetyError('HARDLINK')
            actual = self.final_name()
            if actual.casefold() != str(self.path).casefold(): raise SafetyError('FINAL_PATH_MISMATCH')
        except BaseException:
            self.close(); raise
    def info(self):
        if self.h is None: raise SafetyError('HANDLE_CLOSED')
        info = FileInfo(); checked(get_info(self.h, C.byref(info))); return info
    def size(self):
        info = self.info(); return (info.size_hi << 32) | info.size_lo
    def identity(self):
        i = self.info()
        return (i.volume, i.index_hi, i.index_lo, i.links, i.attrs,
                (i.size_hi << 32)|i.size_lo, time_int(i.written))
    def final_name(self):
        size = final_path(self.h, None, 0, 0)
        if not size: raise C.WinError(C.get_last_error())
        buf = C.create_unicode_buffer(size+1); n = final_path(self.h,buf,len(buf),0)
        if not n or n >= len(buf): raise SafetyError('FINAL_PATH_QUERY_FAILED')
        name = buf.value
        if not name.startswith('\\\\?\\') or name.startswith('\\\\?\\UNC\\'): raise SafetyError('UNSUPPORTED_ROOT')
        return name[4:]
    def seek(self): checked(seek_file(self.h, 0, None, 0))
    def read(self, size):
        buf = C.create_string_buffer(size); got = W.DWORD()
        checked(read_file(self.h,buf,size,C.byref(got),None)); return buf.raw[:got.value]
    def write(self, raw):
        if not raw: return
        buf = C.create_string_buffer(raw); got = W.DWORD()
        checked(write_file(self.h,buf,len(raw),C.byref(got),None))
        if got.value != len(raw): raise OSError('SHORT_WRITE')
    def close(self):
        if self.h is not None:
            h,self.h = self.h,None; checked(close_handle(h))
    def __enter__(self): return self
    def __exit__(self,*_): self.close()

def current_sid():
    ensure_windows(); token = W.HANDLE(); checked(open_token(process(),8,C.byref(token)))
    try:
        count = W.DWORD(); token_info(token,1,None,0,C.byref(count))
        buf = C.create_string_buffer(count.value); checked(token_info(token,1,buf,count,C.byref(count)))
        sid = C.cast(buf,C.POINTER(C.c_void_p))[0]; out = W.LPWSTR()
        checked(sid_string(sid,C.byref(out)))
        try: return out.value
        finally: local_free(C.cast(out,C.c_void_p))
    finally: checked(close_handle(token))

def private_directory(path):
    """Create only a NEW owned test directory with a protected user+SYSTEM DACL."""
    ensure_windows(); sid = current_sid(); descriptor = C.c_void_p()
    sddl = 'O:'+sid+'D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;'+sid+')'
    checked(sddl_sd(sddl,1,C.byref(descriptor),None))
    try:
        sa = SecurityAttributes(C.sizeof(SecurityAttributes),descriptor,False)
        checked(mkdir_native(extended(Path(path)),C.byref(sa)))
    finally: local_free(descriptor)

def security_sddl(handle):
    sd = C.c_void_p(); owner = C.c_void_p(); dacl = C.c_void_p()
    error = security_info(handle.h,1,1|4,C.byref(owner),None,C.byref(dacl),None,C.byref(sd))
    if error: raise C.WinError(error)
    try:
        if not dacl.value: raise SafetyError('NULL_DACL')
        value = W.LPWSTR(); checked(sd_string(sd,1,1|4,C.byref(value),None))
        try: return value.value
        finally: local_free(C.cast(value,C.c_void_p))
    finally: local_free(sd)

def verify_private_acl(handle):
    """Conservative fail-closed check for the simple prototype DACL, no generic ACL evaluator."""
    import re
    value = security_sddl(handle); sid = current_sid()
    if value.split('D:',1)[0] != 'O:'+sid: raise SafetyError('UNTRUSTED_OWNER')
    aces = re.findall(r'\(([^()]*)\)',value)
    if not aces: raise SafetyError('EMPTY_OR_UNSUPPORTED_DACL')
    for ace in aces:
        fields = ace.split(';')
        if len(fields) != 6 or fields[0] != 'A' or fields[5] not in [sid,'SY']:
            raise SafetyError('UNTRUSTED_DACL')
    if not any(ace.split(';')[-1] == sid for ace in aces): raise SafetyError('MISSING_OWNER_ACCESS')
    return value

def configured_root(path):
    """Reject redirects before content; root parents must remain trusted by configuration."""
    ensure_windows(); raw = os.fspath(path); p = Path(raw)
    if not p.is_absolute() or not p.drive or len(p.drive)!=2 or '..' in p.parts or raw.startswith('\\\\'):
        raise SafetyError('UNSUPPORTED_ROOT')
    root = p.drive+'\\'
    if drive_type(root) != 3: raise SafetyError('UNSUPPORTED_VOLUME')
    fs = C.create_unicode_buffer(64); flags = W.DWORD()
    checked(volume_info(root,None,0,None,None,C.byref(flags),fs,len(fs)))
    if fs.value != 'NTFS' or not flags.value & 8: raise SafetyError('UNSUPPORTED_FILESYSTEM')
    for ancestor in [*reversed(p.parents),p]:
        attr = attributes(extended(ancestor))
        if attr == 0xffffffff: raise C.WinError(C.get_last_error())
        if attr & 0x400: raise SafetyError('REPARSE_ROOT_OR_PARENT')
    handle = Handle(p,directory=True)
    try: verify_private_acl(handle)
    except BaseException: handle.close(); raise
    return handle


class SQLiteGuard:
    """Pin DB identity while allowing SQLite reads/writes. Sidecar checks are
    ephemeral so SQLite can delete its journal. Parent/current owner remain
    trusted; this is not protection against that owner changing file ACLs.
    """
    def __init__(self,path):
        self.path=Path(path);self.handle=None
        try:
            self.handle=Handle(self.path,_share=3) # READ|WRITE sharing, no DELETE
            verify_private_acl(self.handle);self.key=self.handle.identity()[:3]
            self.check()
        except BaseException:self.close();raise
    def check(self):
        verify_private_acl(self.handle)
        info=self.handle.info()
        if self.handle.identity()[:3]!=self.key or info.links!=1 or info.attrs&0x400:
            raise SafetyError('SQLITE_FILE_CHANGED')
        # No connect/SELECT may recover a preexisting untrusted sidecar.
        for suffix in ['-journal','-wal','-shm']:
            path=Path(str(self.path)+suffix)
            try:h=Handle(path,_share=7)
            except FileNotFoundError:continue
            with h:
                verify_private_acl(h)
                if suffix!='-journal':raise SafetyError('UNSUPPORTED_SQLITE_SIDECAR')
        return self
    def close(self):
        if self.handle is not None:self.handle.close();self.handle=None
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
