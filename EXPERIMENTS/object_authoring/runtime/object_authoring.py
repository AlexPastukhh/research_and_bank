"""Immutable object preparation over the existing Bank contracts and shared lease."""
from pathlib import Path
from contextlib import ExitStack, contextmanager
import codecs, copy, hashlib, json, os, sys, uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'EXPERIMENTS/first_bank'))
import integration as first
a = first.p.a
io = a.io
need = a.need
encoded = a.encoded
o_read = first.p.base.read
PROFILE = 'r1-object-authoring/1'
ROLES = a.ROLES | {'object_authoring'}
PRODUCER = {'name': 'research-bank-object-authoring', 'version': '1'}
TYPES = {'Asset', 'Entity', 'Annotation', 'Collection'}

class Workspace(a.Workspace):
    def __init__(self, roots, backend, **kw):
        super().__init__(roots, **kw)
        self.backend = backend
        self.limits.update(policy_version=PROFILE, references_per_list=128, aliases=128,
                           external_ids=128, alias_utf8_bytes=4096, namespace_utf8_bytes=4096,
                           external_value_utf8_bytes=8192, entity_kind_utf8_bytes=4096,
                           base_document_bytes=2097152)
        self.limits.update(kw.get('_limits') or {})
        self.journal_root = self.roots['object_authoring']

    @contextmanager
    def session(self):
        need(os.name == 'nt' or self.portable, 'UNSUPPORTED_PLATFORM')
        need(set(self.roots) == ROLES, 'INVALID_ROOT_CONFIGURATION')
        paths = list(self.roots.values())
        need(all(p.is_absolute() and '..' not in p.parts for p in paths), 'INVALID_ROOT_CONFIGURATION')
        need(all(not (x.is_relative_to(y) or y.is_relative_to(x))
                 for i, x in enumerate(paths) for y in paths[i+1:]), 'ROOT_OVERLAP')
        with ExitStack() as stack:
            for path in paths:
                stack.enter_context(io.Directory(path, write=True, root=True))
            stack.enter_context(io.WorkspaceLock(self.roots['authoring'] / 'LOCK'))
            yield stack

    def usage(self):
        size = entries = count = 0
        def walk(path):
            nonlocal size, entries
            with os.scandir(path) as it:
                for entry in it:
                    entries += 1
                    need(entries <= self.limits['workspace_scan_entries'], 'AUTHORING_SCAN_LIMIT')
                    st = entry.stat(follow_symlinks=False)
                    need(not entry.is_symlink() and not getattr(st, 'st_file_attributes', 0) & 0x400,
                         'UNTRUSTED_WORKSPACE_ENTRY')
                    if entry.is_dir(follow_symlinks=False):
                        with io.Directory(Path(entry.path)): walk(Path(entry.path))
                    else:
                        need(entry.is_file(follow_symlinks=False), 'UNTRUSTED_WORKSPACE_ENTRY')
                        with io.File(Path(entry.path)) as handle: size += handle.size(); handle.check()
        with os.scandir(self.journal_root) as it:
            for entry in it:
                need(a.reader.UUID.fullmatch(entry.name) and entry.is_dir(follow_symlinks=False)
                     and not entry.is_symlink(), 'UNTRUSTED_WORKSPACE_ENTRY')
                count += 1
        walk(self.journal_root); walk(self.roots['source'])
        return size, count

    def pin(self, ref):
        need(type(ref) is dict and set(ref) == {'object_type', 'object_id', 'revision_id'}, 'INVALID_REFERENCE')
        need(ref['object_type'] in TYPES and all(type(ref[k]) is str and a.reader.UUID.fullmatch(ref[k])
             for k in ['object_id', 'revision_id']), 'INVALID_REFERENCE')
        return copy.deepcopy(ref)

    def read_base(self, ref, budget=None):
        ref = self.pin(ref)
        # bank.get does not expand Collection members; the exact pinned version is the authority.
        with self.backend.base.controller() as controller:
            q = self.backend.base.query('bank.get', object_type=ref['object_type'], object_id=ref['object_id'],
                                        selector={'mode': 'pinned', 'revision_id': ref['revision_id']})
            result = controller.query(encoded(q))
        need(result.get('status') == 'OK', 'BASE_' + result.get('code', 'UNAVAILABLE'))
        d = result['data']; doc = d['document']
        need({k: doc[k] for k in ref} == ref, 'BASE_IDENTITY_MISMATCH')
        self.contracts.schema(doc)
        need((doc['object_type'], doc['schema']) in self.contracts.allowed, 'UNSUPPORTED_SCHEMA')
        raw = encoded({'ref': ref, 'document': doc, 'commit_sequence': d['commit_sequence'],
                       'accepted_at': d['accepted_at']})
        need(len(raw) <= self.limits['base_document_bytes'], 'BASE_DOCUMENT_LIMIT')
        if budget: budget.charge(len(raw))
        return self.parse(raw, self.limits['base_document_bytes']), raw

    def defaults(self, typ):
        if typ == 'Entity': return {'entity_kind': 'other', 'aliases': [], 'external_ids': [], 'asset_refs': []}
        if typ == 'Collection': return {'members': []}
        if typ == 'Annotation':
            return {'kind': 'note', 'content_format': 'plain_text', 'body': '',
                    'author': {'kind': 'unknown', 'identity': None, 'model': None}, 'targets': []}
        raise a.Problem('NEW_ASSET_USE_EXISTING_FORM')

    def verify_refs(self, refs, budget):
        refs = {encoded(ref): ref for ref in refs}.values()
        read = o_read
        api = read.ReadAPI(self.roots['bank'])
        try:
            with a.im.Store(self.roots['bank'], contracts=self.contracts) as store:
                with read.ReadSession(store, read.Budget(api.limits)) as session:
                    for ref in refs:
                        budget.tick()
                        doc, _, _ = session.select({'object_type': ref['object_type'], 'object_id': ref['object_id'],
                            'selector': {'mode': 'pinned', 'revision_id': ref['revision_id']}})
                        need({k: doc[k] for k in ref} == ref, 'REFERENCE_IDENTITY_MISMATCH')
                        budget.charge(len(encoded(doc)))
        except read.ReadError as e: raise a.Problem('BASE_' + e.code) from e

    def validate_doc(self, doc):
        self.contracts.schema(doc)
        need((doc['object_type'], doc['schema']) in self.contracts.allowed, 'UNSUPPORTED_SCHEMA')
        lim = self.limits
        a.text(doc['title'], lim['title_utf8_bytes'])
        data = doc['data']; provenance = doc['provenance']
        lists = [provenance['derived_from']]
        if doc['object_type'] == 'Entity':
            a.text(data['entity_kind'], lim['entity_kind_utf8_bytes'])
            need(len(data['aliases']) <= lim['aliases'] and len(data['external_ids']) <= lim['external_ids'], 'OBJECT_LIST_LIMIT')
            for v in data['aliases']: a.text(v, lim['alias_utf8_bytes'])
            for v in data['external_ids']:
                a.text(v['namespace'], lim['namespace_utf8_bytes']); a.text(v['value'], lim['external_value_utf8_bytes'])
            lists.append(data['asset_refs'])
        elif doc['object_type'] == 'Annotation':
            a.text(data['body'], lim['body_utf8_bytes'])
            for k in ['identity', 'model']: a.text(data['author'][k], lim['identity_or_model_utf8_bytes'], optional=True)
            lists.append(data['targets'])
        elif doc['object_type'] == 'Collection': lists.append(data['members'])
        elif data['storage']['mode'] == 'locator':
            a.text(data['storage']['uri'], lim['locator_utf8_bytes'])
            a.text(data['storage']['label'], lim['title_utf8_bytes'], optional=True)
        else:
            a.text(data['storage']['original_filename'], lim['filename_utf8_bytes'])
            need(data['storage']['byte_length'] <= self.contracts.policy['file_bytes'], 'AUTHORING_INPUT_LIMIT')
        a.text(provenance['source_locator'], lim['locator_utf8_bytes'], optional=True)
        need(provenance['source_ref'] is None, 'UNSUPPORTED_REFERENCE')
        refs = []
        for values in lists:
            need(len(values) <= lim['references_per_list'], 'OBJECT_LIST_LIMIT')
            refs.extend(self.pin(v) for v in values)
        need(len(encoded(doc)) <= min(lim['document_bytes'], self.contracts.policy['object_json_bytes']), 'AUTHORING_INPUT_LIMIT')
        return refs

    def template(self, fields, base, created, oid, rid):
        need(type(fields) is dict and set(fields) <= {'object_type', 'title', 'data', 'provenance'}, 'INVALID_INPUT')
        typ = base['document']['object_type'] if base else fields.get('object_type')
        need(typ in TYPES and fields.get('object_type', typ) == typ, 'OBJECT_TYPE_IMMUTABLE')
        if base: doc = copy.deepcopy(base['document'])
        else:
            doc = {'schema': 'bank-' + typ.lower() + '/1', 'object_type': typ, 'object_id': oid,
                   'revision_id': rid, 'revision_created_at': created, 'title': fields.get('title'),
                   'data': self.defaults(typ), 'provenance': {'origin_kind': 'unknown', 'producer': PRODUCER,
                   'source_locator': None, 'captured_at': None, 'source_ref': None, 'derived_from': []}}
        doc.update(revision_id=rid, revision_created_at=created)
        for key in ['title', 'data']:
            if key in fields: doc[key] = copy.deepcopy(fields[key])
        if 'provenance' in fields:
            p = fields['provenance']
            need(type(p) is dict and set(p) <= {'origin_kind', 'source_locator', 'derived_from'}, 'INVALID_PROVENANCE_INPUT')
            doc['provenance'].update(copy.deepcopy(p))
        # Content authorship is explicit; the producer identifies this preparation.
        doc['provenance']['producer'] = copy.deepcopy(PRODUCER)
        if typ == 'Annotation':
            author = doc['data'].get('author', {}).get('kind')
            if author in ['user', 'ai']: doc['provenance']['origin_kind'] = author + '_authored'
        return doc

    def doc(self, intent, original=None):
        doc = copy.deepcopy(intent['template'])
        if original:
            doc['data']['storage'].update(file_path='payload/original.bin', byte_length=original[0], sha256=original[1])
        return doc

    def draft(self, intent, doc, files):
        return {'protocol': 'local-bank-draft/1', 'transaction_id': intent['transaction_id'],
                'command': 'commit_revisions', 'intent': 'independent_save', 'created_at': intent['created_at'],
                'producer': copy.deepcopy(PRODUCER), 'operations': [{'object_id': doc['object_id'],
                'revision_id': doc['revision_id'], 'base_revision_id': intent['base_ref']['revision_id'] if intent['base_ref'] else None,
                'type': doc['object_type'], 'schema_ref': doc['schema'], 'document_path': 'docs/object.json'}], 'files': sorted(files)}

    def prepare(self, fields, *, base_ref=None, replacement=None, cancel=None):
        tx = None; sealed = False; budget = a.Budget(self, cancel)
        try:
            with self.session() as stack:
                base, raw_base = self.read_base(base_ref, budget) if base_ref else (None, None)
                created = a.utc(); oid = base_ref['object_id'] if base else str(uuid.uuid4()); rid = str(uuid.uuid4())
                template = self.template(fields, base, created, oid, rid)
                original = None; expected = None; capture = None
                if template['object_type'] == 'Asset':
                    need(base is not None, 'NEW_ASSET_USE_EXISTING_FORM')
                    old = base['document']['data']['storage']; new = template['data']['storage']
                    need(old['mode'] == new['mode'], 'ASSET_MODE_IMMUTABLE')
                    if old['mode'] == 'locator' and old['uri'] != new['uri']:
                        declared = fields.get('provenance', {})
                        old_provenance = base['document']['provenance']
                        origin = declared.get('origin_kind', 'unknown')
                        source = declared.get('source_locator', new['uri'])
                        if origin == old_provenance['origin_kind'] and source == old_provenance['source_locator']:
                            origin = 'unknown'; source = new['uri']
                        template['provenance'].update(origin_kind=origin, source_locator=source,
                            captured_at=created, source_ref=None, derived_from=copy.deepcopy(declared.get('derived_from', [])))
                    if old['mode'] == 'bytes':
                        need(new == old, 'ASSET_STORAGE_READONLY')
                        if replacement is None:
                            # Export is a private owned copy, not a user-selected external file.
                            exported = self.backend.base.dispatch('export', {'ref': base_ref})
                            need(exported.get('status') == 'OK' and exported.get('data', {}).get('availability') == 'bytes', 'ORIGINAL_UNAVAILABLE')
                            value = exported['data']['original']; path = Path(value['path'])
                            need(path.is_absolute() and path.is_relative_to(self.roots['output']), 'INVALID_RETAINED_EXPORT')
                            expected = (old['byte_length'], old['sha256'])
                            need((value['byte_length'], value['sha256']) == expected, 'ORIGINAL_DESCRIPTOR_MISMATCH')
                            original = stack.enter_context(io.File(path)); capture = {'kind': 'retained', 'ref': self.pin(base_ref)}
                        else:
                            need(type(replacement) is dict and set(replacement) == {'path', 'input_mode'}, 'INVALID_REPLACEMENT')
                            mode = replacement['input_mode']; need(mode in ['utf8_text', 'binary'], 'INVALID_INPUT_MODE')
                            a.text(replacement['path'], self.limits['source_path_utf8_bytes'])
                            original = stack.enter_context(io.SelectedOriginal(replacement['path'], self.roots.values(), portable_fixture=self.portable))
                            template['data']['storage'].update(original_filename=Path(replacement['path']).name,
                               media_type='text/plain' if mode == 'utf8_text' else 'application/octet-stream', byte_length=original.size(), sha256='0'*64)
                            declared = fields.get('provenance', {})
                            template['provenance'].update(origin_kind=declared.get('origin_kind', 'unknown'), source_locator=declared.get('source_locator'), captured_at=created, source_ref=None, derived_from=copy.deepcopy(declared.get('derived_from', [])))
                            capture = {'kind': 'replacement', 'path': replacement['path'], 'input_mode': mode}
                        need(original.size() <= self.contracts.policy['file_bytes'], 'AUTHORING_INPUT_LIMIT')
                        if expected: need(original.size() == expected[0], 'ORIGINAL_DESCRIPTOR_MISMATCH')
                need(replacement is None or original is not None, 'REPLACEMENT_REQUIRES_BYTES_ASSET')
                refs = self.validate_doc(template)
                if refs: self.verify_refs(refs, budget)
                txid = str(uuid.uuid4())
                intent = {'protocol': 'local-bank-object-intent/1', 'transaction_id': txid, 'object_id': oid,
                          'revision_id': rid, 'created_at': created, 'profile': copy.deepcopy(self.limits),
                          'base_ref': self.pin(base_ref) if base else None, 'base_sha256': a.sha(raw_base) if base else None,
                          'template': template, 'capture': capture}
                raw_intent = encoded(intent); need(len(raw_intent) <= self.limits['intent_record_bytes'], 'AUTHORING_INPUT_LIMIT')
                size, count = self.usage(); reserve = len(raw_intent) + len(raw_base or b'') + len(encoded(template)) + self.limits['seal_record_bytes'] + self.contracts.policy['manifest_bytes'] + (original.size() if original else 0)
                need(2*reserve <= self.limits['work_bytes'], 'AUTHORING_WORK_LIMIT')
                need(count < self.limits['intents'] and size+reserve <= self.limits['workspace_bytes_including_managed_source'], 'AUTHORING_WORKSPACE_LIMIT')
                budget.tick(); journal = self.journal_root / txid; source = self.roots['source'] / txid
                need(not io.present(journal) and not io.present(source), 'INTENT_COLLISION')
                tx = txid; io.mkdir(journal); stack.enter_context(io.Directory(journal, write=True)); self.event('allocated', tx)
                self.control(journal, 'INTENT', raw_intent, budget, 'intent_published')
                if raw_base: self.control(journal, 'BASE', raw_base, budget, 'base_published')
                io.mkdir(source); stack.enter_context(io.Directory(source, write=True)); self.event('source_created', tx)
                io.mkdir(source / 'docs'); descriptors = []; original_descriptor = None
                if original:
                    io.mkdir(source / 'payload'); digest = hashlib.sha256(); total = 0
                    decoder = codecs.getincrementaldecoder('utf8')('strict') if capture.get('input_mode') == 'utf8_text' else None
                    with io.File(source / 'payload/original.bin', new=True) as dest:
                        while chunk := original.read(self.limits['chunk_bytes']):
                            if decoder:
                                try: decoder.decode(chunk, final=False)
                                except UnicodeDecodeError as e: raise a.Problem('INVALID_UTF8') from e
                            total += len(chunk); need(total <= self.contracts.policy['file_bytes'], 'AUTHORING_INPUT_LIMIT')
                            budget.charge(len(chunk)); digest.update(chunk); dest.write(chunk); self.event('capture_chunk', tx)
                        if decoder:
                            try: decoder.decode(b'', final=True)
                            except UnicodeDecodeError as e: raise a.Problem('INVALID_UTF8') from e
                        original.check(); need(total == original.size(), 'SOURCE_CHANGED'); dest.flush()
                    original_descriptor = (total, digest.hexdigest())
                    if expected: need(original_descriptor == expected, 'ORIGINAL_DESCRIPTOR_MISMATCH')
                    descriptors.append({'path': 'payload/original.bin', 'byte_length': total, 'sha256': digest.hexdigest()})
                    self.event('original_flushed', tx)
                doc = self.doc(intent, original_descriptor); self.validate_doc(doc)
                raw_doc = encoded(doc); self.write(source / 'docs/object.json', raw_doc, budget, 'document_flushed')
                descriptors.append({'path': 'docs/object.json', 'byte_length': len(raw_doc), 'sha256': a.sha(raw_doc)})
                descriptors.sort(key=lambda v: v['path']); draft = self.draft(intent, doc, [v['path'] for v in descriptors])
                need(next(self.dv.iter_errors(draft), None) is None, 'INVALID_DRAFT')
                raw_draft = encoded(draft); self.write(source / 'DRAFT.pending', raw_draft, budget, 'draft_flushed')
                seal = {'protocol': 'local-bank-object-seal/1', 'transaction_id': tx, 'intent_sha256': a.sha(raw_intent),
                        'base_sha256': intent['base_sha256'], 'draft_sha256': a.sha(raw_draft), 'files': descriptors}
                raw_seal = encoded(seal); need(len(raw_seal) <= self.limits['seal_record_bytes'], 'AUTHORING_INPUT_LIMIT')
                budget.tick(); self.control(journal, 'SEAL', raw_seal, budget, 'seal_published'); sealed = True
                self.verify_source(intent, seal, raw_intent, 'DRAFT.pending', budget)
                io.move_no_replace(source / 'DRAFT.pending', source / 'DRAFT.json'); self.event('draft_published', tx)
                return self.prepared_result(intent, seal, draft)
        except a.Cancelled: return self.result(tx, 'INCOMPLETE' if tx else 'CANCELLED', 'SEALED_VERIFY_REQUIRED' if sealed else 'PREPARATION_CANCELLED')
        except (Exception, KeyboardInterrupt) as e: return self.failure(tx, e, sealed)

    def read_intent(self, tx, budget):
        raw = self.small(self.journal_root / tx / 'INTENT.json', self.limits['intent_record_bytes'], budget)
        d = self.parse(raw, self.limits['intent_record_bytes'])
        need(type(d) is dict and set(d) == {'protocol', 'transaction_id', 'object_id', 'revision_id', 'created_at', 'profile', 'base_ref', 'base_sha256', 'template', 'capture'}, 'INVALID_INTENT')
        need(d['protocol'] == 'local-bank-object-intent/1' and d['transaction_id'] == tx and raw == encoded(d), 'INVALID_INTENT')
        need(all(type(d[k]) is str and a.reader.UUID.fullmatch(d[k]) for k in ['transaction_id', 'object_id', 'revision_id']), 'INVALID_INTENT')
        need(len({d[k] for k in ['transaction_id', 'object_id', 'revision_id']}) == 3, 'INVALID_INTENT')
        need(type(d['profile']) is dict and set(d['profile']) == set(self.limits) and d['profile']['policy_version'] == PROFILE, 'UNSUPPORTED_AUTHORING_PROFILE')
        for k, v in self.limits.items():
            if type(v) is int: need(type(d['profile'][k]) is int and d['profile'][k] >= 0, 'INVALID_AUTHORING_PROFILE')
        doc = d['template']; self.validate_doc(doc)
        need((doc['object_id'], doc['revision_id'], doc['revision_created_at']) == (d['object_id'], d['revision_id'], d['created_at']), 'INVALID_INTENT')
        if d['base_ref']:
            ref = self.pin(d['base_ref']); need(ref['object_id'] == d['object_id'] and ref['object_type'] == doc['object_type'] and ref['revision_id'] != d['revision_id'], 'INVALID_BASE')
            base_raw = self.small(self.journal_root / tx / 'BASE.json', self.limits['base_document_bytes'], budget)
            need(a.sha(base_raw) == d['base_sha256'], 'BASE_INTEGRITY')
            base = self.parse(base_raw, self.limits['base_document_bytes']); need(base_raw == encoded(base) and base['ref'] == ref, 'BASE_INTEGRITY')
            self.contracts.schema(base['document']); need({k: base['document'][k] for k in ref} == ref, 'BASE_INTEGRITY')
        else: need(d['base_sha256'] is None and doc['object_type'] != 'Asset', 'INVALID_BASE')
        capture = d['capture']
        if capture:
            need(doc['object_type'] == 'Asset' and doc['data']['storage']['mode'] == 'bytes', 'INVALID_CAPTURE')
            need(type(capture) is dict and (set(capture) == {'kind', 'ref'} and capture['kind'] == 'retained' and capture['ref'] == d['base_ref'] or
                 set(capture) == {'kind', 'path', 'input_mode'} and capture['kind'] == 'replacement' and capture['input_mode'] in ['binary', 'utf8_text']), 'INVALID_CAPTURE')
        else: need(doc['object_type'] != 'Asset' or doc['data']['storage']['mode'] == 'locator', 'INVALID_CAPTURE')
        return d, raw

    def read_seal(self, tx, budget):
        raw = self.small(self.journal_root / tx / 'SEAL.json', self.limits['seal_record_bytes'], budget)
        d = self.parse(raw, self.limits['seal_record_bytes'])
        need(type(d) is dict and set(d) == {'protocol', 'transaction_id', 'intent_sha256', 'base_sha256', 'draft_sha256', 'files'}, 'INVALID_SEAL')
        need(d['protocol'] == 'local-bank-object-seal/1' and d['transaction_id'] == tx and raw == encoded(d), 'INVALID_SEAL')
        for key in ['intent_sha256', 'draft_sha256']:
            need(type(d[key]) is str and len(d[key]) == 64 and all(c in '0123456789abcdef' for c in d[key]), 'INVALID_SEAL')
        need(d['base_sha256'] is None or type(d['base_sha256']) is str and len(d['base_sha256']) == 64 and all(c in '0123456789abcdef' for c in d['base_sha256']), 'INVALID_SEAL')
        need(type(d['files']) is list and 1 <= len(d['files']) <= 2, 'INVALID_SEAL')
        for f in d['files']:
            need(type(f) is dict and set(f) == {'path', 'byte_length', 'sha256'} and type(f['byte_length']) is int and f['byte_length'] >= 0,
                 'INVALID_SEAL')
            need(type(f['sha256']) is str and len(f['sha256']) == 64 and all(c in '0123456789abcdef' for c in f['sha256']), 'INVALID_SEAL')
        return d

    def verify_source(self, intent, seal, intent_raw, draft_name, budget):
        need(seal['intent_sha256'] == a.sha(intent_raw) and seal['base_sha256'] == intent['base_sha256'], 'INTENT_INTEGRITY')
        source = self.roots['source'] / intent['transaction_id']; names = ['docs/object.json'] + (['payload/original.bin'] if intent['capture'] else [])
        need([f['path'] for f in seal['files']] == sorted(names), 'SEAL_INVENTORY')
        with ExitStack() as stack:
            stack.enter_context(io.Directory(source, write=True))
            pub = a.producer.Publisher(self.roots['intake'], self.roots['source'], _portable_fixture=self.portable)
            parents = pub._parts(names)
            for parent in parents: stack.enter_context(io.Directory(source / parent, write=True))
            pub._inventory(source, names, parents, [draft_name])
            raw = self.small(source / draft_name, self.contracts.policy['manifest_bytes'], budget)
            need(a.sha(raw) == seal['draft_sha256'], 'DRAFT_INTEGRITY'); draft = self.parse(raw, self.contracts.policy['manifest_bytes'])
            descriptors = {}
            for f in seal['files']:
                cap = self.limits['document_bytes'] if f['path'] == 'docs/object.json' else self.contracts.policy['file_bytes']
                need(f['byte_length'] <= cap, 'AUTHORING_WORK_LIMIT'); total = 0; digest = hashlib.sha256()
                with io.File(source / f['path']) as handle:
                    need(handle.size() == f['byte_length'], 'PREPARED_FILE_INTEGRITY')
                    while chunk := handle.read(self.limits['chunk_bytes']): total += len(chunk); budget.charge(len(chunk), False); digest.update(chunk)
                    handle.check(); need(total == f['byte_length'] and digest.hexdigest() == f['sha256'], 'PREPARED_FILE_INTEGRITY')
                descriptors[f['path']] = (f['byte_length'], f['sha256'])
            raw_doc = self.small(source / 'docs/object.json', self.limits['document_bytes'], budget)
            doc = self.parse(raw_doc, self.limits['document_bytes']); expected = self.doc(intent, descriptors.get('payload/original.bin'))
            need(raw_doc == encoded(expected) and doc == expected, 'PREPARED_DOCUMENT_MISMATCH')
            if intent['capture'] and intent['capture']['kind'] == 'retained':
                old = intent['template']['data']['storage']; need(descriptors['payload/original.bin'] == (old['byte_length'], old['sha256']), 'ORIGINAL_DESCRIPTOR_MISMATCH')
            need(draft == self.draft(intent, doc, names), 'PREPARED_DRAFT_MISMATCH')
            a.im.Store._doc_check(self, doc, draft['operations'][0], descriptors, self.contracts.policy)
            return draft

    def prepared_result(self, intent, seal, draft, status='PREPARED'):
        manifest = {**draft, 'protocol': a.reader.PROTOCOL, 'files': seal['files']}; raw = encoded(manifest)
        need(len(raw) <= self.contracts.policy['manifest_bytes'] and len(raw)+sum(f['byte_length'] for f in seal['files'])+self.contracts.policy['ready_bytes'] <= self.contracts.policy['package_bytes'], 'AUTHORING_INPUT_LIMIT')
        doc = intent['template']
        return self.result(intent['transaction_id'], status, 'INPUT_VERIFIED' if status == 'PREPARED' else 'FINISH_PREPARATION_REQUIRED',
                           ref={k: doc[k] for k in ['object_type', 'object_id', 'revision_id']},
                           manifest_sha256=a.sha(raw), base_ref=intent['base_ref'],
                           preview=self.display_fields({'title': doc['title'], 'kind': doc['object_type']}))

    def inspect(self, tx, *, finish=False):
        budget = a.Budget(self)
        try:
            need(type(tx) is str and a.reader.UUID.fullmatch(tx), 'INVALID_TRANSACTION_ID')
            with self.session() as stack:
                journal = self.journal_root / tx
                if not io.present(journal): return self.result(tx, 'NOT_FOUND', 'INTENT_NOT_FOUND')
                stack.enter_context(io.Directory(journal, write=True))
                if not io.present(journal / 'INTENT.json'): return self.result(tx, 'INCOMPLETE', 'INTENT_NOT_PUBLISHED')
                if not io.present(journal / 'SEAL.json'): return self.result(tx, 'INCOMPLETE', 'INPUT_NOT_SEALED')
                intent, raw = self.read_intent(tx, budget); seal = self.read_seal(tx, budget); source = self.roots['source'] / tx
                marker = 'DRAFT.json' if io.present(source / 'DRAFT.json') else 'DRAFT.pending'
                draft = self.verify_source(intent, seal, raw, marker, budget)
                if marker == 'DRAFT.pending':
                    if not finish: return self.prepared_result(intent, seal, draft, 'SEALED')
                    with io.Directory(source, write=True): io.move_no_replace(source / marker, source / 'DRAFT.json'); self.event('draft_published', tx)
                return self.prepared_result(intent, seal, draft)
        except Exception as e: return self.failure(tx if type(tx) is str and a.reader.UUID.fullmatch(tx) else None, e)

    def listing(self, after=None):
        try:
            need(after is None or type(after) is str and a.reader.UUID.fullmatch(after), 'INVALID_CURSOR')
            budget = a.Budget(self)
            with self.session():
                _, count = self.usage(); need(count <= self.limits['intents'], 'AUTHORING_SCAN_LIMIT')
                ids = sorted(p.name for p in self.journal_root.iterdir() if after is None or p.name > after)
                selected = ids[:self.limits['page_items']]; items = []
                for tx in selected:
                    with io.Directory(self.journal_root / tx):
                        path = self.journal_root / tx / 'INTENT.json'
                        title = 'Прерванная подготовка'; kind = None
                        if io.present(path):
                            raw = self.small(path, self.limits['intent_record_bytes'], budget); d = self.parse(raw, self.limits['intent_record_bytes'])
                            need(d.get('protocol') == 'local-bank-object-intent/1' and d.get('transaction_id') == tx, 'INVALID_INTENT')
                            title = self.display_fields({'title': d['template']['title']})['values']['title']; kind = d['template']['object_type']
                        items.append({'transaction_id': tx, 'title': title, 'kind': kind, 'state': 'UNVERIFIED'})
                return self.result(None, 'OK', 'INTENT_PAGE', items=items, has_more=len(ids) > len(selected), next_after=selected[-1] if len(ids) > len(selected) else None)
        except Exception as e: return self.failure(None, e)

class Backend(first.Backend):
    def __init__(self, roots, **kw):
        all_roots = {k: Path(v) for k, v in roots.items()}
        need(set(all_roots) == ROLES, 'INVALID_ROOT_CONFIGURATION')
        super().__init__({k: v for k, v in all_roots.items() if k != 'object_authoring'}, **kw)
        allowed = {k: v for k, v in kw.items() if k in ['_portable_fixture', '_hook', '_limits']}
        self.objects = Workspace(all_roots, self, **allowed)
        self.identity = hashlib.sha256(encoded({k: str(v) for k, v in sorted(all_roots.items())})).hexdigest()

    def config(self):
        super().config()
        with self.objects.session(): pass

    def dispatch(self, action, args):
        w = self.objects; tx = args.get('transaction_id')
        if action == 'object_prepare': return w.prepare(args['fields'], base_ref=args.get('base_ref'), replacement=args.get('replacement'), cancel=self.cancel.is_set)
        if action == 'object_load': return w.inspect(tx)
        if action == 'object_finish': return w.inspect(tx, finish=True)
        if action == 'object_list': return w.listing(args.get('after'))
        if action == 'object_base':
            try:
                with w.session(): base, _ = w.read_base(args['ref'])
                return {'status': 'OK', 'code': 'PINNED_BASE_READY', 'data': base}
            except Exception as e: return w.failure(None, e)
        if action in ['publish', 'resume', 'inspect', 'save', 'receipt'] and type(tx) is str and a.reader.UUID.fullmatch(tx) and io.present(w.journal_root / tx):
            try:
                with w.session() as stack:
                    if action in ['publish', 'resume']:
                        stack.enter_context(io.Directory(w.journal_root / tx, write=True)); budget = a.Budget(w)
                        intent, raw = w.read_intent(tx, budget); seal = w.read_seal(tx, budget)
                        draft = w.verify_source(intent, seal, raw, 'DRAFT.json', budget)
                        expected = w.prepared_result(intent, seal, draft)['manifest_sha256']
                        return first.p.SealedPublisher(w.roots['intake'], w.roots['source'], expected=expected, **self.base.pkw).execute(action, tx)
                    return self.base.dispatch(action, args)
            except Exception as e:
                out = w.failure(tx, e); return {k: out[k] for k in ['status', 'code', 'transaction_id']}
        return super().dispatch(action, args)
