# Bank operations, ownership and lifecycle — design 1.0.0

2026-10-06; R0-GATE-READINESS-001. Protocol `local-bank-query/1`; R1 target system 2.0.0-alpha.2 / app 0.1.0.
This is a scoped developer Proposal, recorded independently of the user's three answers. It changes no requirement classification, release number, persisted object schema or accepted baseline. No runtime endpoint is delivered here.

## Ownership and navigation

One personal local Bank is the canonical owner of Asset/Entity/Annotation/Collection revisions, original bytes and receipts. The application alone commits accepted state; ChatGPT/Commander submits commands and performs read-only queries. No Project, Lens, intake path or search cache owns raw bytes. The configured app-owned Bank root remains outside the repository by default.

R1 primary navigation: Bank, Collections, History. BankItem is a type+ID projection, Document an Asset view, Note an Annotation(kind=note), not new canonical identities. A working title suffices. Bank detail exposes type/ID, saved commit, provenance/author, original availability and revision history. Saved time is app accepted_at, not producer revision_created_at or event time. Collection detail preserves stored membership and order. Unsupported renderers are visible; opening HTML/markup cannot execute it.

Workspace is the single personal context, not an additional persisted R1 object. Future R2 Project organizes research references and presentation, not Bank ownership; Project removal must not delete Bank records. Lens owns semantic intent, SourcePolicy source boundary, Recipe methods, Watch cadence, immutable RunSpec the resolved execution snapshot. R1 accepts none of those richer types automatically. Reuse across future Projects references the same Bank identity; collaboration, separate workspaces and cross-Bank imports need their own design and identity mapping.

## Semantic operation surface

`BANK_QUERY.schema.json` validates closed read requests. Stable semantic names are independent of transport. The implementation task must supply an actual local CLI/helper and validated request/result exchange usable through Commander; these names are not already callable tools. Read calls never initialize a Bank, import intake, fetch a locator, execute research or publish data. Unknown protocol/fields/type/version are errors, without coercion.

| Operation | Inputs | Successful output and boundary |
|---|---|---|
| bank.save / collection.save | Existing `local-bank-intake/1` commit_revisions package; collection.save uses Collection operations | Existing durable ACCEPTED/REPLAY receipt, whole-command CAS; no new write envelope or ID allocation on retry |
| bank.get | Supported object_type, object_id, selector current or pinned revision_id | Exact validated persisted document, resolved pinned ref, commit_sequence and accepted_at; current resolved once in a read snapshot |
| collection.get | Same selector, Collection type only | Same revision document; members in stored order as pinned refs, no automatic latest substitution or recursive expansion |
| bank.original | Pinned Asset ref | bytes storage: exact retained BLOB, byte_length, sha256, media_type and display filename; locator storage: URI metadata with availability=locator_only, no bytes/fetch |
| bank.history | Supported type + object_id | Ordered newest-first retained revision refs with commit_sequence/accepted_at; paginated against explicit snapshot, not event-time history |
| bank.search | See BANK_SEARCH_R1.md | Pinned hits, matched field names, extraction coverage, resolved snapshot and profile identity; lexical results are not similarity/research judgments |
| receipt.get | transaction_id and nullable expected_manifest_sha256 | Original canonical accepted receipt if present; latest diagnostic attempt separately, never overriding accepted result; actual manifest hash returned for comparison |

Read success envelope: protocol, request_id, operation, status=OK, snapshot_sequence and operation-specific data above. Error envelope: same identity, status=ERROR, code, bounded plain-text message (<=8192 UTF-8 bytes), no success data. An unavailable Bank may omit snapshot_sequence (null), but never fabricate an empty success. Both envelopes and outputs need runtime conformance tests before release; existing BANK_TYPES/envelope schemas still validate their respective payloads. Exact original download uses a separately generated app-owned output handle/path, never a caller-supplied destination. Verify bytes before exposing OK; outputs must not use mutable intake paths. Do not inline arbitrarily large originals into JSON.

| Error | Required behavior |
|---|---|
| INVALID_REQUEST / UNSUPPORTED_PROTOCOL / UNSUPPORTED_TYPE / UNSUPPORTED_MODE | Reject before query, no silent fallback |
| OBJECT_NOT_FOUND / REVISION_NOT_FOUND / TYPE_MISMATCH | Pinned revision absent or wrong object/type never resolves to current |
| UNSUPPORTED_SCHEMA | Preserve retained original, report unsupported read; do not synthesize defaults |
| INTEGRITY_ERROR | Missing/corrupt retained bytes or inconsistent refs fail affected read; no success based on cache |
| BANK_UNAVAILABLE / BANK_BUSY | Visible unavailable/retryable, not empty Bank or new DB initialization |
| INDEX_UNAVAILABLE / INDEX_NOT_READY / INDEX_PROFILE_MISMATCH | Search incomplete/stale cache is an error, not zero matches |
| SNAPSHOT_NOT_AVAILABLE | Supplied sequence exceeds durable accepted history or cannot be read consistently |
| RECEIPT_NOT_FOUND / TRANSACTION_HASH_MISMATCH | Absence is not proof a command failed; different hash never replayed as caller success |
| LIMIT_EXCEEDED | Reject oversized query/output request; no silent truncation of individual data |

Current read returns a pinned ref that a caller can retain. Historical get/original uses precisely that ref after later updates. Read failure during a long operation is ERROR, not partial successful bytes. Integrity failures in search corpus prevent complete-success search for affected scope until repaired from validated originals; cache cannot repair originals. Collection detail can show an explicitly unavailable member, but cannot replace or omit it. Producer command timeout stays UNKNOWN until receipt lookup/recovery resolves it; retry exact same IDs/bytes, never create a new identity automatically.

## Retention and privacy boundary

Accepted commits, full revisions, originals and receipts are append-only with no automatic expiry or delete in R1. Removing membership creates a new Collection revision; older membership and original persist. Incomplete/rejected/conflicted packages stay unaccepted, visible with diagnostics; never searchable Bank objects. No automatic intake deletion, orphan cleanup, semantic dedupe or TTL is enabled. Closed private staging is never read as Bank state. Once a durable commit is established, a future explicit maintenance action may reclaim only disposable staging/cache and must verify it cannot remove canonical/history/pinned bytes. No cleanup implementation is delivered here.

Disk-full/backpressure must refuse or leave the command pending/rejected without partial canonical commit; no silent deletion of retained history to free space. A manual intake cleanup/export/restore requires a scoped action, inventory and retained diagnostics before removing user's material. Backups follow LOCAL_STORAGE_DECISION.md (online backup, integrity/FK/hash verification, separate validated restore); automatic scheduling and external destinations are undecided. This policy deliberately trades disk usage for retained originals; revisit on measured growth or a deletion request, not by silently weakening history.

Public sources plus possible own ideas/analysis, no secrets planned, are user decisions; ideas/analysis do not inherit public visibility. Extra AI analysis/embedding providers are not currently planned. Bank read through the existing authorized ChatGPT/Commander workflow returns only the requested material; there is no background bulk export or provider handoff. Implementation must validate roots/access, suppress unnecessary content in diagnostics, and review applicable COND-003 controls before nonpublic real use. A local path/hash alone does not establish privacy acceptance. PC-on availability is sufficient; PC-off means BANK_UNAVAILABLE, not a promised cloud fallback. Independently permitted retrieval capabilities remain available under their own scope.

## Acceptance boundary

Synthetic request/expected-ID checks are contract evidence, not an installed application. R1 must exercise command→receipt→pinned read→search→update→old reopen across restart, query errors/limits, integrity, cache rebuild and visible UI results. LW01–LW13 remain separate (LW11 is R2). No full R0, R1, hardware durability, Windows confinement or privacy acceptance follows from this document.
