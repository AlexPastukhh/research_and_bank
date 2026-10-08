# R0 readiness — остаток решений после полного ревью

2026-10-06; R0-PLAN-REVIEW-FIXES-001. Это актуальный decision checklist, не release acceptance.
Канонические сроки: REQUIREMENTS_RELEASE_MAP.json; каноническая текущая task pointer: SESSION_STATE CURRENT_WORK_ITEM.
Owner проверки checklist — development/application contract owner по UC19; продуктовые privacy/deployment ответы — пользователь.
Статусы здесь фиксируют проверенный design checkpoint; approved runtime/evidence не подразумеваются.

| Gate | Срок | Что уже известно | Статус | Следующее проверяемое действие |
|---|---|---|---|---|
| OPEN-001 | R0 | R1 Bank/Collections/History and working title recorded | scoped_design_recorded | BANK_OPERATIONS_R1.md; actual UI R1 |
| OPEN-002 | R0 | Single personal Workspace context; future Project organizes references, Lens owns intent | scoped_design_recorded | BANK_OPERATIONS_R1.md; persisted research UX/types R2 separately |
| OPEN-003 | R0 | One personal Bank owns raw; no Project ownership or new R1 workspace schema | scoped_design_recorded | BANK_OPERATIONS_R1.md; collaboration/cross-Bank identity deferred |
| OPEN-004 | R0 | R1 BankItem/Document views, Note=Annotation; schemas prepared | partially_resolved_design | Принять соответствующий minimal boundary с evidence; richer alternatives не принимать автоматически |
| OPEN-005 | R1/R4 | R1 pinned minimal references prepared; full general registry R4 | partially_resolved_design | Проверить ссылки/reopen в R1; не блокировать их full Relation registry |
| OPEN-007 | R0 | Accepted originals/history/receipts retained; unaccepted and staging excluded; no silent cleanup | scoped_design_recorded | BANK_OPERATIONS_R1.md; runtime disk-full/cleanup/backup and real-use controls separate |
| OPEN-009 | R0/R7 | Allowlist/version/explicit converter boundaries prepared | partially_resolved_design | Принять minimal compatibility; mature Domain Pack evolution до R7 |
| OPEN-010 | R0/R6 | Disposable local SQLite lexical cache; canonical physical v1 unchanged | scoped_design_recorded | BANK_SEARCH_R1.md; runtime postings/rebuild/profile parity R1; advanced stores R6 |
| OPEN-011 | R0 | SQLite+BLOB originals/revisions/receipt и finite limits selected design | partially_resolved_design | Runtime secure importer/CAS/recovery/I-O/backup/privacy остаются отдельными критериями; не переоткрывать выбранный backend |
| OPEN-012 | R0 | Versioned read requests + semantic outputs/errors; existing write envelope preserved | scoped_design_recorded | BANK_QUERY.schema.json / BANK_OPERATIONS_R1.md; actual adapter/response byte conformance R1 |
| OPEN-015 | R0 | Local path выбран; доступ при включённом ПК достаточен для MVP | partially_resolved_user_scope | Ответ USER-AVAILABILITY-01 записан; runtime/network/UI validation отдельно, cloud/PC-off access не добавлять |
| OPEN-018 | R0/R6/R7 | Explicit fields/UTF-8 extraction cap/snapshot modes and 22 expected-ref controls | scoped_design_recorded | BANK_SEARCH_R1.md / BANK_QUERY_EXAMPLES.json; actual supported Windows/cache/UI parity R1; profiles R6/R7 |
| PLAN-SOURCE-ENTITY | R0 | Docs+Source boundary fixtures prepared; полной gate acceptance нет | partially_resolved_design | Уточнить достаточный actual-types/compatibility scope R0 и future R2/R4 contracts; schema boundary не равна runtime Source |
| PLAN-CLAIM-ENUM | R0 | Naming/legacy alias documentation resolved | resolved_documentation | Runtime alias normalizer проверить до R4; не переделывать closed naming task |
| PLAN-CLUSTERING-PARITY | R0 | TARGET TGT-020 parity resolved | resolved_documentation | R5 supported input/method/evaluation отдельная будущая работа; вопрос не блокирует R1 |
| PLAN-INVENTORY | R0 | 115 metadata + 159 triage + 45 proposals preserved; 41 pending | partially_resolved_design | Только обязательные scope clarifications перед затронутыми contracts; не принимать новые requirements/splits blanket |
| PLAN-LOCAL-WRITE | R0 | Envelope/domain schemas/SQLite limits prepared; production runtime pending | partially_resolved_design | Design decision acceptance отдельно от LW01–LW13 runtime implementation acceptance |
| PLAN-WINDOWS-PARITY | R0 | Known tests/TESTS issue; full legacy suite не принята заново | unresolved_maintenance | Maintenance copy/patch до reliance на affected baseline validators; accepted tree не править |
| COND-003 / OPEN-017 | По фактическому триггеру | Публичные материалы + возможные идеи/анализ; секреты и дополнительные AI-сервисы сейчас не планируются | user_boundary_recorded_controls_pending | Идеи/анализ не public автоматически; actual nonpublic controls до соответствующего use, не принимать privacy по одному ответу |
| COND-005/006/007 | По фактическому триггеру | Строгие claims, critical rankers и bitemporal не выключены exclusion list MVP | trigger_review_pending | Перепроверять активность перед соответствующей функцией; synthetic prototype сам по себе не включает все триггеры |

## Вопросы пользователю

USER-DATA-01, USER-PROVIDERS-01 и USER-AVAILABILITY-01 отвечены пользователем 2026-10-06 14:15:38 Asia/Bangkok. Exact answers/evidence: USER_DECISIONS_BANK_SCOPE_2026-10-06_141538.json; карточка обновлена, pending user questions=0. Ответы не спрашивать повторно.
Пользовательская неопределённость снята в текущем scope; реальные contract/runtime controls и deployment acceptance ещё проверить. Дополнительные AI providers и доступ при выключенном ПК не планируются в MVP.

## Что решается самостоятельно

P-1/P-2 — исправление pointer/deadlines без смены scope. R1 search proposal подготовить как scoped contract с expected IDs и visible unsupported modes, не как уже принятое пользовательское требование.
Самостоятельно можно выбрать implementation primitive и удобный working title, сохранить единственный personal Bank, оформить current/pinned read distinction, выделить минимальные MVP links.
Нельзя самостоятельно уменьшать обязательный TARGET, вводить shared/cloud/scheduled scope, объявлять privacy controls достаточными для неизвестных данных или отмечать gate accepted по одному probe PASS.

## Следующее действие

Ответы внесены с контекстом/evidence. Следующее действие: завершить minimal R0 operation/search/ownership/retention contracts и отдельную gate acceptance assessment.
Bounded synthetic importer разрешён как evidence gathering после подготовки его собственной карточки/inputs, без UI/research/R2 расширения и без заявления R0/R1 accepted.
R5 supported clustering question (FPR Q-2/U-3) сохранён как future prerequisite; согласовать перед clustering implementation, не задерживать R1.

## Contract completion checkpoint — 2026-10-06

R0-GATE-READINESS-001 completed in scoped design/oracle scope. Gate assessment: R0_GATE_ASSESSMENT_2026-10-06.md. Native checks/readback evidence: WORK_ITEMS/R0_GATE_READINESS_RECEIPT.json. No full integrated R0/runtime acceptance.
Current next task is R1_SECURE_INTAKE.json via SESSION_STATE; earlier next-action prose above is historical.
