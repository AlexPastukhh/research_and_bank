# GP04 — Daily monitoring and diff

Creates two comparable dated runs, records stable/changed/new entities, builds a diff, verifies expected semantics, then routes UC09→UC17.

## Contract

The canonical request, expected UC sequence, and assertions are in `CORE/GOLDEN_PATH_REGISTRY.json`. This document is explanatory only; release conformance is executed by `TOOLS/run_golden_paths.py`.
