"""Check the active documentation overlay; does not accept runtime or product scope."""
import argparse
import json
import re
from pathlib import Path


def verify(root):
    def read(path):
        return (root / path).read_text(encoding='utf-8-sig')

    def obj(path):
        return json.loads(read(path))

    def check(condition, message):
        if not condition:
            raise ValueError(message)

    source = obj('DRAFT_NOTES/REQUIREMENTS_MAP.json')
    ids = {r['id'] for r in source['requirements']}
    plan = obj('docs/OUTCOME_MAP.json')
    covered = [i for group in plan['groups'].values() for i in group]
    check(len(ids) == len(source['requirements']) == plan['source_count'] == 115,
          'Source ID/count drift')
    check(len(covered) == len(set(covered)) and set(covered) == ids,
          'Outcome groups lose or duplicate requirements')
    check(set(plan['source_overrides']) <= ids, 'Unknown override ID')
    check(plan['status'] == 'candidate' and plan['transaction_status'] == 'TRANSACTION OPEN',
          'Candidate silently committed')
    check(source['current_interpretation_path'] == 'docs/OUTCOME_MAP.json', 'Authority drift')
    check(obj('DRAFT_NOTES/INDEX.json')['active_documentation'] == 'docs/README.md',
          'Entry index drift')
    legacy = obj('PLANNING/REQUIREMENTS_RELEASE_MAP.json')
    check(legacy['state'] == 'historical_release_allocation', 'Legacy release plan still active')
    check(read('PLANNING/VERSION_ROADMAP.md').startswith('# Историческое распределение'),
          'Historical renderer lost authority boundary')
    scenarios = read('DRAFT_NOTES/research_bank_desired_scenarios.md')
    old = re.findall(r'^#### (SC-\d{3}) —', scenarios, re.M)
    check(len(old) == 74 and set(old) == {f'SC-{i:03}' for i in range(1, 75)},
          'Legacy scenario coverage drift')
    extra = re.findall(r'^## (SC-\d{3}) —', read('docs/SCENARIOS.md'), re.M)
    check(extra == plan['new_scenarios'] == ['SC-075', 'SC-076'], 'New scenario ID drift')
    state = read('PLANNING/SESSION_STATE.md')
    ptr = re.findall(r'^CURRENT_WORK_ITEM: \[[^\]]+\]\(([^)]+)\)', state, re.M)
    check(ptr == ['WORK_ITEMS/NEXT_GENERIC_DATA_PROBE.json'], 'Current pointer ambiguous')
    card = obj('PLANNING/' + ptr[0])
    check(card['status'] == 'candidate_ready_for_card_review_not_started',
          'Future experiment silently marked executed')
    check(card['scenario_refs'] == extra, 'Card/scenario drift')
    pages = list((root / 'docs').glob('*.md')) + [root / 'PLANNING/HISTORY/README.md']
    links = 0
    for path in pages:
        for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^\s)]+)\)', path.read_text(encoding='utf-8')):
            if ':' in target or target.startswith('#'):
                continue
            target = target.split('#')[0]
            check((path.parent / target).is_file(), f'Broken link: {path.name} -> {target}')
            links += 1
    check('docs/README.md' in read('README.md'), 'Root navigation missing')
    return {'status': 'PASS', 'requirements': len(ids), 'legacy_scenarios': len(old),
            'new_scenarios': len(extra), 'local_links': links, 'runtime_acceptance': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    print(json.dumps(verify(parser.parse_args().root), ensure_ascii=False))
