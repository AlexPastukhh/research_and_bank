# R1 local storage and limits — decision checkpoint 1.0.0

2026-10-06; R0-LOCAL-STORAGE-001 / PLAN-LOCAL-WRITE / OPEN-011.
Selected R1 implementation design: one local SQLite DB owns accepted commits, all document/original bytes
and accepted receipts. This closes the minimal R1 backend choice, not production acceptance or every OPEN-011 question.
App R1/system versions and 115 requirement classifications remain unchanged. GitHub stays optional project history/sync.

## Why this backend

| Alternative | Disposition for R1 |
|---|---|
| SQLite + original BLOBs in the same transaction | Selected: standard local atomic commit, no external service, one accepted-state owner |
| SQLite metadata + external original files | Deferred: would need recovery/retention protocol across DB and file publication boundaries |
| Mutable JSON ledger + original files | Deferred: would introduce custom transaction/locking/recovery infrastructure |
| Server/cloud DB or Git as writeback backend | Not selected for first local exchange; future topology/migration triggers remain open |

This is a small personal/local store design, not an assertion that large media belongs in SQLite indefinitely.
Assets keep separate stable object IDs even for identical bytes; physical content dedupe/semantic merge NEW-008 not adopted.
Default future Bank root: `%LOCALAPPDATA%\ResearchAndBank\Bank`, configured/validated by app owner;
this task creates no production bank there. Project/checkout, public GitHub, cloud-synced and network roots
are not production defaults. Support local fixed-disk filesystem with correctly working SQLite VFS/locks/flush.
Custom/network/removable storage requires its own acceptance; privacy/encryption/backup destinations remain conditional/open.

## Physical version and authority

`LOCAL_STORAGE_SCHEMA.sql` defines candidate physical format v1, `user_version=1`, `application_id=1380076337`.
Minimum SQLite >=3.37 for STRICT tables; tested native version recorded in probe evidence. This is separate
from object schema versions and system/app releases. Reject mismatched existing DB format; never run CREATE
or reset pragmas/user_version over an unknown existing DB. No v1.11 registry/schema migration is performed.
Initial physical schema is created in one transaction only for a new validated DB; interrupted initialization
does not turn a partial schema into accepted Bank state. Check required tables/constraints as well as version headers.

Canonical append-only tables: commits, files, revisions, accepted_receipts. Files retain exact bytes under
transaction/document path mapping; no future canonical read depends on mutable intake paths.
Canonical receipt belongs to the same SQLite commit. A deferred cyclic FK requires receipt existence at commit.
Revisions point to retained file rows; operation order/old versions stay available. Immutable SQL triggers
forbid UPDATE/DELETE; DB migration/cleanup is a governed separate copy/restore operation, not disabling triggers.
attempt_receipts is separate append-only diagnostic state, never a replacement for original ACCEPTED receipt.
object_heads is a rebuildable view over committed revisions; search/extraction/vector indexes remain derived.
Damage/missing originals cannot be repaired from search index. Validate source DB and BLOB hashes before rebuilding.

Writable connection configuration: journal_mode=DELETE, synchronous=EXTRA (3), foreign_keys=ON,
trusted_schema=OFF; verify actual returned values before writes. Use defensive SQLite mode where required API available;
Python 3.12+ connection setconfig/getconfig is the intended writer adapter. No SQL/extension/VFS/ATTACH names from payload.
SQLite mode selection is based on official documentation: rollback journaling provides atomicity and EXTRA strengthens
durability in DELETE mode. It still depends on filesystem, VFS and storage honoring locks/flush operations.
Read-only application query connections do not initialize schema or silently run import/external refresh.
Never use OFF/MEMORY journals, NORMAL/OFF sync or read_uncommitted for Bank writes.

## Commit and recovery algorithm to implement

1. Under bounded safe intake read, validate strict envelope, domain schemas/provenance/refs and finite limits.
   Keep a closed private staged copy / secured handles; no filesystem security guarantee comes from SQLite.
2. BEGIN IMMEDIATE; lookup exact transaction/hash before base-head CAS. Busy/locked is retryable, not conflict or ACCEPTED.
3. Check all current base revisions and object types under the writer lock. Resolve pinned refs to retained/current-package
   revisions. A conflict on any operation rejects the entire object command; diagnostics can be recorded separately.
4. Insert commit record including exact manifest/READY/policy bytes, all original file BLOBs and all revision rows.
   Stream BLOBs with verified digest/count; cap allocation before zeroblob; close every BLOB handle before COMMIT.
   Insert original ACCEPTED receipt with app-generated attempt/commit IDs and the acquired commit sequence.
5. COMMIT returns success only after selected sync behavior. Then emit/return stored receipt. If COMMIT reports BUSY,
   do not claim success; retry within bounded lock budget or rollback. Unknown I/O/commit outcome requires reopen/recovery
   and exact transaction lookup before any replay; do not assume every SQLite exception means failed commit.
6. Abrupt process death before commit recovers journal on reopen; after commit, missing exported receipt/UI can be
   recreated from canonical DB. Same-ID/hash replay returns original result; changed hash conflicts. Do not remove journals.

SQLite does not enforce all application semantics: schema/UUID checks, type stability, active policy limits,
exact manifest/hash replay, cross-object base ownership and current-head CAS require importer checks.
The physical FK/unique constraints and append-only triggers support those checks but do not replace them.
No crash test performed here authorizes power-off of the user's computer.

## Initial finite intake policy

Canonical machine policy: `LOCAL_INTAKE_LIMITS.json`, policy_version `r1-local-limits/1`.
These are chosen conservative R1 implementation limits, not measurements of maximum throughput or accepted large-media UX.

| Limit | Initial value | Over limit |
|---|---|---|
| One file | 64 MiB (67,108,864 bytes) | LIMIT_EXCEEDED, no truncated import |
| Package total incl manifest/READY | 256 MiB (268,435,456 bytes) | LIMIT_EXCEEDED before large allocations |
| Data files / object operations | 128 / 128 | Whole command rejected |
| Manifest / READY | 512 KiB / 16 KiB | Reject before JSON parse |
| One object JSON / nesting | 2 MiB / 64 containers | Reject before decode/parser recursion; semantic checks after decode |
| Annotation body / title / one locator / diagnostic string | 1 MiB / 4,096 / 8,192 / 8,192 UTF-8 bytes | Explicit limit diagnostic |
| BLOB I/O chunk / writer lock wait | 1 MiB / 1,000 ms | Bounded I/O and retryable SQLITE_BUSY |

Enforce actual bytes, sizes/counts both during descriptor preflight and streaming; manifest claims alone insufficient.
JSON-depth preflight must respect strings/escapes, enforce bound before recursive decoder; static parsed-data probe
below only proves policy boundary semantics, not hostile parser behavior. Reject limit type/bool/floats and duplicates.
One policy snapshot/digest is retained per commit; changing policy does not retroactively invalidate old retained originals.
Large videos/PDFs and unsupported schemas are preserved in unaccepted intake with visible error, not silently shrunk
or redirected to GitHub/cloud. Raising limits/external raw storage requires memory/disk/latency/recovery evidence.
Disk-space preflight requires headroom for DB growth + rollback journal + staging; I/O/ENOSPC tests remain before release.

## Backup, integrity and later migration

Use SQLite online backup API to create a unique local snapshot, then integrity/FK/BLOB-hash checks before restore acceptance.
Restore into separate validated DB and reopen, never overwrite live Bank in place. Probe tests API snapshot round-trip
with live connection; concurrent-writer/large-media backup behavior is still a runtime gate. No automatic backup schedule,
cloud upload, encryption, retention deletion or destination is chosen here. Do not copy an actively written DB alone.
Physical version upgrade requires explicit copy converter and preservation of original IDs/history/receipts; failed migration
leaves prior DB untouched. Export API must provide exact original bytes and supported open metadata independently of SQLite.

## Evidence and remaining gate

`EXPERIMENTS/local_storage_commit/probe.py` uses synthetic direct SQL in disposable temporary DBs. It checks selected
pragmas, atomic multi-table commit/rollback, unique IDs/immutable rows, writer lock, stale-head guard, pre/post-commit
process death, receipt recovery, derived-head rebuild, backup snapshot and numeric/parsed-data policy boundaries.
It is not a production importer: no hostile intake/Windows safe handles, full schemas/provenance, UI, large-media throughput
or hardware power loss are accepted. LW01–LW13 remain runtime acceptance; power loss/OS/storage assumptions stay explicit.
Next step: bounded R1 importer with secure Windows intake reads, whole-command validation/CAS, SQLite writer and receipt
query/original retrieval. Proceed as implementation, preserve safety/failed inputs and run relevant LW cases on synthetic copies.

Official primary references, checked 2026-10-06:
- https://sqlite.org/pragma.html#synchronous — EXTRA/DELETE and per-connection settings.
- https://sqlite.org/atomiccommit.html — atomic single-database commit and storage assumptions.
- https://sqlite.org/lang_transaction.html — BEGIN IMMEDIATE, BUSY and BLOB handle lifetime.
- https://sqlite.org/backup.html — online snapshot API.
