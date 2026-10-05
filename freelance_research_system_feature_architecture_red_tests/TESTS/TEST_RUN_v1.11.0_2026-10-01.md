# Test Run — v1.11.0 Stage 2 — 2026-10-01

## Summary

- Use-case validation: PASS — 25 complete v3 contracts.
- Use-case unittest suite: PASS — 16 tests.
- Architecture validation: PASS — 25 UCs / 6 groups / 5 query UCs / one router.
- Phase 2 acceptance validator: PASS — A2.1–A2.8.
- Golden Paths: PASS — 6/6 existing paths unchanged.
- Quick release regression gate: PASS — 8 groups.
- Runtime regressions: PASS — 14/14 methods, executed in isolated batches.
- Smoke: PASS.
- Benchmark: PASS — 100,000 observations / 25,000 entities in ~0.319 s (limit 10 s).
- Workbook formula scan: 0 errors.

## Routing preservation

All 47 v1.10 routing fixtures remain stable. New Phase-2 fixtures add English/Russian result queries and state-sensitive command/query distinctions.

## Harness note

The monolithic `run_tests.py --full` launcher can exceed the environment's single-call timeout. The same 14 runtime regression methods were therefore executed in isolated batches and all passed. Quick release gate remains green.


## Acceptance Q&A model patch

Targeted checks after acceptance model 1.1 integration:

- `TOOLS/validate_phase_records.py`: **PASS** — 8/8 phase records; accepted phases have 0 unresolved blocking questions; Phase 3–7 are prospective with pending answers.
- `TESTS.test_phase_records`: **2/2 PASS**.
- `TESTS.test_use_cases`: **16/16 PASS**.
- `TESTS.test_golden_paths`: **2/2 PASS**, including execution assertion for GP01–GP06 = 6/6.
- System Map parity: **PASS**.
- Phase Q&A view parity: **PASS**.

A combined quick launcher attempt again hit environment runner contention after the structural gates. This patch does not alter research runtime semantics; the already-recorded Stage-2 runtime/smoke/benchmark evidence remains unchanged, while all changed acceptance/map/use-case surfaces were rerun directly.
