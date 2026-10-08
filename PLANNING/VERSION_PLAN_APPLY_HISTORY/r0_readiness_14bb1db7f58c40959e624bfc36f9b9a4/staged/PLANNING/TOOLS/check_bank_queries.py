"""Read-only synthetic contract oracle; no Bank connection, importer or runtime API."""
from pathlib import Path
import base64, hashlib, json, re, unicodedata
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / 'PLANNING/CONTRACTS'
FIELDS = ['title', 'filename', 'uri', 'aliases', 'body', 'content']
TYPES = ['Asset', 'Entity', 'Annotation', 'Collection']
TEXT_LIMIT = 4 * 1024 * 1024
class QueryError(ValueError): pass
def need(ok, code):
    if not ok: raise QueryError(code)
def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'INVALID_REQUEST')
            result[key] = value
        return result
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(QueryError('INVALID_REQUEST')))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise QueryError('INVALID_REQUEST') from exc
def tokens(value):
    value = unicodedata.normalize('NFC', unicodedata.normalize('NFC', value).casefold())
    out, word = [], ''
    for char in value:
        category = unicodedata.category(char)[0]
        if category in 'LN' or (category == 'M' and word): word += char
        else:
            if word: out.append(word)
            word = ''
    if word: out.append(word)
    return set(out)
def validate_request(request, schema):
    if isinstance(request, dict):
        if request.get('protocol') != 'local-bank-query/1': raise QueryError('UNSUPPORTED_PROTOCOL')
        need(not list(Draft202012Validator(schema).iter_errors(request)), 'INVALID_REQUEST')
    else: raise QueryError('INVALID_REQUEST')
    if request['operation'] == 'bank.search':
        text = request['query']
        try: size = len(text.encode('utf-8'))
        except UnicodeError as exc: raise QueryError('INVALID_REQUEST') from exc
        need(size <= 1024, 'LIMIT_EXCEEDED')
        terms = tokens(text)
        need(bool(terms), 'INVALID_REQUEST')
        need(len(terms) <= 32, 'LIMIT_EXCEEDED')
    return request
def payload(item):
    source = item['payload']
    if source['kind'] == 'utf8': return source['text'].encode('utf-8')
    if source['kind'] == 'base64': return base64.b64decode(source['data'], validate=True)
    if source['kind'] == 'repeat_ascii':
        need(len(source['char']) == 1 and source['char'].isascii(), 'INVALID_FIXTURE')
        return source['char'].encode() * source['count']
    raise QueryError('INVALID_FIXTURE')
def key(doc): return (doc['object_type'], doc['object_id'], doc['revision_id'])
def ref(doc): return dict(zip(['object_type', 'object_id', 'revision_id'], key(doc)))
def build_corpus(fixture):
    bank_schema = json.loads((CONTRACTS/'BANK_TYPES.schema.json').read_text(encoding='utf-8'))
    validate = Draft202012Validator(bank_schema, format_checker=FormatChecker())
    rows = []
    for item in fixture['revisions']:
        doc = item['document']
        need(not list(validate.iter_errors(doc)), 'OBJECT_SCHEMA')
        need(doc['object_type'] in TYPES, 'UNSUPPORTED_TYPE')
        values = {field: [] for field in FIELDS}
        values['title'] = [doc['title']]
        state, data, kind = 'not_applicable', doc['data'], doc['object_type']
        if kind == 'Entity': values['aliases'] = data['aliases']
        if kind == 'Annotation': values['body'] = [data['body']]
        if kind == 'Asset':
            storage = data['storage']
            if storage['mode'] == 'locator':
                state = 'locator_only'; values['uri'] = [storage['uri']]
            else:
                raw = payload(item)
                need(len(raw) == storage['byte_length'] and hashlib.sha256(raw).hexdigest() == storage['sha256'], 'INTEGRITY_ERROR')
                if storage['original_filename'] is not None: values['filename'] = [storage['original_filename']]
                if storage['media_type'] != 'text/plain': state = 'unsupported_media'
                elif len(raw) > TEXT_LIMIT: state = 'size_limit'
                else:
                    try: values['content'] = [raw.decode('utf-8')]; state = 'indexed'
                    except UnicodeDecodeError: state = 'invalid_utf8'
        rows.append(dict(document=doc, commit_sequence=item['commit_sequence'], coverage=state,
                         terms={f: set().union(*(tokens(v) for v in vals)) for f, vals in values.items()}))
    need(len({key(x['document']) for x in rows}) == len(rows), 'DUPLICATE_REVISION')
    return rows
def search(request, rows, schema, cache=None):
    validate_request(request, schema)
    need(request['operation'] == 'bank.search', 'UNSUPPORTED_MODE')
    maximum = max((x['commit_sequence'] for x in rows), default=0)
    snapshot = maximum if request['snapshot_sequence'] is None else request['snapshot_sequence']
    need(snapshot <= maximum, 'SNAPSHOT_NOT_AVAILABLE')
    if cache is not None:
        need(cache['available'], 'INDEX_UNAVAILABLE')
        need(cache['unicode_data_version'] == unicodedata.unidata_version and
             cache['profile_id'] == 'r1-lexical/1' and cache['normalization_version'] == 1, 'INDEX_PROFILE_MISMATCH')
        need(cache['complete_through_sequence'] >= snapshot, 'INDEX_NOT_READY')
    corpus = [x for x in rows if x['commit_sequence'] <= snapshot]
    if request['revisions_mode'] == 'current':
        heads = {}
        for row in corpus:
            oid = row['document']['object_id']
            if oid not in heads or row['commit_sequence'] > heads[oid]['commit_sequence']: heads[oid] = row
        corpus = list(heads.values())
    corpus = [x for x in corpus if x['document']['object_type'] in request['object_types']]
    query = tokens(request['query']); matches = []
    coverage = {s: 0 for s in ['indexed','locator_only','unsupported_media','invalid_utf8','size_limit','not_applicable']}
    for row in corpus:
        coverage[row['coverage']] += 1
        available = set().union(*(row['terms'][f] for f in request['fields']))
        if query <= available:
            matches.append(dict(ref=ref(row['document']), commit_sequence=row['commit_sequence'],
                                matched_fields=[f for f in FIELDS if f in request['fields'] and row['terms'][f] & query],
                                extraction_state=row['coverage']))
    matches.sort(key=lambda x: (-x['commit_sequence'], x['ref']['object_id'], x['ref']['revision_id']))
    start, count = request['offset'], request['limit']
    return dict(hits=matches[start:start+count], total_matches=len(matches),
                has_more=start+count < len(matches), snapshot_sequence=snapshot, coverage=coverage,
                profile_id='r1-lexical/1', normalization_version=1, unicode_data_version=unicodedata.unidata_version)
def get(request, rows, schema):
    validate_request(request, schema)
    need(request['operation'] in ['bank.get','collection.get'], 'UNSUPPORTED_MODE')
    known = [x for x in rows if x['document']['object_id'] == request['object_id']]
    need(bool(known), 'OBJECT_NOT_FOUND')
    need(all(x['document']['object_type'] == request['object_type'] for x in known), 'TYPE_MISMATCH')
    if request['selector']['mode'] == 'pinned':
        candidates = [x for x in known if x['document']['revision_id'] == request['selector']['revision_id']]
        need(bool(candidates), 'REVISION_NOT_FOUND')
        return candidates[0]['document']
    return max(known, key=lambda x: x['commit_sequence'])['document']
def check_all():
    schema = json.loads((CONTRACTS/'BANK_QUERY.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    fixture = json.loads((CONTRACTS/'BANK_QUERY_EXAMPLES.json').read_text(encoding='utf-8'))
    rows = build_corpus(fixture)
    from check_bank_contracts import validate_documents
    validate_documents([], profile='R1', accepted=[x['document'] for x in rows])
    for case in fixture['queries']:
        actual = search(case['request'], rows, schema)
        need([x['ref'] for x in actual['hits']] == case['expected_refs'], 'EXPECTED_REFS:'+case['id'])
        need(actual['total_matches'] == case['expected_total'], 'EXPECTED_TOTAL:'+case['id'])
        need(sum(actual['coverage'].values()) == case['expected_corpus_count'], 'EXPECTED_COVERAGE:'+case['id'])
        if 'expected_coverage' in case: need(actual['coverage'] == case['expected_coverage'], 'EXPECTED_COVERAGE_STATES:'+case['id'])
    return schema, fixture, rows
if __name__ == '__main__':
    _, f, rows = check_all()
    print(json.dumps(dict(status='PASS', scope='synthetic_contract_oracle_only',
                         revisions=len(rows), control_queries=len(f['queries']), unicode_data_version=unicodedata.unidata_version)))
