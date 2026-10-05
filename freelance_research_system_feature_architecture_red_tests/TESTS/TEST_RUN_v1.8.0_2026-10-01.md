# Test Run — v1.8.0 — 2026-10-01

## Full regression gate

- 14 runtime regression methods: PASS
- 10 use-case architecture test methods: PASS
- 46 routing fixtures inside the routing fixture contract: PASS
- Parallel full runner: PASS

Covered regressions include path confinement, task acceptance, enum/schema validation, manifest integrity, bootstrap workbook pointer, 1.7→1.8 migration, observation idempotency with independent-source provenance, temporal gap/new/reopen semantics, source-route comparability, immutable DailyRun finalization, secret redaction, dependency propagation and project-config strictness.

## Smoke

`init → validate → DailyRun → observation → finalize → checkpoint → validate`: PASS.

## Benchmark

100,000 synthetic observations / 25,000 entities processed below the declared 10-second release target: PASS.

## Workbook

Final formula error scan during workbook build: 0 matches. Required use-case/audit/architecture sheets are present.
