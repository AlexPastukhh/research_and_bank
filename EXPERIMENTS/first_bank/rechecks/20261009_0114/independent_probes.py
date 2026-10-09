"""Read-only real-config check and owned headless review probes; no Tk window."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--real-config', action='store_true')
    args = parser.parse_args()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo / 'EXPERIMENTS/first_bank'))
    import integration as i
    import runtime
    import app
    import test_first_bank as fixtures
    records = []
    started = time.monotonic()

    def check(name, passed, **details):
        records.append({'id': name, 'status': 'PASS' if passed else 'FAIL', **details})
        if not passed:
            raise AssertionError(name)

    fixture = fixtures.Tests('test_01_utf8_split_bom_crlf_exact_export_interior_search')
    fixture.setUp()
    try:
        roots = fixture.roots
        backend = fixture.backend
        source = fixture.temp / 'independent-review.TXT'
        exact = b'\xef\xbb\xbf' + 'First\r\nсередина independentinterior 🙂\r\n'.encode('utf-8')
        source.write_bytes(exact)
        forms = [
            {'kind': 'file', 'path': str(source), 'title': 'File without the search word'},
            {'kind': 'url', 'uri': 'https://example.invalid/review-locator', 'title': 'Locator'},
            {'kind': 'note', 'body': 'Independent note notebodyreview\r\n🙂', 'title': 'Note'},
        ]
        prepared = []
        for form in forms:
            out = backend.dispatch('author_prepare', {'fields': form})
            check('prepare_' + form['kind'], out['status'] == 'PREPARED', actual=out['status'])
            prepared.append(out)
        source.unlink()
        for form, out in zip(forms, prepared):
            pub = backend.dispatch('publish', {'transaction_id': out['transaction_id']})
            saved = backend.dispatch('save', {'transaction_id': out['transaction_id']})
            check('publish_save_' + form['kind'], pub['status'] == 'PUBLISHED' and saved['status'] == 'ACCEPTED' and saved['diagnostic_attempt']['availability'] == 'available')
        with i.im.Store(roots['bank']) as store:
            connection = store._connect(False, _allow_recovery=False)
            try:
                counts = [connection.execute('SELECT count(*) FROM ' + table).fetchone()[0] for table in ['commits', 'revisions', 'accepted_receipts']]
            finally:
                connection.close()
        check('independent_SQL_cardinality', counts == [3, 3, 3], counts=counts)
        check('index_rebuild', backend.dispatch('rebuild', {})['status'] == 'BUILT')
        for word, fields, out in [('independentinterior', ['content'], prepared[0]), ('notebodyreview', ['body'], prepared[2])]:
            found = backend.dispatch('search', {'query': word, 'fields': fields, 'object_types': ['Asset', 'Annotation'], 'revisions_mode': 'current'})
            check('search_' + fields[0], found['status'] == 'OK' and [hit['ref'] for hit in found['data']['hits']] == [out['ref']])
        exported = backend.dispatch('export', {'ref': prepared[0]['ref']})
        raw = Path(exported['data']['original']['path']).read_bytes()
        check('original_exact_after_source_deleted', raw == exact and hashlib.sha256(raw).hexdigest() == exported['data']['original']['sha256'])
        url = backend.dispatch('export', {'ref': prepared[1]['ref']})
        check('locator_no_fetch_claim', url['data']['availability'] == 'locator_only' and url['data']['uri'] == forms[1]['uri'])
        kwargs = {}
        if os.name != 'nt':
            kwargs = {'_portable_fixture': True, '_controller_kwargs': {'_transport': fixtures.creation.old.ct.portable_read, '_store_factory': fixtures.creation.old.ct.PortableStore}, '_publisher_kwargs': {'_portable_fixture': True}}
        reopened = i.Backend(roots, context='independent-reopen', **kwargs)
        receipts = []
        for out in prepared:
            result = reopened.dispatch('receipt', {'transaction_id': out['transaction_id'], 'expected_manifest_sha256': out['manifest_sha256']})
            receipts.append(result['status'] == 'OK' and result['data']['receipt']['manifest_sha256'] == out['manifest_sha256'])
        replay = reopened.dispatch('save', {'transaction_id': prepared[0]['transaction_id']})
        check('reopen_receipts_and_exact_replay', all(receipts) and replay['status'] == 'REPLAY')
        copy_result = runtime.safeguard(roots, portable=os.name != 'nt')
        check('backup_consistent_copy', copy_result['status'] == 'OK' and copy_result['snapshot_sequence'] == 3 and copy_result['verified_commits'] == 3, observed_status=copy_result['status'])

        # Exercise the actual poll method without constructing widgets or a Tk root.
        class Value:
            def __init__(self): self.value = ''
            def set(self, value): self.value = value
        class Root:
            def after(self, delay, callback): return 'headless-scheduled'
        class Bridge:
            def __init__(self, result): self.result = result
            def poll(self): return self.result
        window = app.Window.__new__(app.Window)
        window.root = Root()
        window.model = i.p.Model()
        window.flow = i.Flow('review-context', 'review-root')
        window.background = True
        window.events = []
        window.status = Value()
        window.sync_status = Value()
        window.tx = Value()
        window.set_busy = lambda busy: None
        window.drive = lambda: None
        pinned = copy.deepcopy(prepared[0]['ref'])
        window.model.selected = pinned
        detail = {'status': 'OK', 'data': {'pinned_detail': 'keep'}, 'code': 'DETAIL'}
        window.model.result = copy.deepcopy(detail)
        observation = {'status': 'OK', 'code': 'BANK_OBSERVED', 'context': 'review-context', 'root_generation': 'review-root', 'identity': [1, 2, 'bank'], 'token': [3, str(uuid.uuid4())], 'cache_ready': True}
        window.model.begin('observe', {}, None)
        window.bridge = Bridge(observation)
        app.Window.poll(window)
        check('actual_poll_preserves_pinned_detail', window.model.result == detail and window.model.selected == pinned)

        flow = i.Flow('review-context', 'review-root')
        flow.apply('observe', observation)
        flow.apply('rebuild', {'status': 'ERROR', 'code': 'OWNED_TRANSIENT_FAILURE'})
        before = flow.notice
        flow.apply('rebuild', {'status': 'BUILT', 'code': 'INDEX_BUILT'})
        flow.apply('observe', observation)
        check('counterexample_stale_index_failure_notice', flow.index_ready is True and 'недоступен' in flow.notice, finding='F-P-001', old_notice=before, resulting_notice=flow.notice, index_ready=flow.index_ready)
    finally:
        fixture.tearDown()

    if args.real_config:
        base = runtime.default_base()
        config_before = (base / 'config.json').read_bytes()
        database_before = hashlib.sha256((base / 'bank/bank.sqlite').read_bytes()).hexdigest()
        cfg = runtime.load(base)
        actual = i.Backend(cfg['roots'], context=cfg['config_id'])
        actual.config()
        observed = actual.dispatch('observe', {})
        check('real_config_readonly_reopen', observed['status'] == 'OK' and len(cfg['roots']) == 7 and (base / 'config.json').read_bytes() == config_before and hashlib.sha256((base / 'bank/bank.sqlite').read_bytes()).hexdigest() == database_before, real_bank_modified=False)

    source_paths = ['EXPERIMENTS/first_bank/app.py', 'EXPERIMENTS/first_bank/integration.py', 'EXPERIMENTS/first_bank/runtime.py', 'EXPERIMENTS/draft_authoring/authoring.py', 'EXPERIMENTS/draft_authoring/LIMITS.json', 'PLANNING/WORK_ITEMS/R1_OBJECT_AUTHORING.json']
    result = {'record_kind': 'first_bank_independent_recheck', 'run_id': str(uuid.uuid4()), 'at': i.im.now(), 'platform': sys.platform, 'success': True, 'checks': records, 'elapsed_seconds': round(time.monotonic() - started, 3), 'GUI_created_or_automated': False, 'runtime_code_changed': False, 'limitations': ['Headless paths only; human visual/adoption gate remains pending', 'Owned synthetic material, no actual user Bank imports', 'Counterexample success means the display defect was independently reproduced'], 'source_sha256': {p: hashlib.sha256((repo / p).read_bytes()).hexdigest() for p in source_paths}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'success': True, 'checks': len(records), 'confirmed_findings': ['F-P-001'], 'output': str(args.output)}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
