# R0 readiness — остаток решений после полного ревью

2026-10-06; R0-PLAN-REVIEW-FIXES-001. Это актуальный decision checklist, не release acceptance.
Канонические сроки: REQUIREMENTS_RELEASE_MAP.json; каноническая текущая task pointer: SESSION_STATE CURRENT_WORK_ITEM.
Owner проверки checklist — development/application contract owner по UC19; продуктовые privacy/deployment ответы — пользователь.
Статусы здесь фиксируют проверенный design checkpoint; approved runtime/evidence не подразумеваются.

| Gate | Срок | Что уже известно | Статус | Следующее проверяемое действие |
|---|---|---|---|---|
| OPEN-001 | R0 | Минимальная navigation Bank/Collections/History описана в R1; working title достаточен | design_to_record | Зафиксировать UI navigation contract; название не спрашивать и не блокировать брендированием |
| OPEN-002 | R0 | Workspace/Project/Lens ownership ещё не accepted | unresolved_contract | Описать минимальный research UX до R2, сохраняя Bank независимым; не делать Project владельцем raw |
| OPEN-003 | R0 | План уже задаёт один local personal scope для MVP | design_to_record | Оформить global/scoped references/ownership; shared collaboration не добавлять |
| OPEN-004 | R0 | R1 BankItem/Document views, Note=Annotation; schemas prepared | partially_resolved_design | Принять соответствующий minimal boundary с evidence; richer alternatives не принимать автоматически |
| OPEN-005 | R1/R4 | R1 pinned minimal references prepared; full general registry R4 | partially_resolved_design | Проверить ссылки/reopen в R1; не блокировать их full Relation registry |
| OPEN-007 | R0 | Accepted original/revision retention append-only; deletion/cleanup не выбраны | partially_resolved_design | Явно задать minimal retention/orphan/error package handling и export/privacy triggers; не удалять молча |
| OPEN-009 | R0/R7 | Allowlist/version/explicit converter boundaries prepared | partially_resolved_design | Принять minimal compatibility; mature Domain Pack evolution до R7 |
| OPEN-010 | R0/R6 | SQLite canonical store выбран; search index/fields ещё не accepted | unresolved_search_contract | Подготовить minimal lexical index design и query semantics; advanced store split только при обосновании |
| OPEN-011 | R0 | SQLite+BLOB originals/revisions/receipt и finite limits selected design | partially_resolved_design | Runtime secure importer/CAS/recovery/I-O/backup/privacy остаются отдельными критериями; не переоткрывать выбранный backend |
| OPEN-012 | R0 | Envelope/write receipts prepared; публичные read/query callable contracts pending | partially_resolved_design | Описать bank/get/search/collection/receipt equivalents и ошибки перед приёмкой операций; dedicated MCP необязателен |
| OPEN-015 | R0 | Local path выбран; PC-off/offline/multi-device expectations unknown | awaiting_user_answer | USER-AVAILABILITY-01; topology не расширять без ответа |
| OPEN-018 | R0/R6/R7 | R1 indexed fields/searchable text/extraction/control queries ещё не приняты | unresolved_search_contract | Proposal: title, filename/URI, Entity aliases, Annotation body и supported retained UTF-8 text; historical/current mode и expected IDs explicit. PDF/DOCX/OCR support не обещать по MIME |
| PLAN-SOURCE-ENTITY | R0 | Docs+Source boundary fixtures prepared; полной gate acceptance нет | partially_resolved_design | Уточнить достаточный actual-types/compatibility scope R0 и future R2/R4 contracts; schema boundary не равна runtime Source |
| PLAN-CLAIM-ENUM | R0 | Naming/legacy alias documentation resolved | resolved_documentation | Runtime alias normalizer проверить до R4; не переделывать closed naming task |
| PLAN-CLUSTERING-PARITY | R0 | TARGET TGT-020 parity resolved | resolved_documentation | R5 supported input/method/evaluation отдельная будущая работа; вопрос не блокирует R1 |
| PLAN-INVENTORY | R0 | 115 metadata + 159 triage + 45 proposals preserved; 41 pending | partially_resolved_design | Только обязательные scope clarifications перед затронутыми contracts; не принимать новые requirements/splits blanket |
| PLAN-LOCAL-WRITE | R0 | Envelope/domain schemas/SQLite limits prepared; production runtime pending | partially_resolved_design | Design decision acceptance отдельно от LW01–LW13 runtime implementation acceptance |
| PLAN-WINDOWS-PARITY | R0 | Known tests/TESTS issue; full legacy suite не принята заново | unresolved_maintenance | Maintenance copy/patch до reliance на affected baseline validators; accepted tree не править |
| COND-003 / OPEN-017 | По фактическому триггеру | Data/external exposure boundary unknown | awaiting_user_answer | USER-DATA-01 и USER-PROVIDERS-01 до corresponding real-data/provider use |
| COND-005/006/007 | По фактическому триггеру | Строгие claims, critical rankers и bitemporal не выключены exclusion list MVP | trigger_review_pending | Перепроверять активность перед соответствующей функцией; synthetic prototype сам по себе не включает все триггеры |

## Вопросы пользователю

USER-DATA-01, USER-PROVIDERS-01 и USER-AVAILABILITY-01 записаны в WORK_ITEMS/R0_GATE_READINESS.json с why/proposal/autonomy/blocking scope. Ответы pending, не приписаны пользователю.
Они не блокируют synthetic/local contract preparation. Они блокируют только соответствующие реальные data/provider/deployment promises.

## Что решается самостоятельно

P-1/P-2 — исправление pointer/deadlines без смены scope. R1 search proposal подготовить как scoped contract с expected IDs и visible unsupported modes, не как уже принятое пользовательское требование.
Самостоятельно можно выбрать implementation primitive и удобный working title, сохранить единственный personal Bank, оформить current/pinned read distinction, выделить минимальные MVP links.
Нельзя самостоятельно уменьшать обязательный TARGET, вводить shared/cloud/scheduled scope, объявлять privacy controls достаточными для неизвестных данных или отмечать gate accepted по одному probe PASS.

## Следующее действие

Внести ответы пользователя в readiness card с контекстом и evidence; завершить minimal R0 operation/search/ownership/retention contracts и отдельную gate acceptance assessment.
Bounded synthetic importer разрешён как evidence gathering после подготовки его собственной карточки/inputs, без UI/research/R2 расширения и без заявления R0/R1 accepted.
R5 supported clustering question (FPR Q-2/U-3) сохранён как future prerequisite; согласовать перед clustering implementation, не задерживать R1.
