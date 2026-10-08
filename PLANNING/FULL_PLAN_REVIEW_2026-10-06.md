# Независимое ревью всего vNext-плана — 2026-10-06

Review ID: FPR-20261006. Проект: `C:\Users\alexa\research_and_bank`.
Итог: основное распределение R0–R8 согласовано с текущим продуктовым замыслом. Найдены три подтверждённые проблемы в управлении планом; они не доказывают неисправность приложения, которого ещё нет. P-1/P-2 требуют правок, P-3 относится к актуальности review ledger и уточняется записью этого ревью. Приёмка R0 или приложения не установлена.

## Объект, исходная задача и границы

Проверяется весь актуальный план Universal Research / Intelligence Bank: master и 115 требований, классификации, две линии версий, R0–R8, зависимости, критерии приёмки, решения и условные gates, сохранение backlog/предложений, процедура разработки и подготовленные R1 контракты. Последний SQLite-шаг — только часть объекта. Исторический development plan v1.11 используется для проверки границ наследования, а не как автоматически действующий план универсального приложения.

Цель: персональный долговечный Bank вокруг ChatGPT, независимое сохранение, поиск и повторное использование материалов, сохранённое исследовательское состояние и история. ChatGPT ведёт исследование; приложение владеет долговечным состоянием, детерминированной валидацией и UI. Первый путь: Commander → локальные файлы → приложение; GitHub вспомогателен. CORE/ANTI ограничивают соответствующий scope; TARGET не становится MVP; активный COND может потребовать дополнительных мер уже в MVP. Принятая система 1.11.0 сохраняется отдельно.

Критерии проверки: сохранность намерений и классификаций; полное покрытие текущих ID; отсутствие противоречий между человеческими и машинными обязательствами; реализуемая последовательность контрактов; проверяемая приёмка; воспроизводимое продолжение работы; честная граница design/static/probe/runtime acceptance. Календарный срок и бюджет пользователем не заданы: отсутствие оценок не признано ошибкой.

Постановка соответствует контексту. Расширять MVP всеми Golden Scenarios или 41 непринятым предложением оснований нет. Новые требования не используются для ретроактивной оценки v1.11.

## Как выполнена независимая проверка

Зафиксирован свежий snapshot 85 документов/скриптов и hashes 264 файлов baseline. Сначала из master/registry восстановлены обязательные outcomes, затем проверены slices и milestones. Отдельный проверочный скрипт не использует `release_plan.validate` или `inventory.validate`: заново считает ID/классы, сопоставляет statements, строит топологический порядок по dependencies и sequencing, проверяет две линии версий, окончания MVP slices и backlog/proposal states. Подтверждающие результаты сохранены в CHECKS.json.

На Windows заново выполнены семь команд: inventory, release map, две их regression suites, стандартная schema/fixture conformance, bank regression suite и SQLite mechanism probe. Все завершились с exit code 0; группы regression tests: 3 + 3 + 5, storage probe: 8. Это независимый повтор исполнения существующих проверок, а не независимое доказательство полноты самих проверок. Дополнительные три контрпримера получены прямым чтением текущих полей/карточек/ledger.

Процесс прежних шагов подтверждается карточками и receipts: Source/Entity, Claim enum, clustering/MVP parity, inventory traceability, local-write, minimal Bank types, SQLite/limits. Их evidence разделяет documentation, static conformance и synthetic mechanism tests. Неизвестные действия вне этих записей не реконструируются как факты.

## 1. Реальные проблемы

### P-1 — Действующая инструкция продолжения направляет на завершённую первую задачу

**Влияние:** среднее, локальное для продолжения работы; не меняет продуктовый scope. Связь: долговечный контекст/воспроизводимый handoff, INT-006/ANTI-016, AX-V19/20/22.

`PLANNING/DEVELOPMENT_WORKFLOW.md` называет «Карточка текущей задачи» `R0_SOURCE_ENTITY.json`; шаблон передачи в новый чат тоже жёстко указывает её. Последний раздел утверждает, что выполнение Source/Entity ещё впереди. Сейчас эта карточка имеет `status=completed`, а SESSION_STATE заканчивается завершённым storage/limits шагом и следующим bounded importer шагом.

**Механизм и воспроизведение:** новый чат получает готовую инструкцию handoff → открывает completed Source/Entity вместо актуальной задачи → пытается повторять consolidation или вынужден вручную искать точку продолжения. Это противоречит цели продолжения без реконструкции чата и создаёт риск повторной записи. Реальный новый чат в этом ревью не запускался: подтверждён противоречивый маршрут инструкции, а не наблюдавшаяся порча файлов.

**Proposal:** workflow оставить общей процедурой; текущую задачу брать из одного актуального указателя SESSION_STATE/отдельного checkpoint. Source/Entity пометить как исторический пример. Для следующего действия создать новую ограниченную карточку, а не повторять completed. Высокая уместность самостоятельного решения. Исправление не внесено; нормальная продолжимость требует устранения этого указателя.

### P-2 — Машинные deadlines не выражают ранние части некоторых decision gates

**Влияние:** среднее, локальное для машинного планирования gates; не доказана пропажа MVP ссылок. Связь: minimal provenance/use links и честные temporal expectations; MVP-001, OPEN-005/006, COND-007, AX-V09/19/20.

В `REQUIREMENTS_RELEASE_MAP.json`:

| ID | Текст обязательства | Машинный deadline |
|---|---|---|
| OPEN-005 | basic provenance/use links до R1; полный registry до R4 | только R4, без decision_checkpoints |
| OPEN-006 | при COND-007; до R5 явно указать unsupported bitemporal expectations | null, без отдельного checkpoint R5 |

**Механизм:** потребитель строит checklist по `decision_before_milestone`/`decision_checkpoints` → ранняя часть OPEN-005 отсутствует в раннем checklist, а обязательная проверка ожиданий OPEN-006 выглядит только trigger-based. Человеческий scope требует более раннего действия. OPEN-018 уже показывает подходящий способ разделения стадий.

**Минимальное воспроизведение:** выбрать entries OPEN-005/006, сравнить указанные поля с `decision_scope`; затем сформировать checklist до R1/R5 только из структурированных deadlines. Ранние обязательства отсутствуют. Обычный validator проходит текущую карту: он проверяет корректность существующих checkpoints, но не извлекает ранние deadlines из prose.

**Контрдоказательство:** R1 pinned refs уже подготовлены отдельно, MVP-001 требует links, а полный валидный consumer может читать prose. Поэтому это не доказательство отсутствия ссылок в схемах или возможности честно принять неполный MVP.

**Proposal:** оформить раннюю и позднюю части явными checkpoints, сохранив классификации и сроки поставки; для OPEN-006 отделить безусловное объявление поддерживаемой temporal semantics до R5 от реализации bitemporal по COND-007. Проверить остальные составные OPEN-009/010 аналогично, без автоматического объявления их дефектными. Высокая уместность самостоятельного решения. Исправление не внесено; блокирует доверие к checklist, который читает только структурированные поля.

### P-3 — Текущая оценка DF-MRQ-003 не учитывает уже появившуюся версию и tooling

**Влияние:** низкое, локальное для review ledger; связь: AX-V19/20, сохранение актуальных findings без уничтожения истории.

В `DRAFT_NOTES/REVIEW/FINDINGS.json` текущий `finding` DF-MRQ-003 говорит об отсутствии `schema_version`, а latest assessment сохраняет объяснение «consumer вне DRAFT_NOTES не обнаружен». Сегодня registry имеет `schema_version=1.0.0`, действуют `inventory.py`, `release_plan.py` и generator/parity/regression checks в PLANNING/TOOLS.

**Механизм:** последующий агент читает current finding как остаток работ → заново добавляет уже существующую версию/валидацию либо неверно оценивает зрелость inventory. Старая датированная assessment была корректной для своего snapshot; проблема именно в неприведённой к текущему состоянию оценке, а не в исторической записи.

**Proposal:** сохранить исходные finding/history и добавить assessment: version и базовое tooling уже есть; формальная schema/migration compatibility остаётся отдельным follow-up D-3. Высокая уместность самостоятельного решения. Эта bookkeeping assessment записывается с Review Log; underlying plan/tooling не изменяются.

## 2. Спорные или неопределённые места

**U-1 — Полный остаток R0 ещё не сведён в одну проверяемую gate-карту.** OPEN-001/002/003/007/009/010/012/015/018 и PLAN-* содержат будущие решения; часть уже решена в ограниченных контрактах. Из записей нельзя установить полное R0 acceptance. Следующий synthetic importer можно использовать для получения evidence, но это не разрешение объявить R0/R1 accepted. Перед затронутой приёмкой нужны owner, текущий ответ, evidence и точный remaining scope для каждого блокера. Не требуется принять все 41 proposals: обязательные уточнения существующего scope и новые возможности надо различать. Связь: Q-1.

**U-2 — Runtime пригодность R1 не проверена.** Готовы design schemas/SQLite DDL/limits; importer, защищённое Windows чтение, весь CAS/replay path, публичный read/search API и UI пока не реализованы. LW01–LW13 pending. Unknown commit outcome, disk-full/I/O, TOCTOU и реальные материалы нельзя считать проверенными по static conformance или direct-SQL probe. Это предусмотренный остаток реализации, а не нынешний runtime bug. Блокирует runtime acceptance, не текущий review и synthetic development.

**U-3 — Входы и критерии clustering R5 предстоит concretize.** TGT-020 включает supported semantic/topic/mechanics grouping, а richer text/media representations поставляются R6/R7. Обязательного цикла не обнаружено: R5 может использовать сохранённый текст, structured observations и явно обозначенные annotations/features; это не требует именно R6 embeddings или R7 media vectors. Но без перечня supported inputs, versioned method/features, контрольных cases и comparability нельзя утверждать полноту R5 clustering. Связь: Q-2; решать до его implementation acceptance.

**U-4 — Indexed fields, searchable retained text и extraction policy R1 не выбраны до конца.** OPEN-018 требует это до R0/R1; bytes retention и MIME ещё не определяют поиск. Неизвестны набор контрольных queries/expected IDs и границы title/body/metadata/history indexing. Отсутствие готового решения нормально для unfinished R0, но generic SQL/importer PASS этого не закрывает. Блокирует search acceptance R1; не блокирует bounded raw-save prototype.

## 3. Что выдержало проверку

| Проверка | Результат и предел |
|---|---|
| Полнота registry → release map | 115 уникальных ID, точное совпадение statements/classifications; CORE 12, MVP 11, TARGET 25, COND 10, OPP 19, OPEN 18, ANTI 16, EXP 4 |
| Все обязательные delivery outcomes | 36 staged requirements имеют slices; все 11 MVP заканчиваются не позже R2; нет обнаруженной потерянной обязательной категории |
| Две линии версий | R1 2.0.0-alpha.2/0.1.0 partial MVP; R2 2.0.0/0.2.0 full MVP; R3 2.0.1/1.0.0 stable MVP; system-only/application-only contributions не требуют фиктивного релиза другой стороны |
| Граф и последовательность | Объединённый граф dependencies/sequencing ацикличен; порядок R0…R8 допустим. Очередность не объявлена неизменной технической зависимостью |
| История и provenance | Source≠Entity, optional subject link; SourceRoute owner=Source; pinned revisions, frozen RunSpec/results, raw/annotation/derived distinctions согласованы на проверенном scope |
| MVP и TARGET | Три сокращённых MVP journeys сохранены; mechanics similarity/full Trend-Health/formal reusable registries не введены в MVP. OPP-017 TARGET R7 с soft/hard/dimensions/explanations/evaluation, не обещанное улучшение |
| Условия | COND triggers сохранены и могут advance необходимый scope в MVP; нет общего обещания scheduler/security/statistical calibration только в поздней версии |
| Backlog и предложения | Все 159 bullets сохранены/связаны; 45 proposals: 41 pending, 2 consolidated, 2 superseded. Не приняты автоматически ни новые ID, ни semantic dedupe |
| Local-write → R1 schemas → storage | READY≠ACCEPTED; единственный атомарный owner оригиналов/revisions/receipt, append-only history; текущий head/index derived; schema allowlist не обещает future research schemas; limits конечные и errors явные |
| Прежние выводы | Старые VSR-001…006 и именованные MRQ-001…004 documentation fixes не переоткрыты без основания. Исторические карточки/SESSION_STATE блоки не сочтены competing current instructions сами по себе |

SQLite DELETE+EXTRA выбор согласуется с официальной документацией; online backup API предусмотрен для согласованного snapshot. Документация также сохраняет зависимости atomic/durable behavior от storage/VFS/flush. Это подтверждает обоснование design, но не доказывает аппаратную сохранность данного компьютера. Первичные источники: [synchronous](https://sqlite.org/pragma.html#synchronous), [atomic commit](https://sqlite.org/atomiccommit.html), [backup API](https://sqlite.org/backup.html), повторно проверены 2026-10-06.

## 4. User Assistance / Process Improvement

**UA-1 — Классификация первых реальных материалов.** Перед переходом от synthetic/public fixtures к настоящему персональному Bank достаточно указать, будут ли первые материалы публичными, приватными или чувствительными, и какие внешние model/provider endpoints допустимы. Передавать сами приватные файлы для этого не требуется. Это снимает неопределённость COND-003/OPEN-017 и позволяет задать минимальные access/encryption/retention/export/exposure controls. Только пользователь может надёжно задать допустимый уровень обработки своих данных: требуется решение пользователя. Отсутствие ответа не блокирует review/synthetic development; блокирует приёмку соответствующего private/sensitive use. Сейчас дополнительных файлов или доступа для этого ревью не нужно.

## 5. Deferred / Follow-up Items

| ID | Что сохранить и почему не исправлять сейчас | Триггер возврата | Последствие после триггера |
|---|---|---|---|
| D-1 | SQLite+BLOB подходит выбранному bounded R1; performance/large media/concurrent backup не доказаны. Нет реального Bank/замеров, менять backend сейчас без оснований нельзя | Поднятие 64 MiB/256 MiB limits, bulk ingestion/COND-002, большая DB, backup при постоянном writer | Задержки, нехватка диска/staging/journal, backup без завершения; нужны измерения и supported deployment policy |
| D-2 | Port/generalization baseline contracts, UC ownership и whole-system generated views должны быть явно привязаны к vNext acceptance; baseline сейчас менять не нужно. PLAN-WINDOWS-PARITY остаётся отдельной maintenance работой | Первое принятие изменённых vNext UC/contracts/release, либо reliance на affected baseline validation | Routing/map/schema/release views могут разойтись; нельзя переносить legacy PASS как доказательство нового runtime |
| D-3 | Версия registry и базовые validators уже есть; formal registry/overlay schema, supported historical format/migration semantics — отдельный остаток, а не повтор missing-version работы DF-MRQ-003 | Новая структура schema_version, внешний consumer/CI/API или migration | Старый consumer может неверно читать новые поля/классификации; нужна явная compatibility policy |
| D-4 | Генератор roadmap преимущественно описывает плановые обязательства и не выводит все checkpoint resolutions/current remaining. Это допустимо для intent view, но менее удобно как live progress view | Использование roadmap как единственного dashboard/checklist или много completed checkpoints | Повторное обсуждение решённых подзадач; полезен generated progress view из одного status owner, без второго editable source |

Возврат к U-2 до runtime acceptance, U-3 до R5 и U-4 до R1 search acceptance уже записан в их канонических записях. UA-1 охватывает private-data trigger; отдельный дубликат deferred privacy finding здесь не создан.

## 6. Вопросы и Proposals

**Q-1 — Как продолжать после review?** Значение: P-1/P-2 мешают надёжному handoff/checklist, U-1 не разрешает выдавать prototype за accepted release. Proposal: сначала исправить workflow pointer и checkpoints, собрать компактный ответ/evidence/remaining по R0; затем bounded synthetic importer по новой карточке, сохраняя R0/R1 unaccepted до выполнения критериев. Высокая уместность самостоятельного решения: не меняет нужду, scope и сложность кардинально. Non-blocking для review/prototype, blocking для соответствующей приёмки. Правки плана здесь не выполнены.

**Q-2 — Какой supported clustering outcome принимается в R5?** Значение: U-3; строка TGT-020 сама по себе не доказывает полезное semantic/mechanics grouping. Proposal: выбрать versioned доступные features, минимальные annotated examples, критерии membership/explanation/history и insufficient-data behavior; richer modalities оставить по согласованным стадиям. Для конкретного минимального supported domain/method желательно согласование: полнота желаемой mechanics capability может зависеть от выбора. Non-blocking для R1, blocking до clustering acceptance R5. Перенос или уменьшение обязательного TARGET без решения пользователя не предлагается как рабочее изменение.

Вопрос о допустимых настоящих данных и Proposal содержатся в UA-1; категория — требуется решение пользователя при переходе к соответствующему use, не для нынешнего review.

## Ограничения и проверка опровержений

Проверка не доказывает feasibility всех future algorithms/providers, human relevance, стоимость/сроки, full security, OS/hardware power-loss behavior или полноценный new-chat/UI journey. Формальные tests не покрывают все намерения: P-1/P-2/P-3 воспроизводятся при PASS. Полная legacy baseline suite не запускалась, известный Windows tests/TESTS вопрос не объявлен закрытым. Snapshot hashes позволяют проверить неизменность baseline во время этого review; это не повтор acceptance всех 264 файлов.

Отдельно отвергнуты как неподтверждённые дефекты: «R5 обязательно циклично зависит от R7», «R3 обязан включать TARGET», «Source schema означает готовый R2 SourcePolicy», «SQLite probe доказывает полный importer/durability», «исторический Golden Scenario автоматически расширяет MVP», «все 41 proposals обязательно принять», «отсутствие cloud/MCP/push блокирует локальную работу». Для каждого есть явное разграничение scope/стадий/условий либо доступный контрпример.

## Review Log и сохранение

Компактная запись: `DRAFT_NOTES/REVIEW/2026-10-06_FULL_PLAN_REVIEW_LOG.md`.
Evidence: `DRAFT_NOTES/REVIEW/2026-10-06_FULL_PLAN_REVIEW_CHECKS.json`.
Этот report, log, ledger assessment и SESSION_STATE checkpoint сохраняются с source-hash guards, резервной копией изменяемых bookkeeping файлов и readback hashes. План, master, schemas, tooling и baseline остаются без исправлений. Факт успешной записи подтверждается отдельным `FULL_PLAN_REVIEW_2026-10-06_SAVE_RECEIPT.json`; до такого подтверждения текст этого раздела не считается доказательством сохранения.
