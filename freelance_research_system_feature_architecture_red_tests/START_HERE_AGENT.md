# START HERE — Agent Entry Point v1.11

## First action: route through the canonical registry

Read `CORE/USE_CASE_REGISTRY.json`. Select exactly one use case using the current request plus project context. Do not maintain or consult a second routing table in README, decision trees, AtomicPlan or this file.

Canonical flow:

`REQUEST + CONTEXT → USE CASE → WORKFLOW → TASK MANIFEST → REFERENCED METHODS/SOURCES/PRINCIPLES → EXECUTE → ACCEPTANCE → OUTCOME → GUARDED TRANSITION → CHECKPOINT`

For deterministic conformance/testing use `TOOLS/route_use_case.py`; representative multilingual/state-sensitive expectations live in `CORE/USE_CASE_ROUTING_FIXTURES.json`. Semantic agent routing is allowed, but the selected Task Manifest must preserve routing lineage.

## After routing

1. Read only the selected `USE_CASES/UC*.md` workflow.
2. Load only the UC `reads`, `capabilities`, required inputs, and canonical contracts declared in the registry.
3. For a concrete task, create/load a Task Manifest with `use_case_id`, `request_ref`, `route_reason`, `use_case_registry_version`, and `router_kind`.
4. Execute one atomic task.
5. Run acceptance checks.
6. Emit exactly one declared use-case outcome.
7. Follow exactly the transition bound to that outcome.

## No-match / ambiguity

Follow the `routing_contract` in the registry. Never invent a parallel workflow.

## Canonical role separation

See `CORE/USE_CASE_ARCHITECTURE.md`.


## Golden-path conformance

For end-to-end reference workflows and release expectations, read `CORE/GOLDEN_PATH_REGISTRY.json` and `GOLDEN_PATHS/README.md`. Golden Paths are tests of public workflow contracts, not alternative routing logic.

## Development acceptance

Before starting a development phase, read its `AUDIT/PHASE_EXECUTION_RECORDS/PHASE<n>_EXECUTION_RECORD.json` and the acceptance contract in `REFERENCE/DEVELOPMENT_PLAN_vNext.md`. Capture pre-execution questions first; append emergent questions without rewriting history. Before `accepted`, every blocking question must have a post-execution answer, decision and evidence. Use `REFERENCE/PHASE_ACCEPTANCE_QA.md` as the generated human view. Tests remain evidence; acceptance criteria plus resolved blocking questions define completion.



## Result/query boundary

Read `CORE/USE_CASE_REGISTRY.json` for the canonical distinction between commands/orchestration and read-only result queries. Query UCs must never silently perform external research or mutate research truth. The result-product contracts are in `CORE/RESULT_PRODUCT_CONTRACTS.json`; their builders remain a later phase until the System Map marks them implemented.
