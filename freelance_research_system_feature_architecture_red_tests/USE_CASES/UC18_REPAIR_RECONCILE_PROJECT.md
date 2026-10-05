# UC18 — Repair and reconcile a project

This file owns **procedure ordering only**. The complete use-case contract (routing, inputs/outputs, reads/writes, acceptance, failures, side effects, freshness/comparability, outcomes/transitions, UI/API links) is canonical only in `CORE/USE_CASE_REGISTRY.json`.

## Procedure

1. Detect broken pointers/incomplete transactions/ledger conflicts.
2. Repair conservatively or mark unrecoverable.
3. Revalidate before research resumes.
