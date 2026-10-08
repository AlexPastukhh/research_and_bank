# Состояние работы — 2026-10-05

## Цель

Персональный Universal Research / Intelligence Bank: удобно сохранять материалы и результаты, находить их позже и возвращать в работу через ChatGPT. Исследовательская система v1.11 является принятой исходной системой; Universal Bank остаётся проектом следующего этапа.

## Источники текущего состояния

- `DRAFT_NOTES/11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md` и `REQUIREMENTS_MAP.json` — основной инвентарь намерений vNext. Полная нормализация пока не применена.
- `DRAFT_NOTES/08_IDEA_BACKLOG_AND_OPEN_DECISIONS.md` — исторический inbox, который после переноса/triage не должен конкурировать с master inventory.
- Два отчёта в этой папке — анализ и предложения, а не автоматически принятые новые требования.
- `DRAFT_NOTES/REVIEW/` — прежние ревью, Findings ledger, сохранённые Review Logs и история решений. История сохранена.

## Решения, подтверждённые в разговоре

1. Source и Entity — отдельные канонические типы. Связь Source → Entity опциональна; SourceRoute относится к Source. Документация ещё требует согласования (MRQ-004).
2. Поиск сходства игровых механик относится к TARGET и Golden Scenario, вне блокирующего MVP. Проверка MVP должна доказывать сохранение, исследование и повторное использование материалов.
3. OPP-017 (positive + negative examples) повышен до TARGET_REQUIRED, вне MVP. Пользователь задаёт измерения сходства, мягкое снижение ранга или жёсткое исключение; нужны объяснения и сравнительная оценка релевантности. Улучшение качества поиска пока является проверяемой гипотезой. Это точечное изменение уже внесено в архив и отчёт нормализации с сохранением истории.
4. Нормализацию всех 115 требований сначала подготовили как review-предложение. Остальные изменения, включая новые записи и splits, не должны считаться применёнными.
5. 2026-10-05 пользователь выбрал `AlexPastukhh/research_and_bank` и локальную копию под `C:\Users\alexa` для системы и планов и явно поручил push.

## Уточнение хранения после независимого ревью

Пользователь хочет иметь удобный доступ ко всем материалам и результатам Bank, включая изображения и приватные файлы. В текущем GitHub-подключении приватная картинка, по наблюдению пользователя, передаётся как содержимое файла, но не как визуальный контекст.

Следовательно, доступность файла и пригодность для визуального анализа нужно проверять отдельно. Публичный GitHub допустим для публикуемых материалов. Приватное хранение и конкретный backend Bank остаются OPEN. Выбор этого GitHub-репозитория для проектных документов не закрывает выбор backend Bank.

В сохранённом ревью RVP-001 исходил из более раннего понимания GitHub как выбранного первоначального backend Bank. Позднейшее уточнение ограничивает этот вывод: нельзя считать выбор другого backend нарушением решения пользователя. Старое ревью сохранено как исторический результат; это явное дополнение к нему, а не переписывание истории.

## Dropbox: состояние проверки

- Плагин установлен; пользователь явно выбрал его.
- Скриншот Dropbox подтвердил подключение ChatGPT и разрешения на чтение/изменение файлов и папок.
- Инструкции плагина доступны, но операции поиска и чтения в этой сессии не были доступны агенту.
- Поэтому ни визуальный анализ приватного PNG/JPEG, ни сохранение результата обратно не проверены.
- Проверены официальные возможные причины: обновление инструментов в новом чате, загрузка операций серверного подключения, правила workspace/ролей и действующая авторизация. Точная причина неизвестна.

## Следующая работа

1. Завершить согласование authoritative inventory: kind/axes/origin/history, dispositions backlog, принятые Source/Entity и MVP/TARGET границы. Сохранить стабильные ID и происхождение.
2. Согласовать мастер-текст и JSON и добавить явный MVP acceptance checkpoint в план A–F. Полный список текущих проблем — в критическом ревью; они не исправлены самим переносом в Git.
3. Проверить выбранное подключение на приватных тестовых файлах: сохранить → в новом чате найти → открыть оригинал → визуально проанализировать → сохранить результат с ссылкой на оригинал. Не публиковать приватный материал как обязательное условие.
4. Выбрать storage topology по результату этого теста и ожидаемому объёму файлов, а не только по наличию плагина или общей API-квоте.

Deferred / Follow-up Items и условия возврата к ним сохранены в отчёте критического ревью и Findings ledger. Перед реализацией соответствующей возможности нужно вернуться к её acceptance criteria и рискам.


## Текущее решение — 2026-10-05, 18:12 Asia/Bangkok

Этот блок уточняет исторические OPEN/storage и Dropbox-записи выше.
Для первого прототипа пользователь выбрал ChatGPT → Desktop Commander → локальные файлы → приложение.
GitHub выполняет вспомогательную роль истории/синхронизации; локальный обмен не требует commit/push.
Формат production-данных, необходимость локальной БД, media/backup и политика приватных материалов остаются открытыми.

В этой ветке операции Dropbox работают: JPEG скачан и визуально просмотрен, PNG загружен обратно.
Это подтверждает файловый путь, но не полный цикл исследования/импорта.
Полная запись выбора и результатов: [LOCAL_FILE_EXCHANGE_TRIAL_2026-10-05.md](LOCAL_FILE_EXCHANGE_TRIAL_2026-10-05.md).

Изолированная локальная проба завершилась PASS: сохранение синтетического отчёта, чтение готового пакета,
стабильный повторный scan и отказ при незавершённой/изменённой/неполной записи и выходе пути за пакет.
Это не готовое приложение Bank и не утверждение его полной готовности.
Следующий шаг — минимальный production-контракт локальной записи и потребитель приложения с явным MVP acceptance.


## Версии системы и приложения — план 2026-10-05

Все 115 текущих ID распределены по двум линиям версий в PLANNING/REQUIREMENTS_RELEASE_MAP.json; human view — PLANNING/VERSION_ROADMAP.md.
Принятая система остаётся 1.11.0; Universal Bank 2.x — отдельные плановые контракты. Готового приложения пока нет.
Система 2.0-alpha.1 / без приложения — контракты; 2.0-alpha.2 + app 0.1 — local Bank; 2.0 + app 0.2 — полный MVP; 2.0.1 + app 1.0 — стабильный MVP.
Далее планируются пары system/app: 2.1/1.1 evidence/sources; 2.2/1.2 temporal/projections; 2.3/1.3 identity/search; 2.4/1.4 multimodal/profiles/OPP-017; 2.5/1.5 Watch.
Номера плановые, сроки не назначены; ни один будущий релиз не принят по наличию этой карты.
CORE/ANTI — сквозные ограничения; COND — trigger gates; OPEN — decision gates; EXP/OPP не получили обещаний поставки.
MVP-011 уточнён по прежнему решению о mechanics similarity вне MVP с сохранением предыдущей записи. Reduced two-run proof — acceptance proposal этой версии плана.
Source/Entity, claim enums, clustering parity, full normalization/159-item triage и Windows parity остаются явными подготовительными работами.
Сохранение через Commander/local files остаётся первым маршрутом. GitHub push и отдельный MCP не обязательны.


## Правки version staging после ревью — 2026-10-05

По разрешению пользователя применены VSR-001..006 из VERSION_STAGING_REVIEW_2026-10-05_BRANCH.md. Уточнены положительные scopes/ответственность, минимальная сохранность и exact/full-text приёмка R1, RunSpec/SourcePolicy приёмка R2, identity R6 и lifecycle Watch R8. OPEN-018 разделён на checkpoints R0/R6/R7.
Валидатор проверяет checkpoint versions/coverage, per-side scopes, очередность и decision checkpoints; source count берётся из текущего inventory. Есть regression tests. Schema overlay 1.1; номера продуктовых версий, текущие 115 ID, статусы и сроки slices сохранены.
Это правки плана и проверки документов, не реализация приложения и не закрытие PLAN-SOURCE-ENTITY/CLAIM-ENUM/CLUSTERING/INVENTORY/LOCAL-WRITE/WINDOWS-PARITY. Полная нормализация и R0 contract work остаются следующими задачами.


## Точка продолжения разработки — проверка процесса 2026-10-05

Порядок: [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md). Одна следующая задача: [R0_SOURCE_ENTITY.json](WORK_ITEMS/R0_SOURCE_ENTITY.json); её актуальный status и acceptance находятся в карточке.
Подготовлен ограниченный шаг согласования уже принятого Source/Entity решения в definitions/examples/JSON. Приложение и accepted v1.11 этим шагом не меняются.
Проверка процесса охватывает подготовку, доступность inputs и сохранение checkpoint; независимый новый чат и выполнение самой задачи ещё не проверены. Receipt: [WORKFLOW_CHECK_RECEIPT_2026-10-05.json](WORKFLOW_CHECK_RECEIPT_2026-10-05.json).
Следующее действие: прочитать required_inputs карточки, сверить актуальный diff и выполнить её documentation consolidation с evidence A1–A8. Это не закрытие полного PLAN-SOURCE-ENTITY/R0.


## Выполненный шаг Source/Entity — 2026-10-05

R0-SOURCE-ENTITY-001 завершён в пределах documentation consolidation. Актуальный результат и evidence A1–A8: [WORK_ITEMS/R0_SOURCE_ENTITY.json](WORK_ITEMS/R0_SOURCE_ENTITY.json); команды/hashes/audit scope/backup: [WORK_ITEMS/R0_SOURCE_ENTITY_RECEIPT.json](WORK_ITEMS/R0_SOURCE_ENTITY_RECEIPT.json).
Согласованы master, bank model, source examples, MVP-004/TGT-005 JSON и release snapshots; roadmap сгенерирован. В durable MRQ-004 сохранена история и отмечено устранение documentation drift.
Native validator/generated parity и existing release-plan regression suite PASS. Все 115 IDs/statuses/areas и stages сохранены; accepted v1.11 (264 файла) byte-identical.
Остаток PLAN-SOURCE-ENTITY: actual persisted types/schema compatibility перед R0 acceptance. Приложение, R0 и релиз этим шагом не приняты; независимый новый чат ещё не проверен.
Один следующий шаг: PLAN-CLAIM-ENUM — сравнить статусы Claim в master и REQUIREMENTS_MAP.json, согласовать названия до проектирования evidence schemas.


## Выполненный шаг Claim enum — 2026-10-05

R0-CLAIM-ENUM-001 завершён для naming/compatibility документации. Карточка и evidence: [WORK_ITEMS/R0_CLAIM_ENUM.json](WORK_ITEMS/R0_CLAIM_ENUM.json); checks/hashes/backup: [WORK_ITEMS/R0_CLAIM_ENUM_RECEIPT.json](WORK_ITEMS/R0_CLAIM_ENUM_RECEIPT.json).
Каноническое имя PARTIALLY_SUPPORTED; PARTIAL сохранён как legacy read/import alias только для Claim verification status. Master, research note, TGT-014 JSON и release snapshot согласованы; roadmap сгенерирован. Runtime normalizer/миграция остаются будущей работой R4.
115 IDs/classifications/stages сохранены; validator/generated parity и existing regression suite PASS; accepted v1.11 (264 файла) byte-identical. MRQ-003 закрыт только в части enum naming; остальные parity компоненты остаются открытыми. R0 и релизы не приняты.
Один следующий шаг: PLAN-CLUSTERING-PARITY — согласовать TARGET clustering intent в master §8.2 и TGT-020 JSON без изменения MVP и без скрытого добавления новых IDs.


## Выполненный шаг TARGET clustering — 2026-10-05

R0-CLUSTERING-001 завершён для documentation parity. Карточка/evidence: [WORK_ITEMS/R0_CLUSTERING_PARITY.json](WORK_ITEMS/R0_CLUSTERING_PARITY.json); checks/hashes/backup: [WORK_ITEMS/R0_CLUSTERING_PARITY_RECEIPT.json](WORK_ITEMS/R0_CLUSTERING_PARITY_RECEIPT.json).
Existing TARGET clustering включён в TGT-020: supported semantic/topic/mechanics grouping, versioned derived memberships/history и scoped descriptive cluster dynamics. Уточнены system/app scopes R5 (2.2.0/1.2.0); новые IDs/MVP obligations/algorithms не добавлены. Advanced-method adoption и richer representations сохраняют свои отдельные gates/stages.
115 IDs/classifications/stage assignments сохранены; validator/generated parity и existing regression suite PASS; accepted v1.11 (264 файла) byte-identical. PLAN-CLUSTERING-PARITY и TARGET disposition URVP-003 разрешены в документах; runtime validation впереди. MRQ-003 остаётся открытым в остальных частях; R0/релизы не приняты.
Один следующий шаг: MRQ-003 MVP parity — согласовать master §5.1/5.5 с MVP-001/MVP-011: минимальные provenance links и mechanics similarity вне MVP.


## Выполненный шаг MVP scope/link parity — 2026-10-06

R0-MVP-PARITY-001 завершён в documentation scope. Карточка/evidence: [WORK_ITEMS/R0_MVP_PARITY.json](WORK_ITEMS/R0_MVP_PARITY.json); checks/hashes/backup: [WORK_ITEMS/R0_MVP_PARITY_RECEIPT.json](WORK_ITEMS/R0_MVP_PARITY_RECEIPT.json).
Согласованы минимальные applicable provenance/use links MVP-001: R1 Asset/item/Annotation/Collection/capture references; R2 research-produced Observation/source/run/result links. Independent save не требует fictitious Entity/Source/ResearchRun; общий typed Relation остаётся TGT-001/R4.
Master §5.5/MVP-011 game proof уже был согласован и сохранён: save→seed→research→reuse, mechanics similarity вне MVP. MRQ-003 named documentation parity components устранены; original finding/history сохранены. Schemas/runtime acceptance и full inventory normalization ещё открыты.
115 IDs/classifications/stage assignments сохранены; validator/generated parity и existing regression suite PASS; accepted v1.11 (264 файла) byte-identical. R0/релизы не приняты.
Один следующий шаг: PLAN-INVENTORY — согласовать kind/axes/origin/history и dispositions backlog с текущими 115 requirements, сохранив IDs и границу current decisions/proposals.


## Выполненный шаг inventory traceability — 2026-10-06

R0-INVENTORY-001 завершён для metadata/backlog preservation. Карточка/evidence: [WORK_ITEMS/R0_INVENTORY_TRACEABILITY.json](WORK_ITEMS/R0_INVENTORY_TRACEABILITY.json); checks/hashes/backup: [WORK_ITEMS/R0_INVENTORY_TRACEABILITY_RECEIPT.json](WORK_ITEMS/R0_INVENTORY_TRACEABILITY_RECEIPT.json).
Все 115 requirements получили kind/axes/human links/rationale/origin-confidence/history; master содержит generated stable-ID crosswalk. Неизвестная историческая user attribution остаётся unknown; предыдущие explicit decision histories сохранены.
Все 159 bullets связаны через DRAFT_NOTES/BACKLOG_TRIAGE.json; DRAFT_NOTES/NORMALIZATION_PROPOSALS.json сохраняет 45 NEW/split labels (41 pending, 2 consolidated, 2 superseded backend proposals). Candidate dependencies/reference mappings не приняты автоматически. Authoritative map/master явно делегируют сохранение непринятых идей этим supplemental ledgers.
MRQ-001/002 named traceability/preservation gaps устранены в draft docs; pending statement clarifications/new IDs/splits и нужные scope choices остаются отдельными решениями до соответствующих контрактов. Полная adoption normalization/R0/релизы не заявлены. Native inventory/release validators и обе regression suites PASS; 115 IDs/statuses/statements/triggers/stages сохранены; accepted v1.11 (264 файла) byte-identical.
Один следующий шаг: PLAN-LOCAL-WRITE — определить минимальный production-контракт локальной записи/импорта: готовность пакета, IDs, повторные записи, конфликты, recovery и confinement.
