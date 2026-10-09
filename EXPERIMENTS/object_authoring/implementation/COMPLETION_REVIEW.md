# Проверка выполнения R1_OBJECT_AUTHORING

Review ID: OAI-20261009-01. Дата: 2026-10-09T02:56:33.337257+00:00. Scope: committed B; текущие исходники и фактическая Windows-конфигурация.

## Краткий результат / Для пользователя

Создание Entity/Collection/targeted Annotation и редактирование четырёх типов подключены к прежнему Bank. Все17 новых и22 прежних проверки прошли локально и на Windows, без пропусков; G1/G2/G3 и включение восьмого каталога подтверждены. Исходный config и bytes Bank сохранены. Существенных текущих подтверждённых Problems в проверенном scope не осталось. OAI-F-P-001/002 исправлены; история сохранена.

OAI-EG-001 / OAI-UA-001: визуальная пользовательская приёмка пока отсутствует. Она блокирует закрытие FUB10 и визуальных частей OBJ10/OBJ11. Следующий шаг — открыть обычный launcher и проверить маршрут из инструкции; дополнительных решений A/B нет. Главные разделы ниже: «Что реализовано», «Доказательства и границы», «Исправленные находки и предложения», «Визуальная приёмка и дальнейший шаг», «Review Log».

## Что реализовано

Отдельный INTENT/BASE/SEAL журнал, точные версии и полные pinned refs, закрытые поля Entity/Annotation/Collection, редактирование Asset/Entity/Annotation/Collection. Общий старый LOCK удерживается один раз; прежний шестикаталожный backend и семикаталожные материальные подготовки сохранены. Оригинал копируется через guarded retained export либо явно выбранный external replacement; ранее принятые bytes и версии остаются. Поля/IDs/base/profile/time замораживаются, seal восстанавливается без Bank/original reselection. Конфликт не ребейзится; квитанция остаётся канонической даже при повреждённом журнале. Формы используют существующий единственный worker/Flow и человеческий запуск GUI.

Для128 refs проверка выполняется в одном bounded accepted ReadSession, с неизменными контрактами и pinned snapshot, затем canonical commit проверяет refs/CAS повторно. Разные revisions одного объекта допустимы, порядок сохраняется. Модель `Source`, произвольные Entity.data properties, research и сети не добавлены.

## Доказательства и границы

- [Локальные17](evidence/LOCAL_3a89c6a9fc8047e8ac4ac37d5b990a48.json) и [Windows17](evidence/NATIVE_fcb206390e9d479a97f83cff82e369a3.json) — полный новый набор, same-source guard true. [Карта OBJ1–OBJ11](CHECK_EVIDENCE_MAP.json).
- [Прежний Bank local22](../../first_bank/evidence/LOCAL_14ce7bf146f34806b38b32c0634ad4b8.json) и [Windows22](../../first_bank/evidence/NATIVE_7f479f8e7b0742ab98eb1862889862bd.json) подтверждают старую подготовку1/2, чтение/поиск/наблюдение/диагностику и восстановление.
- G1: фактические два процесса, busy, OS-exit release, старый и новый writer, отсутствие вложенного lock; configuration8-root reopen/rollback. G2: точный retained original и explicit replacement,64MiB normal,64MiB+1 refusal. G3: SQL version/base, CAS conflict/whole rollback, exact retry/receipt, actual process exits при journal/capture/seal/publication/postcommit, controller callback/pinned context/search/history.
- [Реальная конфигурация](REAL_CONFIGURATION_CHECK.json): исходный config побайтово сохранён; БД before/after SHA совпадает; `runtime.py check` возвращает READY с8 roots. Расширение включено явно; материалы пользователя не импортировались, GUI не открывался. Native rollback проверен на owned roots; real rollback не выполнялся поверх пользовательской настройки.
- Принятые264 и schemas/query/DDL не менялись. Полный релиз, production usability, original4Win1314, research/provider/Watch/restore/hardware не приняты. Во время итерации были промежуточные прогоны; они сохранены как история, текущим proof служат указанные source-guarded17.

## Исправленные находки и предложения

OAI-F-P-001 → OAI-PR-001 (committed, NORMAL, Autonomy HIGH): неверная интерпретация availability при retained export блокировала допустимое metadata edit. Контрпример — принятый Asset → редактирование title → ORIGINAL_UNAVAILABLE вместо PREPARED. Исправлена работа с существующим `bytes` контрактом; точность и64MiB подтверждены test_obj03/07. Данных/контракта Bank не меняли.

OAI-F-P-002 → OAI-PR-002 (committed, NORMAL, Autonomy HIGH): при новой URI без explicit provenance source_locator становился None. Исправлена заморозка актуального locator/time и сброс прежних acquisition claims; test_obj16 подтверждает новое значение и неизменность старой версии. Пользовательские explicit declarations сохраняются. Эти исправления — текущий implementation level, не изменение Need/FR/scope B.

Каноническая история, reproduction, IDs и статусы: [ISSUES](ISSUES.json). Исправления тестовой SQL-фикстуры не выдаются за ошибки Bank. Необоснованных новых Risks/Decision Uncertainties не добавлено.

## Визуальная приёмка и дальнейший шаг

OAI-EG-001 / OAI-UA-001 — partially blocking: только фактическая GUI/usability/adoption приёмка. Пользователь запускает обычный `EXPERIMENTS\first_bank\launch_bank.cmd` и проходит [инструкцию](../runtime/README.md): Entity(problem/algorithm/theory), targeted note, ordered mixed Collection, edit четырёх типов, старые/новые версии и originals, stale conflict и explicit new edit, sealed reopen/receipt, cancel/close/busy/status, внешний save второго окна. Скриншот нужен при материальном визуальном вопросе. Результат фиксируется в receipt; обнаруженная проблема исправляется и проверяется по соответствующей части.

Первый FUB10 также остаётся открытым. CURRENT_WORK_ITEM сохраняется на этой незакрытой приёмке; R1_OBJECT_AUTHORING технически выполнен как разрешённая параллельная разработка. OBJ10/OBJ11 не помечены целиком PASS. Следующую work card из оставшегося R1 следует сформировать после закрытия этих gates, а не выдумывать следующий реализованный шаг.

## Review Log

[COMPLETION_REVIEW_LOG](COMPLETION_REVIEW_LOG.json) содержит source/version scope, Needs/requirements, canonical findings/proposals, evidence gaps, OAI-UA-001, реальные measured verification times и границы. Часы разработки, user-time, deadlines и budgets из длительности тестов не выводятся. История прежней карточки: [CARD_BEFORE_IMPLEMENTATION](CARD_BEFORE_IMPLEMENTATION.json); принятый scope B сохранён.
