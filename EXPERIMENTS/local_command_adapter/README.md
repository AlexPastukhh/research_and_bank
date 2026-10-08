# R1 local command entrypoint — synthetic component

Task R1-LOCAL-COMMAND-ADAPTER-001. Existing accepted secure reader, importer, typed reads and lexical search are delegated unchanged. The canonical `bank.sqlite` and existing `local-bank-intake/1` / `local-bank-query/1` protocols are preserved. This component supplies an actual CLI/controller for existing READY packages; package producer/editor and visible UI are separate future work.

```text
python commands.py save --bank-root BANK --intake-root INTAKE --stage-root STAGE --transaction-id UUID
python commands.py collection-save --bank-root BANK --intake-root INTAKE --stage-root STAGE --transaction-id UUID
python commands.py query --bank-root BANK --cache-root CACHE --output-root OUTPUT
python commands.py rebuild-search --bank-root BANK --cache-root CACHE
```

All roots are trusted operator configuration: absolute, pairwise disjoint, already existing/private, with native NTFS/root/parent/ACL checks when consumed. Commands never initialize Bank, rewrite an intake package, fetch a locator, render/execute originals, generate new retry IDs, or implicitly rebuild the index. Query reads one bounded unchanged request from stdin; its output remains the accepted closed query result. Cache/output roots are needed for search/original bytes respectively. Save requires an existing known-format Bank and validates the immutable secure snapshot once; collection-save rejects any non-Collection operation before invoking importer, then retains the importer's full validation/CAS/replay semantics.

Save output is the experimental `local_bank_command_outcome` result (save_result.schema.json), not a new canonical receipt protocol. It preserves exact importer status/code and receipt, or explicit null when no receipt exists. The reader can produce INCOMPLETE, IO_ERROR or CANCELLED; the writer can also produce CONFLICT, INTEGRITY_ERROR, RETRYABLE_BUSY and UNKNOWN. A bounded identity-correlated result is validated before returning. Unclassified failure after entering import or result/output loss remains UNKNOWN; inspect receipt.get with the same transaction/hash, then retry the exact same IDs/bytes if appropriate. A missing receipt does not prove failure. The canonical original accepted receipt is recovered separately; REPLAY does not replace it.

Snapshot handles are closed in finally. `cleanup_status=failed` exposes cleanup failure without negating known ACCEPTED/REPLAY; diagnostics contain only bounded codes. A child process killed during staging may leave an owned private quarantine directory; it is not Bank state and is not automatically deleted by application maintenance. The current writer has no durable failed-attempt ledger; receipt.get explicitly reports that limitation. Tests remove only their own synthetic roots.

Exit codes: 0 OK/BUILT/ACCEPTED/REPLAY; 2 other errors/conflicts/incomplete; 3 retryable writer busy; 4 unknown/lost stdout; 130 cancellation before import. Broken stdout is closed before process shutdown so Python does not replace exit4 with its flush-error exit120. A Commander timeout is a caller-side UNKNOWN regardless of whether an exit code was observed. Save acceptance is independent of search cache maintenance; a later query can require explicit rebuild and return INDEX_NOT_READY.

LIMITS.json references the unchanged intake/read/search caps and bounds save output to128KiB; fallback error output is bounded separately to8KiB. All requests/documents/media and outputs retain delegated component limits. No throughput claim for large real Bank follows; search audits its complete generation within explicit work limits.

LOCAL_RESULTS.json / NATIVE_RESULTS.json contain 30 per-case integration groups, actual CLI/controller paths, runtimes and source hashes. Tests cover save→receipt→read→rebuild→search→retained original→update→pinned reopen across process restart, mixed collections, CAS/replay/conflicts, exact bytes, no init/cleanup/fetch, native hardlink refusal, errors/limits/exports, busy, real importer fault states, interrupts, cleanup warning, child death before/after commit, and actual closed stdout recovery. Portable transport is a bounded trusted fixture, not native confinement proof. TEST_HISTORY/ISSUES retain failures and resolutions; original REVIEW_LOG remains intact; completion requires Windows evidence/readback receipt.

No user data is imported, real Bank installed, UI/producer implemented or R0/R1/privacy/backup/hardware release accepted.

## Native completion — 2026-10-07

30/30 local and30/30 Windows integration groups PASS, no skips, same source hashes. CMD1–CMD7 completed; actual CLI/default native secure reader/NTFS/SQLite, closed stdout exit4 and original receipt recovery, process death/restart verified. Completion receipt: PLANNING/WORK_ITEMS/R1_LOCAL_COMMAND_ADAPTER_RECEIPT.json. Review/ISSUES/TEST_HISTORY retained. Next producer card prepared; actual user workflow/install/UI/release remain pending.

## Current source follow-up — AWR-FIX-20261007-01

После AWR fixes текущая source-dependent evidence: [native regression](../completed_work_review/implementation_20261007/native/REGRESSION_NATIVE.json), [local regression](../completed_work_review/implementation_20261007/REGRESSION_LOCAL.json), [Review Log](../completed_work_review/implementation_20261007/REVIEW_LOG.json). Local247PASS/5 platform skips; native290PASS/294 with4 original reader Win1314 fixture blockers. Component LOCAL_RESULTS/NATIVE_RESULTS and previous receipts remain historical immutable runs; they are not rewritten to represent changed-source acceptance. Actual mapped UI10 cases PASS. Full reader native/release/real deployment not accepted.
