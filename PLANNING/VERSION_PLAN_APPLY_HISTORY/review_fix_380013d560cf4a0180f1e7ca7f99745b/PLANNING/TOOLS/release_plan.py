"""Validate and render the planning overlay, without accepting any release."""
import argparse
import json
from collections import Counter
from pathlib import Path

KINDS = {
    'CORE_INTENT': 'cross_cutting', 'ANTI_GOAL': 'cross_cutting',
    'MVP_REQUIRED': 'staged', 'TARGET_REQUIRED': 'staged',
    'CONDITIONAL_REQUIRED': 'conditional', 'FUTURE_OPPORTUNITY': 'opportunity_unassigned',
    'OPEN_DECISION': 'decision_gate', 'EXPERIMENT': 'evaluation_gate',
}

def validate(plan, requirements):
    src = {r['id']: r for r in requirements}
    entries = plan['requirements']
    assert len(src) == len(requirements) == 115
    assert len(entries) == len({e['requirement_id'] for e in entries}) == 115
    assert set(src) == {e['requirement_id'] for e in entries}
    milestones = {m['id']: m for m in plan['milestones']}
    assert len(milestones) == len(plan['milestones'])
    rank = {m['id']: i for i, m in enumerate(plan['milestones'])}
    for m in plan['milestones']:
        assert m['state'] == 'planned_not_implemented'
        assert all(d in milestones and rank[d] < rank[m['id']] for d in m['dependencies'])
    for e in entries:
        r = src[e['requirement_id']]
        assert (e['classification'], e['statement_snapshot']) == (r['status'], r['statement']), e['requirement_id']
        assert e['delivery_kind'] == KINDS[r['status']]
        assert e['owner'] in ('system', 'application', 'shared')
        assert e['system_work'] if e['owner'] != 'application' else e['system_work'] is None
        assert e['application_work'] if e['owner'] != 'system' else e['application_work'] is None
        slices = e['slices']
        if e['delivery_kind'] == 'staged':
            assert slices
            ids = [s['milestone'] for s in slices]
            assert len(ids) == len(set(ids)) and ids == sorted(ids, key=rank.get)
            for s in slices:
                m = milestones[s['milestone']]
                assert s['scope'] and s['state'] == 'planned_not_implemented'
                assert s['system_version'] == (None if e['owner'] == 'application' else m['system_version'])
                assert s['application_version'] == (None if e['owner'] == 'system' else m['application_version'])
            if r['status'] == 'MVP_REQUIRED':
                assert rank[slices[-1]['milestone']] <= rank['R2']
        else:
            assert not slices, e['requirement_id']
        if r['status'] == 'CONDITIONAL_REQUIRED':
            assert e['trigger'] == r['trigger'] and e['activation_gate']
        for k in ('applies_from', 'decision_before_milestone', 'evaluation_before_milestone'):
            if e.get(k) is not None:
                assert e[k] in milestones
    assert set(plan['mvp_checkpoint']['required_ids']) == {r['id'] for r in requirements if r['status'] == 'MVP_REQUIRED'}
    assert len(plan['mvp_checkpoint']['required_ids']) == 11
    neg = next(e for e in entries if e['requirement_id'] == 'OPP-017')
    assert neg['classification'] == 'TARGET_REQUIRED' and all(rank[s['milestone']] > rank['R3'] for s in neg['slices'])
    assert plan['streams']['system']['current_accepted_version'] == '1.11.0'
    assert plan['streams']['application']['current_version'] is None
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
                    rows.append([e['requirement_id'], owner[e['owner']], s['scope'], s.get('system_scope', e['system_work']), s.get('application_scope', e['application_work'])])
        if rows:
            lines += table(['ID', 'Ответственность', 'Часть требования', 'Изменение системы', 'Работа приложения'], rows)
        else:
            lines += ['Новых этапных требований нет. Применяются инварианты, решения R0 и повторная приёмка существующего scope.']
        lines += ['', 'Приёмка:', ''] + ['- ' + g for g in m['acceptance']] + ['']
    lines += ['## Условные требования — без обещанного номера версии', '', 'Проверяются перед каждым релизом. Активный триггер нельзя отложить до R8 или будущего номера.', '']
    lines += table(['ID', 'Ответственность', 'Триггер', 'Когда включить', 'Что добавить'], [[e['requirement_id'], owner[e['owner']], e['trigger'], e['activation_gate'], e['statement_snapshot']] for e in p['requirements'] if e['delivery_kind'] == 'conditional'])
    lines += ['', '## Решения до соответствующего этапа', '', 'Срок решения не означает срок поставки функции. Локальный путь уже выбран, но остаток OPEN-011/012/015 не закрыт этим выбором.', '']
    lines += table(['ID', 'Ответственность', 'До этапа', 'Что решить'], [[e['requirement_id'], owner[e['owner']], e['decision_before_milestone'] or 'по триггеру', e['decision_scope']] for e in p['requirements'] if e['delivery_kind'] == 'decision_gate'])
    lines += ['', '## Эксперименты и возможности', '', 'Они не превращены в обязательные релизы. Сначала evidence/disposition, затем назначение версии.', '']
    lines += table(['ID', 'Тип', 'Оценка / предпосылка'], [[e['requirement_id'], e['delivery_kind'], e.get('evaluation_gate') or e.get('prerequisite_context')] for e in p['requirements'] if e['delivery_kind'] in ('evaluation_gate', 'opportunity_unassigned')])
    lines += ['', '## Инварианты и запреты во всех релевантных версиях', '']
    lines += table(['ID', 'Класс', 'Ограничение'], [[e['requirement_id'], e['classification'], e['statement_snapshot']] for e in p['requirements'] if e['delivery_kind'] == 'cross_cutting'])
    lines += ['', '## Сохранившиеся пробелы и обязательные подготовительные работы', '']
    for x in p['supplemental_planning_items']:
        lines += ['- **' + x['id'] + '** — ' + x['statement'] + ' До: ' + x['before'] + '.']
    lines += ['', 'Полнота этой карты — **115 текущих ID**. Она не доказывает завершение нормализации всех требований или перенос triage всех 159 backlog-пунктов; эти работы остаются в R0. Clustering, claim enums и Source/Entity не считаются автоматически исправленными.', '',
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
        assert target.read_text(encoding='utf-8') == document, 'Generated roadmap drift; rerender'
    print(json.dumps({'status': 'PASS', 'requirements': len(requirements), 'counts': counts}, ensure_ascii=False))
