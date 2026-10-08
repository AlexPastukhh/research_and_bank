# Версии исследовательской системы и приложения Bank

Дата: 2026-10-05. Это план распределения требований; будущие версии не реализованы и не приняты. Номера плановые, календарных сроков нет.

**Система** — методология, типы и исследовательские контракты, правила provenance/history/quality, роли исполнителей и доменные процедуры.
**Приложение** — локальное хранение, validated intake/операции, каталог/индексы, проекции, UI и восстановление.

Принятая система остаётся **1.11.0**. Для Universal Bank заведена отдельная плановая линия **2.x**: старые VERSION.json, baseline и phase acceptance не переписываются. Рабочего приложения Bank пока нет; проба обмена файлами не является приложением 0.1.

Выбран транспорт **ChatGPT → Desktop Commander → локальные файлы → приложение**. GitHub вспомогателен. Production-формат и внутренняя БД остаются решениями R0; экспериментальный READY.json не принимается автоматически как формат продукта.

## Связки версий

| Этап | Система | Приложение | Результат |
| --- | --- | --- | --- |
| R0 | 2.0.0-alpha.1 | — | Контракты и граница MVP |
| R1 | 2.0.0-alpha.2 | 0.1.0 | Локальный Bank — частичный MVP |
| R2 | 2.0.0 | 0.2.0 | Первый полный MVP |
| R3 | 2.0.1 | 1.0.0 | Стабильный MVP |
| R4 | 2.1.0 | 1.1.0 | Источники и качество исследования |
| R5 | 2.2.0 | 1.2.0 | Время, проекции и аналитика |
| R6 | 2.3.0 | 1.3.0 | Идентичность и расширенный поиск |
| R7 | 2.4.0 | 1.4.0 | Мультимодальность и доменные профили |
| R8 | 2.5.0 | 1.5.0 | Watch и повторное наблюдение |

**R1 / приложение 0.1** — часть MVP. **R2 / система 2.0 + приложение 0.2** — первый полный MVP. **R3 / приложение 1.0** — стабильность того же MVP, без обязательного включения всего TARGET.

## Правила распределения

- Номера будущих версий — плановые обозначения, без сроков и оценок. Распределение по версиям не меняет классы CORE/MVP/TARGET/COND/OPP/EXP/OPEN/ANTI.
- Для каждого требования отдельно указано участие системы и приложения. Общее требование не готово, если выполнена только одна сторона. Методологические требования используют хранилище общих объектов.
- Версия в этапе требования означает планируемую поставку и проверку только указанной части, а не факт реализации.
- R2: система 2.0.0 + приложение 0.2.0 — полный MVP. Приложение 0.1.0 — частичный MVP; 1.0.0 — стабильная версия того же MVP.
- Система 2.0 — новая линия универсальных контрактов. Каталог принятой 1.11, VERSION.json, 25 UC и прежние записи приёмки не переименовываются.
- CORE/ANTI действуют во всех релевантных релизах. Полные возможности, стоящие за инвариантами, поставляются по этапам MVP/TARGET.
- COND включается по триггеру перед затронутой возможностью, даже в MVP. Приватность и строгие проверки важных claims нельзя отложить до произвольной будущей версии.
- OPP/EXP не имеют обещанного релиза. Предпосылки и этапы оценки не означают повышение статуса. OPEN имеет сроки принятия решений, а не обещания готовых функций.
- У широких TARGET-требований есть частичные этапы и последний планируемый этап полного покрытия. Частичная поставка не помечается как полное выполнение.
- Первый транспорт — Commander и локальные файлы. Push, dedicated MCP, облачная БД и прямые provider APIs не обязательны для локального обмена.
- Формат данных, миграции, индекс/БД, media/private/backup остаются решениями R0. Экспериментальный READY.json не принимается автоматически как формат Bank.
- Совместимость релизов доказывается поддерживаемыми версиями чтения/записи схем и проверкой обновления. Сам номер major/minor не гарантирует совместимость.
- Очередность релизов отделена от зависимостей контрактов. Например, разработка semantic search не обязана ждать всей аналитики; изменение порядка требует проверки затронутых зависимостей.

## Состав и приёмка каждого этапа

### R0 — Контракты и граница MVP

Intent parity, Source≠Entity, IDs/версии/эпистемические слои, минимальный validated local handoff и acceptance. UI ещё нет.

Зависимости контрактов: нет. Очередность: после подготовки. Связь с A–F: A.

Требования этой версии (scope каждой строки ограничен указанной частью):

| ID | Ответственность | Часть требования | Изменение системы | Работа приложения |
| --- | --- | --- | --- | --- |
| MVP-010 | система | Стратегия/роли в contracts. | Контракт/метод/проверка: Стратегия/роли в contracts. | — |
| TGT-024 | оба | Минимальные boundaries, без giant GenericObject. | Контракт/метод/проверка: Минимальные boundaries, без giant GenericObject. | Дизайн границы приложения; выпуска и реализации ещё нет. |

Приёмка:

- Приняты версии минимальных типов/операций, local intake contract, ownership и восстановление; все blocking design вопросы записаны и отвечены.
- Master/JSON/MVP не расходятся; provider internals unknown не выдумываются; результат — контракт, не runtime release.

### R1 — Локальный Bank — частичный MVP

Сохранение файлов/URL/notes/objects без исследования; Bank/Collections/History, exact/full-text, local intake с видимыми ошибками.

Зависимости контрактов: R0. Очередность: после R0. Связь с A–F: B.

Требования этой версии (scope каждой строки ограничен указанной частью):

| ID | Ответственность | Часть требования | Изменение системы | Работа приложения |
| --- | --- | --- | --- | --- |
| MVP-001 | оба | IDs/Asset/Entity/Annotation/Collection, basic provenance/use links. | Контракт/метод/проверка: IDs/Asset/Entity/Annotation/Collection, basic provenance/use links. | Реализация/хранение/UI: IDs/Asset/Entity/Annotation/Collection, basic provenance/use links. |
| MVP-002 | оба | Материалы без исследования. | Контракт/метод/проверка: Материалы без исследования. | Реализация/хранение/UI: Материалы без исследования. |
| MVP-003 | приложение | Basic Bank UI/search/history. | — | Реализация/хранение/UI: Basic Bank UI/search/history. |
| MVP-009 | оба | bank/collection save/get/search. | Контракт/метод/проверка: bank/collection save/get/search. | Реализация/хранение/UI: bank/collection save/get/search. |
| TGT-009 | оба | Stable saved-item identity, не full entity resolution. | Контракт/метод/проверка: Stable saved-item identity, не full entity resolution. | Реализация/хранение/UI: Stable saved-item identity, не full entity resolution. |
| TGT-010 | оба | Exact/full-text, required by MVP-003. | Контракт/метод/проверка: Exact/full-text, required by MVP-003. | Реализация/хранение/UI: Exact/full-text, required by MVP-003. |
| TGT-022 | приложение | Bank/Collections/History. | — | Реализация/хранение/UI: Bank/Collections/History. |
| TGT-023 | оба | IDs/save/get/explain existing material. | Контракт/метод/проверка: IDs/save/get/explain existing material. | Реализация/хранение/UI: IDs/save/get/explain existing material. |

Приёмка:

- Сохранённый через Commander материал автоматически появляется в приложении и открывается без research.
- Незавершённая/ошибочная запись даёт видимый статус; повторное сохранение не создаёт дубль.
- Работа не требует push, dedicated MCP или direct provider APIs; basic links/provenance/history присутствуют.

### R2 — Первый полный MVP

Lens, Source/Policy, frozen RunSpec/Run/ResultSet/Occurrence, наблюдения и три end-to-end proof journeys.

Зависимости контрактов: R1. Очередность: после R1. Связь с A–F: B + reduced C/D.

Требования этой версии (scope каждой строки ограничен указанной частью):

| ID | Ответственность | Часть требования | Изменение системы | Работа приложения |
| --- | --- | --- | --- | --- |
| MVP-001 | оба | Observation, run links и research history; полный MVP-001. | Контракт/метод/проверка: Observation, run links и research history; полный MVP-001. | Реализация/хранение/UI: Observation, run links и research history; полный MVP-001. |
| MVP-004 | оба | Source→Entity опционально; SourceRoute не Entity. | Контракт/метод/проверка: Source→Entity опционально; SourceRoute не Entity. | Реализация/хранение/UI: Source→Entity опционально; SourceRoute не Entity. |
| MVP-005 | оба | Персистентный Lens. | Контракт/метод/проверка: Персистентный Lens. | Реализация/хранение/UI: Персистентный Lens. |
| MVP-006 | оба | Без обязательной полной Recipe/Route registry. | Контракт/метод/проверка: Без обязательной полной Recipe/Route registry. | Реализация/хранение/UI: Без обязательной полной Recipe/Route registry. |
| MVP-007 | оба | Tracked ResearchRun. | Контракт/метод/проверка: Tracked ResearchRun. | Реализация/хранение/UI: Tracked ResearchRun. |
| MVP-008 | оба | Историческая выдача и repeat-safe save. | Контракт/метод/проверка: Историческая выдача и repeat-safe save. | Реализация/хранение/UI: Историческая выдача и repeat-safe save. |
| MVP-009 | оба | lens/run/result operations; полный MVP-009. | Контракт/метод/проверка: lens/run/result operations; полный MVP-009. | Реализация/хранение/UI: lens/run/result operations; полный MVP-009. |
| MVP-010 | система | Применение в research journeys. | Контракт/метод/проверка: Применение в research journeys. | — |
| MVP-011 | оба | Full MVP checkpoint, без full Trend/Health/mechanics similarity. | Контракт/метод/проверка: Full MVP checkpoint, без full Trend/Health/mechanics similarity. | Реализация/хранение/UI: Full MVP checkpoint, без full Trend/Health/mechanics similarity. |
| TGT-012 | оба | Reduced comparable two-run/history proof. | Контракт/метод/проверка: Reduced comparable two-run/history proof. | Реализация/хранение/UI: Reduced comparable two-run/history proof. |
| TGT-013 | оба | Run history и reduced observation comparison, не пять builders. | Контракт/метод/проверка: Run history и reduced observation comparison, не пять builders. | Реализация/хранение/UI: Run history и reduced observation comparison, не пять builders. |
| TGT-022 | приложение | Research/Sources/runs. | — | Реализация/хранение/UI: Research/Sources/runs. |
| TGT-023 | оба | Compare/research/reuse. | Контракт/метод/проверка: Compare/research/reuse. | Реализация/хранение/UI: Compare/research/reuse. |
| TGT-024 | оба | Freelance/game proof adapters. | Контракт/метод/проверка: Freelance/game proof adapters. | Реализация/хранение/UI: Freelance/game proof adapters. |

Приёмка:

- Все 11 MVP_REQUIRED, CORE/ANTI и уже активные COND выполнены.
- Два comparable freelance-прогона сохраняют наблюдения/provenance; not_seen не становится closed.
- Game save→seed→research→save→reuse и independent image/file save проходят через публичные операции приложения.
- RunSpec и membership/order/reasons старых результатов immutable; query не запускает hidden refresh.
- Mechanics similarity, full Trend/Health, formal Recipe/Route registries и scheduler не блокируют приёмку.

### R3 — Стабильный MVP

Стабилизация принятого MVP: recovery, совместимость, backup/export/restore, ошибки и повторная полная приёмка. Новые TARGET-функции не обязательны.

Зависимости контрактов: R2. Очередность: после R2. Связь с A–F: B acceptance/hardening.

Требования этой версии (scope каждой строки ограничен указанной частью):

Новых этапных требований нет. Применяются инварианты, решения R0 и повторная приёмка существующего scope.

Приёмка:

- MVP journeys проходят на retained/reopened data и поддерживаемых обновлениях.
- Заявленные backup/export/restore/recovery проверены; ошибки и supported-format policy видимы.
- Версия 1.0 означает stable MVP, а не полный TARGET; новые capabilities не добавляются ради номера.

### R4 — Источники и качество исследования

Typed relations, Routes, Recipes, Capability/Executor, evidence/claims, counter-search, verifier context, genealogy/retrieval provenance.

Зависимости контрактов: R2. Очередность: после R3. Связь с A–F: C.

Требования этой версии (scope каждой строки ограничен указанной частью):

| ID | Ответственность | Часть требования | Изменение системы | Работа приложения |
| --- | --- | --- | --- | --- |
| TGT-001 | оба | Full Relation layer; basic provenance links уже R1/R2. | Контракт/метод/проверка: Full Relation layer; basic provenance links уже R1/R2. | Реализация/хранение/UI: Full Relation layer; basic provenance links уже R1/R2. |
| TGT-005 | оба | SourceRoute registry. | Контракт/метод/проверка: SourceRoute registry. | Реализация/хранение/UI: SourceRoute registry. |
| TGT-006 | оба | Recipe registry/reuse. | Контракт/метод/проверка: Recipe registry/reuse. | Реализация/хранение/UI: Recipe registry/reuse. |
| TGT-008 | оба | Reusable executor abstractions без обязательных direct APIs. | Контракт/метод/проверка: Reusable executor abstractions без обязательных direct APIs. | Реализация/хранение/UI: Reusable executor abstractions без обязательных direct APIs. |
| TGT-014 | оба | Claim→evidence со всеми согласованными status enums. | Контракт/метод/проверка: Claim→evidence со всеми согласованными status enums. | Реализация/хранение/UI: Claim→evidence со всеми согласованными status enums. |
| TGT-015 | система | Сохраняемые counter-search outputs; storage через shared evidence contracts. | Контракт/метод/проверка: Сохраняемые counter-search outputs; storage через shared evidence contracts. | — |
| TGT-016 | система | Independent verification process. | Контракт/метод/проверка: Independent verification process. | — |
| TGT-017 | оба | Full admissibility model; basic distinction с R0. | Контракт/метод/проверка: Full admissibility model; basic distinction с R0. | Реализация/хранение/UI: Full admissibility model; basic distinction с R0. |
| TGT-018 | оба | Source genealogy. | Контракт/метод/проверка: Source genealogy. | Реализация/хранение/UI: Source genealogy. |
| TGT-019 | оба | Retrieval process model; opaque details остаются unknown. | Контракт/метод/проверка: Retrieval process model; opaque details остаются unknown. | Реализация/хранение/UI: Retrieval process model; opaque details остаются unknown. |
| TGT-022 | приложение | Evidence и Discover context. | — | Реализация/хранение/UI: Evidence и Discover context. |

Приёмка:

- Claim enums согласованы; support links/admissibility/genealogy не выдают AI summary за независимый raw source.
- Counter-search/verifier outputs сохраняются с scope/limitations; Recipe/Route changes не изменяют frozen past RunSpec.
- Retrieval metadata только по доступным данным; неизвестные детали провайдера остаются unknown.

### R5 — Время, проекции и аналитика

Events/MetricObservation, lifecycle/as-of, Current/Changes/Trend/Interpretation/Health и coverage/comparability-aware аналитика.

Зависимости контрактов: R2, R4. Очередность: после R4. Связь с A–F: C.

Требования этой версии (scope каждой строки ограничен указанной частью):

| ID | Ответственность | Часть требования | Изменение системы | Работа приложения |
| --- | --- | --- | --- | --- |
| TGT-002 | оба | Event objects. | Контракт/метод/проверка: Event objects. | Реализация/хранение/UI: Event objects. |
| TGT-003 | оба | Structured MetricObservation. | Контракт/метод/проверка: Structured MetricObservation. | Реализация/хранение/UI: Structured MetricObservation. |
| TGT-010 | оба | Temporal/as-of/change search. | Контракт/метод/проверка: Temporal/as-of/change search. | Реализация/хранение/UI: Temporal/as-of/change search. |
| TGT-012 | оба | First/last seen/reopen/reappearance/as-of; formal bitemporal conditional. | Контракт/метод/проверка: First/last seen/reopen/reappearance/as-of; formal bitemporal conditional. | Реализация/хранение/UI: First/last seen/reopen/reappearance/as-of; formal bitemporal conditional. |
| TGT-013 | оба | Full generalized query products. | Контракт/метод/проверка: Full generalized query products. | Реализация/хранение/UI: Full generalized query products. |
| TGT-020 | оба | Descriptive target analytics as data permits; lifecycle activates COND-009. | Контракт/метод/проверка: Descriptive target analytics as data permits; lifecycle activates COND-009. | Реализация/хранение/UI: Descriptive target analytics as data permits; lifecycle activates COND-009. |
| TGT-022 | приложение | Current/Changes/Trends/Health. | — | Реализация/хранение/UI: Current/Changes/Trends/Health. |

Приёмка:

- Пять query products строятся из runtime truth; stale/partial/insufficient/not-comparable явные.
- Method/unit/scope/coverage не склеиваются скрыто; raw points/derived stats/interpretations имеют lineage.
- Lifecycle/survival включает COND-009; formal bitemporal только с активным COND-007; clustering gap решён отдельно до реализации.

### R6 — Идентичность и расширенный поиск

Merge/split/corrections, semantic/graph/evidence-lineage/hybrid search, versioned textual representations и объяснимые профили.

Зависимости контрактов: R1, R2, R4. Очередность: после R5. Связь с A–F: D.

Требования этой версии (scope каждой строки ограничен указанной частью):

| ID | Ответственность | Часть требования | Изменение системы | Работа приложения |
| --- | --- | --- | --- | --- |
| TGT-004 | оба | Versioned textual representations. | Контракт/метод/проверка: Versioned textual representations. | Реализация/хранение/UI: Versioned textual representations. |
| TGT-009 | оба | Full target correction без переписывания выдач. | Контракт/метод/проверка: Full target correction без переписывания выдач. | Реализация/хранение/UI: Full target correction без переписывания выдач. |
| TGT-010 | оба | Structured/semantic/graph/evidence-lineage/hybrid. | Контракт/метод/проверка: Structured/semantic/graph/evidence-lineage/hybrid. | Реализация/хранение/UI: Structured/semantic/graph/evidence-lineage/hybrid. |
| TGT-011 | оба | Supported explainable profiles. | Контракт/метод/проверка: Supported explainable profiles. | Реализация/хранение/UI: Supported explainable profiles. |

Приёмка:

- Merge/split не переписывают retained ResultOccurrences; index rebuilding воспроизводим из canonical truth.
- Ranking/representations versioned и не canonical truth; modes assessed on tasks.
- COND-006 quality sets активируются по триггеру; неподдерживаемые modes/unknown features раскрыты.

### R7 — Мультимодальность и доменные профили

OCR/captions/hashes/media/domain-structural search, OPP-017 positive/negative examples, personal relevance и зрелые Domain Packs.

Зависимости контрактов: R6. Очередность: после R6. Связь с A–F: D.

Требования этой версии (scope каждой строки ограничен указанной частью):

| ID | Ответственность | Часть требования | Изменение системы | Работа приложения |
| --- | --- | --- | --- | --- |
| TGT-004 | оба | OCR/captions/perceptual hashes/domain feature vectors. | Контракт/метод/проверка: OCR/captions/perceptual hashes/domain feature vectors. | Реализация/хранение/UI: OCR/captions/perceptual hashes/domain feature vectors. |
| TGT-010 | оба | Example/multimodal/domain-structural; full target breadth. | Контракт/метод/проверка: Example/multimodal/domain-structural; full target breadth. | Реализация/хранение/UI: Example/multimodal/domain-structural; full target breadth. |
| TGT-011 | оба | Domain/media dimensions; full target profiles. | Контракт/метод/проверка: Domain/media dimensions; full target profiles. | Реализация/хранение/UI: Domain/media dimensions; full target profiles. |
| TGT-021 | оба | Explainable personalization. | Контракт/метод/проверка: Explainable personalization. | Реализация/хранение/UI: Explainable personalization. |
| TGT-023 | оба | Find-similar. | Контракт/метод/проверка: Find-similar. | Реализация/хранение/UI: Find-similar. |
| TGT-024 | оба | Developed packs + apps/news proofs. | Контракт/метод/проверка: Developed packs + apps/news proofs. | Реализация/хранение/UI: Developed packs + apps/news proofs. |
| OPP-017 | оба | Full TARGET capability, explicitly outside MVP; EXP-004/COND-006. | Контракт/метод/проверка: Full TARGET capability, explicitly outside MVP; EXP-004/COND-006. | Реализация/хранение/UI: Full TARGET capability, explicitly outside MVP; EXP-004/COND-006. |

Приёмка:

- Supported multimodal/domain profiles имеют human relevance evaluation.
- OPP-017 поддерживает dimensions/soft vs hard/explanations и сравнение с baseline; improvement не объявлено заранее.
- Freelance/games/apps/news расширяются packs; personal relevance остаётся projection.

### R8 — Watch и повторное наблюдение

Saved Watch всех target scopes, ручной запуск и сохранённый intent/cadence. Unattended automation — отдельный COND-001 gate.

Зависимости контрактов: R2, R4, R5, R7. Очередность: после R7. Связь с A–F: E interactive.

Требования этой версии (scope каждой строки ограничен указанной частью):

| ID | Ответственность | Часть требования | Изменение системы | Работа приложения |
| --- | --- | --- | --- | --- |
| TGT-007 | оба | All target watch scopes; unattended требует COND-001. | Контракт/метод/проверка: All target watch scopes; unattended требует COND-001. | Реализация/хранение/UI: All target watch scopes; unattended требует COND-001. |
| TGT-022 | приложение | Watch; full target surface coverage. | — | Реализация/хранение/UI: Watch; full target surface coverage. |
| TGT-023 | оба | Watch; full target action set. | Контракт/метод/проверка: Watch; full target action set. | Реализация/хранение/UI: Watch; full target action set. |

Приёмка:

- Watch покрывает все заявленные scopes без дублирования semantics; user-triggered run сохраняет history/frozen spec.
- Unattended expectation включает COND-001 до выпуска, а statistical mass alerts — COND-010.
- Обязательный Watch не понижается до opportunity; scheduler не обещается без executor readiness.

## Условные требования — без обещанного номера версии

Проверяются перед каждым релизом. Активный триггер нельзя отложить до R8 или будущего номера.

| ID | Ответственность | Триггер | Когда включить | Что добавить |
| --- | --- | --- | --- | --- |
| COND-001 | оба | User expects unattended or scheduled watches/research. | До first unattended release; R8 не обещает background без gate. | Add scheduler/background jobs/retries/idempotency/budget/alerts/automatable executors. |
| COND-002 | приложение | Data volume exceeds practical interactive/small-store operation. | До bulk/streaming, без fixed version. | Add bulk ingestion/queues/object or columnar storage/incremental projections/index lifecycle/retention policies. |
| COND-003 | оба | Authenticated/private/sensitive sources or data are stored/queried. | До first such data, может быть R0/R1. | Add secret management, ACL/auth boundaries, encryption, retention/deletion/export and provider exposure controls. |
| COND-004 | оба | Multi-user/shared collaboration enters scope. | До first collaborative feature, без fixed version. | Add workspace ownership, roles/ACLs, shared/personal boundaries, audit/conflict semantics. |
| COND-005 | система | Claims become high-stakes or materially drive decisions. | До такого research, включая MVP при trigger. | Apply stricter primary-source/counter-search/independent-verification/source-genealogy/uncertainty gates. |
| COND-006 | оба | Similarity/ranking is product-critical or models/rankers/providers change regularly. | До такого ranking; likely R6/R7, может раньше. | Maintain evaluation sets/relevance judgments/regression runs. |
| COND-007 | оба | Need to distinguish what was true then from what the system knew then across backfills/corrections. | До relevant history feature; R5 as-of не обещает formal bitemporal. | Implement formal valid-time/system-time semantics. |
| COND-008 | оба | Automation, bulk volume, cost/latency, exact reproducibility, missing connector capability, reliability, governance, or direct streaming makes ChatGPT-mediated execution insufficient. | До feature requiring direct integration; не обязателен без trigger. | Add direct provider/API/backend integration. |
| COND-009 | оба | Lifecycle/survival analysis is implemented. | Activate/test before relevant R5 analytics. | Handle right/left/interval censoring and source-missingness explicitly. |
| COND-010 | оба | Large numbers of statistical alerts/tests create meaningful false-positive risk. | До таких alerts, не каждый manual Watch. | Use alert calibration/multiple-comparison controls when statistically applicable. |

## Решения до соответствующего этапа

Срок решения не означает срок поставки функции. Локальный путь уже выбран, но остаток OPEN-011/012/015 не закрыт этим выбором.

| ID | Ответственность | До этапа | Что решить |
| --- | --- | --- | --- |
| OPEN-001 | приложение | R0 | Минимальная navigation до R1; working title допустим, бренд не блокирует MVP. |
| OPEN-002 | оба | R0 | Minimal Workspace/Project/Lens UX и ownership до research R2. |
| OPEN-003 | оба | R0 | Один local personal scope для MVP, global/scoped refs. |
| OPEN-004 | оба | R0 | Minimal BankItem/Asset/Document/Note boundaries перед save. |
| OPEN-005 | оба | R4 | Basic provenance/use links до R1; full typed registry до R4. |
| OPEN-006 | оба | по триггеру | При COND-007; до R5 явно указать unsupported bitemporal expectations. |
| OPEN-007 | оба | R0 | Minimum retained captures/receipts policy before R1; further retention conditional. |
| OPEN-008 | оба | R4 | Genealogy granularity before evidence lineage; high-stakes может advance. |
| OPEN-009 | оба | R0 | Minimal version/migration contract before R1; mature pack evolution before R7. |
| OPEN-010 | приложение | R0 | Minimal local index; advanced store split before R6 only if needed. |
| OPEN-011 | оба | R0 | Local Commander path выбран; production format/internal DB/media/backup open; cloud remains open. |
| OPEN-012 | оба | R0 | Commander выбран; validated file handoff/receipts/API equivalence; dedicated MCP optional. |
| OPEN-013 | приложение | по триггеру | До active COND-001/002/008 async feature, не обязателен в MVP. |
| OPEN-014 | приложение | по триггеру | До notification/alert feature; manual Watch не требует всех channels заранее. |
| OPEN-015 | оба | R0 | MVP local trial выбран; offline/device availability/sync scope уточнить; future cloud open. |
| OPEN-016 | оба | по триггеру | До active COND-004; multi-user не обещан текущими versions. |
| OPEN-017 | оба | по триггеру | До private/auth/sensitive source (COND-003), может быть R0/R1. |
| OPEN-018 | оба | R6 | Supported profiles metrics before release; EXP-004/OPP-017 evaluation before R7. |

## Эксперименты и возможности

Они не превращены в обязательные релизы. Сначала evidence/disposition, затем назначение версии.

| ID | Тип | Оценка / предпосылка |
| --- | --- | --- |
| OPP-001 | opportunity_unassigned | R5 comparable longitudinal data |
| OPP-002 | opportunity_unassigned | R5 data + valid anomaly model |
| OPP-003 | opportunity_unassigned | R5/R6 versioned data/representation |
| OPP-004 | opportunity_unassigned | R5 enough comparable history |
| OPP-005 | opportunity_unassigned | R5 comparable distributions |
| OPP-006 | opportunity_unassigned | R4/R6 typed graph + user value |
| OPP-007 | opportunity_unassigned | R5 temporal histories + R6 similarity |
| OPP-008 | opportunity_unassigned | R7 profile/skill projection |
| OPP-009 | opportunity_unassigned | R5 assumptions/causal limits |
| OPP-010 | opportunity_unassigned | R5 valid analytical inputs |
| OPP-011 | opportunity_unassigned | R5 comparable metrics + R7 preferences |
| OPP-012 | opportunity_unassigned | R5 history/uncertainty model |
| OPP-013 | opportunity_unassigned | R5 defensible sampling |
| OPP-014 | opportunity_unassigned | R5 explicit sampling/independence assumptions |
| OPP-015 | opportunity_unassigned | R6/R7 collection/example retrieval |
| OPP-016 | opportunity_unassigned | R7 media/provenance + source discovery |
| OPP-018 | opportunity_unassigned | R4 retrieval evaluation + measured cost/latency bottleneck |
| OPP-019 | opportunity_unassigned | EXP-002 benchmark + interoperability need |
| OPP-020 | opportunity_unassigned | EXP-001/002 domain benchmark + active COND-008 |
| EXP-001 | evaluation_gate | До изменения retrieval policy/routing; marginal evidence/overlap/primary/counterevidence/cost/latency; не полный provider benchmark перед MVP. |
| EXP-002 | evaluation_gate | Перед значительным commodity subsystem build; baseline local UI/intake не требует обзора всех платформ. |
| EXP-003 | evaluation_gate | Перед advanced analytics promotion; assumptions/coverage/data; не все advanced методы включаются в R5. |
| EXP-004 | evaluation_gate | До treating similarity as useful signal в R6/R7; OPP-017 comparison before R7; fail blocks acceptance, not silently demotes TARGET. |

## Инварианты и запреты во всех релевантных версиях

| ID | Класс | Ограничение |
| --- | --- | --- |
| INT-001 | CORE_INTENT | Product is a universal personal research/intelligence bank around ChatGPT, not a vacancy/freelance-specific product. |
| INT-002 | CORE_INTENT | User can save arbitrary useful material independently of an active research project. |
| INT-003 | CORE_INTENT | Saved items can later act as search seeds, research inputs/results, evidence/reference, comparison items, collection members, or watch subjects. |
| INT-004 | CORE_INTENT | Repeated research enriches one longitudinal bank/history rather than producing isolated reports only. |
| INT-005 | CORE_INTENT | System supports scope/coverage-aware current state, changes, trends, lifecycle/history, and research health. |
| INT-006 | CORE_INTENT | ChatGPT is the primary interactive reasoning/orchestration layer; the application owns durable state/history/UI/deterministic contracts. |
| INT-007 | CORE_INTENT | Sources/tools/providers are reusable but replaceable; research semantics should depend on capabilities/contracts rather than vendor brands. |
| INT-008 | CORE_INTENT | New domains should normally be added through Domain Packs rather than universal-core schema rewrites. |
| INT-009 | CORE_INTENT | Preserve provenance, history, comparability, counterevidence and command/query boundaries. |
| INT-010 | CORE_INTENT | Discovery is not measurement; search-result frequency is not demand/prevalence without valid method/sampling. |
| INT-011 | CORE_INTENT | Raw evidence, canonical identity, annotation, derived representation, analytical projection and search ranking remain distinct epistemic layers. |
| INT-012 | CORE_INTENT | “Complete/current state” is always relative to declared scope, method and coverage; never imply total-world exhaustiveness by default. |
| ANTI-001 | ANTI_GOAL | Job/vacancy as universal root object |
| ANTI-002 | ANTI_GOAL | ResearchProject owns all durable knowledge |
| ANTI-003 | ANTI_GOAL | Build general web search/crawler merely to avoid existing ChatGPT/providers |
| ANTI-004 | ANTI_GOAL | Hard-code provider brands into universal research semantics |
| ANTI-005 | ANTI_GOAL | Assume multiple retrieval providers equal independent evidence |
| ANTI-006 | ANTI_GOAL | Treat vector index/embedding/ranking as canonical truth |
| ANTI-007 | ANTI_GOAL | Create one giant GenericObject schema |
| ANTI-008 | ANTI_GOAL | Use one opaque similarity score for every purpose |
| ANTI-009 | ANTI_GOAL | Silently overwrite history after identity/model/method changes |
| ANTI-010 | ANTI_GOAL | Treat not_seen as disappeared/closed |
| ANTI-011 | ANTI_GOAL | Claim complete market/world state without scope and coverage |
| ANTI-012 | ANTI_GOAL | Treat discovery counts as demand/frequency measurement by default |
| ANTI-013 | ANTI_GOAL | Hide source disagreement inside a single aggregate |
| ANTI-014 | ANTI_GOAL | Silently refresh/mutate on a read-only query without authorization |
| ANTI-015 | ANTI_GOAL | Implement every analytics idea or provider integration before user value |
| ANTI-016 | ANTI_GOAL | Use chat transcript memory as durable product state |

## Сохранившиеся пробелы и обязательные подготовительные работы

- **PLAN-SOURCE-ENTITY** — Source отдельно от Entity; relation optional; SourceRoute belongs to Source. Must be consistent in actual types/master/JSON before release acceptance; current map text not fully normalized. До: R0.
- **PLAN-CLUSTERING-PARITY** — Master includes target clustering, registry lacks explicit obligation. Resolve inventory gap during consolidation; do not infer removal from this roadmap or silently invent child IDs. Any affected R5 acceptance blocked until disposition. До: R0.
- **PLAN-CLAIM-ENUM** — Master/registry status names must be aligned before evidence schema consumers. Roadmap does not silently choose one enum. До: R0.
- **PLAN-INVENTORY** — 115-entry version coverage does not mean all 159 backlog dispositions or per-entry rationale/axes/origins are consolidated; normalization report remains separate work. До: R0.
- **PLAN-LOCAL-WRITE** — Define complete-write detection, repeat-safe IDs/version/conflicts/recovery/confinement/index rebuild before production writable app. Synthetic probe evidence is limited. До: R0.
- **PLAN-WINDOWS-PARITY** — Investigate tests/TESTS parity on Windows in a separate maintenance copy/patch; do not change accepted baseline identity or mark legacy gates passed. Required before relying on affected baseline validation in a release. До: R0.

Полнота этой карты — **115 текущих ID**. Она не доказывает завершение нормализации всех требований или перенос triage всех 159 backlog-пунктов; эти работы остаются в R0. Clustering, claim enums и Source/Entity не считаются автоматически исправленными.

## Старый development plan

- Phase 0–2: Accepted v1.10/v1.11 history retained; not reassigned to new releases as new implementation.
- Phase 3–4: Five projection/query products and hermetic query Golden Paths are related to R5; existing pending legacy work is not retroactively accepted.
- Phase 5: Derived UI composition principle used in R1/R2 and richer R5 UI; no UI routing duplication.
- Phase 6–7: Audit/QA/release discipline applies at every release, including R2/R3; existing legacy plan remains an independent historical plan.

## Совместимость, история и проверка

Каждый новый релиз фиксирует версии формата/schema, поддерживаемые read/write версии, migration/backup/restore и поведение неизвестных полей. Major/minor номер сам по себе не гарантирует совместимость.

У требования не один флаг done: учитываются system contribution, app contribution, acceptance evidence и scope каждой slice. Scope до последней slice частичный. CORE/ANTI всегда ограничения; OPP/EXP/OPEN/COND не считаются реализованными по наличию строки в плане.

Проверка карты: `python PLANNING/TOOLS/release_plan.py --requirements DRAFT_NOTES/REQUIREMENTS_MAP.json`. Генерация этого документа: та же команда с `--render`.

Машинная карта: [REQUIREMENTS_RELEASE_MAP.json](REQUIREMENTS_RELEASE_MAP.json). Старый план: `freelance_research_system_feature_architecture_red_tests/REFERENCE/DEVELOPMENT_PLAN_vNext.md`.

## Ограничения сохранения

При подготовке первого пакета ПК был Offline, а точечные правки вернули тайм-аут. Применение проверяется по фактическим исходным файлам; успешный PLANNING/APPLICATION_RECEIPT.json подтверждает сохранение плановых документов, но не приёмку релизов. Скрипт не выполняет GitHub push.

Coverage and planning consistency only; no running app, v2 implementation, search relevance, performance/cost or production security acceptance.
