# UC19 — Audit or modify the reusable system

This file owns **procedure ordering only**. The complete use-case contract (routing, inputs/outputs, reads/writes, acceptance, failures, side effects, freshness/comparability, outcomes/transitions, UI/API links) is canonical only in `CORE/USE_CASE_REGISTRY.json`.

## Procedure

1. Run AX01–AX26 audit.
2. For architecture changes update canonical contract first.
3. Add regression tests for every fixed release-gate finding.
