# UC09 — Monitor known scope over time

This file owns **procedure ordering only**. The complete use-case contract (routing, inputs/outputs, reads/writes, acceptance, failures, side effects, freshness/comparability, outcomes/transitions, UI/API links) is canonical only in `CORE/USE_CASE_REGISTRY.json`.

## Procedure

1. Start a dated Daily Run.
2. Collect append-only observations.
3. Finalize coverage and compare only with a compatible prior run.
4. Treat absence as not_seen unless terminal state is explicitly verified.
