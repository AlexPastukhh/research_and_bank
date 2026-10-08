# Локальная запись и импорт Bank — контракт 1.0.0

Дата: 2026-10-06. Work item: R0-LOCAL-WRITE-001 / PLAN-LOCAL-WRITE, до R0.
Статус: проект контракта для реализации; production validation ещё не выполнена.
Маршрут: ChatGPT → Remote Desktop Commander → локальный intake → приложение.
Protocol `local-bank-intake/1` отличается от `local-exchange-trial-v1`.

## 1. Граница и владельцы

Этот контракт определяет файловый command handoff, а не полные persisted Bank types, UI или backend.
Приложение — единственный владелец принятого Bank state. Producer пишет только новые входящие пакеты;
не редактирует canonical history, heads, receipts или индекс. ОС/доступ к папкам задают локальную авторизацию.
SHA-256 проверяет целостность, но не подлинность автора и не достоверность исследования.
GitHub — необязательная история/синхронизация; private/media/backup/cloud policy остаются OPEN-011.
Intake и canonical Bank roots конфигурируются отдельно; контракт не создаёт хранилище в публичном репозитории.

Связи: MVP-001 — stable IDs и applicable provenance; MVP-009 — save/get operations;
MVP-006/007/008 — frozen research history в R2. R1 — independent save; R2 — tracked research.
OPEN-012 получает file-command design checkpoint; отдельный MCP и полный query/search API ещё не выбраны.
41 pending normalization proposals сохраняют статус. NEW-008 не принят: repeat-safe transport IDs
не означают semantic/content dedupe, identity merge или общий импорт произвольных архивов.
Оси: AX-V07, AX-V09, AX-V12, AX-V15, AX-V16, AX-V19, AX-V20, AX-V22.

## 2. Пакет и публикация

Один пакет: `incoming/<transaction_id>/manifest.json`, объявленные файлы и `READY.json`.
ID — lowercase UUID v4; имя папки равно transaction_id. Пакет выполняет одну атомарную команду
`commit_revisions`; операции — новые полные revisions объектов, без delete, patch и автоматического merge.
Producer сохраняет transaction/object/revision IDs и точные bytes для повтора после timeout.

Порядок producer:
1. Создать новую папку без перезаписи существующей; записать payloads/attachments.
2. Закрыть файлы; собрать byte lengths и SHA-256; записать и закрыть manifest.json.
3. Перечитать всё и проверить inventory. Записать READY.pending, закрыть/flush.
4. Опубликовать READY.json последним с no-overwrite и атомарной видимостью на том же volume.
   Нельзя применять replacement к уже опубликованному пакету. Конкретная Windows primitive подлежит проверке.
5. После READY пакет неизменяем. Producer ждёт app receipt; наличие READY само по себе не означает сохранение в Bank.

Если финальную публикацию нельзя обеспечить используемым transport/tool, пакет остаётся incomplete:
нельзя заменить её записью частично видимого READY.json. Producer helper можно запускать через Commander.
Atomic visibility не гарантирует сохранность при потере питания. Требование ACCEPTED ниже строже.
READY содержит protocol, transaction_id, byte length и SHA-256 точных bytes manifest.json.
manifest перечисляет все data files, их sizes/hashes и операции; READY/manifest не входят в files inventory.
Дополнительные обычные файлы, оставшиеся pending files и вложенные READY/manifest отклоняются.
Папки допустимы только как родители объявленных файлов. ZIP extraction и исполняемые команды не поддерживаются.

Примеры в `LOCAL_WRITE_EXAMPLES/` синтетические: полный independent save и его update.
`bank-example-item/1` служит только примером envelope, не принимается production importer как Bank schema.
Не копировать эти примеры в production incoming; это не результаты исследования.

## 3. Валидация перед изменением

`LOCAL_WRITE_ENVELOPE.schema.json` — Draft 2020-12 schema с `$defs.manifest`, `$defs.ready` и `$defs.receipt`.
Обязателен strict JSON: UTF-8 без BOM, без duplicate keys, NaN/Infinity; неизвестные поля envelope отвергаются.
Даты — RFC3339 UTC с Z; версии protocol/schema поддерживаются явно, без догадок и silent migration.
Schema проверяет форму; следующие semantic правила обязательны сверх неё:

* Все UUID соответствуют роли; transaction ID совпадает в папке/marker/manifest.
  object_id стабилен между revisions; revision_id новый и уникален; один object_id только один раз в пакете.
* files paths уникальны; каждый operation document_path ровно один раз в files; каждый файл объявлен.
  Проверяются фактические bytes/size/hash всех документов и attachments, не только отчёта.
* type/schema_ref есть в allowlist поддерживаемого persisted schema registry; каждый документ проходит
  его проверку, включая совпадение object/revision identity и обязательные provenance links.
* Все ссылки разрешаются в принятую pinned revision или в этот пакет. Внешний URL допустим как locator,
  а не как разрешение автоматически скачать отсутствующий файл/источник. Forward links валидируются целиком.
* Independent save не требует фиктивных Entity, Source или ResearchRun. Применимые capture/source/author/use
  ссылки определяют domain schemas, а не файловый transport. Source и Entity не сливаются.
* Для tracked_research валидны frozen RunSpec/ResearchRun/ResultSet/Occurrence links и фактическая
  история membership/order/reasons. Полный пакет может содержать partial/failed research outcome;
  file completeness не повышает epistemic status результата. Это R2 domain validation, не уже готовая схема.
* Импорт использует конечные configured limits: files count, individual/total bytes, JSON depth,
  operations count. До production release значения фиксируются и проверяются на supported media.
  Превышение — LIMIT_EXCEEDED до записи, а не бесконечное чтение или тихая обрезка.

## 4. Confinement на Windows

Path в manifest — относительный lower ASCII POSIX path, максимум 180 символов; без `..`, пустых сегментов,
backslash, drive/UNC, colon/ADS, percent escapes, trailing dots/spaces. Только schema pattern.
Windows reserved device basenames CON/PRN/AUX/NUL/COM1..9/LPT1..9 отвергаются также с extension.
READY/manifest и их pending names зарезервированы и не могут быть payload.
Проверка containment проводится после разрешения root; root и его parents должны быть доверенно настроены.
Внутри root не принимаются symlinks, junctions/reparse points или иные redirects; hard links отклоняются.
Producer не задаёт destination paths. Importer сам генерирует canonical paths из validated IDs.

Одна path.resolve проверка недостаточна: importer копирует через защищённые handles либо закрытый staging,
проверяет identity/link attributes при чтении и хеши именно сохранённых bytes, повторно проверяет marker/manifest.
После copy не читает mutable source для commit. Подмена source/marker во время чтения — reject, без частичного commit.
Файловые ACLs и single importer writer обязательны; защита от администратора с полным доступом не обещается.
До реализации безопасного Windows чтения production acceptance остаётся pending.

## 5. IDs, повторы и конкуренция

Create: base_revision_id = null, object_id ещё не существует. Update: base_revision_id равен текущему head;
новый revision_id сохраняет старую revision. Сравнение heads выполняется внутри одного сериализованного commit.
Не mtime, не last-write-wins; полная команда либо применяется целиком, либо не применяется вовсе.

| Ситуация | Решение |
|---|---|
| Принятый transaction_id + прежний exact manifest hash, bytes retained valid | REPLAY, прежняя receipt, ноль новых revisions |
| Тот же transaction_id + другой manifest hash | CONFLICT / TRANSACTION_ID_REUSED, исходный commit сохранён |
| Существующий revision_id в новой transaction | CONFLICT / REVISION_ID_REUSED, даже если content похож |
| Новый object_id с base = null | ACCEPTED после всех проверок |
| Существующий object_id с base = null | CONFLICT / OBJECT_EXISTS |
| Update с неверным или исчезнувшим base | CONFLICT / BASE_REVISION_MISMATCH либо OBJECT_NOT_FOUND |
| Два update одного head | Один commit; второй conflict, все его операции отменены |
| Равные bytes при разных object IDs | Самостоятельные объекты; semantic dedupe/merge не выполняется |

Повтор проверяется прежде CAS: он возвращает исходный результат, даже если head позже обновлён.
Same-ID replay проверяет исходную integrity/accepted commit; повреждённый пакет не скрывается как успешный replay.
Конфликт нельзя обходить выдачей нового ID для того же намерения. Для разрешения прочитать current revision,
явно выбрать сохранение новой версии/отдельного объекта, сформировать новую команду и указать исходную конфликтную transaction
в development/application action lineage; workflow UI и format этого future resolution отдельно до реализации.

## 6. Durable commit, квитанции и recovery

Importer повторно валидирует закрытую private staging copy; переносит immutable verified bytes в app-owned storage.
Затем фиксирует атомарный durable acceptance record: transaction_id, manifest hash, commit sequence,
object/base/revision IDs и retained bytes references. Registry implementation/DB остаётся отдельным OPEN-011 решением.
Commit record — canonical факт принятия; current heads и индекс выводятся из принятых ordered commits.
Нужны single-writer serialization и backend transactional/durable primitive; частичная запись текстового ledger недостаточна.
На serialization lock contention команда остаётся pending/retryable; importer не выполняет concurrent CAS по stale cache.
Локальный ACCEPTED выдаётся только после сохранения всех bytes и durable commit; не после staging/индексирования.
Если durability гарантия выбранной ОС/storage configuration недоступна, production release заблокирован.

Receipt: protocol, transaction_id, manifest_sha256, status, code; для ACCEPTED/REPLAY — original commit_id,
commit_sequence и committed object/revision pairs; для ошибок — диагностические file/object refs без изменения Bank.
Каждая попытка получает app-generated attempt_id и recorded_at UTC. ACCEPTED code = OK; REPLAY code = ALREADY_ACCEPTED.
Error diagnostics — ограниченные plain-text строки; transaction/hash могут быть null только когда их нельзя достоверно прочитать.
Error/incomplete receipt не содержит commit fields. REJECTED/CONFLICT и INCOMPLETE — разные исходы;
INCOMPLETE не terminal и не означает research failure. Общий timeout UNKNOWN — client state, не receipt success.
Durable accepted receipt восстанавливается из commit record; producer читает её по transaction_id и ожидаемому hash.
Ошибочная попытка с тем же ID хранится отдельно по attempt hash и никогда не заменяет accepted receipt.
REPLAY ссылается на original accepted receipt. Transport timeout означает UNKNOWN, а не failed/accepted;
сначала query receipt/recovery, затем безопасный повтор тех же bytes/IDs. get receipt/read original — read-only,
без внешнего refresh/research. Точные callable names и query API — следующий application contract, MVP-009.

| Момент сбоя | Поведение после restart |
|---|---|
| Нет READY, partial payload/marker | INCOMPLETE; не импортировать, не удалить пользовательский пакет |
| Marker есть, schema/hash/refs невалидны | REJECTED с кодом; ноль изменений, retained diagnostic |
| Проверено, staging/storage copy есть, commit отсутствует | Uncommitted orphan; не виден в Bank; безопасный повтор валидации |
| Commit завершён, receipt/UI/index не созданы | Восстановить receipt/index из commit; повтор — REPLAY |
| Index/catalog потерян | Rebuild только по accepted records + verified retained bytes, без сети/изменения history |
| Повреждён retained file/commit | INTEGRITY_ERROR; явно обозначить unavailable, не выдумывать успешный rebuild |
| Неизвестна граница commit после timeout/crash | Recovery сначала проверяет durable ledger; до решения не выдаёт success/новый commit |

Rejected/conflicted packages не переименовываются/удаляются молча. Cleanup orphan/incomplete/history — отдельная
явная lifecycle policy с retention/backup; протокол не вводит delete или автоматическую публикацию в GitHub.
Экспериментальный catalog.json — disposable projection, не canonical accepted ledger.

## 7. Матрица приёмки реализации

Все строки ниже — pending_implementation; проверка design fixtures не закрывает их.

| ID | Сценарий | Требуемое наблюдение |
|---|---|---|
| LW01 | Supported independent report + attachment | ACCEPTED; оригинальные bytes/IDs доступны после reopen, без fictitious Run |
| LW02 | Повтор точных bytes/IDs после timeout | Original receipt; один commit/одна revision |
| LW03 | Same transaction ID, changed content/manifest | CONFLICT, original bytes/history неизменны |
| LW04 | Valid update и stale-base update | Новая revision и старый original сохранены; stale-base даёт conflict |
| LW05 | Два writers + multi-object transaction, один stale base | Serialized heads; conflict transaction не изменяет ни один объект |
| LW06 | Missing READY, truncated JSON, missing file, tampered bytes, extra file | Ignore incomplete / reject ready; нет partial objects |
| LW07 | Unsupported schema/type, duplicates, invalid UUID/date, unresolved refs, limits | Typed diagnostics; ноль canonical mutations |
| LW08 | Windows traversal/ADS/reserved path/case collision/reparse/hardlink и TOCTOU swap | Confinement rejection, ни одного чтения/записи вне разрешённых roots |
| LW09 | Fault injection до copy / после copy / до commit / после commit / до receipt | Restart даёт ровно ноль или один commit; receipt восстанавливается |
| LW10 | Удаление/повреждение индекса и изменение поисковой модели | Rebuild и исторический reopen без сети; corrupt originals обозначены как unavailable |
| LW11 | Tracked research с Source + attachment + frozen run + occurrences (R2) | Реальные pinned links/status/order сохраняются и открываются после продолжения |
| LW12 | Producer/app reopen в другом чате, реальные supported материалы | Command → receipt → read original → continuation, без duplicates; UI evidence в R1/R2 |
| LW13 | Crash/потеря питания в поддерживаемой Windows/storage configuration | Durable ACCEPTED подтверждён отдельно от atomic marker; отказ блокирует release |

## 8. Что подготовлено и что ещё требуется

Evidence сейчас: прежняя изолированная проба проверяла один synthetic report/READY hash, repeat scan и некоторые failures.
Этот шаг сохраняет design, envelope schema и два synthetic package fixtures; production importer, watcher/UI,
CAS/durable registry, schema allowlist и Windows safe handles ещё не реализованы и не испытаны.
Не объявлены R0/R1 acceptance или production save. OPEN-011/012 сохраняют OPEN_DECISION status.
Следующий шаг: минимальные persisted R1 Bank schemas и supported read/write versions, Source/Entity compatibility
boundary; затем реализация importer/receipts по этой матрице. Все design blockers до runtime перечислены выше.


## Minimal types checkpoint — 2026-10-06

BANK_TYPES_R1.md / BANK_TYPES.schema.json / BANK_SCHEMA_COMPATIBILITY.json define prepared R1 domain schemas and a separate Source/Entity boundary profile. BANK_TYPE_EXAMPLES are static synthetic fixtures; check_bank_contracts.py is read-only schema/link conformance tooling, not a production importer. R0-BANK-TYPES-001 evidence also performs standard JSON Schema validation of the earlier envelope/receipt schema and legacy synthetic fixtures. Production CAS/recovery/Windows confinement, supported-media limits and durable backend remain pending LW01–LW13.
