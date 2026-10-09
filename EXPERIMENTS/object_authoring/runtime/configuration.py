"""Explicit optional eighth-root overlay. Original seven-root configuration is retained."""
from pathlib import Path
import sys, uuid
import object_authoring as o
r = o.first.runtime
io = o.io
NAME = 'object-authoring-config.json'
PROFILE = 'research-bank-object-config/1'

def load(base, *, portable=False):
    base = Path(base); old = r.load(base, portable=portable)
    with io.Directory(base, root=True):
        with io.File(base / NAME) as f:
            o.need(f.size() <= 16384, 'CONFIG_LIMIT'); raw = f.read(16385); f.check()
        value = o.a.reader.strict_json(raw, 16384, 16)
        o.need(type(value) is dict and set(value) == {'profile', 'config_id', 'base_config_id', 'base_config_sha256', 'object_authoring_root'}, 'INVALID_OBJECT_CONFIGURATION')
        with io.File(base / 'config.json') as f: before = f.read(16385); f.check()
        o.need(value['profile'] == PROFILE and o.a.reader.UUID.fullmatch(value['config_id']) and
               value['base_config_id'] == old['config_id'] and value['base_config_sha256'] == o.a.sha(before), 'BASE_CONFIG_CHANGED')
        root = Path(value['object_authoring_root']); o.need(root == base / 'object_authoring', 'CONFIG_ROOT_MISMATCH')
        roots = {**old['roots'], 'object_authoring': str(root)}
        with io.Directory(root, root=True): pass
        return {'config_id': value['config_id'], 'base_config_id': old['config_id'], 'roots': roots, 'overlay': value}

def setup(base, *, portable=False, hook=None):
    base = Path(base); old = r.load(base, portable=portable)
    if io.present(base / NAME): return load(base, portable=portable)
    with io.Directory(base, root=True, write=True), io.WorkspaceLock(Path(old['roots']['authoring']) / 'LOCK'):
        with io.File(base / 'config.json') as f: original = f.read(16385); f.check()
        root = base / 'object_authoring'
        if not io.present(root): io.mkdir(root)
        with io.Directory(root, root=True): pass
        if hook: hook('object_root_ready', root)
        value = {'profile': PROFILE, 'config_id': str(uuid.uuid4()), 'base_config_id': old['config_id'],
                 'base_config_sha256': o.a.sha(original), 'object_authoring_root': str(root)}
        pending = base / ('object-config-' + uuid.uuid4().hex + '.pending'); raw = o.encoded(value)
        with io.File(pending, new=True) as f: f.write(raw); f.flush()
        with io.File(pending) as f: o.need(f.read(16385) == raw, 'CONFIG_READBACK'); f.check()
        if hook: hook('object_config_pending', pending)
        with io.File(base / 'config.json') as f: o.need(f.read(16385) == original, 'BASE_CONFIG_CHANGED'); f.check()
        io.move_no_replace(pending, base / NAME)
        if hook: hook('object_config_published', base / NAME)
    return load(base, portable=portable)

def rollback(base, *, portable=False):
    """Disable the overlay by preserving it under a new name; keep all material and journals."""
    base = Path(base); cfg = load(base, portable=portable); old = r.load(base, portable=portable)
    with io.Directory(base, root=True, write=True), io.WorkspaceLock(Path(old['roots']['authoring']) / 'LOCK'):
        saved = base / ('object-authoring-config-' + cfg['config_id'] + '.disabled')
        io.move_no_replace(base / NAME, saved)
    r.load(base, portable=portable)
    return {'status': 'OK', 'code': 'OBJECT_CONFIG_DISABLED_DATA_RETAINED', 'preserved_overlay': str(saved)}
