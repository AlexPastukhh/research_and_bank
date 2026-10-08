# Universal bank and data model draft

## Why `Entity` alone is insufficient

The desired bank contains both real/conceptual things and stored material. A screenshot is not the same kind of object as the game shown in it; a web-page snapshot is not the same thing as the company described by it.

The model therefore needs separate layers.

## Proposed core concepts

### `Asset`
Stored content/bytes or an immutable capture.

Examples:

- image;
- video;
- audio;
- PDF;
- HTML/page snapshot;
- raw JSON/API response;
- screenshot;
- local file;
- archived text;
- source capture.

Important fields may include content hash, media type, size, capture provenance, stored-at time, source URI, original filename, and extraction status.

### `Entity`
A stable canonical identity for a thing in the observed/conceptual world.

Examples:

- game;
- app;
- company;
- person;
- job post/opportunity;
- article/story;
- product;
- technology;
- service unit in the freelance domain.

An entity may reference many assets and may accumulate observations over time. `Source` has separate canonical identity and is not an Entity subtype. Entity merge/split does not automatically merge/split Sources.

### `Source`
A durable acquisition endpoint/corpus, distinct from the real/conceptual subject or provider represented by an Entity. A Source may optionally reference that Entity; creating a Source does not require creating an Entity.

Examples:

- a local archive folder Source without any subject Entity;
- Reuters website Source and Reuters RSS Source, both optionally referencing the Reuters organization Entity.

### `SourceRoute`
Source-specific access/query configuration belongs to its Source, not to a linked Entity. A route change preserves Source identity; reusable route history is TARGET work.

These are the already confirmed vNext identity boundaries, not persisted schemas or changes to accepted v1.11. Exact persisted field names/cardinality and schema compatibility remain actual-types work before R0 acceptance.

### `Observation`
A source-linked statement or captured fact about an entity at a time.

Examples:

- price = 29.99;
- Steam concurrent players = 35,412;
- rating = 4.7;
- mechanics include colony management;
- opportunity payout = $150;
- source says company launched product X.

Observations are append-only where temporal history matters. Corrections should not silently rewrite prior evidence.

### `Event`
Something that happened or is believed to have happened.

Examples:

- game release;
- update release;
- price change;
- acquisition;
- funding round;
- article correction;
- vacancy closure;
- policy change.

### `MetricObservation`
Typed quantitative/categorical measurement with method/version, unit, scope and provenance.

### `Annotation`
User- or AI-authored interpretation, tag, note, classification, reaction or comment. It is not raw truth and must preserve author/model/method provenance.

### `Relation`
A typed link between objects.

Examples:

- game `uses_mechanic` mechanic;
- story `about` company;
- image `reference_for` project;
- app `competitor_of` app;
- entity `same_as` external ID;
- observation `supports` claim.

### `Collection`
User- or system-defined grouping of mixed bank items.

A collection can itself become a discovery/research seed. Example: “games with interesting inventory systems” may contain games, screenshots, videos, notes and articles.

### `Representation`
A derived searchable/comparable representation of a bank object.

Examples:

- text embedding;
- image embedding;
- style embedding;
- mechanics vector;
- theme vector;
- audience vector;
- perceptual hash;
- OCR text;
- generated caption;
- graph features.

Representations must be versioned by model/method. Re-embedding must create a new representation version rather than rewriting the canonical item.

### `BankItem`
Optional UX/container abstraction that lets the application say “save this” while the internal target can be an Asset, Entity, Note, Collection or other supported durable object.

### `ResultSet` / `ResultOccurrence`
A research/search run may return an already-known bank item without creating a new external observation. Historical reproducibility therefore needs a durable record of **what the run returned**, not only what facts were observed.

Proposed draft concepts:

- `ResultSet` — immutable identity for one produced candidate/result set within a run;
- `ResultOccurrence` — membership of a bank item in that result set, with its role and retrieval context at that time.

A `ResultOccurrence` may retain:

- `run_id` / `result_set_id` / `item_id`;
- candidate/result role;
- rank/order at production time;
- retrieval/similarity profile and version;
- score vector or named similarity dimensions when meaningful;
- matched representations/features and human-readable reason/explanation;
- bank-only vs external-discovery origin;
- source-route/tool lineage when external acquisition contributed;
- produced-at time and relevant method/model versions.

This is **lineage**, not a new claim that the item itself changed. Later re-ranking or re-embedding must not rewrite an older result occurrence. The exact persisted shape remains a vNext architecture decision, but the historical requirement is now explicit.

## Roles are independent of object type

An item can carry one or more contextual roles without changing its canonical identity:

```text
saved
favorite
search_seed
research_seed
research_result
evidence
counterevidence
reference
comparison_item
collection_member
monitored_subject
```


## Epistemic class and evidence eligibility

Because the bank can contain arbitrary saved material, **being in the bank does not automatically make an item independent evidence**. Research methods should explicitly distinguish epistemic role from storage role.

Candidate epistemic classes include:

- `source_capture` / `source_assertion` — externally captured material or an assertion attributable to a source;
- `user_annotation` — user-authored note/judgment;
- `ai_annotation` — model-authored interpretation/classification;
- `derived_metric` — deterministic/statistical result derived from identified inputs and a method version;
- `synthesized_interpretation` — higher-level synthesis derived from other evidence/results;
- `claim` / `result_product` — research output whose support graph is explicit.

Evidence eligibility is method- and claim-specific. A derived item must not be counted as **independent confirmation of its own upstream inputs** merely because it was saved and rediscovered later. Preserve `derived_from` / dependency lineage and, where relevant, independence groups or equivalent semantics.

This section is a guardrail for future implementation, not a retroactive claim that current v1.11 evidence contracts are defective.

## Identity resolution

Cross-run and cross-source canonical identity is essential. Suggested staged strategy:

1. exact stable external IDs;
2. deterministic aliases/canonicalization;
3. probabilistic record linkage;
4. semantic similarity and domain rules;
5. AI-assisted adjudication for ambiguous cases;
6. explicit user merge/split/correction path.

The system should preserve identity confidence and merge/split history rather than pretending every resolution is certain.

## Time model

Do not overload one `created_at`.

Possible times include:

- `saved_at` — user/system saved the item;
- `captured_at` — source content was captured;
- `observed_at` — system observed a fact;
- `first_seen_at` / `last_seen_at` — lifecycle in our observation system;
- domain event times such as `released_at`, `published_at`, `posted_at`, `announced_at`, `closed_at`;
- `valid_time` — when a fact was true in the outside world;
- `system_time` — when the system learned/recorded it.

Bitemporal semantics (`valid_time` + `system_time`) should be evaluated for historical correctness and backfilled research.

## Not everything must be monitored

Saving is cheap and passive. Monitoring is an explicit opt-in role/policy. A stored image may remain static forever; a game or company may be watched daily; an image could still anchor a watch for “find new appearances/similar items elsewhere”.


## News/content distinction: Publication, Story and Event

For news-oriented domain packs, avoid collapsing source content and real-world occurrences into one identity:

- **Publication/Article** — a source-authored content item (often backed by an Asset/snapshot);
- **Story/Narrative** — a versioned semantic grouping of related publications/coverage around a developing subject;
- **Event** — an occurrence in the observed world with its own valid/event time.

One publication may mention multiple events; one event may be covered by many publications; a story may span multiple related events. Story clustering is derived and may evolve as new evidence arrives. This preserves source diversity instead of resolving many articles directly into one event entity.

## Raw → normalized → analytical layers

A medallion-like separation is useful:

- **Raw/Bronze** — immutable captures and source payloads;
- **Normalized/Silver** — validated entities, observations, relations, resolved identity;
- **Analytical/Gold** — current state, trends, clusters, scores, projections, interpretations.

Derived Gold data must be reproducible from versioned lower layers and methods where practical.

## Avoid a universal mega-schema

The universal bank should define protocols and common metadata, not one gigantic object with every field for every domain. Domain schemas/packs should add typed properties and metrics without forcing core changes.


## Minimal persisted R1 contract checkpoint — 2026-10-06

R0-BANK-TYPES-001 prepared PLANNING/CONTRACTS/BANK_TYPES_R1.md, BANK_TYPES.schema.json and BANK_SCHEMA_COMPATIBILITY.json. Asset/Entity/Annotation/Collection v1 support independent save semantics; BankItem/Document are views of existing canonical objects, standalone Note is Annotation(kind=note). Source v1 is a separate R0 boundary/R2 candidate with nullable pinned Entity link; R1 write profile excludes Source. No fake Source/Entity/Run is required to save a file/note.
Standard JSON Schema and static package conformance evidence are recorded in PLANNING/WORK_ITEMS/R0_BANK_TYPES_RECEIPT.json. Original bytes, author/provenance and pinned revision refs are distinct. Existing 115 classifications/IDs/MVP/TARGET stages remain; richer types, R2 SourcePolicy/research, SourceRoute schema/history and runtime durability/confinement/acceptance are separate. OPEN-004 only minimum R1 boundary checkpoint resolved; no full R0/release or schema migration acceptance.


## R1 local storage decision checkpoint — 2026-10-06

R0-LOCAL-STORAGE-001 selects local SQLite with immutable document/original BLOBs, revision records and accepted receipts in a single durable transaction; object_heads/search indexes remain derived. PLANNING/CONTRACTS/LOCAL_STORAGE_DECISION.md / LOCAL_STORAGE_SCHEMA.sql / LOCAL_INTAKE_LIMITS.json describe physical v1 and conservative R1 limits (64 MiB/file, 256 MiB/package, bounded counts/JSON). Bank root is app-owned outside the repository by default; no production bank is created by this design step.
OPEN-011 remains OPEN_DECISION: minimal R1 backend choice resolved, production secure importer/CAS/receipts/runtime/Windows/hardware acceptance and private/media/backup/cloud policy remain open. Source/Entity/object schema identities, 115 requirement classifications and all milestone versions unchanged. Synthetic direct-SQL mechanism evidence is separate from real Bank ingestion; see PLANNING/WORK_ITEMS/R0_LOCAL_STORAGE_RECEIPT.json.
