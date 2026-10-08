# Минимальные persisted Bank types — design 1.0.0

Дата: 2026-10-06; R0-BANK-TYPES-001. System contract target 2.0.0-alpha.1.
Это проверяемый контракт для реализации R1 (system 2.0.0-alpha.2 / app 0.1.0), не runtime release.
Форма объектов: BANK_TYPES.schema.json; поддерживаемые пары type/schema: BANK_SCHEMA_COMPATIBILITY.json.
Local command envelope/receipt: LOCAL_WRITE_ENVELOPE.schema.json (`local-bank-intake/1`).

## Объекты и границы

| Тип | Persisted данные | Граница |
|---|---|---|
| Asset | Immutable original bytes с file_path/size/hash/media_type либо сохранённый URI locator | Locator не утверждает, что содержимое скачано; payload bytes копируются в app-owned storage |
| Entity | Canonical subject identity, entity_kind, aliases, external IDs и pinned asset_refs | Не acquisition Source; добавление alias не выполняет merge |
| Annotation | note/tag/comment/interpretation, текст, author, pinned targets | Может быть standalone Note с targets=[]; не raw evidence |
| Collection | Название и ordered pinned members разных R1 типов | В версиях сохраняется membership/order; одинаковый member не повторяется |
| Source | Acquisition source_kind/locator и nullable subject_entity_ref | R0 boundary fixture / R2 candidate; не доступен для записи профилем R1 |

Минимальное OPEN-004 решение для R1: BankItem — UX projection, type+ID исходного persisted объекта,
без второго canonical ID. Note — Annotation(kind=note), включая standalone; Document — представление
Asset с document media type. Отдельные Document/Note schemas, richer domain properties, extraction state,
Evidence/Observation и full Relation graph не вводятся этим шагом.
Это частичное разрешение R1 boundary, OPEN-004 остаётся OPEN_DECISION для будущего расширения.

Каждый объект содержит schema, object_type, object_id, revision_id, revision_created_at, title, provenance, data.
IDs — lowercase UUID v4; object_id остаётся стабильным, revision_id — новый при изменении.
revision_created_at — UTC время подготовки данной revision producer, не capture/event/app commit time.
Base revision находится только в envelope operation; app хранит собственные durable accepted_at/sequence.
Любое изменение создаёт новую полную immutable revision. Object type не меняется при update.
Источник истины для CAS/повторов — app commit registry, не этот static validator.

## Ссылки и происхождение

Typed reference = object_type + object_id + revision_id. Все ссылки pinned:
Annotation targets, Collection members, Entity assets, provenance derived_from и Source subject.
Существующая revision должна быть retained; смена current head не перенаправляет старую ссылку.
Application read оригинала возвращает именно эту revision; latest lookup — отдельная явная операция.
В одном пакете могут быть forward references, проверяются после полной валидации всех объектов.
Цикл derived_from внутри submitted package отклоняется; self reference также. Annotation targets и
Collection membership не имеют причинной семантики и не обязаны образовывать DAG.
Для ссылок на accepted objects app проверяет durable history; static fixtures передают её явно, без сети.

Provenance origin_kind: user_capture, external_capture, user_authored, ai_authored, derived, unknown.
producer name/version фиксирует исполнителя записи, не автоматически автора содержимого.
source_locator/captured_at nullable, unknown не заменяется текущим временем или выдуманным Source/Run.
external_capture требует source_locator; derived требует непустой derived_from.
source_ref nullable и типизирован отдельно как Source: профиль R1 требует null, R2 boundary допускает Source.
Annotation author отдельно: kind=user/ai/system/unknown, identity/model nullable;
для user/ai kind origin_kind должен соответственно быть user_authored/ai_authored.
Unknown author/AI model сохраняется null, не приписывается пользователю или выбранному провайдеру.
AI note, summary и saved research report не становятся независимым evidence от факта сохранения.
Файл AI report допустим как Asset(origin_kind=ai_authored), а не только source capture.

Source subject_entity_ref — null либо pinned Entity; Source-only local archive не требует Entity.
Два Sources могут ссылаться на одну Entity без объединения Sources. SourceRoute принадлежит Source;
route history/SourcePolicy/RunSpec/Observation ещё требуют R2/R4 контрактов. Source entity link не заменяет ownership route.
Не мигрируются SourceRegistry/SourceInbox v1.11; их схемы и IDs не переписываются.

## Сохранение и original retrieval

R1 supported forms в design: bytes Asset, URI locator Asset, standalone/targeted Annotation,
Entity metadata и mixed Collection. Text extraction, search ranking, renderer/media support и UI capabilities
определяются отдельно; сохранённый media_type не означает успешное извлечение текста или проигрывание.
Asset byte file descriptor должен совпадать с manifest descriptor и фактическими original bytes.
file_path — ссылка только внутри входящего пакета; app при commit сохраняет immutable original и mapping
на app-owned path, не открывает этот intake path при позднем read. Producer path не становится destination.
Locator URI ограничен http/https/file и возвращается как metadata; import не делает network/local fetch.
HTML/markup возвращается как original bytes либо безопасный text; просмотр не должен исполнять input.
Finite supported-media limits и private/backup policy остаются gate перед production.

## Совместимость

Registry — canonical allowlist; writer и reader поддерживают explicit type/schema_ref пары.
Профиль R1: Asset/Entity/Annotation/Collection v1. Source v1 — только design fixture profile
R0_SOURCE_BOUNDARY до отдельной R2 runtime приёмки. Наличие Source schema не означает поставку SourcePolicy.
Schema document закрыт по fields; отсутствующие обязательные, неизвестные поля/типы/версии дают error.
Envelope operation type/schema_ref/IDs совпадают с document. Никаких silent alias/coercion/default migrations.
Writer сохраняет v1; unknown v2 остаётся сохранённым входящим rejected package, accepted state не меняется.
Reader не подменяет unsupported original пустым объектом. Дальнейшая новая версия требует explicit read/write
matrix, converter tests, rollback/backup и retained original version. Даже additive поля требуют версии при closed schema.
System/app release numbers не равны protocol/object schema versions.
Legacy UUID formats/imports и v1.11 conversion пока unsupported, не «починяются» сменой identity.

## Evidence и следующий шаг

BANK_TYPE_EXAMPLES содержит synthetic create (Asset/Entity/Annotation/Collection), Annotation continuation
и Source-only/two Sources-one Entity boundary. Это fixture, не реальное исследование.
PLANNING/TOOLS/check_bank_contracts.py — read-only static conformance aid: standard JSON Schema,
profile allowlist, strict JSON, hashes/IDs/pinned links/provenance. Он не watcher/importer/ledger и не security boundary.
test_bank_contracts.py проверяет invalid schema/links/provenance/history/fixture bytes и envelope/receipt rules.
Production Windows confinement, CAS concurrency, durable commits, recovery/index/UI/real material workflow
ещё проверяются отдельно по LW01–LW13; R0/R1/PLAN-SOURCE-ENTITY полная приёмка не заявляется.
Следующий шаг: выбрать и обосновать локальный durable commit backend и finite intake limits для R1,
после чего реализовать importer/receipt/recovery с Windows confinement по local-write matrix.


## R1 local storage decision checkpoint — 2026-10-06

R0-LOCAL-STORAGE-001 selects local SQLite with immutable document/original BLOBs, revision records and accepted receipts in a single durable transaction; object_heads/search indexes remain derived. PLANNING/CONTRACTS/LOCAL_STORAGE_DECISION.md / LOCAL_STORAGE_SCHEMA.sql / LOCAL_INTAKE_LIMITS.json describe physical v1 and conservative R1 limits (64 MiB/file, 256 MiB/package, bounded counts/JSON). Bank root is app-owned outside the repository by default; no production bank is created by this design step.
OPEN-011 remains OPEN_DECISION: minimal R1 backend choice resolved, production secure importer/CAS/receipts/runtime/Windows/hardware acceptance and private/media/backup/cloud policy remain open. Source/Entity/object schema identities, 115 requirement classifications and all milestone versions unchanged. Synthetic direct-SQL mechanism evidence is separate from real Bank ingestion; see PLANNING/WORK_ITEMS/R0_LOCAL_STORAGE_RECEIPT.json.
