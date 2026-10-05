# Test Run — v1.10.0 Stage 1 — 2026-10-01

## Complete Use Case Contract v3

- `TOOLS/validate_use_cases.py`: PASS — 20 complete v3 contracts.
- `TOOLS/validate_architecture.py`: PASS.
- `TESTS.test_use_cases`: 13 tests PASS.
- Full parallel regression gate: 16 test groups PASS.
- Golden Paths: 6/6 PASS.
- Smoke test: PASS.
- Benchmark: 100,000 observations / 25,000 entities in 0.3423s against 10s limit: PASS.
- Workbook formula error scan after Stage 1 update: 0 matches.
- Generated Use Case view parity: PASS.
- Generated System Map parity: PASS.

## Stage 1-specific regressions

- Every implemented UC validates against `CORE/SCHEMAS/USE_CASE_REGISTRY_SCHEMA.json`.
- Workflow Markdown is procedure-only and contains no Acceptance/Allowed-outcome contract copy.
- Golden Path membership in each UC is checked against the canonical Golden Path Registry.
- Registry v3 preserves routing/Golden Paths while adding typed I/O and dependency surfaces.
- Direct project migration v1.9.x → v1.10.0 passes.
