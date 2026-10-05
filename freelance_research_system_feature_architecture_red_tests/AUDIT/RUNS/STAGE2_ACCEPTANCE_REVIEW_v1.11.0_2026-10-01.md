# Stage 2 Acceptance Review — v1.11.0 — 2026-10-01

**Decision: ACCEPTED**

| Criterion | Status | Evidence |
|---|---|---|
| A2.1 | **PASS** | UC21–UC25 exist as complete results/query UCs and return the five typed result products. |
| A2.2 | **PASS** | English/Russian command-query contrasts and state-sensitive what-changed routing pass; RF047–RF066 added. |
| A2.3 | **PASS** | All five query UCs have writes=[] and explicit read-only semantics; refresh/measurement/evidence/repair/audit remain non-query UCs. |
| A2.4 | **PASS** | No Direction Detail or other UI screen is a top-level UC; UI composition remains derived in System Map/UI screen map. |
| A2.5 | **PASS** | Projection builders are capability dependencies only; no build/render projection UC was added. |
| A2.6 | **PASS** | All 47 v1.10 routing fixtures preserved with zero regressions; 6/6 existing Golden Paths pass. |
| A2.7 | **PASS** | Architecture budget deliberately revised to 25 top-level UCs, six semantic groups and five query UCs; one canonical USE_CASE_REGISTRY remains. |
| A2.8 | **PASS** | Generated System Map contains UC21–UC25 as implemented nodes, typed result-contract nodes and UI composition links; no PLANNED:UC21–UC25 nodes. |

## Boundary preserved

Result product contracts and query intents are implemented; the Result Projection backend that actually builds those products remains Phase 3 by design.

## Release evidence

- Phase-2 acceptance validator: `TOOLS/validate_stage2_acceptance.py`.
- Frozen v1.10 routing baseline: `REFERENCE/PHASE2_ROUTING_BASELINE_v1.10.json`.
- Test evidence: `TESTS/TEST_RUN_v1.11.0_2026-10-01.md`.
- System Map: `REFERENCE/SYSTEM_MAP.md`.
- Release integrity: **PASS** — `validate_system.py` returned `SYSTEM VALIDATION: OK — 1.11.0`; manifest is rebuilt after this acceptance record update.

## Questions & answers used in acceptance

Capture mode: `retrospective_reconstruction`.

| Question | Blocking | Post-execution answer / decision | Evidence |
|---|---|---|---|
| **Q2.1** Should user intents that read/show existing research results be first-class use cases separate from research commands? | yes | Yes. UC21–UC25 are first-class query UCs representing Current State, Changes, Trend, Interpretation and Research Health. Decision: Model read/explain intents separately from command UCs. | `CORE/USE_CASE_REGISTRY.json`, `CORE/RESULT_PRODUCT_CONTRACTS.json` |
| **Q2.2** Should every future UI screen become a use case? | yes | No. Composite screens such as Direction Detail invoke multiple query UCs and command actions but are not domain use cases. Decision: Keep screen composition in UI mapping/System Map. | `REFERENCE/UI_SCREEN_MAP.md`, `CORE/SYSTEM_MAP_SPEC.json` |
| **Q2.3** Should projection builders become top-level use cases? | yes | No. Projection builders remain capabilities/internal implementation, not top-level UCs. Decision: Avoid internal build/render UCs. | `CORE/USE_CASE_REGISTRY.json`, `REFERENCE/SYSTEM_MAP.md` |
| **Q2.4** How do we distinguish “show what changed” from “run research to find what changed”? | yes | Route using action intent plus state hints: existing result/read intent selects UC22; explicit refresh/research intent selects UC09 (and analogous boundaries for other products). Decision: Preserve user intent rather than routing by screen wording. | `CORE/USE_CASE_ROUTING_FIXTURES.json`, `TOOLS/route_use_case.py` |
| **Q2.5** May query use cases mutate research truth or silently trigger refresh/measurement? | yes | No. Query UCs are read-only with writes=[]; missing/stale data is surfaced, not silently repaired by mutation. Decision: Refresh remains an explicit command-side action. | `CORE/USE_CASE_REGISTRY.json`, `TOOLS/validate_stage2_acceptance.py` |
| **Q2.6** Is increasing from 20 to 25 top-level UCs architecturally justified? | yes | Yes, because result/query is a genuinely new user-capability class. The budget is explicitly revised to 25 UCs, six groups and five query UCs while retaining one router. Decision: Accept bounded complexity increase, not arbitrary growth. | `CORE/ARCHITECTURE_BUDGET.json`, `TOOLS/validate_architecture.py` |
| **Q2.7** Are the five result products real backend outputs in Phase 2, or only contracts until Phase 3? | yes | Only the query contracts and typed result-product contracts are implemented in Phase 2. Projection/build execution remains Phase 3. Decision: Mark backend projection layer planned and never claim products are buildable yet. | `CORE/RESULT_PRODUCT_CONTRACTS.json`, `REFERENCE/SYSTEM_MAP.md`, `STAGE_STATUS.json` |
| **Q2.E1** Did adding UC21–UC25 change any of the 47 pre-existing v1.10 routing fixtures? | yes | No. All 47 v1.10 routing fixtures were preserved with zero regressions, and GP01–GP06 remained green. Decision: Accept new query routing only after legacy route preservation is demonstrated. | `REFERENCE/PHASE2_ROUTING_BASELINE_v1.10.json`, `AUDIT/RUNS/STAGE2_ACCEPTANCE_REVIEW_v1.11.0_2026-10-01.md` |

