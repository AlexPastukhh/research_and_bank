# R1 lexical search — synthetic component

Task: R1-LEXICAL-SEARCH-001. Canonical Store remains `bank.sqlite`; this component owns only a separate disposable `search-cache.sqlite3` in an existing private cache root. Existing importer, typed reads, canonical DDL and accepted baseline are unchanged.

## Operations

Use the same supported Python environment as the accepted importer (Python with SQLite defensive configuration and jsonschema). Both roots must already exist, be private and configured; the cache root must not overlap the Bank root.

```text
python search.py rebuild --bank-root BANK_ROOT --cache-root CACHE_ROOT
python search.py query --bank-root BANK_ROOT --cache-root CACHE_ROOT
```

`query` reads one bounded `bank.search` request from stdin using BANK_QUERY.schema.json. It emits a closed OK/ERROR JSON envelope. Rebuild emits BUILT/ERROR/UNKNOWN maintenance JSON; UNKNOWN is not a canonical accepted receipt and must be resolved by inspecting the published generation. Query never creates an index or silently rebuilds it. Profile mismatch requires an explicit rebuild.

## Semantics and integrity

NFC → casefold → NFC; letters/numbers and following combining marks form tokens. Distinct query tokens use literal AND matching across independently tokenized selected values. Current/all-revisions, pinned references, explicit canonical snapshot, exact coverage and totals, deterministic order and pagination follow BANK_SEARCH_R1.md. Only verified text/plain strict UTF-8 originals up to 4 MiB enter content postings; unsupported, invalid, absent and oversized content remains visibly classified, without network fetching or rendering.

Rebuild streams bounded canonical documents/originals for one snapshot and atomically replaces corpus/postings/generation in one cache transaction. Every query independently verifies the complete generation against retained canonical bytes and exact postings, including corruption after build. LIMITS.json specifies request/output/work/time/corpus/postings/cache limits. Exceeding a limit produces an error, never truncated successful coverage. This full-generation audit is a bounded correctness prototype; large-Bank latency/throughput has not been accepted.

Known-format cache hot journals may be rolled back by SQLite before reopening readonly; no application generation write or manual journal deletion occurs during query. Unknown cache files/schemas are rejected without reinitialization. Private root/NTFS checks reuse the accepted native reader; current owner, trusted code/operator and root parents remain trust assumptions.

## Evidence and history

LOCAL_RESULTS.json and NATIVE_RESULTS.json record runtime versions, source hashes and per-case assertions. The 34 integration groups include 22 independently expected control queries, oracle comparisons, original/cache corruption, profile mismatch, bounded SQL work, actual spill/process death and rollback, SQLite-full within an owned page cap, concurrency, restart, pagination and typed pinned reopen. TEST_HISTORY preserves previous results; ISSUES.json records failures and resolution transitions. REVIEW_LOG.json is the original independent card review; COMPLETION_REVIEW_LOG.json and the work-item receipt record completion only after native evidence passes.

No real Bank is initialized, no user files imported, and no UI, installation, whole-Unicode equivalence, hardware durability or R0/R1 release acceptance is claimed.
