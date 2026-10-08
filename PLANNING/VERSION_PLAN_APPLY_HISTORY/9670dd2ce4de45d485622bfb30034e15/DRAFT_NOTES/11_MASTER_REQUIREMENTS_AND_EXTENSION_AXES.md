# Master product-intent map — requirements, future needs, optional capabilities, and extension axes

## Status and authority

This document is the **current authoritative map of user intent for vNext exploration**. It exists so future architecture, implementation, review, and ChatGPT reasoning can distinguish:

- what the product **must fundamentally be**;
- what is **required for the first useful implementation**;
- what is **required later to realize the intended product**, even if not in MVP;
- what becomes required only under specific conditions;
- what is an opportunity or experiment rather than a requirement;
- what must explicitly **not** be treated as a current requirement;
- along which dimensions the product may evolve without redefining its core.

It is **not an accepted implementation contract** and does not supersede accepted v1.11. It is a product-intent baseline for deciding what future contracts should contain.

## Classification vocabulary

Every requirement/idea should be classified using one of these statuses.

| Status | Meaning |
|---|---|
| `CORE_INTENT` | Fundamental to the product identity. An implementation that permanently excludes it would be a different product. |
| `MVP_REQUIRED` | Required for the first useful vNext implementation. |
| `TARGET_REQUIRED` | Required to realize the intended target product, but not necessarily the first MVP. |
| `CONDITIONAL_REQUIRED` | Becomes required when a stated trigger/scale/use case appears. |
| `FUTURE_OPPORTUNITY` | Plausibly useful extension; not required without evidence/user value. |
| `EXPERIMENT` | Should be evaluated empirically before adoption. |
| `OPEN_DECISION` | Product/architecture decision intentionally unresolved. |
| `ANTI_GOAL` | Explicitly avoid unless the product intent itself changes. |

A later requirement may change status, but history should be preserved rather than silently rewritten.

The companion `REQUIREMENTS_MAP.json` assigns stable IDs to the current registry. At the time of this capture it contains **115 classified entries** (core intent, MVP, target, conditional, experiments, opportunities, open decisions and anti-goals) plus **22 extension axes**. The JSON is a reasoning/index aid; this document carries the fuller human rationale.

---

# 1. Product north star

## 1.1 Core formulation — `CORE_INTENT`

The desired product is a **personal research, intelligence, and durable knowledge bank around ChatGPT**.

The user should be able to save almost anything worth keeping, retrieve it later, use it as input to new search/research, repeatedly observe changing things over time, and analyze accumulated evidence/history through ChatGPT plus a persistent application UI.

The product is **not centered on jobs, vacancies, freelance, news, games, or any one domain**. Those are domain packs/use cases over a reusable core.

The product is also **not intended to rebuild ChatGPT, Perplexity, a general web crawler, or every search provider**. ChatGPT can remain the primary interactive research/orchestration agent while the application owns persistent state, history, reusable context, analytical projections, and durable organization.

## 1.2 Primary user outcomes — `CORE_INTENT`

The product must eventually let the user:

1. **Save** arbitrary useful material without requiring an active research project.
2. **Organize** saved material into a durable personal bank.
3. **Retrieve** old material by exact fields, text, semantics, time, relationships, or similarity.
4. **Use saved material as a seed** for finding more things internally or externally.
5. **Research a question** with explicit scope, sources, methods, evidence, and reusable state.
6. **Repeat research over time** and update one longitudinal body of knowledge instead of producing isolated reports.
7. **Inspect current state** within a declared scope/coverage boundary.
8. **Inspect what changed** between runs/periods.
9. **Inspect trends and lifecycle** when comparable history exists.
10. **Watch** chosen entities, collections, lenses, queries, similarity neighborhoods, metrics, sources, or relations when continued observation is useful.
11. **Understand why** a conclusion/result exists via provenance, evidence, and method lineage.
12. **Use ChatGPT conversationally** to operate on saved items and research state while retaining a normal persistent UI for browsing, filtering, timelines, tables, charts, history, and evidence.
13. **Reuse sources and tools** instead of rediscovering/reconfiguring them for every research task.
14. **Add new domains** without rewriting the universal core.

---

# 2. Stable product invariants

These are `CORE_INTENT` unless explicitly reclassified later.

## 2.1 Bank is independent of research

- A saved item can exist before any research project/lens/run.
- Research references bank objects; it does not exclusively own them.
- One canonical object can participate in many runs and roles.
- Results from repeated research enrich the same durable bank/history.

## 2.2 Historical evidence is preserved

- Raw/source captures should not be silently rewritten when history matters.
- New interpretation should not erase old evidence.
- Corrections/merges/splits should preserve traceable history.
- Derived representations are versioned rather than treated as canonical truth.

## 2.3 Observation is not reality itself

- `not_seen` is not automatically `closed`, `deleted`, or `disappeared`.
- Source/page change is not automatically real-world entity change.
- AI/user annotations are not automatically raw facts.
- Search rank/similarity score is not an intrinsic truth about an entity.

## 2.4 Query and mutation remain distinct

- Reading current/historical state should not silently trigger expensive research unless the user intent/policy explicitly authorizes it.
- A query can report stale/partial/unavailable state and recommend refresh.

## 2.5 Comparability must be explicit

- Trends require comparable scope/method/source-route conditions or an explicit normalization model.
- Coverage changes must be visible.
- Method/model versions must be retained where they affect interpretation.

## 2.6 Provenance crosses all boundaries

Where meaningful, a result should remain traceable to source, route, tool/executor, run, raw capture, extraction/normalization method, and analytical method/version.

## 2.7 No universal mega-schema

The core defines generic protocols and metadata. Domain packs add typed domain semantics, metrics, identity rules, analysis recipes, and presentation hints.

## 2.8 No mandatory direct provider integration

A capability may be executed by ChatGPT, the application, an external job, a direct API integration, or manually. The architecture should depend on capabilities/contracts rather than permanently binding research logic to one vendor.

---

# 3. What the system must represent

## 3.1 Universal bank primitives

### `Asset` — `MVP_REQUIRED`
Stored bytes/content/capture, including images, files, screenshots, HTML/page snapshots, PDFs, video/audio, API payloads, transcripts, etc.

### `Entity` — `MVP_REQUIRED`
Stable canonical identity for a real/conceptual thing: game, app, company, person, job/opportunity, product, publication, source, technology, mechanic, etc.

### `Observation` — `MVP_REQUIRED`
A source-linked fact/statement observed about an entity at a time.

### `Annotation` — `MVP_REQUIRED`
User/AI-authored note/tag/interpretation distinct from raw evidence.

### `Collection` — `MVP_REQUIRED`
A user/system grouping of mixed items that can itself be browsed, searched, or used as a seed.

### `Relation` — `TARGET_REQUIRED`
Typed link among bank objects. MVP may implement a minimal relation subset; the target product needs explicit relation semantics.

### `Event` — `TARGET_REQUIRED`
Something believed to have happened at a domain-relevant time. Particularly important for news, releases, updates, closures, funding, policy changes, etc.

### `MetricObservation` — `TARGET_REQUIRED`
Typed quantitative/categorical measurement with method/unit/scope/provenance.

### `Representation` — `TARGET_REQUIRED`
Versioned derived searchable/comparable representation: text/image/style/mechanics embeddings, OCR, caption, perceptual hash, graph/trajectory features, etc.

### `BankItem` — `OPEN_DECISION`
Potential UX abstraction for “save this”; not necessarily a canonical domain entity.

## 3.2 Research primitives

### `ResearchLens` — `MVP_REQUIRED`
Semantic intent: what qualifies, target types, filters, similarity seeds/profile, time boundary, ranking/projection intent, personalization context.

### `SourcePolicy` — `MVP_REQUIRED`
Allowed/preferred source boundary: bank-only, saved sources, selected sources, saved+external, broad discovery, trusted-only, etc.

### `Source` — `MVP_REQUIRED`
Durable description of where information may be found.

### `SourceRoute` — `TARGET_REQUIRED`
Concrete reusable source-specific access/query configuration whose history matters for reproducibility/comparability.

### `ResearchRecipe` — `TARGET_REQUIRED`
Reusable execution design: methods, tools/capabilities, steps, acceptance/quality rules. It does **not** own semantic intent or cadence.

### `RunSpec` — `MVP_REQUIRED`
Immutable compiled effective configuration of one run. It freezes resolved lens, source policy/routes, recipe/tool/method versions, overrides, coverage intent, and relevant evaluation parameters.

### `ResearchRun` — `MVP_REQUIRED`
One concrete execution associated with a frozen `RunSpec`.

### `ResultSet` / `ResultOccurrence` — `MVP_REQUIRED`
Historical record of what a run/query returned, including membership and, when relevant, rank, score/profile, match reasons, origin, and result role. This preserves old output even if models/indexes change later.

### `Claim`, `EvidenceLink`, `Interpretation` — `TARGET_REQUIRED`
Explicit research reasoning layer for important analytical claims and verification.

## 3.3 Monitoring primitives

### `Watch` — `TARGET_REQUIRED`
Repeated observation policy over entity/collection/lens/query/similarity neighborhood/metric/relation/source.

Watch owns cadence, alert rules, pause/resume/lifecycle, and budget constraints; it does not redefine semantic intent or execution methods.

## 3.4 Capability/execution primitives

### `Capability` — `TARGET_REQUIRED`
Vendor-neutral operation needed by the research/product, e.g. `web_search`, `semantic_web_search`, `crawl_site`, `extract_page`, `query_news`, `find_similar_images`, `resolve_identity`, `compute_embedding`, `verify_claim`.

### `CapabilityExecutor` — `TARGET_REQUIRED`
How a capability is currently executed:

- ChatGPT built-in capability/tool/connector;
- application/direct API adapter;
- external job/platform;
- manual/user-assisted execution.

This prevents the research contract from depending on Exa/Tavily/Firecrawl/etc. directly.

---

# 4. Required responsibility boundaries

## 4.1 User — `CORE_INTENT`
Owns goals, preferences, selections, corrections, meaningful approvals, personal judgment, and explicit changes to intended scope.

## 4.2 ChatGPT / research agent — `CORE_INTENT`
Primary interactive reasoning/orchestration surface:

- interpret intent;
- retrieve relevant bank context;
- propose/use lenses and recipes;
- perform research/search using available capabilities;
- reason semantically;
- conduct counter-search/verification where appropriate;
- explain results and limitations;
- write structured results back through application contracts.

ChatGPT should **retrieve durable state** rather than rely on chat memory as the canonical store.

## 4.3 Application — `CORE_INTENT`
Owns persistent/deterministic state and durable user experience:

- bank/storage/history;
- authorization;
- IDs/identity records;
- run/result history;
- source/tool registries;
- query projections;
- deterministic validation;
- UI state;
- scheduling/background jobs when implemented;
- provenance/history;
- review/repair/migration machinery.

## 4.4 External providers — `CORE_INTENT`
Provide search/acquisition/processing capabilities under contracts. Their outputs are inputs/evidence candidates, not automatic canonical truth.

---

# 5. First useful vNext implementation — `MVP_REQUIRED`

The MVP should prove the product model without rebuilding commodity web infrastructure.

## 5.1 MVP Bank

Must support:

- save arbitrary supported item/file/URL/note;
- stable IDs;
- Asset + Entity distinction where applicable;
- basic metadata/provenance;
- Collections;
- Annotation;
- basic relations/links sufficient for provenance/use references;
- browse/item detail;
- exact/full-text search over local bank;
- basic historical item/run lookup.

## 5.2 MVP Research state

Must support:

- Lens;
- Source registry;
- SourcePolicy;
- immutable RunSpec;
- ResearchRun;
- ResultSet/ResultOccurrence;
- basic Observation/history;
- link run/results back to source/provenance;
- current run status and past run retrieval.

## 5.3 MVP ChatGPT boundary

Must let ChatGPT/application perform at least:

- `bank.save`;
- `bank.get/search`;
- `collection.create/update`;
- `source.list/get`;
- `research.create_or_use_lens`;
- `research.start_record_run` or equivalent structured handoff;
- `research.save_result_set`;
- `research.get_run`;
- `research.get_current_state/changes` when projections exist.

Exact tool names are not fixed here; semantic capabilities are.

## 5.4 MVP external research strategy

Default strategy:

- use ChatGPT native web/search/Deep Research capabilities;
- optionally use ChatGPT-accessible connectors/tools such as Exa/Tavily/Firecrawl when they materially help;
- do **not** require direct provider APIs in application backend initially;
- record provider/tool provenance when accessible;
- direct integrations are conditional, not MVP assumptions.

## 5.5 MVP proof domains

At minimum, implementation/design tests should cover substantially different cases:

1. freelance/opportunity longitudinal research — preserves legacy value;
2. games — domain structure and mechanics similarity;
3. arbitrary image/file saving — Bank independence from Research.

Apps/news can initially remain golden/design scenarios if implementation scope is constrained.

---

# 6. Target product requirements — `TARGET_REQUIRED`

These may be staged after MVP but are part of the intended product unless explicitly re-scoped.

## 6.1 Rich search/discovery

Support eventually:

- exact/structured filters;
- full text;
- semantic search;
- example/similarity search;
- multimodal image/media search;
- domain-structural similarity;
- relation/graph search;
- temporal/historical search;
- change-based search;
- evidence/research-lineage search;
- hybrid combinations;
- **`OPP-017` — positive and negative examples (`TARGET_REQUIRED`, outside MVP):** specify which similarity dimensions to include or avoid, choose whether a negative example lowers rank or causes a hard exclusion, and explain the applied match/exclusion reasons. Actual quality gains must be evaluated against search without negative examples using human relevance judgments (`EXP-004`, and regression sets when `COND-006` is active);
- collection-as-seed;
- explainable similarity dimensions.

## 6.2 Entity identity across runs/sources

- stable external IDs when available;
- aliases/canonicalization;
- probabilistic/semantic matching where needed;
- identity confidence;
- merge/split/correction history;
- reindex/reprojection after identity correction without deleting raw observations.

## 6.3 Longitudinal state

- repeated comparable runs;
- `first_seen`, `last_seen`, reappeared/reopened;
- current projection;
- historical as-of query;
- changes between periods/runs;
- explicit coverage/comparability;
- domain event times distinct from system/capture time where needed.

## 6.4 Current/Changes/Trend/Interpretation/Health

Retain/generalize the existing v1.11 result-product boundary:

- `CurrentStateSnapshot`;
- `ChangeSet`;
- `TrendSeries`;
- `InterpretationRecord`;
- `ResearchHealthSnapshot`.

## 6.5 Source/tool reuse

- save Sources and source groups;
- source roles/quality/trust notes;
- reusable SourceRoutes;
- Capability/Executor registry;
- method/tool versions;
- cost/rate-limit/health metadata where relevant.

## 6.6 Watch

Allow repeated observation of:

- Entity;
- Collection;
- Lens/query;
- similarity neighborhood;
- relation/event pattern;
- metric threshold;
- source health.

## 6.7 Domain packs

A new domain should add meaning through a pack/profile rather than core-schema rewrites.

A pack may define:

- entity/event types;
- properties/facets;
- metrics;
- identity rules;
- extraction/normalization;
- source adapters/routes;
- similarity profiles;
- analysis recipes;
- UI hints;
- domain-specific tests/use cases.

Target proof domains: freelance, games, apps, news; images/media test the Asset/Representation layer.

---

# 7. Research-quality requirements

## 7.1 Discovery is not measurement — `CORE_INTENT`

A discovery sample cannot automatically be interpreted as frequency/prevalence/demand evidence.

## 7.2 Claims must be linked to evidence — `TARGET_REQUIRED`

Important claims should support structured verification states such as:

- `SUPPORTED`;
- `PARTIALLY_SUPPORTED`;
- `CONTRADICTED`;
- `INSUFFICIENT`;
- `MISSCOPED`;
- `SOURCE_DOES_NOT_SUPPORT`.

## 7.3 Counter-search — `TARGET_REQUIRED` for serious tracked research

The system should support a separate pass whose goal is to find evidence that contradicts, narrows, or provides alternative explanations for important claims.

No counterevidence found does **not** mean the claim is proven.

## 7.4 Independent verification — `TARGET_REQUIRED` for high-value claims

Researcher and verifier should be separable roles/contexts so verification does not merely restate the synthesis.

## 7.5 Evidence admissibility/epistemic class — `TARGET_REQUIRED`

The Bank may contain raw source captures, user notes, AI annotations, derived metrics, summaries, etc. Saved material is not automatically independent evidence.

Research methods must retain derivation/dependency/independence where important.

## 7.6 Source genealogy — `TARGET_REQUIRED` for news/statistics/serious research

Track relations such as:

- cites;
- derived_from;
- syndicated_from;
- reports_on;
- based_on_dataset;
- republishes.

This helps avoid false triangulation from multiple pages that ultimately repeat one source.

## 7.7 Retrieval itself is measurable — `TARGET_REQUIRED`

For external discovery, store/evaluate `RetrievalRun`/provider origin where practical and measure marginal value rather than assuming multiple providers are independent.

Possible metrics:

- overlap;
- unique useful sources;
- unique primary sources;
- new independent evidence;
- counterevidence contribution;
- duplicate/low-quality rate;
- latency/cost.

## 7.8 Search/similarity regression evaluation — `CONDITIONAL_REQUIRED`

Trigger: similarity/ranking becomes an important product function or models/rankers change regularly.

Then maintain evaluation sets, relevance judgments, and evaluation runs rather than trusting newer embeddings/rankers automatically.

---

# 8. Analytics capability ladder

Analytics must be staged. Presence in this section does not imply MVP implementation.

## 8.1 Level A — basic descriptive analytics — `TARGET_REQUIRED`

- counts;
- quantiles/median/distributions rather than only averages;
- new/known/changed/reappeared/not-seen decomposition;
- basic grouped comparisons;
- source/coverage counts;
- simple time-series change.

## 8.2 Level B — longitudinal analytics — `TARGET_REQUIRED`

- velocity/acceleration;
- persistence;
- lifecycle/survival;
- cohorts;
- source divergence;
- coverage-normalized/comparable subsets;
- novelty;
- semantic/topic/mechanics clusters;
- emerging/declining phenomena.

Lifecycle methods must respect censoring/missingness and `not_seen != disappeared`.

## 8.3 Level C — advanced analytical extensions — `FUTURE_OPPORTUNITY`

- change-point detection;
- anomaly detection;
- concept/data drift;
- seasonality decomposition;
- distribution-shift metrics;
- graph/network analysis;
- trajectory similarity;
- personal-fit/skill-gap projections;
- counterfactual analysis;
- sensitivity/robustness analysis;
- Pareto frontiers;
- forecasting with uncertainty;
- sparse-segment/hierarchical estimation;
- capture-recapture under explicit assumptions.

## 8.4 Personalization — `TARGET_REQUIRED`, exact scoring method open

Personal relevance is a projection over bank/research state, not raw truth.

Possible dimensions:

- skills/requirements;
- interests/taste;
- language/location;
- minimum value/pay;
- time availability;
- learning willingness;
- exclusions;
- similarity to positive/negative examples.

Avoid opaque master scores unless their components and uncertainty are explainable.

---

# 9. Tool/provider strategy

## 9.1 Current strategic default — `CORE_INTENT`

Use ChatGPT as the primary interactive research/orchestration agent. Do not duplicate commodity capabilities in the application merely because an API exists.

## 9.2 Candidate provider classes — `EXPERIMENT`

Examples to evaluate, not mandatory dependencies:

- native ChatGPT web search / Deep Research;
- Exa / Tavily / Parallel for alternate retrieval;
- Firecrawl for extraction/crawling;
- Apify for repeatable specialized scraping/jobs;
- Airbyte/direct APIs for structured ingestion;
- GDELT/domain datasets/providers;
- personal knowledge/reference systems as sources/integration references.

## 9.3 When direct application integration becomes required — `CONDITIONAL_REQUIRED`

A direct provider/API/backend integration becomes justified when one or more are demonstrated:

1. reliable unattended scheduling is required;
2. volume/bulk ingestion exceeds practical interactive ChatGPT use;
3. exact reproducibility/control over provider parameters/results is required;
4. direct API materially reduces cost/latency;
5. ChatGPT-accessible connector lacks a needed capability;
6. provider-specific data/licensing/authentication must be handled server-side;
7. deterministic ingestion guarantees are required;
8. external provider output must stream directly into ongoing projections without an interactive chat step.

Until then, prefer ChatGPT-accessible tools/connectors to reduce custom integration work.

## 9.4 Build-vs-buy must remain open — `CORE_INTENT`

Before building major commodity subsystems, compare partial/full alternatives in relevant product classes:

- crawling/acquisition;
- search/vector retrieval;
- personal knowledge/AI workspace/reference banks;
- research intelligence platforms;
- data/lakehouse infrastructure;
- domain-specific market intelligence.

Comparison should include exportability, APIs/MCP, provenance, privacy, local/cloud boundaries, temporal semantics, lock-in, cost, and fit with the persistent bank model.

---

# 10. UI/product-surface requirements

## 10.1 Chat is not the only UI — `CORE_INTENT`

ChatGPT is ideal for intent, orchestration, interpretation, and natural-language operations. Persistent state must also be inspectable without reconstructing it from chat history.

## 10.2 Target UI surfaces — `TARGET_REQUIRED`

Potential primary surfaces:

- Bank;
- Discover;
- Collections;
- Item/Entity detail + timeline;
- Research lenses/runs;
- Current State;
- Changes;
- Trends;
- Watch center;
- Sources;
- Tools/Capabilities;
- History;
- Evidence/provenance;
- Research Health.

Exact navigation/naming remains `OPEN_DECISION`.

## 10.3 Selection-to-ChatGPT — `TARGET_REQUIRED`

Stable bank IDs should let the user select objects in UI and ask ChatGPT to compare, explain, find similar, research, save, or watch them.

---

# 11. Domain-specific examples that must remain possible

These are not all MVP requirements; they constrain the reusable design.

## 11.1 Freelance/work

- observe what work/tasks are bought;
- payout/value distributions;
- demand frequency when methodologically valid;
- requirements/skills;
- lifecycle;
- competition proxies;
- personal fit;
- practical/market tests as freelance-pack capabilities.

## 11.2 Games

- release/early-access/update dates;
- mechanics/core loop/player verbs/progression/systemic behavior;
- visual/theme/audience/monetization/session structure;
- similarity by mechanics independently of art style;
- trajectory/popularity/history watches.

## 11.3 Images/media

- save raw media;
- near-duplicate/perceptual similarity;
- visual composition;
- style;
- objects/content;
- color/texture;
- semantic caption meaning;
- source/original-finding watch as a possible extension.

## 11.4 Apps

- release/update/version history;
- price/rating/review/rank observations;
- cross-store identity;
- category/competitor analysis;
- lifecycle/cohort/trend.

## 11.5 News

Keep separate:

- `Publication/Article` — source-authored content;
- `Story/Narrative` — derived grouping of related coverage;
- `Event` — occurrence in the world.

Need source diversity, chronology, event-vs-publication-vs-known time, source genealogy, and duplicate/syndication handling.

---

# 12. Conditional requirements and their triggers

## 12.1 Automated Watches

**Trigger:** user expects research/monitoring to run when no interactive ChatGPT session exists.

Then require:

- scheduler/background worker;
- durable job state/retries;
- budgets/rate limits;
- alert/notification rules;
- direct/automatable CapabilityExecutors;
- idempotency;
- run failure/partial-coverage semantics.

## 12.2 High-volume ingestion

**Trigger:** thousands/millions of recurring observations or large media/data collections make interactive workflows insufficient.

Then consider:

- object storage/Parquet;
- analytical DB/time-series store;
- bulk ingestion/queues;
- incremental projections;
- index lifecycle/rebuild strategy;
- cost/retention policies.

## 12.3 Private/authenticated sources

**Trigger:** sources require credentials or contain private user data.

Then require:

- secret management;
- source/account permissions;
- encrypted storage/transport;
- authorization boundaries;
- deletion/export/retention guarantees;
- provider/model exposure controls.

## 12.4 Multi-user/shared workspaces

**Trigger:** product moves beyond one user or introduces collaboration.

Then require:

- workspace ownership;
- ACL/roles;
- item/source visibility;
- audit log;
- conflict/merge rules;
- shared vs personal annotations/projections;
- possibly tenant isolation.

## 12.5 High-stakes claims

**Trigger:** decisions depend materially on factual/quantitative correctness.

Then require stricter:

- claim-evidence verification;
- primary-source preference;
- counter-search;
- independent verifier;
- source genealogy;
- uncertainty disclosure;
- stronger acceptance gates.

## 12.6 Model/provider changes

**Trigger:** embeddings, LLMs, rankers, clustering models, or retrieval providers change.

Then require:

- versioned representations/methods;
- regression/evaluation where functionally important;
- reproducible historical results;
- compatibility/reindex plan;
- visible comparability breaks where relevant.

## 12.7 Strong bitemporal requirements

**Trigger:** user needs both “what was true then?” and “what did we know then?” across backfilled/corrected data.

Then require formal valid-time/system-time semantics rather than only loose timestamp fields.

---

# 13. Explicit anti-goals / do not assume

These are `ANTI_GOAL` unless intent changes.

- Do not make vacancy/job the universal root object.
- Do not make `ResearchProject` own all durable knowledge.
- Do not rebuild a general search engine just to avoid using ChatGPT/providers.
- Do not hard-code Exa/Tavily/Firecrawl/Perplexity/etc. into universal research semantics.
- Do not equate more providers with independent evidence without measuring overlap/dependency.
- Do not let vector indexes/embeddings become canonical truth.
- Do not create one giant GenericObject with all possible domain fields.
- Do not collapse all similarity to one opaque score.
- Do not silently overwrite history after identity/model/method changes.
- Do not infer closure/disappearance from one missing observation.
- Do not report “complete market/current state” without declared scope and coverage.
- Do not use discovery samples as frequency estimates without valid sampling/comparability.
- Do not hide source disagreement inside one aggregate.
- Do not silently perform refresh/research for a read-only query without authorized policy.
- Do not implement every analytics idea before user value is demonstrated.
- Do not integrate every external service into the application preemptively.
- Do not rely on chat transcript memory as the durable product state.

---

# 14. Open decisions that future work must not silently resolve

These remain `OPEN_DECISION` until explicitly decided.

## Product

- final product name;
- user-facing meaning of Workspace/Project/Lens;
- primary navigation;
- first implemented proof domains beyond freelance;
- degree of local-first vs cloud-first behavior;
- whether/when collaboration is in scope.

## Data model

- exact naming/boundary of BankItem/Document/Asset/Note;
- global bank vs workspace scoping;
- relation type registry/extensibility;
- exact bitemporal implementation stage;
- raw capture retention policy;
- source genealogy granularity;
- schema evolution strategy for domain packs.

## Search

- one combined search engine vs relational + lexical + vector + graph components;
- which similarity representations/models are worth maintaining;
- how collection-level similarity is computed;
- when external discovery is automatic vs explicit;
- exact quality thresholds/evaluation metrics.

## Execution

- internal orchestration framework;
- MCP vs other external tool protocol boundary;
- how ChatGPT invokes durable application capabilities;
- which direct provider integrations ever become first-class;
- background execution/notification platform.

## Storage

- initial trial route selected by the user on 2026-10-05: ChatGPT via Desktop Commander writes local files, application reads them; GitHub is optional history/sync, not the required ingestion transport;
- production file contract, internal DB/index and later Postgres/object store/vector index remain open; see ../PLANNING/LOCAL_FILE_EXCHANGE_TRIAL_2026-10-05.md;
- when Timescale/ClickHouse/search engines become justified;
- media storage/sync policy.

## Security/compliance

- credential store;
- per-source ToS/robots/access policy;
- data deletion/export guarantees;
- sensitive/private data handling;
- model-provider exposure policy.

---

# 15. Axes of change and expansion

These axes are intended to help future reasoning. A proposal should say **which axis it changes**, whether core invariants survive, and what conditional requirements become active.

## AX-V01 — Domain breadth

Current direction: freelance + games + apps + news + arbitrary media/examples.

Can expand to products, companies, technologies, papers, real estate, finance-like observations, personal media, datasets, etc.

Rule: adding a domain should primarily add a domain pack/adapters, not generic core fields.

## AX-V02 — Bank object/media breadth

Text/URL/note → images/files → video/audio → datasets → richer external object references.

Expansion affects storage, extraction, representation, preview/UI, and search modalities.

## AX-V03 — Retrieval breadth

Bank-only → saved sources → native web → multiple external retrieval providers → domain-specific datasets.

Expansion must preserve provenance and measure marginal provider value rather than assume independence.

## AX-V04 — Search sophistication

Exact/full-text → semantic → multi-vector/multimodal → graph → temporal → trajectory → hybrid learned ranking.

More sophistication activates stronger evaluation/versioning requirements.

## AX-V05 — Similarity semantics

Generic semantic similarity → domain-specific dimensions → user-defined profiles → positive/negative example learning → time/trajectory similarity.

Rule: similarity meaning must remain inspectable/explainable enough for the use case.

## AX-V06 — Source sophistication

URL/source record → source groups/quality roles → SourceRoutes → source genealogy/dependency → health/reliability scoring.

## AX-V07 — Capability/executor sophistication

ChatGPT-only interactive execution → ChatGPT connectors → direct APIs → external jobs → application-managed deterministic pipelines.

Direct integration is conditional on demonstrated need.

## AX-V08 — Research rigor

Exploratory search → reproducible RunSpec → claims/evidence → counter-search → independent verification → high-stakes acceptance gates.

Different research tasks may choose different rigor levels.

## AX-V09 — Temporal depth

Saved timestamp → repeated observations → lifecycle/current state → as-of history → bitemporal truth/knowledge-time → trajectory modeling/forecasting.

## AX-V10 — Automation/autonomy

User-triggered only → saved recipes → scheduled watches → conditional alerts → higher autonomy.

Greater autonomy activates permission, budget, reliability, and audit requirements.

## AX-V11 — Analytics sophistication

Descriptive → longitudinal → anomaly/change-point → semantic/graph → counterfactual/forecasting/robustness.

Rule: methods require assumptions/coverage/sample-quality checks.

## AX-V12 — Identity resolution sophistication

Exact external ID → deterministic aliases → probabilistic linking → semantic/domain rules → user adjudication → temporal identity/version handling.

## AX-V13 — Personalization

Manual filters → user profile → taste/skill projections → learned preferences → counterfactual personal recommendations.

Personalization remains projection, not universal entity truth.

## AX-V14 — Scale

Personal/small bank → large bank → high-volume repeated ingestion → near-real-time stream.

Scale may change storage/index/executor choices without changing product semantics.

## AX-V15 — Deployment/storage topology

Single local machine → local+cloud sync → hosted backend → distributed analytical stores.

Privacy/exportability constraints must remain explicit.

## AX-V16 — Privacy/security

Public-only data → personal saved data → authenticated private sources → sensitive/collaborative data.

Each step activates stricter permission/encryption/audit requirements.

## AX-V17 — Collaboration

Single user → shared read-only views → shared collections/research → multi-user workspaces and roles.

Not currently required for MVP.

## AX-V18 — UI richness

Chat-first + basic bank → persistent browse/search → dashboards/timelines → visual research builder → rich graph/multimodal exploration.

UI should expose persistent state, not duplicate reasoning already done well in chat.

## AX-V19 — Interoperability

Closed internal API → MCP/tool resources → import/export → third-party knowledge tools → reusable domain/tool plugin ecosystem.

## AX-V20 — Evaluation/quality assurance

Manual inspection → golden scenarios → deterministic contract tests → probabilistic search evaluation → provider experiments → continuous quality regression monitoring.

## AX-V21 — Cost/latency optimization

Quality-first interactive research → provider routing → caching/reuse → bulk/direct API optimization → budget-aware scheduling.

Optimization must not silently weaken provenance/coverage/quality.

## AX-V22 — Data ownership/lifecycle

Save forever by default → retention policies → archiving/tiering → user delete/export/sync policies → organization/tenant governance.

---

# 16. Current recommended sequencing

This is a planning recommendation, not a permanent invariant.

## Phase A — consolidate intent/contracts

1. Keep accepted v1.11 baseline unchanged.
2. Treat this master map as current product-intent reference.
3. Finalize Universal Bank + research-state contracts.
4. Finalize capability/executor model.
5. Convert interaction scenarios into acceptance-oriented product journeys.
6. Amend current red architecture proposal only after these boundaries are accepted.

## Phase B — minimal durable product

1. Bank / IDs / Assets / Entities / Collections / Annotations.
2. Local search/browse/detail/history.
3. Sources/SourcePolicy.
4. Lens + RunSpec + Run + ResultSet/Occurrence.
5. ChatGPT ↔ application tool/API boundary.
6. Basic provenance and history.

External web research remains primarily ChatGPT-driven.

## Phase C — one strong longitudinal research workflow

1. Preserve freelance domain as first end-to-end longitudinal proof.
2. Current State / Changes / Trend / Health.
3. Repeated comparable runs.
4. Verification/counter-search for important claims.

## Phase D — universality proof

1. Games/mechanics similarity.
2. Images/multimodal save/search.
3. Apps/news domain packs as next proofs.

## Phase E — Watch and automation

Only after interactive workflows and data contracts are trustworthy.

## Phase F — direct integrations/scale/advanced analytics

Add only where measured bottlenecks justify them.

---

# 17. How future ChatGPT reasoning should use this map

Before proposing a feature/architecture change, determine:

1. Which product outcome or requirement ID/category does it support?
2. Is it `CORE_INTENT`, `MVP_REQUIRED`, `TARGET_REQUIRED`, `CONDITIONAL_REQUIRED`, `FUTURE_OPPORTUNITY`, `EXPERIMENT`, or `OPEN_DECISION`?
3. Which extension axis/axes does it move?
4. Does it violate a stable invariant or anti-goal?
5. Does it activate a conditional requirement?
6. Can the need be satisfied by ChatGPT/existing tools before adding application infrastructure?
7. Is it domain-specific and therefore better placed in a Domain Pack?
8. Does it create new canonical truth, a derived representation, or only an index/projection?
9. Does it affect historical comparability/provenance?
10. What concrete user scenario proves its value?
11. What evidence/review finding supports promoting it from opportunity to requirement?

Do not silently promote every idea to a requirement. Do not silently demote a target product goal merely because it is deferred from MVP.

---

# 18. Success criteria for the architecture direction

The architecture direction is healthy if all of these can be true simultaneously:

- saving a game/image/article/note/source does not require creating a research project;
- the same object can be reused across many research runs without duplication;
- a historical run can reproduce what it returned at that time;
- ChatGPT can perform external research without the application implementing every provider directly;
- repeated research updates one longitudinal bank and preserves old observations;
- current state is always scoped/coverage-aware rather than pretending to cover the whole world;
- games, apps, news and freelance can use the same kernel with domain packs;
- similarity can mean different things without corrupting canonical data;
- direct provider integrations can be added later without rewriting research semantics;
- future analytics can be layered on historical observations without overwriting raw evidence;
- review findings/opportunities/risks remain durable and can be reclassified over time.

If a future design cannot satisfy these simultaneously, it should be treated as a likely architectural regression against current product intent.
