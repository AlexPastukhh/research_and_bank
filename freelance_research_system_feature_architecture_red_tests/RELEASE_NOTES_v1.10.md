# Release Notes v1.10.0 — Stage 1

## Complete Use Case Contract v3

- Archived the vNext development plan and v1.9 baseline review inside the release.
- Added canonical System Map spec + generated System Map release artifacts.
- Bumped Use Case Registry to contract/registry v3.0.0.
- Expanded all existing 20 UCs with group, interaction type, actor intent, typed inputs/outputs, reads/writes, capabilities, freshness/comparability, acceptance, failure modes, side effects, idempotency, capability requirements, UI/API hooks, and Golden Path links.
- Removed duplicate acceptance/outcome contract text from workflow Markdown; workflows now own procedure ordering only.
- Added schema validation for the complete UC contract.
- Strengthened AX20/AX22–AX26 evidence without adding a new audit axis.

Phase 2 (UC21–UC25 result/query use cases) is intentionally not included in this release.
## Stage 1 acceptance revision

- Added explicit phase acceptance contracts to `REFERENCE/DEVELOPMENT_PLAN_vNext.md`; completion and acceptance are now separate concepts.
- Added recorded acceptance status for Phases 0–7 in `STAGE_STATUS.json`.
- Retrospectively reviewed Phase 0 and Phase 1 against their acceptance contracts.
- Acceptance review found and corrected a contradictory current migration target in `REFERENCE/MIGRATION_SUPPORT.md`.
- System Map now includes development/acceptance status as part of the living release view.
- Stage 1 acceptance evidence is stored in `AUDIT/RUNS/STAGE1_ACCEPTANCE_REVIEW_v1.10.0_2026-10-01.*`.

