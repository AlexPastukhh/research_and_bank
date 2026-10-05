# UC04 — Discover candidate channels and sources

This file owns **procedure ordering only**. The complete use-case contract (routing, inputs/outputs, reads/writes, acceptance, failures, side effects, freshness/comparability, outcomes/transitions, UI/API links) is canonical only in `CORE/USE_CASE_REGISTRY.json`.

## Procedure

1. Search discovery routes.
2. Store candidates in SourceInbox with discovered_via.
3. Do not infer effectiveness from mentions.
