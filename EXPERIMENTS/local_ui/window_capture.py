"""Native test evidence: capture only the caller's own mapped Tk client window."""
import ctypes as C,struct,zlib,os
from ctypes import wintypes as W
def capture(root):
    if os.name!='nt':raise RuntimeError('NATIVE_CAPTURE_REQUIRED')
    root.update();hwnd=root.winfo_id();w=root.winfo_width();h=root.winfo_height()
    if not root.winfo_ismapped() or not(200<=w<=2000 and 100<=h<=1400):raise RuntimeError('WINDOW_CAPTURE_BOUNDS')
    u=C.WinDLL('user32',use_last_error=True);g=C.WinDLL('gdi32',use_last_error=True)
    def api(d,n,args,res):f=getattr(d,n);f.argtypes=args;f.restype=res;return f
    get=api(u,'GetDC',[W.HWND],W.HDC);release=api(u,'ReleaseDC',[W.HWND,W.HDC],C.c_int);create=api(g,'CreateCompatibleDC',[W.HDC],W.HDC);bitmap=api(g,'CreateCompatibleBitmap',[W.HDC,C.c_int,C.c_int],W.HBITMAP);select=api(g,'SelectObject',[W.HDC,W.HANDLE],W.HANDLE);blt=api(g,'BitBlt',[W.HDC,C.c_int,C.c_int,C.c_int,C.c_int,W.HDC,C.c_int,C.c_int,W.DWORD],W.BOOL);bits=api(g,'GetDIBits',[W.HDC,W.HBITMAP,W.UINT,W.UINT,C.c_void_p,C.c_void_p,W.UINT],C.c_int);delete=api(g,'DeleteObject',[W.HANDLE],W.BOOL);dcdelete=api(g,'DeleteDC',[W.HDC],W.BOOL)
    dc=get(hwnd);mem=None;bm=None;old=None
    try:
        if not dc:raise C.WinError(C.get_last_error())
        mem=create(dc);bm=bitmap(dc,w,h)
        if not mem or not bm:raise C.WinError(C.get_last_error())
        old=select(mem,bm)
        if not old or not blt(mem,0,0,w,h,dc,0,0,0x00CC0020):raise C.WinError(C.get_last_error())
        select(mem,old);old=None;buf=C.create_string_buffer(w*h*4);header=C.create_string_buffer(struct.pack('<IiiHHIIiiII',40,w,-h,1,32,0,w*h*4,0,0,0,0)+b'\0'*4)
        if bits(dc,bm,0,h,buf,header,0)!=h:raise C.WinError(C.get_last_error())
        bgra=buf.raw;rows=[]
        for y in range(h):
            line=bgra[y*w*4:(y+1)*w*4];rgb=bytearray(w*3);rgb[0::3]=line[2::4];rgb[1::3]=line[1::4];rgb[2::3]=line[0::4];rows.append(b'\0'+rgb)
        def chunk(k,v):return struct.pack('>I',len(v))+k+v+struct.pack('>I',zlib.crc32(k+v)&0xffffffff)
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b'')
        return png,{'method':'GetDC(owned mapped Tk client)/BitBlt/GetDIBits; not desktop capture','window_id':hwnd,'width':w,'height':h,'unique_pixel_bytes':len(set(bgra))}
    finally:
        if old:select(mem,old)
        if bm:delete(bm)
        if mem:dcdelete(mem)
        if dc:release(hwnd,dc)
