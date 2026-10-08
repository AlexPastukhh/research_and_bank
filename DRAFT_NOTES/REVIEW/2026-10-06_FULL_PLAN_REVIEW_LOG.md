# Review Log — FPR-20261006

Дата: 2026-10-06, Asia/Bangkok. Объект: весь актуальный vNext-план Universal Bank в `C:\Users\alexa\research_and_bank`: master/115 IDs, две линии версий R0–R8, gates/приёмка/зависимости, backlog/proposals, workflow и подготовленные R1 write/types/SQLite contracts. Не только последний ответ/SQLite-шаг; не аудит всей принятой v1.11.

## Итог

Основное распределение R0–R8 выдержало review. Три подтверждённые локальные проблемы в управлении планом; P-1/P-2 оставлены для правки, P-3 актуализируется bookkeeping assessment этого review. Нет установленного разрушительного runtime дефекта, отсутствующего mandatory delivery класса или dependency cycle. R0/R1 и следующие релизы не приняты.

## Подтверждённые проблемы

| ID | Статус | Суть и влияние |
|---|---|---|
| P-1 | confirmed / open | DEVELOPMENT_WORKFLOW current pointer и handoff шаблон направляют на completed R0_SOURCE_ENTITY; новый чат может повторить завершённую задачу вместо продолжения. Исправить источник текущего указателя/исторический пример |
| P-2 | confirmed / open | OPEN-005 prose требует early links до R1, structured deadline только R4; OPEN-006 требует supported temporal expectations до R5, structured deadline null. Checklist по полям теряет ранние gates; не доказана пропажа самих MVP links. Добавить явные checkpoints без смены delivery scope |
| P-3 | confirmed at review / ledger reassessed | DF-MRQ-003 current finding/assessment предшествует schema_version=1.0.0 и PLANNING validators/generator. Сохранить историю, отметить выполненные components и отдельно оставить D-3; не выдавать partial validation за formal compatibility acceptance |

Полные causal scenarios/repros/requirements/evidence: `PLANNING/FULL_PLAN_REVIEW_2026-10-06.md`. Ledger IDs: FPR-20261006-P01/P02/P03.

## Неопределённости

- U-1: полный remaining R0 gate scope/answers/evidence ещё не сведен в единый checklist. Blocking для соответствующего acceptance; bounded synthetic implementation сама по себе не принимает R0. 41 proposals не имеют blanket approval.
- U-2: production importer, Windows secure reads/TOCTOU, full CAS/replay/public queries/UI, disk-full/I/O и hardware durability не проверены; LW01–LW13 pending. Blocking runtime acceptance, non-blocking review/synthetic development.
- U-3: exact supported inputs/method/quality/examples для semantic/topic/mechanics clustering R5 неизвестны. Цикл R5→R7 не доказан: text/structured/annotated features могут быть доступны раньше. Вернуться до R5 implementation acceptance.
- U-4: searchable retained fields/text, supported extraction и expected IDs/control queries R1 не выбраны до конца. Вернуться до R1 search acceptance; raw-save prototype допустим отдельно.

## Что подтверждено

115 ID/statements/classifications covered; 11 MVP slices завершаются не позже R2; граф dependencies+sequencing ацикличен. R1 partial / R2 full / R3 stable MVP согласованы. CORE/ANTI/active COND не заменены TARGET. OPP-017 TARGET вне MVP. Source≠Entity/optional refs, frozen history, provenance/derived layers согласованы на проверенном scope. Все 159 backlog bullets сохранены; 45 proposals: 41 pending, 2 consolidated, 2 superseded. Design/static/mechanism evidence не объявляет runtime acceptance.

Семь повторных native commands exit 0: inventory, release map, inventory/release regressions (3+3 groups), bank conformance/regressions (5 groups), SQLite probe (8 groups). Independent script отдельно пересчитал coverage/versions/graph/proposal states и воспроизвёл P-1/P-2/P-3. Точные outputs и source hashes: `2026-10-06_FULL_PLAN_REVIEW_CHECKS.json`.

## User Assistance / External Dependencies

UA-1: до первых реальных private/sensitive данных пользователь должен указать класс первых материалов и допустимые внешние model/provider endpoints; сами файлы не нужны. Это определяет COND-003/OPEN-017 controls. Требуется решение пользователя при переходе к private use; non-blocking текущему review/synthetic development, blocking соответствующему acceptance. Сейчас доступа/файлов для этого review не требуется.

## Deferred / Follow-up

- D-1: large-media/performance/concurrent backup не измерены; не менять bounded R1 backend без данных. Trigger: повышение limits, bulk/COND-002, большая DB, постоянные writes. Иначе latency/disk pressure/незавершаемый backup; измерить поддерживаемый storage profile.
- D-2: vNext UC/contract port, generated whole-system views и baseline Windows parity — перед новым release acceptance/reliance на affected validation. Сейчас baseline не менять; иначе возможна несогласованность routing/map/release и ошибочный перенос legacy PASS.
- D-3: schema_version и baseline tooling уже есть; formal registry/overlay schema и migration/consumer compatibility при изменении формата/внешнем consumer/CI/API. Иначе consumer может неверно читать новый формат. Связь: DF-MRQ-003 reassessment/P-3.
- D-4: generated roadmap может быть удобнее с current checkpoint/resolution/remaining view. Пока intent view достаточно; вернуться, если он становится единственным progress dashboard. Иначе повторные решения/работы. Не заводить второй editable status owner.

## Questions / Proposals

- Q-1: продолжение после review. Proposal — исправить P-1/P-2, свести R0 blockers с evidence, затем новая bounded synthetic importer card; оставить acceptance unaccepted до выполнения критериев. Высокая уместность самостоятельного решения; не меняет need/scope/сложность кардинально. Non-blocking review/prototype, blocking соответствующему acceptance. Правки плана не выполнены этим review.
- Q-2: какой supported clustering outcome R5 принимать? Proposal — versioned доступные features, annotated/control examples, membership/history/explanation criteria, explicit insufficient data. Желательно согласование конкретного domain/method: может влиять на desired mechanics outcome. Non-blocking R1, blocking R5 clustering acceptance; mandatory TARGET не уменьшать самостоятельно.
- Private-data вопрос/Proposal/категория и blocking status — каноническая UA-1 выше.

## Ограничения

Нет production Bank/UI/importer, hardware power-off/TOCTOU/disk-full acceptance, human relevance/performance/cost evidence, полноценного нового chat journey. Не выполнена full legacy suite и не закрыт known Windows tests/TESTS issue. Baseline hashes проверяют неизменность во время review, не повтор всей baseline acceptance. Tool PASS не доказывает всё: P-1/P-2/P-3 проходят обычные validators. Исторические записи не сочтены current defects только из-за старой даты.

## Сохранение

Этот log добавляется новым файлом; прежние reviews сохранены. Записываются report/evidence, assessment history FINDINGS.json, индекс REVIEW/README.md и append checkpoint SESSION_STATE.md. Readback/source guards/backup/baseline preservation подтверждаются `PLANNING/FULL_PLAN_REVIEW_2026-10-06_SAVE_RECEIPT.json`. До успешного receipt нельзя заявлять log сохранённым.
