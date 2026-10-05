# Test Run — v1.9.0 — 2026-10-01

## Release-focused checks

- Golden Paths: **6/6 PASS**.
- Use-case + Golden Path unit suite: **12 tests PASS**.
- Quick regression gate: **8/8 groups PASS**.
- Runtime regressions: **14/14 cases observed PASS**; six are in the quick gate and the remaining eight were executed individually in isolated processes.
- Smoke test: **PASS**.
- Benchmark: **100,000 observations / 25,000 entities**, below the 10-second target.
- Workbook formula scan: **0 formula-error matches** after adding the `GoldenPaths` derived view.

## Golden-path coverage

GP01 checks new-project initialization; GP02 baseline continuation; GP03 paid-work research flow; GP04 dated monitoring/diff; GP05 source management; GP06 method-change migration.

The monolithic audit launcher is not used as evidence for this report because the current execution environment intermittently times out long nested subprocess trees. The constituent release checks above were executed directly.
