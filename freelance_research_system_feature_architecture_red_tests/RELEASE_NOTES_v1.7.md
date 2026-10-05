# Release notes — v1.7

## Architectural simplification

- Added canonical `CORE/USE_CASE_REGISTRY.json` with 20 explicit use cases.
- Added one workflow file per use case under `USE_CASES/`.
- Task Manifests now require `use_case_id`.
- START_HERE routes every requested action through the registry before methods/sources are loaded.
- Research/monitoring decision trees are now derived navigation views, not independent routing contracts.
- Added `CORE/USE_CASE_ARCHITECTURE.md` to separate Use Case, Task Manifest, Method, Source, State and Principles responsibilities.
- Added routing/registry validation and helper tooling.

This release is intentionally architectural: it reduces duplicated orchestration logic without changing the underlying research/evidence/temporal semantics.
