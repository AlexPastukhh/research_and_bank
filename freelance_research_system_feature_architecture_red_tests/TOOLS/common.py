from pathlib import Path
import json, hashlib, os, tempfile

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def save_json(path,obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+".tmp")
    tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    os.replace(tmp,p)

def confined(root, relative):
    root=Path(root).resolve()
    p=(root/relative).resolve()
    try: p.relative_to(root)
    except ValueError: raise ValueError(f"path escapes project root: {relative}")
    return p

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
