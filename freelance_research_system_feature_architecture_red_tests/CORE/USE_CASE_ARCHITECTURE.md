# Use-case-centered architecture — Complete Contract v3 + Result Query Boundary

## Control flow

`request + context → UseCaseRegistry → complete UC contract → procedure workflow/capability → typed output → acceptance → outcome`

Commands/orchestration may update research/project truth. Query UCs are read-only and do not silently execute commands.

## Canonical ownership

- `CORE/USE_CASE_REGISTRY.json`: sole top-level router + complete use-case contracts.
- `USE_CASES/UC*.md`: procedure ordering only.
- `CORE/RESULT_PRODUCT_CONTRACTS.json`: canonical typed result-product contract names/required fields.
- Task Manifest: one concrete command/orchestration invocation and route lineage.
- Methods/sources/system spec: reusable method/source/invariant semantics.
- RunState: current/next execution pointer.
- System Map: generated view, never an independent contract.

## Semantic groups

`lifecycle`, `acquisition`, `analysis`, `maintenance`, `results`, `governance`.

Orthogonal interaction types are `command`, `query`, and `orchestration`.

Execution ownership is a separate axis declared by `execution_owner` on every use case:

- `research_agent` — primarily executed by the research agent (currently ChatGPT); the application may ingest/validate/persist/present the result without owning the research action.
- `application` — primarily executed by the application as a product/runtime interaction.
- `mixed` — intentionally split between research-agent semantic work and application deterministic/state/query/presentation work.
- `internal` — software maintenance/runtime behavior, not a primary application feature.
- `development` — reusable-system development/governance outside runtime product behavior.

`execution_owner` does **not** mean one system use case maps one-to-one to one application feature. Application features are a separate product-surface model and may support several system use cases.

## Phase 2 query plane

- `UC21 Get Current State` → `CurrentStateSnapshot`
- `UC22 Get Changes` → `ChangeSet`
- `UC23 Get Trend` → `TrendSeries`
- `UC24 Get Interpretation` → `InterpretationRecord`
- `UC25 Get Research Health` → `ResearchHealthSnapshot`

These use cases own **user intent and result contracts**, not projection implementation. The projection builders/query backend remain Phase 3 capabilities. Query UCs have no research-truth writes and must return explicit `refresh_recommended` or `projection_unavailable` rather than silently run UC08/UC09/UC11/UC18/UC19.

## UI boundary

A screen is not automatically a use case. `Direction Detail`, for example, composes UC21/UC22/UC23/UC25 plus explicit command actions. UI surfaces do not own routing semantics.

## Assurance

Routing fixtures, Phase-2 acceptance validation, architecture budget, Golden Paths and generated-map parity enforce the boundary. Query-side executable Golden Paths are intentionally deferred to Phase 4 after Phase 3 builders exist.
