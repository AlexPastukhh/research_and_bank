# Review карточки SQLite-импортёра — 2026-10-06

Объект: `PLANNING/WORK_ITEMS/R1_SQLITE_IMPORTER.json`, вся карточка и её исходные 18 required_inputs. Проверка — следующий шаг после завершения secure reader; это не повтор его приёмки и не реализация приложения. Источники, original fixtures, static validator и candidate SQL не изменены.

Задача: bounded synthetic R1 independent-save importer, controlled snapshot → domain/history/CAS → одна SQLite transaction с exact bytes/revisions/original ACCEPTED receipt → безопасный replay/recovery. Production Bank, UI/search, новый provider, hardware shutdown и release acceptance вне scope. Задача соответствует предыдущим решениям пользователя. User answers уже даны; новых blocking user questions нет.

## Реальные проблемы карточки и исправления

- **P-1 — Asset binding.** Pure document validator принимает Asset SHA=нули при других actual original bytes. Rehashed документ/manifest/READY валиден, но full reference validator выдаёт ASSET_DESCRIPTOR_MISMATCH. Если следовать только pure helper recipe, можно принять неверное описание оригинала. DB2/DB6 теперь явно требуют safe declared path + exact size/hash + retained commit mapping; locator-only не загружает bytes.
- **P-2 — replay ordering.** `validate_documents(create, accepted=create)` выдаёт DUPLICATE_REVISION. Replay до CAS недостаточно: нужен lookup/verified stored replay branch до fresh-command duplicate/history checks. Это теперь execution_sequence и DB3; exact retry не создаёт новые IDs/revisions и не маскирует corrupt retained bytes.
- **P-3 — history bounds.** Одна новая команда с валидной newest-first цепочкой 1100 accepted документов вызывает RecursionError в helper. Incoming caps не ограничивают весь Bank. Карточка теперь требует targeted indexed history reads, streaming integrity и iterative current-package graph. DB8 отдельно проверит рост/длинную историю; это не удаление/обрезка retained history и не разрешение пропускать проверки.
- **P-4 — R1 intent.** Static `validate_package(profile=R1)` принимает tracked_research с четырьмя R1-документами, хотя соответствующая RunSpec/research семантика относится к R2. DB2 теперь явно допускает только independent_save; новые Source/Run/tracked_research в этом R1 importer отвергаются.

Это подтверждённые пропуски/неоднозначности конкретной карточки и предлагаемой последовательности, а не обнаруженные дефекты уже написанного импортёра: его ещё нет. Все четыре исправлены на уровне карточки; runtime проверки остаются pending.

## Неопределённости и границы

- **U-1 — BLOB authority.** В настоящем SQLite 3.50.4 SQL UPDATE блокируется immutable trigger, но writable blobopen меняет hello → jello даже при defensive mode. Это демонстрирует границу примитива через намеренно доверенную connection, а не incoming exploit. DB4/DB6 требуют private writer/new current-transaction rows only; old BLOB access read-only, producer не выбирает row/table/column/DB path. Реализация и regression ещё нужны.
- **U-2 — outcomes.** Receipt schema содержит шесть canonical статусов. UNKNOWN/BUSY/IO/cancel — отдельное client/attempt состояние; не добавлять их в receipt enum и не выдумывать успех/INCOMPLETE. Это уточнено в карточке, recovery ещё надо доказать.

## Что выдержало проверку

Актуальный pointer, UC19, card status и secure-reader receipt согласованы. Все 43 source/review files доступны и hashes не изменились при переходе на выбранный app. Accepted baseline: 264 файла, byte-identical. Selected backend/atomic receipt/CAS/recovery intent и synthetic-only scope правильны. Native пять helper/API cases воспроизведены, exit 0; это подтверждение наблюдений, не runtime acceptance.

## User Assistance

Не требуется. Проверка и исправления доступны самостоятельно; прежние data/provider/PC-on ответы не переспросены.

## Deferred / Follow-up Items

- **D-1:** streamed whole-DB audit/backup/migration и совместимость accepted history — отдельная последующая работа. Вернуться при real deployment, restore/migration или расширении schemas. Иначе targeted-read trust assumptions могут не покрыть corruption/foreign graph.
- **D-2:** privacy/real-root/producer publication/hardware/VFS durability — будущая deployment приёмка, не эти temp probes. Вернуться перед real-data release/сменой storage; иначе synthetic evidence ошибочно заменит реальные guarantees. Secure-reader follow-ups сохраняются.

## Questions / Proposals

- **Q-1:** как перенести pure validation rules? Proposal: targeted history adapter + iterative new graph + отдельный replay branch; сохранять original integrity/ref semantics. Высокая уместность самостоятельного решения, non-blocking review; DB2/DB3/DB8 blocking для completion.
- **Q-2:** как ограничить writable BLOB authority? Proposal: connection/row IDs private, writes только new active-command rows, existing rows read-only, negative regression. Высокая уместность самостоятельного решения, non-blocking review; DB4/DB6 blocking для completion.

## Review Log и следующий шаг

Машинный Review Log: `REVIEW_LOG.json`. Проблемы с open → resolved_card/runtime_pending историей: `ISSUES.json`; native evidence: `CARD_COUNTEREXAMPLES.json`, replayable source: `card_counterexamples.py`; guarded hashes/readback receipt: `CARD_REVIEW_RECEIPT.json`.

**Review завершён, карточка остаётся prepared. DB1–DB8 pending. Следующий шаг — реализация исправленной bounded synthetic карточки. R0/R1/production acceptance не закрыты.**

Первичные API документы проверены:
- https://www.sqlite.org/lang_transaction.html
- https://www.sqlite.org/c3ref/blob_open.html
- https://www.sqlite.org/c3ref/blob_write.html
- https://docs.python.org/3.14/library/sqlite3.html

Нативный counterexample является самостоятельным доказательством наблюдаемого поведения. Документы не заменяют эти проверки. Предыдущая история review/reader task сохранена.
