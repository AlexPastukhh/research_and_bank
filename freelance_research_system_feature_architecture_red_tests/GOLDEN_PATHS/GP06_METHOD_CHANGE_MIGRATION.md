# GP06 — Method change requiring migration

Routes a method change to UC16, follows `migration_required` to UC20, migrates a synthetic v1.10 project to v1.11, validates it, then follows `migrated` to UC03.

## Contract

The canonical request, expected UC sequence, and assertions are in `CORE/GOLDEN_PATH_REGISTRY.json`. This document is explanatory only; release conformance is executed by `TOOLS/run_golden_paths.py`.
