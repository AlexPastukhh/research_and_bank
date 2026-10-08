# SQLite importer — reviewed card, implementation pending

R1-SQLITE-IMPORTER-001 is **prepared**, not implemented. DB1–DB8 remain pending.

`CARD_REVIEW_2026-10-06.md` and `REVIEW_LOG.json` record the independent review. Four card gaps fixed: Asset-to-inventory binding, exact replay before new-command history/duplicate checks, bounded targeted history/iterative graph, and R1 independent-save intent. `ISSUES.json` retains open → card-resolved/runtime-pending history. `CARD_COUNTEREXAMPLES.json` records five actual native helper/API observations; `card_counterexamples.py` reproduces them using existing fixtures, own temporary copies and in-memory SQLite only. It is review tooling, not an importer or live Bank initializer.

Writable BLOB authority and canonical receipt/client outcomes are explicit implementation obligations. Trusted-writer BLOB mutation probe does not establish an incoming exploit. Current selected transport: app Туннель; original reader/contracts/static schemas and accepted baseline preserved.

Next: implement only the reviewed card, keep issue/retest history, native per-case evidence, hashes/backups/readback and no production/release claims. Review/correction evidence receipt: `CARD_REVIEW_RECEIPT.json`.

## Implementation checkpoint — portable tests complete, Windows verification pending

`importer.py` implements whole-command schema/Asset/intent/reference/CAS validation, exact replay, protected new-row BLOB streaming, atomic revisions/original receipt and recovery. `test_importer.py`: 42 groups PASS locally, Python 3.12.14 / SQLite 3.53.1. The portable adapter is a trusted immutable fixture; Windows must run the same suite through actual secure-reader snapshots before task completion.

Local failures fixed and retested: connection lock waiting, COMMIT BUSY classification, cancellation after committed success, SQLite FULL diagnostic preservation and hot-journal recovery before read. Previous runs retained in TEST_HISTORY; issue histories retained in ISSUES.json. A 64MiB original is streamed exactly, a 1100-command history is checked without full-history recursion, and SQLite FULL uses an owned database page limit, not filling the user's disk.

Read APIs expose no SQL/connections/writable BLOB handles. Writable BLOB capability only covers new rows of an active command. SQLite's own rollback of a hot journal may restore physical pages before a readonly query; this does not import a new command or create schema/acceptance. It runs only on an existing app-controlled candidate-format DB after header/root checks; journals are never removed manually. Unknown foreign headers/schema are rejected without initialization. Current owner/app/root parents remain trusted.

Tests use only synthetic owned temporary stores and child processes. No real Bank, UI/search, schema migration or hardware/VFS power-loss acceptance. Candidate contracts/SQL schema and accepted 1.11 baseline unchanged.

Native command:
```cmd
C:\Users\alexa\research_and_bank\PLANNING\TOOLS\.schema_validation_env\Scripts\python.exe C:\Users\alexa\research_and_bank\EXPERIMENTS\sqlite_importer\test_importer.py
```

Reference for required engine recovery: https://www.sqlite.org/lockingv3.html (hot-journal recovery before reading).

## Native completion — 2026-10-06

42/42 local and 42/42 Windows integration groups PASS, no skips; native actual secure-reader handles, Python 3.14.7/SQLite 3.50.4. DB1–DB8 completed; receipt in PLANNING/WORK_ITEMS/R1_SQLITE_IMPORTER_RECEIPT.json. First native failure and fixture/UTF-8 correction histories retained. Alias proof uses actual Windows hardlink+NTFS junction, Linux file symlink; Windows file-symlink creation unavailable (WinError1314), not claimed tested. Logical readonly API may first perform bounded SQLite-engine hot-journal rollback, then reopen readonly; it does not import or mutate canonical application history. Completion Review Log preserves production/privacy/hardware/read/search/UI follow-ups. Next card R1-BANK-READ-API-001 is prepared, review first.
