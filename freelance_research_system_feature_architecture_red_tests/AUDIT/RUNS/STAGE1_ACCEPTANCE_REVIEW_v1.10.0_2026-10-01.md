# Stage 1 Acceptance Review — v1.10.0 — 2026-10-01

Scope: **Phase 0 + Phase 1**. Acceptance model: **1.0.0**.

Acceptance means the intended post-stage system state is true. Automated checks are evidence, not the definition of acceptance.

| ID | Acceptance condition | Status | Evidence |
|---|---|---|---|
| A0.1 | Baseline identity is unambiguous | **PASS** | REFERENCE/BASELINE_v1.9.md records the v1.9 baseline identity/digest used for Stage 1 comparison. |
| A0.2 | The map has one generation path | **PASS** | CORE/SYSTEM_MAP_SPEC.json declares canonical inputs/outputs; TOOLS/generate_system_map.py is the generation path; REFERENCE/SYSTEM_MAP.* are derived. |
| A0.3 | The map is whole-system, not only a UC list | **PASS** | Generated map contains implemented UCs/transitions/workflows/dependencies, Golden Paths, AX01–AX26, development phase status and planned query/UI overlay. |
| A0.4 | Planned and implemented components cannot be confused | **PASS** | UC21–UC25/result products/UI are emitted under planned overlay; implemented UC count remains 20. |
| A0.5 | Drift is observable | **PASS** | TOOLS/generate_system_map.py --check returned SYSTEM MAP PARITY: OK. |
| A0.6 | The map is part of the release handoff | **PASS** | REFERENCE/SYSTEM_MAP.md/json/mmd and DEVELOPMENT_PLAN_vNext.md are release files; START_HERE/README point to architecture artifacts. |
| A1.1 | Every implemented UC is contract-complete | **PASS** | 20/20 UCs validate as Complete Contract v3; structural review found 0 missing/empty required contract surfaces; TESTS.test_use_cases 13/13 passed. |
| A1.2 | Canonical ownership is unambiguous | **PASS** | Workflow inspection found 0 duplicated Acceptance/Allowed outcome/Intent/Route sections; registry owns contract semantics; generated views are derived. |
| A1.3 | Existing behavior is preserved unless explicitly changed | **PASS** | GP01–GP06 pass 6/6; current use-case tests pass; Stage 1 full regression report records 16/16 groups PASS. Acceptance-revision delta only changes plan/status/map/docs, not research runtime semantics. |
| A1.4 | Declared dependencies describe the real execution surface | **PASS** | Architecture validator reports max dependencies 11 <= 12 and average 7.1 <= 8.0; reads/writes/capabilities are populated for all UCs. |
| A1.5 | Outcomes remain closed and deterministic | **PASS** | Structural review found 0 transition problems; use-case tests require every outcome exactly once and valid targets. |
| A1.6 | Generated human views remain derived | **PASS** | generate_use_case_views.py --check and generate_system_map.py --check both pass. |
| A1.7 | Upgrade/reuse remains viable | **PASS** | Direct v1.9→v1.10 migration test passed; migration preserves historical Task Manifest route-lineage version and updates project runtime version. |
| A1.8 | Release representations agree | **PASS** | VERSION/registry/workbook show v1.10.0 and registry/contract v3.0.0. Acceptance review found stale migration target text; it was corrected from v1.9.0 to v1.10.0 before final acceptance. |
| A1.9 | Release integrity is preserved | **PASS** | Manifest was rebuilt with all acceptance artifacts included; `validate_system.py` returned `SYSTEM VALIDATION: OK — 1.10.0`. Final package is rebuilt after this decision and checked for manifest/ZIP integrity. |
| A1.10 | The map reflects the accepted contract | **PASS** | Regenerated System Map includes development acceptance status: Phase 0/1 accepted; Phase 2–7 planned; UC21–UC25 remain planned overlay. |

## Findings during acceptance review

The review found one real consistency defect that ordinary Stage-1 contract tests did not catch: `REFERENCE/MIGRATION_SUPPORT.md` still called v1.9.0 the current direct migration target while the runtime migration already targeted v1.10.0. The document was corrected before the acceptance decision.

## Evidence rerun on the acceptance revision

- `validate_use_cases.py`: PASS — 20 complete v3 contracts.
- `validate_architecture.py`: PASS.
- generated Use Case view parity: PASS.
- generated System Map parity: PASS.
- `TESTS.test_use_cases`: 13/13 PASS.
- `TESTS.test_golden_paths`: 2/2 test methods PASS; executable Golden Paths: 6/6 PASS.
- direct v1.9→v1.10 migration regression: PASS.
- smoke: PASS.
- benchmark: PASS — 100,000 observations / 25,000 entities in ~0.30s against 10s limit.
- structural acceptance inspection: 0 missing/empty mandatory UC contract surfaces, 0 workflow contract duplication findings, 0 transition closure problems.

The Stage-1 test report already in the release records the earlier full regression gate as **16/16 groups PASS**. A monolithic full rerun was attempted during this acceptance revision but hit the environment runner timeout; because the acceptance-revision delta is documentation/status/map-generation only and the affected/current gates were rerun, this is recorded as evidence context rather than a failed acceptance condition.

## Decision

**ACCEPTED.** Phase 0 and Phase 1 satisfy all mandatory acceptance conditions. The acceptance review itself is included in the rebuilt manifest/package. Final ZIP integrity and digest are verified after this decision is recorded.

## Phase 0 questions & answers

Capture mode: `retrospective_reconstruction`.

| Question | Blocking | Post-execution answer / decision | Evidence |
|---|---|---|---|
| **Q0.1** What exact artifact is the immutable comparison baseline, and how is its identity preserved? | yes | The v1.9 release is the frozen comparison baseline and its identity/digest is recorded in REFERENCE/BASELINE_v1.9.md. Decision: Treat later stages as deltas from the recorded v1.9 baseline. | `REFERENCE/BASELINE_v1.9.md` |
| **Q0.2** Which architecture artifacts are canonical inputs and which are generated views? | yes | Canonical architecture inputs are declared by CORE/SYSTEM_MAP_SPEC.json; REFERENCE/SYSTEM_MAP.md/json/mmd are generated outputs. Decision: Only canonical inputs may own architecture semantics. | `CORE/SYSTEM_MAP_SPEC.json`, `TOOLS/generate_system_map.py` |
| **Q0.3** How will the map distinguish implemented components from planned components? | yes | Development status is explicit: implemented nodes come from canonical registries; future capabilities remain in the planned overlay/status. Decision: Never render planned elements as implemented. | `CORE/SYSTEM_MAP_SPEC.json`, `STAGE_STATUS.json`, `REFERENCE/SYSTEM_MAP.md` |
| **Q0.4** Which changes require System Map regeneration? | yes | Changes to system spec, use-case/golden-path registries, architecture budget, stage status, result/UI composition, methods/tools/schemas require regeneration. Decision: Map parity is part of release discipline. | `CORE/SYSTEM_MAP_SPEC.json` |
| **Q0.5** Must the map and development plan be included in every release handoff? | yes | Yes. System Map and Development Plan are release artifacts referenced from README/START_HERE. Decision: Include them in manifest/package and handoff. | `README.md`, `START_HERE_AGENT.md`, `REFERENCE/SYSTEM_MAP.md`, `REFERENCE/DEVELOPMENT_PLAN_vNext.md` |

## Phase 1 questions & answers

Capture mode: `retrospective_reconstruction`.

| Question | Blocking | Post-execution answer / decision | Evidence |
|---|---|---|---|
| **Q1.1** What must be knowable from a use case for it to count as contract-complete? | yes | Contract v3 makes group/interaction/intent, typed inputs/outputs, reads/writes/capabilities, freshness/comparability, acceptance, failures, side effects, idempotency, UI/API hooks, Golden Paths and transitions first-class. Decision: Require one schema for all implemented UCs. | `CORE/SCHEMAS/USE_CASE_REGISTRY_SCHEMA.json`, `CORE/USE_CASE_REGISTRY.json` |
| **Q1.2** Which semantics belong canonically in USE_CASE_REGISTRY and what remains in workflow Markdown? | yes | USE_CASE_REGISTRY owns routing, acceptance, outcomes, dependencies and transitions; workflow Markdown owns procedure ordering only. Decision: Remove competing editable contract sections from workflows. | `CORE/USE_CASE_REGISTRY.json`, `USE_CASES` |
| **Q1.3** How do we prove the contract refactor did not change established v1.9 behavior accidentally? | yes | Preserve old routing fixtures and GP01–GP06, plus temporal/runtime regression behavior. Decision: Contract refactor is accepted only if existing behavior remains green. | `CORE/USE_CASE_ROUTING_FIXTURES.json`, `CORE/GOLDEN_PATH_REGISTRY.json`, `TESTS` |
| **Q1.4** How detailed must reads, writes and capabilities be? | yes | Declare material direct reads/writes/capabilities and bound them with the architecture budget; do not enumerate every transitive implementation detail. Decision: Use dependency budgets to keep declarations useful and bounded. | `CORE/ARCHITECTURE_BUDGET.json`, `TOOLS/validate_architecture.py` |
| **Q1.5** How will existing projects move to the new contract/runtime version without rewriting historical lineage? | yes | Provide supported v1.9→v1.10 migration that updates runtime version/contract shape while preserving historical task route lineage. Decision: Migration is additive and history-preserving. | `TOOLS/migrate_project.py`, `REFERENCE/MIGRATION_SUPPORT.md` |
| **Q1.6** How will release representations be kept consistent across schemas, migration docs, workbook and generated views? | yes | Use generated view/map parity plus release validation and acceptance inspection across version-bearing artifacts. Decision: Release acceptance includes representation consistency, not only schema/test pass. | `TOOLS/generate_system_map.py`, `TOOLS/generate_use_case_views.py`, `TOOLS/validate_system.py` |
| **Q1.E1** Does migration documentation actually agree with the runtime migration target after the Stage 1 changes? | yes | No at first: MIGRATION_SUPPORT.md still named v1.9.0 as current target. It was corrected before acceptance. Decision: Treat documentation/runtime contradiction as blocking until fixed. | `REFERENCE/MIGRATION_SUPPORT.md`, `AUDIT/RUNS/STAGE1_ACCEPTANCE_REVIEW_v1.10.0_2026-10-01.md` |

