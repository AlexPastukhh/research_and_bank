# UC03 — Execute the next atomic task

This file owns **procedure ordering only**. The complete use-case contract (routing, inputs/outputs, reads/writes, acceptance, failures, side effects, freshness/comparability, outcomes/transitions, UI/API links) is canonical only in `CORE/USE_CASE_REGISTRY.json`.

## Procedure

1. Load exactly one Task Manifest.
2. Load only referenced methods/sources/principles.
3. Execute allowed actions and acceptance checks.
