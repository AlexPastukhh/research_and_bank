# SQLite importer — reviewed card, implementation pending

R1-SQLITE-IMPORTER-001 is **prepared**, not implemented. DB1–DB8 remain pending.

`CARD_REVIEW_2026-10-06.md` and `REVIEW_LOG.json` record the independent review. Four card gaps fixed: Asset-to-inventory binding, exact replay before new-command history/duplicate checks, bounded targeted history/iterative graph, and R1 independent-save intent. `ISSUES.json` retains open → card-resolved/runtime-pending history. `CARD_COUNTEREXAMPLES.json` records five actual native helper/API observations; `card_counterexamples.py` reproduces them using existing fixtures, own temporary copies and in-memory SQLite only. It is review tooling, not an importer or live Bank initializer.

Writable BLOB authority and canonical receipt/client outcomes are explicit implementation obligations. Trusted-writer BLOB mutation probe does not establish an incoming exploit. Current selected transport: app Туннель; original reader/contracts/static schemas and accepted baseline preserved.

Next: implement only the reviewed card, keep issue/retest history, native per-case evidence, hashes/backups/readback and no production/release claims. Review/correction evidence receipt: `CARD_REVIEW_RECEIPT.json`.
