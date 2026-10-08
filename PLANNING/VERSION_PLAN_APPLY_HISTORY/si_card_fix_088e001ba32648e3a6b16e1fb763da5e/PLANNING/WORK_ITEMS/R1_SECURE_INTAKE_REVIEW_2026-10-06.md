# Review карточки R1-SECURE-INTAKE-001 — 2026-10-06

Review ID: SI-CARD-20261006. Объект — PLANNING/WORK_ITEMS/R1_SECURE_INTAKE.json и достаточность постановки до программирования безопасного Windows reader/staging. Scope — цель, входы, контрактные границы, критерии приёмки, ограничения, вопросы и следующий handoff. Это не ревью уже написанного reader: EXPERIMENTS/secure_intake отсутствует на момент проверки.

Итог: цель и ограниченный scope обоснованы. Два пробела карточки следует разрешить до зависимой реализации. Они не означают найденные дефекты работающего Bank: соответствующего компонента ещё нет. Вопросов, требующих новых ответов пользователя, не обнаружено. Полная реализация и приёмка R0/R1/LW не выполнены.

## 1. Реальные проблемы постановки

### P-1 — Не зафиксирована граница transport reader и domain/importer validation

Связь с целью: application_result обещает изолированный safe-reader/staging без canonical DB writes; следующий шаг — отдельный importer/CAS. required_inputs включает полный check_bank_contracts.py и domain schemas, но SI1–SI4 не задают, какие проверки выполняет reader, какой результат он возвращает и что должен проверить следующий importer. В частности не выделено разрешение pinned refs к ранее принятой истории.

Механизм: если реализатор использует validate_package(..., accepted=()) как входной reader, корректное продолжение с ссылкой на принятую Asset revision отклоняется UNRESOLVED_REFERENCE. Если для устранения ошибки reader начинает читать canonical history/выполнять CAS, меняются границы этой карточки. Если просто считать успех копирования domain acceptance, неподтверждённые объекты попадут в следующий этап как якобы принятые. Проблема касается архитектурного handoff и основного результата этого компонента.

Независимый воспроизводимый пример: BANK_TYPE_EXAMPLES/INDEX.json, examples.create и examples.continuation. На Windows с действующим schema environment вызов validate_package для continuation с документами create в accepted_inputs вернул 1 документ; тот же вызов без истории вернул UNRESOLVED_REFERENCE. Это показывает зависимость полного валидатора от истории, а не утверждает, что ещё не написанный reader уже переиспользует его неправильно.

Proposal Q-1: перед кодом зафиксировать transport-only интерфейс. Вход — доверенно настроенные synthetic intake/staging roots, transaction folder и snapshot числовой policy. Выход — проверенный закрытый snapshot точных READY/manifest/document/attachment bytes с фактическими sizes/hashes и логическими относительными именами, либо явный отказ. Доступ к bytes — контролируемый handle/iterator или гарантированно защищённый staging, без повторного чтения исходных paths и без producer-controlled destinations. Успех называется STAGED/VERIFIED_TRANSPORT, никогда ACCEPTED/REPLAY; canonical receipt и commit IDs reader не выдаёт.

Reader проверяет безопасное чтение, complete marker/envelope, strict JSON и preparse bounds, связь marker с exact manifest bytes, совпадение transaction ID/папки, уникальность объявленных paths, полный inventory, фактические bytes/limits/hashes и document_path inventory binding. Domain-schema/provenance/ссылки на accepted history и CAS остаются importer; допустимые pure schema checks reader не должны объявлять семантическое принятие. check_bank_contracts.py полезен как fixture oracle и пример pure rules; его filesystem I/O/path.resolve/read_bytes нельзя считать защищённым runtime reader.

### P-2 — Критерии не покрывают отказ до READY и незавершённый staging

Связь с целью: SI1 проверяет successful copy, SI2 — опасные пути/extra files/swaps, SI3 — bounds/JSON; полного списка обязательных отрицательных исходов и поведения после прерывания нет. LOCAL_WRITE_CONTRACT.md §§2,4,6 и LW06/LW09 уже различают incomplete, invalid и незафиксированный orphan. Это существующий контракт, не новая функциональная потребность.

Механизм: реализация может пройти перечисленные happy-path/path/limit проверки, но при отсутствующем READY ошибочно считать пакет отвергнутым навсегда, удалить исходник либо опубликовать пригодный к handoff каталог после частичного копирования. Например, первый payload скопирован, чтение второго даёт ошибку, а созданный output directory всё равно доступен потребителю. Последующий importer получает неполный snapshot; повтор или диагностика ненадёжны. В рамках synthetic probe нет canonical commit, поэтому это дефект достаточности критериев reader, а не доказанное повреждение SQLite.

Proposal Q-2: добавить явную acceptance matrix и output lifecycle. Минимум: missing/partial READY — INCOMPLETE без выдачи snapshot; ready-invalid/truncated JSON, BOM/duplicates/nonfinite, marker↔manifest mismatch, missing/tampered payload, reserved/colliding names и undeclared empty directories — отказ без успешного результата. Ошибка I/O/заполнения staging/отмена во время copy — нет выдаваемого готового snapshot; исходный пакет неизменен, ресурсы закрыты, bounded diagnostic сохранён. Незавершённая копия изолирована и не используется следующим importer. Успех выдаётся только после проверки всех объявленных bytes и inventory. Детали удаления disposable staging задавать явно; не удалять пользовательский intake/accepted history. Перезапуск после прерывания — новая проверка исходного пакета, не доверие найденной partial копии.

Не требуется в этой карточке проверять durable SQLite commit, UI или потерю питания: это другие LW этапы. Проверки собственных временных файлов и своего child process допустимы; завершение чужих процессов/перезагрузка ПК не нужны.

## 2. Спорные или неопределённые места

U-1 — Native Windows safe-read primitive и доверенная граница roots/ACL ещё не выбраны. Это открытый Q1 самой карточки, а не автоматически ошибка планирования. В ходе review подтверждены Windows/Python/dependencies, но не защита handles, права создания link fixtures, locks/ACLs или race-proof guarantees. Prototype должен записать supported filesystem/root assumptions и фактически измеренные ограничения, а не выводить security из path.resolve/temp directory.

Связанное уточнение SI2: попытка подмены может быть предотвращена удерживаемыми handles либо реальная подмена должна дать отказ. Evidence обязано различать blocked attempt, detected/rejected actual change, unsafe success и unavailable test. Запрет считать skipped тест PASS в карточке уже есть; его следует сохранить. Непроверенный обязательный случай не разрешает заявлять confinement ready для следующего writer.

## 3. Что выдержало проверку

- CURRENT_WORK_ITEM действительно указывает эту карточку; status=prepared, все четыре SI checks pending, предыдущая карточка завершена отдельно. Карточка не заявляет существующий reader.
- Все 10 required_inputs доступны; ещё 2 файла контекста/card проверены. Fresh native hashes совпали с локально прочитанными 12 источниками. AGENTS.md в проверенных repo/ancestor/целевых каталогах не обнаружены.
- Windows 11 build 26200, Python 3.14.7; существующий schema environment импортирует jsonschema и возвращает exit 0. Unicode data version 16.0.0. Это evidence доступности зависимостей, не security acceptance.
- Цель соответствует ближайшей архитектурной задаче: защищённый byte handoff до canonical SQLite writer. Разделение reader и следующего importer полезно при уточнении P-1.
- Synthetic temporary roots, отсутствие watcher/UI/production Bank/DB writes и отсутствие release claims ограничивают scope; baseline/schema/release не требуется менять.
- LOCAL_INTAKE_LIMITS.json задаёт конечные границы: 64 MiB/file, 256 MiB/package, 128 files/operations, READY 16 KiB, manifest 512 KiB, object JSON 2 MiB, depth 64, I/O chunk 1 MiB. Численные значения менять для этого review не нужно.
- Три пользовательских выбора не переоткрыты: публичные источники и возможные идеи/анализ, без запланированных секретов/дополнительных AI providers; достаточно включённого ПК. Ideas/analysis не объявлены публичными автоматически.
- Skip не считается PASS; source/baseline guards и отдельная будущая task для importer уже предусмотрены.

## 4. User Assistance / Process Improvement

UA запросов сейчас нет. Входы, Commander и зависимости доступны; P-1/P-2 разрешимы самостоятельно без смены пользовательской нужды, scope или кардинального увеличения сложности. Если implementation позже выявит реально недоступный обязательный Windows test, сохранить конкретный failure/required capability и запросить только необходимое действие; сейчас отсутствие прав не установлено.

## 5. Deferred / Follow-up

D-1 — End-to-end importer должен проверять schema/provenance/accepted refs, serialized CAS/replay, receipts, commit/recovery и original queries на snapshot из P-1. Это следующий scope, здесь DB writes запрещены. Вернуться при подготовке importer card: без этой связи транспортная копия ошибочно станет считаться принятым объектом.

D-2 — Реальные roots/ACL/storage/durability и соответствующие nonpublic controls. Synthetic probe не принимает deployment на реальных данных. Вернуться перед реальным intake/Bank use или изменением root/filesystem; иначе границы, проверенные в temp fixtures, будут применены вне доказанных условий.

D-3 — Producer READY publication primitive. Reader обязан распознавать incomplete/invalid marker (P-2), но атомарную no-overwrite публикацию самого producer надо проверить при реализации полного handoff. Сейчас reader — потребитель пакета, не writer/publisher. Игнорирование этого пункта при end-to-end реализации даст частично видимый marker или нарушит repeat-safe IDs/bytes.

## 6. Вопросы и Proposals

Q-1 / P-1: каков результат reader и где domain acceptance? Proposal — transport-only verified snapshot, доменные history/CAS/receipt отдельно. Высокая уместность самостоятельного решения; blocking для зависимого кода, non-blocking для пользователя. Это Proposal данного review, а не изначальное требование о конкретном названии API.

Q-2 / P-2: какие отрицательные исходы/cleanup считаются принятыми? Proposal — явная матрица incomplete/invalid/I-O/cancellation, отсутствие готового output на failure, сохранение intake. Высокая уместность самостоятельного решения; blocking перед объявлением reader ready, не требует ответа пользователя.

Q-3 / U-1: какой native primitive и что возможно проверить на ПК? Proposal — выбрать при реализации из реально доступных APIs и доказать assumptions/negative cases; при недоступности обязательного теста отметить ограничение и не выдать общий PASS. Высокая уместность самостоятельного решения в текущем synthetic scope. Evidence блокирует downstream claim безопасного writer; новых user permissions сейчас не требуется.

## Review Log — SI-CARD-20261006

- Target/scope: R1-SECURE-INTAKE-001, достаточность карточки до реализации reader/staging, не всё приложение/роадмап.
- Итог: scope обоснован, P-1/P-2 требуют явных уточнений карточки до зависимого кода; runtime не проверен, implementation не начат.
- P-1: граница transport/domain и result handoff не закреплены; fixture continuation без history даёт UNRESOLVED_REFERENCE, с history проходит. Влияние — неправильные отказы либо расширение scope/ложное принятие.
- P-2: incomplete/failure/cancel staging outcomes не включены явно в критерии; влияние — ошибочная классификация незавершённого пакета/выдача partial output. Основание — действующие §§2,4,6 и LW06/LW09; actual buggy reader не существует.
- U-1: Windows safe-handle/root/ACL/race guarantees и доступность link tests ещё не доказаны; выбрать/проверить при реализации, skip ≠ PASS.
- Проверено: 10 inputs доступны, 12 source hashes согласованы; Windows/Python/schema environment доступны; synthetic/no-DB/no-release boundary и finite policy согласованы.
- UA: отсутствуют; новых пользовательских ответов не нужно.
- D-1: domain/CAS/receipt/commit handoff — при следующей importer card. D-2: deployment/nonpublic root/ACL controls — перед реальными данными. D-3: producer READY publication — перед полным handoff.
- Ограничения: нет runtime reader, Windows confinement/privilege/races/resource exhaustion/cleanup не испытаны; native experiment здесь только статический schema-history counterexample. Прежние R0/R1/LW не приняты этим review.
- Q-1/Q-2/Q-3: Proposals выше; высокая уместность самостоятельного решения; internal clarifications/evidence blocking соответствующий код/ready claims, user answers non-blocking.
- Сохранение: canonical log — этот файл; native guard/write/readback evidence — R1_SECURE_INTAKE_REVIEW_RECEIPT_2026-10-06.json. Предыдущую историю review сохранять; результат записи подтверждается receipt, не этой строкой.
