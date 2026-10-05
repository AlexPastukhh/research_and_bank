# Release Notes v1.9.0

## Golden Paths

- Added canonical `CORE/GOLDEN_PATH_REGISTRY.json`.
- Added six hermetic release-gate Golden Paths: new project, baseline continuation, paid-work research pipeline, daily monitoring, source management, and method-change migration.
- Added `TOOLS/select_use_case.py` to bind a routed request to `RUN_STATE.json` and persist route lineage in `LAST_ROUTE.json`.
- Added `TOOLS/apply_use_case_outcome.py` to execute canonical outcome transitions and persist workflow events.
- Added `TOOLS/run_golden_paths.py` with parallel isolated execution.
- Added `TESTS/test_golden_paths.py` and integrated Golden Paths into the test/release/audit gates.
- Added `LEDGER/WORKFLOW_EVENTS.jsonl` to initialized projects.
- Added direct project migration from v1.8.x to v1.9.0.
- Golden-path dogfooding found and fixed a UC15 routing gap for the natural-language request `добавь этот источник ...`.

Golden Paths remain hermetic. Live websites are deliberately excluded from the release gate.
