"""Validate and render the planning overlay, without accepting any release."""
import argparse
import json
from collections import Counter
import re
from pathlib import Path

KINDS = {
    'CORE_INTENT': 'cross_cutting', 'ANTI_GOAL': 'cross_cutting',
    'MVP_REQUIRED': 'staged', 'TARGET_REQUIRED': 'staged',
    'CONDITIONAL_REQUIRED': 'conditional', 'FUTURE_OPPORTUNITY': 'opportunity_unassigned',
    'OPEN_DECISION': 'decision_gate', 'EXPERIMENT': 'evaluation_gate',
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def has_text(value):
    return isinstance(value, str) and bool(value.strip())

def validate(plan, requirements):
    src = {r['id']: r for r in requirements}
    entries = plan['requirements']
    require(bool(src) and len(src) == len(requirements), 'Duplicate/empty source inventory')
    require(plan['source_requirement_count'] == len(requirements), 'Source requirement count drift')
    require(len(entries) == len({e['requirement_id'] for e in entries}) == len(src), 'Duplicate/missing plan entries')
    require(set(src) == {e['requirement_id'] for e in entries}, 'Requirement ID coverage drift')
    milestones = {m['id']: m for m in plan['milestones']}
    require(len(milestones) == len(plan['milestones']), 'Duplicate milestones')
    rank = {m['id']: i for i, m in enumerate(plan['milestones'])}
    for m in plan['milestones']:
        require(m['state'] == 'planned_not_implemented', m['id'] + ': not a planned milestone')
        require(all(d in milestones and rank[d] < rank[m['id']] for d in m['dependencies']), m['id'] + ': invalid/cyclic dependency order')
        after = m.get('sequencing_after')
        require(after is None or (after in milestones and rank[after] < rank[m['id']]), m['id'] + ': invalid/cyclic sequencing_after')

    for key, expected in (('mvp_checkpoint', 'R2'), ('stable_mvp_checkpoint', 'R3')):
        checkpoint = plan[key]
        require(checkpoint['milestone'] == expected and expected in milestones, key + ': wrong milestone')
        for stream in ('system', 'application'):
            field = stream + '_version'
            require(checkpoint[field] == milestones[expected][field], key + ': ' + field + ' drift')
    required_ids = plan['mvp_checkpoint']['required_ids']
    require(len(required_ids) == len(set(required_ids)), 'Duplicate MVP checkpoint IDs')
    require(set(required_ids) == {r['id'] for r in requirements if r['status'] == 'MVP_REQUIRED'}, 'MVP checkpoint coverage drift')

    for e in entries:
        label = e['requirement_id']
        r = src[label]
        require((e['classification'], e['statement_snapshot']) == (r['status'], r['statement']), label + ': source snapshot drift')
        require(e['delivery_kind'] == KINDS[r['status']], label + ': delivery kind drift')
        require(e['owner'] in ('system', 'application', 'shared'), label + ': invalid owner')
        for stream, excluded_owner in (('system', 'application'), ('application', 'system')):
            value = e[stream + '_work']
            require(value is None if e['owner'] == excluded_owner else has_text(value), label + ': invalid ' + stream + '_work')
        slices = e['slices']
        if e['delivery_kind'] == 'staged':
            require(bool(slices), label + ': missing staged delivery')
            ids = [s['milestone'] for s in slices]
            require(all(i in milestones for i in ids), label + ': unknown slice milestone')
            require(len(ids) == len(set(ids)) and ids == sorted(ids, key=rank.get), label + ': duplicate/unordered slices')
            for s in slices:
                m = milestones[s['milestone']]
                require(has_text(s['scope']) and s['state'] == 'planned_not_implemented', label + ': invalid slice scope/state')
                for stream, excluded_owner in (('system', 'application'), ('application', 'system')):
                    involved = e['owner'] != excluded_owner
                    field = stream + '_version'
                    require(s[field] == (m[field] if involved else None), label + ': ' + field + ' drift')
                    value = s.get(stream + '_scope')
                    require(has_text(value) if involved else value is None, label + ': invalid ' + stream + '_scope')
            if r['status'] == 'MVP_REQUIRED':
                require(rank[slices[-1]['milestone']] <= rank[plan['mvp_checkpoint']['milestone']], label + ': MVP delivery after checkpoint')
        else:
            require(not slices, label + ': unexpected staged slices')
        if r['status'] == 'CONDITIONAL_REQUIRED':
            require(e['trigger'] == r['trigger'] and has_text(e['activation_gate']), label + ': conditional gate drift')
        for k in ('applies_from', 'decision_before_milestone', 'evaluation_before_milestone'):
            require(e.get(k) is None or e[k] in milestones, label + ': invalid ' + k)
        # A declared early deadline must not disappear behind a later/null field.
        # This checks explicit 'до Rn'/'before Rn' declarations, not full prose semantics.
        declared = re.findall(r'\b(?:до|before)\s+(R[0-9]+)\b', e.get('decision_scope', ''), flags=re.I)
        if declared:
            require(e['delivery_kind'] == 'decision_gate', label + ': decision deadline on non-decision entry')
            declared = [d.upper() for d in declared]
            require(all(d in milestones for d in declared), label + ': unknown declared decision deadline')
            first = e.get('decision_before_milestone')
            require(first in milestones and rank[first] <= min(rank[d] for d in declared), label + ': structured decision deadline later than declared scope')
        gates = e.get('decision_checkpoints', [])
        if gates:
            require(e['delivery_kind'] == 'decision_gate', label + ': unexpected decision checkpoints')
            ids = [g['before'] for g in gates]
            require(all(i in milestones for i in ids), label + ': unknown decision checkpoint')
            require(len(ids) == len(set(ids)) and ids == sorted(ids, key=rank.get), label + ': duplicate/unordered decision checkpoints')
            require(e['decision_before_milestone'] == ids[0], label + ': first decision checkpoint drift')
            require(all(has_text(g['scope']) for g in gates), label + ': empty decision checkpoint scope')
    for item in plan['supplemental_planning_items']:
        require(item['before'] in milestones, item['id'] + ': unknown preparation milestone')
        require(set(item.get('requirement_refs', [])) <= set(src), item['id'] + ': unknown requirement reference')
    neg = next(e for e in entries if e['requirement_id'] == 'OPP-017')
    require(neg['classification'] == 'TARGET_REQUIRED' and all(rank[s['milestone']] > rank[plan['stable_mvp_checkpoint']['milestone']] for s in neg['slices']), 'OPP-017 must remain TARGET outside MVP')
    require(plan['streams']['system']['current_accepted_version'] == '1.11.0', 'Accepted baseline drift')
    require(plan['streams']['application']['current_version'] is None, 'Planning does not implement an app')
    return dict(Counter(e['delivery_kind'] for e in entries))

def esc(x):
    return str(x or '—').replace('|', '\\|').replace('\n', ' ')

def table(headers, rows):
    return ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] + ['| ' + ' | '.join(esc(x) for x in row) + ' |' for row in rows]

def render(p):
    lines = ['# Версии исследовательской системы и приложения Bank', '',
        'Дата: 2026-10-05. Это план распределения требований; будущие версии не реализованы и не приняты. Номера плановые, календарных сроков нет.', '',
        '**Система** — методология, типы и исследовательские контракты, правила provenance/history/quality, роли исполнителей и доменные процедуры.',
        '**Приложение** — локальное хранение, validated intake/операции, каталог/индексы, проекции, UI и восстановление.', '',
        'Принятая система остаётся **1.11.0**. Для Universal Bank заведена отдельная плановая линия **2.x**: старые VERSION.json, baseline и phase acceptance не переписываются. Рабочего приложения Bank пока нет; проба обмена файлами не является приложением 0.1.', '',
        'Выбран транспорт **ChatGPT → Desktop Commander → локальные файлы → приложение**. GitHub вспомогателен. Production-формат и внутренняя БД остаются решениями R0; экспериментальный READY.json не принимается автоматически как формат продукта.', '',
        '## Связки версий', '']
    lines += table(['Этап', 'Система', 'Приложение', 'Результат'], [[m['id'], m['system_version'], m['application_version'], m['title']] for m in p['milestones']])
    lines += ['', '**R1 / приложение 0.1** — часть MVP. **R2 / система 2.0 + приложение 0.2** — первый полный MVP. **R3 / приложение 1.0** — стабильность того же MVP, без обязательного включения всего TARGET.', '',
        '## Правила распределения', '']
    lines += ['- ' + x for x in p['policies']]
    lines += ['', '## Состав и приёмка каждого этапа', '']
    owner = {'system': 'система', 'application': 'приложение', 'shared': 'оба'}
    for m in p['milestones']:
        lines += ['### ' + m['id'] + ' — ' + m['title'], '', m['scope'], '',
            'Зависимости контрактов: ' + (', '.join(m['dependencies']) or 'нет') + '. Очередность: после ' + (m.get('sequencing_after') or 'подготовки') + '. Связь с A–F: ' + m['phase'] + '.', '',
            'Требования этой версии (scope каждой строки ограничен указанной частью):', '']
        rows = []
        for e in p['requirements']:
            for s in e['slices']:
                if s['milestone'] == m['id']:
                    rows.append([e['requirement_id'], owner[e['owner']], s['scope'], s['system_scope'], s['application_scope']])
        if rows:
            lines += table(['ID', 'Ответственность', 'Часть требования', 'Изменение системы', 'Работа приложения'], rows)
        else:
            lines += ['Новых этапных требований нет. Применяются инварианты, решения R0 и повторная приёмка существующего scope.']
        if m['id'] == 'R0':
            decisions = [e['requirement_id'] for e in p['requirements'] if e.get('decision_before_milestone') == 'R0']
            preparation = [x['id'] for x in p['supplemental_planning_items'] if x['before'] == 'R0']
            lines += ['', 'Checklist R0 также включает решения ' + ', '.join(decisions) + ' и подготовительные работы ' + ', '.join(preparation) + '. Полные scopes приведены ниже; две строки поставки не исчерпывают R0.']
        lines += ['', 'Приёмка:', ''] + ['- ' + g for g in m['acceptance']] + ['']
    lines += ['## Условные требования — без обещанного номера версии', '', 'Проверяются перед каждым релизом. Активный триггер нельзя отложить до R8 или будущего номера.', '']
    lines += table(['ID', 'Ответственность', 'Триггер', 'Когда включить', 'Что добавить'], [[e['requirement_id'], owner[e['owner']], e['trigger'], e['activation_gate'], e['statement_snapshot']] for e in p['requirements'] if e['delivery_kind'] == 'conditional'])
    lines += ['', '## Решения до соответствующего этапа', '', 'Срок решения не означает срок поставки функции. Локальный путь уже выбран, но остаток OPEN-011/012/015 не закрыт этим выбором.', '']
    decision_rows = []
    for e in p['requirements']:
        if e['delivery_kind'] == 'decision_gate':
            gates = e.get('decision_checkpoints') or [{'before': e['decision_before_milestone'], 'scope': e['decision_scope']}]
            decision_rows += [[e['requirement_id'], owner[e['owner']], g['before'] or 'по триггеру', g['scope']] for g in gates]
    lines += table(['ID', 'Ответственность', 'До этапа', 'Что решить'], decision_rows)
    lines += ['', '## Эксперименты и возможности', '', 'Они не превращены в обязательные релизы. Сначала evidence/disposition, затем назначение версии.', '']
    lines += table(['ID', 'Тип', 'Оценка / предпосылка'], [[e['requirement_id'], e['delivery_kind'], e.get('evaluation_gate') or e.get('prerequisite_context')] for e in p['requirements'] if e['delivery_kind'] in ('evaluation_gate', 'opportunity_unassigned')])
    lines += ['', '## Инварианты и запреты во всех релевантных версиях', '']
    lines += table(['ID', 'Класс', 'Ограничение'], [[e['requirement_id'], e['classification'], e['statement_snapshot']] for e in p['requirements'] if e['delivery_kind'] == 'cross_cutting'])
    lines += ['', '## Сохранившиеся пробелы и обязательные подготовительные работы', '']
    for x in p['supplemental_planning_items']:
        lines += ['- **' + x['id'] + '** — ' + x['statement'] + ' До: ' + x['before'] + '.']
    lines += ['', 'Полнота этой карты — **' + str(p['source_requirement_count']) + ' текущих ID**. Она не доказывает завершение нормализации всех требований или перенос triage всех 159 backlog-пунктов; эти работы остаются в R0. Clustering, claim enums и Source/Entity не считаются автоматически исправленными.', '',
        '## Старый development plan', '']
    lines += ['- Phase ' + x['legacy_phase'] + ': ' + x['disposition'] for x in p['legacy_plan_crosswalk']]
    lines += ['', '## Совместимость, история и проверка', '',
        'Каждый новый релиз фиксирует версии формата/schema, поддерживаемые read/write версии, migration/backup/restore и поведение неизвестных полей. Major/minor номер сам по себе не гарантирует совместимость.', '',
        'У требования не один флаг done: учитываются system contribution, app contribution, acceptance evidence и scope каждой slice. Scope до последней slice частичный. CORE/ANTI всегда ограничения; OPP/EXP/OPEN/COND не считаются реализованными по наличию строки в плане.', '',
        'Проверка карты: `python PLANNING/TOOLS/release_plan.py --requirements DRAFT_NOTES/REQUIREMENTS_MAP.json`. Генерация этого документа: та же команда с `--render`.', '',
        'Машинная карта: [REQUIREMENTS_RELEASE_MAP.json](REQUIREMENTS_RELEASE_MAP.json). Старый план: `freelance_research_system_feature_architecture_red_tests/REFERENCE/DEVELOPMENT_PLAN_vNext.md`.', '',
        '## Ограничения сохранения', '', p['remote_save_state'], '', p['verification_scope'], '']
    return '\n'.join(lines)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    planning = Path(__file__).resolve().parents[1]
    ap.add_argument('--plan', type=Path, default=planning / 'REQUIREMENTS_RELEASE_MAP.json')
    ap.add_argument('--requirements', type=Path)
    ap.add_argument('--render', action='store_true')
    args = ap.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    candidate = planning.parent / 'DRAFT_NOTES' / 'REQUIREMENTS_MAP.json'
    src_path = args.requirements or (candidate if candidate.exists() else planning.parent / 'expected_requirements.json')
    src = json.loads(src_path.read_text(encoding='utf-8'))
    requirements = src['requirements'] if isinstance(src, dict) else src
    counts = validate(plan, requirements)
    document = render(plan)
    target = args.plan.parent / 'VERSION_ROADMAP.md'
    if args.render:
        target.write_text(document, encoding='utf-8')
    elif target.exists():
        require(target.read_text(encoding='utf-8') == document, 'Generated roadmap drift; rerender')
    print(json.dumps({'status': 'PASS', 'requirements': len(requirements), 'counts': counts}, ensure_ascii=False))
