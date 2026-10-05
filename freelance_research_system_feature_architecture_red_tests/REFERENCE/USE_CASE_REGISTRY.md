# Use Case Registry — generated view

> GENERATED from `CORE/USE_CASE_REGISTRY.json` registry **3.2.0**, contract **3.1.0**. Do not edit semantics here.

| UC | Group | Interaction | Execution owner | Action class | Inputs | Outputs | Reads | Writes | Golden Paths |
|---|---|---|---|---|---:|---:|---:|---:|---|
| UC01 Start a new research project | lifecycle | orchestration | `application` | `project.initialize` | 1 | 1 | 2 | 5 | GP01 |
| UC02 Continue from previous research | lifecycle | orchestration | `mixed` | `project.continue` | 1 | 2 | 2 | 3 | GP02 |
| UC03 Execute the next atomic task | lifecycle | orchestration | `research_agent` | `task.execute` | 1 | 1 | 4 | 3 | GP01, GP02, GP06 |
| UC04 Discover candidate channels and sources | acquisition | command | `research_agent` | `discovery.channels` | 1 | 1 | 2 | 1 | — |
| UC05 Verify one channel/source/mechanism | acquisition | command | `research_agent` | `source.verify` | 1 | 1 | 2 | 3 | — |
| UC06 Observe what paid work is being bought | acquisition | command | `research_agent` | `market.observe_paid_work` | 1 | 1 | 2 | 2 | GP03 |
| UC07 Normalize and clean observed work | analysis | command | `mixed` | `market.normalize` | 1 | 1 | 2 | 1 | GP03 |
| UC08 Measure one dimension | analysis | command | `mixed` | `market.measure` | 2 | 1 | 3 | 2 | GP03 |
| UC09 Monitor known scope over time | maintenance | command | `mixed` | `temporal.monitor` | 2 | 1 | 3 | 4 | GP04 |
| UC10 Rediscover novelty beyond the baseline | acquisition | command | `research_agent` | `discovery.rediscover` | 1 | 1 | 2 | 2 | — |
| UC11 Triangulate one claim | analysis | command | `research_agent` | `evidence.triangulate` | 1 | 1 | 1 | 2 | — |
| UC12 Run a practical delivery test | analysis | command | `research_agent` | `experiment.delivery` | 1 | 1 | 2 | 2 | — |
| UC13 Run a market/acquisition test | analysis | command | `research_agent` | `experiment.acquisition` | 1 | 1 | 2 | 2 | — |
| UC14 Filter, compare and update the decision | analysis | command | `mixed` | `decision.compare` | 1 | 1 | 1 | 2 | GP03 |
| UC15 Manage research sources | maintenance | command | `mixed` | `sources.manage` | 1 | 1 | 1 | 4 | GP05 |
| UC16 Change a method or project policy safely | maintenance | command | `mixed` | `system.change_policy` | 1 | 1 | 3 | 4 | GP06 |
| UC17 Checkpoint and hand off | lifecycle | orchestration | `mixed` | `project.checkpoint` | 1 | 1 | 3 | 5 | GP03, GP04, GP05 |
| UC18 Repair and reconcile a project | lifecycle | orchestration | `internal` | `project.repair` | 1 | 1 | 2 | 2 | — |
| UC19 Audit or modify the reusable system | governance | command | `development` | `system.audit_modify` | 1 | 1 | 2 | 4 | — |
| UC20 Migrate a project to a newer system contract | lifecycle | orchestration | `internal` | `project.migrate` | 1 | 1 | 2 | 4 | GP06 |
| UC21 Get Current State | results | query | `application` | `result.current_state` | 2 | 1 | 2 | 0 | — |
| UC22 Get Changes | results | query | `application` | `result.changes` | 2 | 1 | 2 | 0 | — |
| UC23 Get Trend | results | query | `application` | `result.trend` | 4 | 1 | 2 | 0 | — |
| UC24 Get Interpretation | results | query | `application` | `result.interpretation` | 3 | 1 | 2 | 0 | — |
| UC25 Get Research Health | results | query | `application` | `result.research_health` | 1 | 1 | 2 | 0 | — |

## Group definitions

- **lifecycle** — project lifecycle and runtime continuity
- **acquisition** — discover/verify/observe new external research inputs
- **analysis** — normalize, measure, test, reason and compare
- **maintenance** — monitor known scope and maintain reusable project resources/policies
- **results** — read-side result/query use cases returning typed research products without silently performing new research
- **governance** — audit/change reusable system architecture

## Interaction types

- **command** — changes research/project knowledge or configuration
- **query** — returns a result without silently performing new research
- **orchestration** — controls lifecycle/runtime sequencing

## Execution owners

- **research_agent** — Research action is primarily executed by the research agent (currently ChatGPT); the application may ingest, validate, persist, derive from, or present its results without owning the research action itself.
- **application** — The use case is primarily executed by the application as a product/runtime interaction.
- **mixed** — Responsibility is intentionally split between research-agent semantic/research work and application deterministic, state, query, or presentation work.
- **internal** — Internal runtime/maintenance behavior of the software system; not a primary research-agent action or end-user application feature.
- **development** — Development/governance work on the reusable system itself; outside the runtime application feature set.

Canonical routing, typed I/O, reads/writes, acceptance, failure modes, side effects, freshness/comparability, transitions, UI/API hooks and Golden Path links remain only in the JSON registry.
