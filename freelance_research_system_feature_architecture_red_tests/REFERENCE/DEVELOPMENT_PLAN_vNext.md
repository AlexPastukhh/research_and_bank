# Development Plan — complete use cases + result/query layer + living system map

## Acceptance policy

A phase is not complete merely because its implementation tasks or automated tests finished. Each phase has an explicit **acceptance contract** describing the externally observable state that must be true when the phase is done.

Phase status values:
- `planned` — work has not started;
- `in_progress` — implementation is underway but acceptance has not been established;
- `conditionally_accepted` — the intended outcome is usable, but one or more explicitly recorded non-blocking conditions remain;
- `accepted` — every mandatory acceptance condition is true on the release artifact;
- `not_accepted` — one or more mandatory conditions are false or unsupported.

Acceptance evidence may be automated validation, Golden Paths, artifact inspection, migration exercises, generated-view parity, or a documented architectural review. **The evidence is not the acceptance itself**; acceptance is the statement that the intended system outcome is actually achieved.

A phase may be marked `accepted` only when:
1. every mandatory phase-specific acceptance condition below is satisfied;
2. no known contradiction remains between canonical contracts, generated views, release documentation, and runtime behavior;
3. the System Map has been regenerated and reflects the accepted state;
4. the acceptance decision and evidence are stored in the release.


## Phase questions & answers policy

Every phase also has a persistent **execution question record**. Acceptance criteria answer “what must be true when the phase is complete”; phase questions answer “what uncertainties/decisions must be resolved while getting there.” They are complementary and both are required.

Before implementation begins:
1. create/update `AUDIT/PHASE_EXECUTION_RECORDS/PHASE<n>_EXECUTION_RECORD.json`;
2. record the `pre_execution_questions` with stable IDs, why each matters, and whether it is blocking;
3. do not pre-fill the final answer merely to make the plan look resolved.

During implementation:
- new material questions go to `emergent_questions` without deleting or rewriting the original pre-execution questions;
- a question may change a design decision, acceptance criterion, dependency or later phase, but that change must be explicit.

After implementation and before acceptance:
- every blocking pre-execution/emergent question must have a `post_execution_answer`;
- each answer records the answer itself, the resulting decision, evidence references, and acceptance impact;
- `deferred` is allowed only for a non-blocking question and must say where/when it will be resolved;
- an accepted phase cannot contain an unanswered blocking question.

Completed Phase 0–2 records in this release are marked `retrospective_reconstruction` because this policy was introduced after those phases. Phase 3 onward uses `prospective` capture before work starts. The generated human view is `REFERENCE/PHASE_ACCEPTANCE_QA.md`.

## Progress status — 2026-10-01

- **Phase 0 — ACCEPTED**: baseline frozen; living System Map contract/generator/parity established.
- **Phase 1 — ACCEPTED in v1.10.0 Stage 1**: all 20 implemented UCs conform to Complete Use Case Contract v3; acceptance review stored in `AUDIT/RUNS/STAGE1_ACCEPTANCE_REVIEW_v1.10.0_2026-10-01.*`.
- **Phase 2 — ACCEPTED in v1.11.0 Stage 2**: UC21–UC25 are implemented as read-only result/query contracts; command/query routing boundaries accepted; evidence stored in `AUDIT/RUNS/STAGE2_ACCEPTANCE_REVIEW_v1.11.0_2026-10-01.*`.

## Release goal

Evolve v1.9 into a system where every supported user intent routes through a **complete use-case contract**, research commands update append-only truth, result/query use cases expose canonical result products, and a generated whole-system map is rebuilt and delivered with every release.

---

## Phase 0 — Baseline & living System Map contract

### Work

0.1 Freeze current v1.9 as the immutable comparison baseline.  
0.2 Add `CORE/SYSTEM_MAP_SPEC.json` describing the map contract, node/edge types, canonical inputs and generated outputs.  
0.3 Add `TOOLS/generate_system_map.py`.  
0.4 Generate `REFERENCE/SYSTEM_MAP.md`, `REFERENCE/SYSTEM_MAP.json`, and Mermaid graph.  
0.5 Put map regeneration/parity into release discipline so committed map drift is visible.

### Questions before execution

Question set: **retrospectively reconstructed**. Canonical record: `AUDIT/PHASE_EXECUTION_RECORDS/PHASE0_EXECUTION_RECORD.json`.

- **Q0.1** — What exact artifact is the immutable comparison baseline, and how is its identity preserved? *(blocking)*
- **Q0.2** — Which architecture artifacts are canonical inputs and which are generated views? *(blocking)*
- **Q0.3** — How will the map distinguish implemented components from planned components? *(blocking)*
- **Q0.4** — Which changes require System Map regeneration? *(blocking)*
- **Q0.5** — Must the map and development plan be included in every release handoff? *(blocking)*

Post-execution answers are preserved in the canonical phase record and summarized in the acceptance review.

### Acceptance contract

Phase 0 is accepted only when all of the following are true:

- **A0.1 Baseline identity is unambiguous.** The exact v1.9 baseline is named and has a recorded cryptographic digest or equivalent immutable identifier; later work can say exactly what changed from it.
- **A0.2 The map has one generation path.** Map outputs are generated from declared canonical sources; no hand-maintained second architecture map owns competing semantics.
- **A0.3 The map is whole-system, not only a UC list.** It represents current implemented use cases, transitions, workflows, dependencies/runtime artifacts, Golden Paths, audit axes, and a clearly separated planned overlay.
- **A0.4 Planned and implemented components cannot be confused.** Future result/query/UI elements are visibly marked as planned until implemented.
- **A0.5 Drift is observable.** Regenerating the map from unchanged canonical inputs yields the committed map; changing a canonical mapped input without regeneration is detectable.
- **A0.6 The map is part of the release handoff.** A user receiving the release can locate the map and the development plan without reconstructing them from chat history.

**Accepted outcome:** a new maintainer can answer “what exists, what is planned, and how major parts relate?” from release artifacts, and map drift is not silent.

---

## Phase 1 — Complete Use Case Contract v3

### Work

Add first-class fields to every implemented UC:

- `group`
- `interaction_type` (`command | query | orchestration`)
- `actor_intent`
- typed `inputs`
- `reads`
- `writes`
- `capabilities`
- typed `outputs`
- `freshness_requirements`
- `comparability_requirements`
- `acceptance`
- `failure_modes`
- `side_effects`
- `idempotency`
- `capability_requirements`
- `ui_surfaces`
- `api_queries`
- `golden_paths`

Keep routing and UC contract semantics canonical only in `CORE/USE_CASE_REGISTRY.json`; workflow Markdown owns procedure ordering only.

### Questions before execution

Question set: **retrospectively reconstructed**. Canonical record: `AUDIT/PHASE_EXECUTION_RECORDS/PHASE1_EXECUTION_RECORD.json`.

- **Q1.1** — What must be knowable from a use case for it to count as contract-complete? *(blocking)*
- **Q1.2** — Which semantics belong canonically in USE_CASE_REGISTRY and what remains in workflow Markdown? *(blocking)*
- **Q1.3** — How do we prove the contract refactor did not change established v1.9 behavior accidentally? *(blocking)*
- **Q1.4** — How detailed must reads, writes and capabilities be? *(blocking)*
- **Q1.5** — How will existing projects move to the new contract/runtime version without rewriting historical lineage? *(blocking)*
- **Q1.6** — How will release representations be kept consistent across schemas, migration docs, workbook and generated views? *(blocking)*

Questions discovered during execution/acceptance:
- **Q1.E1** — Does migration documentation actually agree with the runtime migration target after the Stage 1 changes? *(blocking)*

Post-execution answers are preserved in the canonical phase record and summarized in the acceptance review.

### Acceptance contract

Phase 1 is accepted only when all of the following are true:

- **A1.1 Every implemented UC is contract-complete.** All 20 Stage-1 UCs conform to one v3 schema and have non-empty, semantically meaningful contract values for the fields required by their behavior; no UC remains on a legacy partial contract.
- **A1.2 Canonical ownership is unambiguous.** Routing, acceptance, outcomes, dependency declarations and transition semantics have one canonical owner in the UC registry; workflow Markdown does not independently own editable copies of those contracts.
- **A1.3 Existing behavior is preserved unless explicitly changed.** The v1.9 routing fixtures, existing Golden Paths, temporal semantics, project validation and runtime regressions still behave as intended after the contract refactor.
- **A1.4 Declared dependencies describe the real execution surface.** `reads`, `writes`, and `capabilities` are sufficient to understand material UC dependencies and fit the architecture complexity budget; they are not merely placeholder labels.
- **A1.5 Outcomes remain closed and deterministic.** Every declared outcome has exactly one canonical transition target (or terminal result), and no workflow introduces an undeclared alternate transition.
- **A1.6 Generated human views remain derived.** UC summary/docs and the whole-system map regenerate from canonical contracts with zero parity drift.
- **A1.7 Upgrade/reuse remains viable.** A supported v1.9 project can move to v1.10 without rewriting historical route lineage, and the migrated project validates under the new runtime version.
- **A1.8 Release representations agree.** `VERSION.json`, schemas, runtime templates/tools, migration documentation, workbook summary, System Map, release notes and Stage Status do not contradict each other about the current release/contract state.
- **A1.9 Release integrity is preserved.** The release manifest matches the packaged files, required artifacts are present, and the archive can be consumed as a self-contained handoff.
- **A1.10 The map reflects the accepted contract.** The delivered System Map shows the Stage-1 UC groups/interactions/dependencies and the development status marks Phase 1 accepted while keeping UC21–UC25 explicitly planned.

**Accepted outcome:** an engineer can take any implemented UC and determine its intent, inputs, outputs, dependencies, side effects, failure/acceptance conditions, transition behavior and assurance links without reconciling competing documents.

---

## Phase 2 — Result/query use cases and command/query boundary

### Work

Use semantic `group` plus orthogonal `interaction_type`.

Target groups:
- `lifecycle`
- `acquisition`
- `analysis`
- `maintenance`
- `results`
- `governance`

Add:
- **UC21 Get Current State** → `CurrentStateSnapshot`
- **UC22 Get Changes** → `ChangeSet`
- **UC23 Get Trend** → `TrendSeries`
- **UC24 Get Interpretation** → `InterpretationRecord`
- **UC25 Get Research Health** → `ResearchHealthSnapshot`

Do **not** create separate use cases for projection builders or every UI screen.

### Questions before execution

Question set: **retrospectively reconstructed**. Canonical record: `AUDIT/PHASE_EXECUTION_RECORDS/PHASE2_EXECUTION_RECORD.json`.

- **Q2.1** — Should user intents that read/show existing research results be first-class use cases separate from research commands? *(blocking)*
- **Q2.2** — Should every future UI screen become a use case? *(blocking)*
- **Q2.3** — Should projection builders become top-level use cases? *(blocking)*
- **Q2.4** — How do we distinguish “show what changed” from “run research to find what changed”? *(blocking)*
- **Q2.5** — May query use cases mutate research truth or silently trigger refresh/measurement? *(blocking)*
- **Q2.6** — Is increasing from 20 to 25 top-level UCs architecturally justified? *(blocking)*
- **Q2.7** — Are the five result products real backend outputs in Phase 2, or only contracts until Phase 3? *(blocking)*

Questions discovered during execution/acceptance:
- **Q2.E1** — Did adding UC21–UC25 change any of the 47 pre-existing v1.10 routing fixtures? *(blocking)*

Post-execution answers are preserved in the canonical phase record and summarized in the acceptance review.

### Acceptance contract

Phase 2 is accepted only when:

- **A2.1 Query intents are first-class.** Each of the five result questions routes to exactly one complete query UC with a clearly typed result product.
- **A2.2 Command/query semantics are distinguishable.** Common English and Russian requests distinguish “perform/refresh research” from “show/return existing result”, including state-sensitive cases.
- **A2.3 Boundaries are explicit.** UC21–UC25 do not absorb collection/measurement logic, while existing command UCs do not silently become presentation/query UCs.
- **A2.4 UI screens are not promoted into fake domain UCs.** Direction Detail and other composite screens remain compositions of query UCs and command actions.
- **A2.5 Projection builders remain capabilities, not top-level UCs.** The registry does not gain internal implementation steps masquerading as user intents.
- **A2.6 Existing routes remain stable.** Previously valid v1.10 command/lifecycle/governance requests retain their intended routes unless a documented boundary change is part of the phase.
- **A2.7 Complexity increase is explicit and bounded.** Architecture budget is deliberately revised for 25 top-level UCs and six semantic groups, with rationale; no duplicate router or competing query registry is introduced.
- **A2.8 System Map and derived views show the new topology.** UC21–UC25 move from planned overlay to implemented nodes and their links to result products/UI surfaces are visible.

**Accepted outcome:** a request can be classified as “change knowledge” versus “read/explain knowledge” without relying on UI wording or hidden implementation conventions.

---

## Phase 3 — Result Projection / Query layer

### Work

Implement canonical schemas/builders/stores or deterministic derived outputs for the five result products.

Required supporting work:
1. result identity/index;
2. freshness/invalidation policy;
3. canonical measurement/economics/claim histories where currently only schemas/workbook concepts exist;
4. compatibility checks reused by ChangeSet/TrendSeries;
5. query interface independent of UI.

### Questions before execution

Question set: **captured prospectively before implementation**. Canonical record: `AUDIT/PHASE_EXECUTION_RECORDS/PHASE3_EXECUTION_RECORD.json`.

- **Q3.1** — For each of the five result products, what exact runtime artifacts are authoritative inputs? *(blocking)*
- **Q3.2** — Which products are persisted versus deterministically derived on read, and why? *(blocking)*
- **Q3.3** — What is the canonical freshness/invalidation policy and how is it versioned? *(blocking)*
- **Q3.4** — Which measurement/economics/claim histories must become first-class runtime stores before projections are possible? *(blocking)*
- **Q3.5** — How will every projected result record builder version, input refs and reversible lineage? *(blocking)*
- **Q3.6** — How should query UCs respond to stale/insufficient/not-comparable inputs without silently mutating research state? *(blocking)*
- **Q3.7** — How will ChangeSet and TrendSeries reuse one compatibility model instead of diverging? *(blocking)*
- **Q3.8** — If caching is introduced, can it be proven semantically transparent and non-mutating to research truth? *(blocking)*

Post-execution answers: **pending until the phase is executed**.

### Acceptance contract

Phase 3 is accepted only when:

- **A3.1 Every query UC can produce its promised product from runtime truth.** No product depends on reading workbook presentation state or mock UI data.
- **A3.2 Current State is actually current.** `CurrentStateSnapshot` selects the latest valid results, excludes stale/invalidated items by policy, records exclusion reasons, preserves history, and supports global and scoped views.
- **A3.3 Changes preserve temporal semantics.** `ChangeSet` compares only compatible research states and keeps `new`, `changed`, `confirmed_closed`, `reopened`, `not_seen`, and `interesting` distinct.
- **A3.4 Trends are comparison-safe.** `TrendSeries` never silently bridges incompatible methods/scopes/routes, exposes missing windows/coverage, and separates raw points from derived trend statistics.
- **A3.5 Interpretation remains evidence-linked.** Every `InterpretationRecord` has scope/period/result or evidence refs/confidence/limitations and cannot be mistaken for a raw measurement or unsupported causal fact.
- **A3.6 Health describes trustworthiness, not cosmetics.** `ResearchHealthSnapshot` surfaces freshness, coverage, comparability, stale/failed/partial areas, unresolved quality flags and release/audit context.
- **A3.7 Result lineage is reversible.** A shown result can be traced back through builder/version/input refs to the underlying runtime evidence or measurements.
- **A3.8 Query behavior is deterministic for a fixed snapshot.** Repeating a query against unchanged canonical inputs produces the same semantic result and does not mutate research truth merely by being read.

**Accepted outcome:** the five user-facing research products exist as real backend contracts and can be consumed independently of any particular UI.

---

## Phase 4 — Query-side Golden Paths

### Work

Add:
- GP07 Current State from existing research;
- GP08 Changes from two comparable runs;
- GP09 Trend from comparable historical measurements;
- GP10 Interpretation with evidence/result refs;
- GP11 Research Health with mixed freshness/coverage;
- GP12 stale Current State → refresh command UC → fresh Current State.

### Questions before execution

Question set: **captured prospectively before implementation**. Canonical record: `AUDIT/PHASE_EXECUTION_RECORDS/PHASE4_EXECUTION_RECORD.json`.

- **Q4.1** — What minimal hermetic fixture represents valid runtime truth for each result product? *(blocking)*
- **Q4.2** — Which insufficient/stale/not-comparable negative outcomes must be represented explicitly? *(blocking)*
- **Q4.3** — How exactly should GP12 compose stale query → command refresh → fresh query without bypassing UCs? *(blocking)*
- **Q4.4** — How will GP07–GP12 remain network-independent while still exercising public contracts? *(blocking)*
- **Q4.5** — What evidence shows GP01–GP06 semantics remain unchanged? *(blocking)*

Post-execution answers: **pending until the phase is executed**.

### Acceptance contract

Phase 4 is accepted only when:

- **A4.1 Every canonical query product has an end-to-end reference path.** GP07–GP11 demonstrate the normal product flow from existing runtime truth to user-facing output.
- **A4.2 Read/write composition works.** GP12 proves a stale query can expose the gap, invoke the correct command-side refresh, then return a fresh result without bypassing canonical UCs.
- **A4.3 Golden Paths are hermetic.** GP01–GP12 do not require live external sites to establish release conformance.
- **A4.4 Existing command-side Golden Paths remain valid.** Adding read-side paths does not invalidate GP01–GP06 semantics.
- **A4.5 Negative/insufficient states are explicit.** At least the query paths that can legitimately lack comparable/fresh/evidenced data demonstrate a defined insufficient/stale/not-comparable outcome rather than fabricating a complete result.

**Accepted outcome:** the main user journeys across command and query sides are demonstrated end-to-end using public contracts rather than isolated helpers.

---

## Phase 5 — UI mapping as derived composition

### Work

Update screen mapping so every screen declares:
- primary query UC(s);
- result product(s);
- command actions/buttons and their command UC;
- stale/error/insufficient-data states.

Examples:
- Current State → UC21; Refresh → UC09/UC08.
- Daily Changes → UC22; Run today → UC09.
- Trends → UC23; Refresh underlying metric → UC08.
- Interpretations → UC24; Gather evidence → UC11.
- Coverage & Quality → UC25; Repair → UC18.
- Direction Detail is **composition**, not a new UC.

### Questions before execution

Question set: **captured prospectively before implementation**. Canonical record: `AUDIT/PHASE_EXECUTION_RECORDS/PHASE5_EXECUTION_RECORD.json`.

- **Q5.1** — Which query UC/result product owns every visible screen block? *(blocking)*
- **Q5.2** — Which UI actions are commands and which are pure query/filter operations? *(blocking)*
- **Q5.3** — What are the required stale, partial, not-comparable, insufficient-evidence and failure states for each screen? *(blocking)*
- **Q5.4** — Which domain semantics are forbidden from being reimplemented in frontend code? *(blocking)*
- **Q5.5** — Can mock prototype data be replaced by real query outputs without changing information architecture? *(blocking)*

Post-execution answers: **pending until the phase is executed**.

### Acceptance contract

Phase 5 is accepted only when:

- **A5.1 Every UI surface is traceable to backend contracts.** Each displayed block identifies its source query UC/result product; each mutating action identifies its command UC.
- **A5.2 UI does not own research semantics.** Freshness, comparison, trend, closure, interpretation and quality rules live below the UI and are not reimplemented in presentation code.
- **A5.3 Required non-happy states are visible.** Screens have defined behavior for stale, partial, not-comparable, insufficient-evidence, loading/refresh and failure states.
- **A5.4 Composite screens remain composition.** Direction Detail and future dashboards combine products without becoming duplicate business-logic layers.
- **A5.5 Prototype/backend substitution is possible.** The UI can replace mock products with real query outputs without redesigning its information architecture or inventing new domain fields.
- **A5.6 Screen map remains derived/documented.** UI composition is represented in the living System Map and does not become a competing UC router.

**Accepted outcome:** the prototype expresses the real backend result model and can evolve into a UI without moving core research logic into the frontend.

---

## Phase 6 — Audit framework strengthening

### Work

Keep AX01–AX26 numbering unless a genuinely new risk class appears. Strengthen mandatory evidence for:
- projection freshness/comparability;
- command/query routing;
- query Golden Paths;
- generated map parity;
- result lineage;
- revised architecture budget.

### Questions before execution

Question set: **captured prospectively before implementation**. Canonical record: `AUDIT/PHASE_EXECUTION_RECORDS/PHASE6_EXECUTION_RECORD.json`.

- **Q6.1** — Do AX01–AX26 cover all new projection/query risks, or is there a genuinely new risk class requiring AX27? *(blocking)*
- **Q6.2** — Which axes must gain mandatory evidence from UC21–UC25 and projection builders? *(blocking)*
- **Q6.3** — How will acceptance reviews, Golden Paths, regressions and architecture validation remain distinct evidence types? *(blocking)*
- **Q6.4** — How should timeouts or unavailable evidence affect audit status? *(blocking)*
- **Q6.5** — What revised complexity limits remain justified after Phase 3–5? *(blocking)*

Post-execution answers: **pending until the phase is executed**.

### Acceptance contract

Phase 6 is accepted only when:

- **A6.1 Existing axes cover the new architecture without semantic gaps.** Any need for AX27 must be justified by a distinct risk class, not by a new feature name.
- **A6.2 AX21–AX26 explicitly evaluate the read-side architecture.** Routing, boundaries, workflow closure, canonical ownership, result/action lineage and complexity all include UC21–UC25/projections where relevant.
- **A6.3 Data correctness axes cover projections.** AX05/06/07/08/09/10 evidence reaches freshness, comparability, evidence lineage, measurement/economics validity and invalidation in user-facing results.
- **A6.4 Assurance quality itself remains auditable.** AX19 distinguishes unit/regression checks, Golden Paths, acceptance reviews and architecture validation instead of treating one green runner as universal proof.
- **A6.5 The 25-UC complexity budget is explicit and still passes.** Added query capability does not silently multiply canonical registries, workflow copies or dependency depth.
- **A6.6 Release audit has a clear decision.** A release is either audit-clear, conditionally accepted with recorded non-blocking conditions, or not accepted; timeouts are not silently converted into passes.

**Accepted outcome:** the audit framework gives credible evidence about the expanded system rather than merely preserving historical green labels.

---

## Phase 7 — Daily orchestration and automation boundary

### Work

Only after query products work:
- due/stale scope planner;
- known-scope monitoring UC09;
- novelty rediscovery UC10;
- due measurements/evidence refresh;
- rebuild projections;
- publish Daily Brief.

Scheduler/automation is a thin trigger around this cycle, not part of result semantics.

### Questions before execution

Question set: **captured prospectively before implementation**. Canonical record: `AUDIT/PHASE_EXECUTION_RECORDS/PHASE7_EXECUTION_RECORD.json`.

- **Q7.1** — What exact policy determines fresh, due, stale, blocked and not-applicable work? *(blocking)*
- **Q7.2** — Which existing UCs compose the daily cycle and in what dependency order? *(blocking)*
- **Q7.3** — Which conditions trigger UC09, UC10, UC08 or UC11 for a scope? *(blocking)*
- **Q7.4** — When are projections rebuilt and when is a Daily Brief publishable? *(blocking)*
- **Q7.5** — Where is the scheduler boundary and what remains outside research semantics? *(blocking)*
- **Q7.6** — How are retries/concurrency/idempotency handled for an interrupted daily cycle? *(blocking)*

Post-execution answers: **pending until the phase is executed**.

### Acceptance contract

Phase 7 is accepted only when:

- **A7.1 Due work is deterministically identified.** Given the same current state/config/time, the planner identifies the same scopes/results as fresh, due, stale, blocked or not applicable.
- **A7.2 Daily orchestration composes existing UCs.** It does not create a second hidden implementation of monitoring, rediscovery, measurement or evidence gathering.
- **A7.3 Retry/recovery does not corrupt history.** Interrupted or repeated daily cycles remain idempotent/recoverable within the runtime guarantees.
- **A7.4 Projections are refreshed after truth changes.** A completed daily cycle leaves Current State/Changes/Trends/Health consistent with the newly committed research state.
- **A7.5 Daily Brief is a composition of standard products.** It does not become a sixth incompatible truth store.
- **A7.6 Scheduler remains replaceable.** Cron/automation/manual trigger can initiate the same cycle; schedule infrastructure does not own research or result semantics.
- **A7.7 “Every day” is operationally complete.** A user can determine what ran, what changed, what is still stale/blocked, and what the current trusted state is after the cycle.

**Accepted outcome:** daily operation is a repeatable lifecycle over the existing command/query architecture, while scheduling remains an external trigger concern.

---

## Release discipline / map rule

Every meaningful phase/system change follows this discipline:

1. **before implementation**, capture/update the phase `pre_execution_questions`;
2. during implementation, append material `emergent_questions` without rewriting the original questions;
3. after implementation, record post-execution answers/decisions/evidence for every blocking question;
4. review the phase against its **acceptance contract**; an unresolved blocking question forbids `accepted`;
5. update the relevant phase acceptance status;
6. regenerate the System Map and Phase Q&A view;
7. run map/Q&A/derived-view parity and architecture validators;
8. run affected unit/regression checks and relevant Golden Paths;
9. run AX01–AX26 audit at the appropriate release depth;
10. rebuild manifest and package;
11. deliver the updated `SYSTEM_MAP.md`, `PHASE_ACCEPTANCE_QA.md`, development plan, acceptance review/status, and release artifact together.

The map must show both **current implemented architecture** and a clearly marked **planned overlay** until planned components become real. A phase label such as `COMPLETE` must not be used as a substitute for acceptance status.
