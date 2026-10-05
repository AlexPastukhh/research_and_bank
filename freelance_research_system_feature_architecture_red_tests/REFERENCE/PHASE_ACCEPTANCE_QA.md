# Phase Acceptance — Questions & Answers

This is a generated human view. Canonical question/answer records live under `AUDIT/PHASE_EXECUTION_RECORDS/`. Questions are captured before execution (or explicitly marked retrospective for completed legacy phases); answers are added after implementation and before acceptance.

| Phase | Status | Capture | Questions | Answered | Unresolved blocking | Record |
|---:|---|---|---:|---:|---:|---|
| 0 | accepted | retrospective_reconstruction | 5 | 5 | 0 | `AUDIT/PHASE_EXECUTION_RECORDS/PHASE0_EXECUTION_RECORD.json` |
| 1 | accepted | retrospective_reconstruction | 7 | 7 | 0 | `AUDIT/PHASE_EXECUTION_RECORDS/PHASE1_EXECUTION_RECORD.json` |
| 2 | accepted | retrospective_reconstruction | 8 | 8 | 0 | `AUDIT/PHASE_EXECUTION_RECORDS/PHASE2_EXECUTION_RECORD.json` |
| 3 | planned | prospective | 8 | 0 | 8 | `AUDIT/PHASE_EXECUTION_RECORDS/PHASE3_EXECUTION_RECORD.json` |
| 4 | planned | prospective | 5 | 0 | 5 | `AUDIT/PHASE_EXECUTION_RECORDS/PHASE4_EXECUTION_RECORD.json` |
| 5 | planned | prospective | 5 | 0 | 5 | `AUDIT/PHASE_EXECUTION_RECORDS/PHASE5_EXECUTION_RECORD.json` |
| 6 | planned | prospective | 5 | 0 | 5 | `AUDIT/PHASE_EXECUTION_RECORDS/PHASE6_EXECUTION_RECORD.json` |
| 7 | planned | prospective | 6 | 0 | 6 | `AUDIT/PHASE_EXECUTION_RECORDS/PHASE7_EXECUTION_RECORD.json` |

## Phase 0 — Baseline & living System Map contract

Status: **accepted**. Capture: `retrospective_reconstruction`.

### Q0.1 — What exact artifact is the immutable comparison baseline, and how is its identity preserved?

- Why it mattered: Without a frozen baseline later architecture changes cannot be compared reliably.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: The v1.9 release is the frozen comparison baseline and its identity/digest is recorded in REFERENCE/BASELINE_v1.9.md.
- Decision: Treat later stages as deltas from the recorded v1.9 baseline.
- Acceptance impact: Supports A0.1.
- Evidence: `REFERENCE/BASELINE_v1.9.md`

### Q0.2 — Which architecture artifacts are canonical inputs and which are generated views?

- Why it mattered: The map must not become a second source of truth.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Canonical architecture inputs are declared by CORE/SYSTEM_MAP_SPEC.json; REFERENCE/SYSTEM_MAP.md/json/mmd are generated outputs.
- Decision: Only canonical inputs may own architecture semantics.
- Acceptance impact: Supports A0.2 and AX24.
- Evidence: `CORE/SYSTEM_MAP_SPEC.json`, `TOOLS/generate_system_map.py`

### Q0.3 — How will the map distinguish implemented components from planned components?

- Why it mattered: A user must not confuse roadmap items with working runtime capabilities.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Development status is explicit: implemented nodes come from canonical registries; future capabilities remain in the planned overlay/status.
- Decision: Never render planned elements as implemented.
- Acceptance impact: Supports A0.3–A0.4.
- Evidence: `CORE/SYSTEM_MAP_SPEC.json`, `STAGE_STATUS.json`, `REFERENCE/SYSTEM_MAP.md`

### Q0.4 — Which changes require System Map regeneration?

- Why it mattered: Living documentation only works if drift has an explicit trigger.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Changes to system spec, use-case/golden-path registries, architecture budget, stage status, result/UI composition, methods/tools/schemas require regeneration.
- Decision: Map parity is part of release discipline.
- Acceptance impact: Supports A0.5.
- Evidence: `CORE/SYSTEM_MAP_SPEC.json`

### Q0.5 — Must the map and development plan be included in every release handoff?

- Why it mattered: The map is useful only if it travels with the system.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Yes. System Map and Development Plan are release artifacts referenced from README/START_HERE.
- Decision: Include them in manifest/package and handoff.
- Acceptance impact: Supports A0.6.
- Evidence: `README.md`, `START_HERE_AGENT.md`, `REFERENCE/SYSTEM_MAP.md`, `REFERENCE/DEVELOPMENT_PLAN_vNext.md`

Acceptance review: `AUDIT/RUNS/STAGE1_ACCEPTANCE_REVIEW_v1.10.0_2026-10-01.md`

## Phase 1 — Complete Use Case Contract v3

Status: **accepted**. Capture: `retrospective_reconstruction`.

### Q1.1 — What must be knowable from a use case for it to count as contract-complete?

- Why it mattered: A partial route description is insufficient for implementation, audit, UI and handoff.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Contract v3 makes group/interaction/intent, typed inputs/outputs, reads/writes/capabilities, freshness/comparability, acceptance, failures, side effects, idempotency, UI/API hooks, Golden Paths and transitions first-class.
- Decision: Require one schema for all implemented UCs.
- Acceptance impact: Supports A1.1.
- Evidence: `CORE/SCHEMAS/USE_CASE_REGISTRY_SCHEMA.json`, `CORE/USE_CASE_REGISTRY.json`

### Q1.2 — Which semantics belong canonically in USE_CASE_REGISTRY and what remains in workflow Markdown?

- Why it mattered: Duplicate editable ownership creates drift.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: USE_CASE_REGISTRY owns routing, acceptance, outcomes, dependencies and transitions; workflow Markdown owns procedure ordering only.
- Decision: Remove competing editable contract sections from workflows.
- Acceptance impact: Supports A1.2 and AX24.
- Evidence: `CORE/USE_CASE_REGISTRY.json`, `USE_CASES`

### Q1.3 — How do we prove the contract refactor did not change established v1.9 behavior accidentally?

- Why it mattered: A structural refactor must preserve routing/runtime semantics.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Preserve old routing fixtures and GP01–GP06, plus temporal/runtime regression behavior.
- Decision: Contract refactor is accepted only if existing behavior remains green.
- Acceptance impact: Supports A1.3.
- Evidence: `CORE/USE_CASE_ROUTING_FIXTURES.json`, `CORE/GOLDEN_PATH_REGISTRY.json`, `TESTS`

### Q1.4 — How detailed must reads, writes and capabilities be?

- Why it mattered: Dependencies must be useful without exploding architecture complexity.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Declare material direct reads/writes/capabilities and bound them with the architecture budget; do not enumerate every transitive implementation detail.
- Decision: Use dependency budgets to keep declarations useful and bounded.
- Acceptance impact: Supports A1.4 and AX26.
- Evidence: `CORE/ARCHITECTURE_BUDGET.json`, `TOOLS/validate_architecture.py`

### Q1.5 — How will existing projects move to the new contract/runtime version without rewriting historical lineage?

- Why it mattered: Reuse and backward compatibility are release requirements.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Provide supported v1.9→v1.10 migration that updates runtime version/contract shape while preserving historical task route lineage.
- Decision: Migration is additive and history-preserving.
- Acceptance impact: Supports A1.7.
- Evidence: `TOOLS/migrate_project.py`, `REFERENCE/MIGRATION_SUPPORT.md`

### Q1.6 — How will release representations be kept consistent across schemas, migration docs, workbook and generated views?

- Why it mattered: Version/document drift can invalidate an otherwise green implementation.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Use generated view/map parity plus release validation and acceptance inspection across version-bearing artifacts.
- Decision: Release acceptance includes representation consistency, not only schema/test pass.
- Acceptance impact: Supports A1.6/A1.8/A1.9.
- Evidence: `TOOLS/generate_system_map.py`, `TOOLS/generate_use_case_views.py`, `TOOLS/validate_system.py`

### Q1.E1 — Does migration documentation actually agree with the runtime migration target after the Stage 1 changes?

- Why it mattered: This inconsistency was discovered during acceptance review and was not caught by contract tests.
- Blocking: **yes**
- Origin: `acceptance review`
- Answer status: **answered**
- Answer: No at first: MIGRATION_SUPPORT.md still named v1.9.0 as current target. It was corrected before acceptance.
- Decision: Treat documentation/runtime contradiction as blocking until fixed.
- Acceptance impact: This finding directly prevented premature acceptance and strengthens A1.8.
- Evidence: `REFERENCE/MIGRATION_SUPPORT.md`, `AUDIT/RUNS/STAGE1_ACCEPTANCE_REVIEW_v1.10.0_2026-10-01.md`

Acceptance review: `AUDIT/RUNS/STAGE1_ACCEPTANCE_REVIEW_v1.10.0_2026-10-01.md`

## Phase 2 — Result/query use cases and command/query boundary

Status: **accepted**. Capture: `retrospective_reconstruction`.

### Q2.1 — Should user intents that read/show existing research results be first-class use cases separate from research commands?

- Why it mattered: Without this boundary UI/read-side requests get mixed with data collection.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Yes. UC21–UC25 are first-class query UCs representing Current State, Changes, Trend, Interpretation and Research Health.
- Decision: Model read/explain intents separately from command UCs.
- Acceptance impact: Supports A2.1.
- Evidence: `CORE/USE_CASE_REGISTRY.json`, `CORE/RESULT_PRODUCT_CONTRACTS.json`

### Q2.2 — Should every future UI screen become a use case?

- Why it mattered: Screen composition and domain intent are not the same abstraction.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: No. Composite screens such as Direction Detail invoke multiple query UCs and command actions but are not domain use cases.
- Decision: Keep screen composition in UI mapping/System Map.
- Acceptance impact: Supports A2.4.
- Evidence: `REFERENCE/UI_SCREEN_MAP.md`, `CORE/SYSTEM_MAP_SPEC.json`

### Q2.3 — Should projection builders become top-level use cases?

- Why it mattered: Internal implementation capabilities should not inflate the user-intent registry.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: No. Projection builders remain capabilities/internal implementation, not top-level UCs.
- Decision: Avoid internal build/render UCs.
- Acceptance impact: Supports A2.5 and AX26.
- Evidence: `CORE/USE_CASE_REGISTRY.json`, `REFERENCE/SYSTEM_MAP.md`

### Q2.4 — How do we distinguish “show what changed” from “run research to find what changed”?

- Why it mattered: Natural-language overlap requires deterministic command/query boundaries.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Route using action intent plus state hints: existing result/read intent selects UC22; explicit refresh/research intent selects UC09 (and analogous boundaries for other products).
- Decision: Preserve user intent rather than routing by screen wording.
- Acceptance impact: Supports A2.2–A2.3.
- Evidence: `CORE/USE_CASE_ROUTING_FIXTURES.json`, `TOOLS/route_use_case.py`

### Q2.5 — May query use cases mutate research truth or silently trigger refresh/measurement?

- Why it mattered: Read-side semantics must remain predictable and auditable.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: No. Query UCs are read-only with writes=[]; missing/stale data is surfaced, not silently repaired by mutation.
- Decision: Refresh remains an explicit command-side action.
- Acceptance impact: Supports A2.3.
- Evidence: `CORE/USE_CASE_REGISTRY.json`, `TOOLS/validate_stage2_acceptance.py`

### Q2.6 — Is increasing from 20 to 25 top-level UCs architecturally justified?

- Why it mattered: The new capability must not bypass the complexity budget.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Yes, because result/query is a genuinely new user-capability class. The budget is explicitly revised to 25 UCs, six groups and five query UCs while retaining one router.
- Decision: Accept bounded complexity increase, not arbitrary growth.
- Acceptance impact: Supports A2.7.
- Evidence: `CORE/ARCHITECTURE_BUDGET.json`, `TOOLS/validate_architecture.py`

### Q2.7 — Are the five result products real backend outputs in Phase 2, or only contracts until Phase 3?

- Why it mattered: The release must not overclaim implementation readiness.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **answered**
- Answer: Only the query contracts and typed result-product contracts are implemented in Phase 2. Projection/build execution remains Phase 3.
- Decision: Mark backend projection layer planned and never claim products are buildable yet.
- Acceptance impact: Supports A2.8 and prevents capability overclaiming.
- Evidence: `CORE/RESULT_PRODUCT_CONTRACTS.json`, `REFERENCE/SYSTEM_MAP.md`, `STAGE_STATUS.json`

### Q2.E1 — Did adding UC21–UC25 change any of the 47 pre-existing v1.10 routing fixtures?

- Why it mattered: A new query plane must not regress established command/lifecycle routing.
- Blocking: **yes**
- Origin: `acceptance review`
- Answer status: **answered**
- Answer: No. All 47 v1.10 routing fixtures were preserved with zero regressions, and GP01–GP06 remained green.
- Decision: Accept new query routing only after legacy route preservation is demonstrated.
- Acceptance impact: Supports A2.6.
- Evidence: `REFERENCE/PHASE2_ROUTING_BASELINE_v1.10.json`, `AUDIT/RUNS/STAGE2_ACCEPTANCE_REVIEW_v1.11.0_2026-10-01.md`

Acceptance review: `AUDIT/RUNS/STAGE2_ACCEPTANCE_REVIEW_v1.11.0_2026-10-01.md`

## Phase 3 — Result Projection / Query layer

Status: **planned**. Capture: `prospective`.

### Q3.1 — For each of the five result products, what exact runtime artifacts are authoritative inputs?

- Why it mattered: Projection correctness depends on an explicit truth surface.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q3.2 — Which products are persisted versus deterministically derived on read, and why?

- Why it mattered: Persistence changes identity, freshness, invalidation and reproducibility.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q3.3 — What is the canonical freshness/invalidation policy and how is it versioned?

- Why it mattered: Current State and Health cannot be reliable without one policy.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q3.4 — Which measurement/economics/claim histories must become first-class runtime stores before projections are possible?

- Why it mattered: Some concepts currently exist mainly as schemas/workbook surfaces.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q3.5 — How will every projected result record builder version, input refs and reversible lineage?

- Why it mattered: AX25 requires results to trace back to runtime truth.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q3.6 — How should query UCs respond to stale/insufficient/not-comparable inputs without silently mutating research state?

- Why it mattered: Read-side purity must survive real implementation.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q3.7 — How will ChangeSet and TrendSeries reuse one compatibility model instead of diverging?

- Why it mattered: Duplicate comparability rules would create contradictory user results.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q3.8 — If caching is introduced, can it be proven semantically transparent and non-mutating to research truth?

- Why it mattered: Performance optimization must not change query meaning.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance


## Phase 4 — Query-side Golden Paths

Status: **planned**. Capture: `prospective`.

### Q4.1 — What minimal hermetic fixture represents valid runtime truth for each result product?

- Why it mattered: Golden Paths need realistic but deterministic inputs.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q4.2 — Which insufficient/stale/not-comparable negative outcomes must be represented explicitly?

- Why it mattered: Happy-path-only assurance would overstate readiness.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q4.3 — How exactly should GP12 compose stale query → command refresh → fresh query without bypassing UCs?

- Why it mattered: This path proves read/write composition rather than helper coupling.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q4.4 — How will GP07–GP12 remain network-independent while still exercising public contracts?

- Why it mattered: Release conformance must be stable and hermetic.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q4.5 — What evidence shows GP01–GP06 semantics remain unchanged?

- Why it mattered: Read-side assurance must not regress command-side paths.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance


## Phase 5 — UI mapping as derived composition

Status: **planned**. Capture: `prospective`.

### Q5.1 — Which query UC/result product owns every visible screen block?

- Why it mattered: Every displayed result must be traceable to backend contracts.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q5.2 — Which UI actions are commands and which are pure query/filter operations?

- Why it mattered: UI controls must not blur mutation boundaries.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q5.3 — What are the required stale, partial, not-comparable, insufficient-evidence and failure states for each screen?

- Why it mattered: The UI must expose uncertainty rather than hide it.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q5.4 — Which domain semantics are forbidden from being reimplemented in frontend code?

- Why it mattered: Freshness/comparison/closure/trend rules belong below UI.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q5.5 — Can mock prototype data be replaced by real query outputs without changing information architecture?

- Why it mattered: This is the core acceptance for prototype-to-product continuity.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance


## Phase 6 — Audit framework strengthening

Status: **planned**. Capture: `prospective`.

### Q6.1 — Do AX01–AX26 cover all new projection/query risks, or is there a genuinely new risk class requiring AX27?

- Why it mattered: New features alone are not a reason to grow the audit taxonomy.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q6.2 — Which axes must gain mandatory evidence from UC21–UC25 and projection builders?

- Why it mattered: Green historical axes must not ignore the read-side.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q6.3 — How will acceptance reviews, Golden Paths, regressions and architecture validation remain distinct evidence types?

- Why it mattered: One green runner must not masquerade as universal proof.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q6.4 — How should timeouts or unavailable evidence affect audit status?

- Why it mattered: Unknown evidence must not silently become PASS.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q6.5 — What revised complexity limits remain justified after Phase 3–5?

- Why it mattered: The expanded system must still satisfy AX26.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance


## Phase 7 — Daily orchestration and automation boundary

Status: **planned**. Capture: `prospective`.

### Q7.1 — What exact policy determines fresh, due, stale, blocked and not-applicable work?

- Why it mattered: Daily planning must be deterministic.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q7.2 — Which existing UCs compose the daily cycle and in what dependency order?

- Why it mattered: The orchestrator must not duplicate research semantics.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q7.3 — Which conditions trigger UC09, UC10, UC08 or UC11 for a scope?

- Why it mattered: Refresh policy must be explicit rather than heuristic drift.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q7.4 — When are projections rebuilt and when is a Daily Brief publishable?

- Why it mattered: User-visible results need a defined completion boundary.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q7.5 — Where is the scheduler boundary and what remains outside research semantics?

- Why it mattered: Triggering time should not own research logic.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance

### Q7.6 — How are retries/concurrency/idempotency handled for an interrupted daily cycle?

- Why it mattered: Automation magnifies crash/retry risks.
- Blocking: **yes**
- Origin: `pre-execution`
- Answer status: **pending**
- Answer: —
- Decision: —
- Acceptance impact: unresolved until execution/acceptance
