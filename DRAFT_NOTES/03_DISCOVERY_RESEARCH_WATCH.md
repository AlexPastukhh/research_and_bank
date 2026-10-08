# Search, discovery, research and watch draft

## Separate concepts

```text
Source       = where data may come from
SourcePolicy = which sources are allowed/preferred for a research intent
SourceRoute  = concrete source-specific access/query configuration
Tool         = how to acquire/process/analyze
Lens         = what qualifies / what question or view the user wants
Recipe       = how to execute the research/analysis reproducibly
RunSpec      = immutable compiled configuration for one execution
Run          = one concrete execution and its outcomes
Watch        = when/how to repeat and when to notify
Bank         = durable accumulated material/knowledge
```

The goal is **single ownership of each concern**, not a stack of objects that silently override each other.

## Configuration authority model

### `ResearchLens` owns semantic intent — **what**

A lens describes the meaning of the requested result, not concrete execution machinery. Possible fields:

- intent / natural-language goal;
- target entity/event types;
- structured filters and exclusions;
- similarity seeds/profiles;
- semantic/historical time window;
- requested result dimensions/projections;
- ranking intent;
- personal profile/lens reference;
- acceptable data-freshness requirement when freshness is part of the meaning of the answer;
- optional `source_policy_ref` as a constraint on where evidence may come from.

A lens does **not** own concrete source routes, tool bindings, execution schedule or crawler parameters.

A lens may be saved, cloned, modified, compared over time, used in a one-off run, or referenced by a Watch.

### `SourcePolicy` owns source boundary — **which sources are allowed/preferred**

Examples:

```text
bank_only
my_saved_sources_only
trusted_group:X
my_sources_plus_external_discovery
explicit_sources:[...]
```

A SourcePolicy expresses source eligibility/priority/trust/compliance constraints. It does not encode a site-specific query.

### `SourceRoute` owns concrete source access — **how to query one source**

A route belongs to a Source and may contain source-specific parameters such as subreddit set, endpoint, category, lookback, API query template or crawl path. Route versions are part of reproducibility.

### `ResearchRecipe` owns execution method — **how**

A recipe is a reusable execution plan for a lens or family of lenses. It may define:

- ordered/conditional steps (`discover → capture → resolve → enrich → measure → compare`);
- required capability/tool bindings and allowed substitutes;
- extraction/normalization/identity-resolution methods;
- measurement/analysis methods and versions;
- route-selection strategy subject to the SourcePolicy;
- acceptance/quality criteria;
- candidate/result limits and cost controls for one run;
- output persistence policy (for example, auto-save observations but require user selection before favoriting candidates).

A recipe does **not** own the repeated schedule. It maps the semantic request into concrete execution.

Example:

```text
goal family: find emerging indie games
steps: discover → capture → resolve → enrich → measure → compare
tools: game-source adapter, web search/crawler, resolver, trend analyzer
methods: identity-v2, review-velocity-v1, growth-v3
quality: minimum source diversity + coverage reporting
```

### `Watch` owns repetition and alert lifecycle — **when**

A Watch references a Lens and normally a Recipe. It owns:

- cadence/event trigger;
- active/paused lifecycle;
- alert/change rules;
- notification policy;
- watch-level cost/budget caps;
- retry/backoff and missed-run policy;
- optional explicit, typed overrides that are allowed by contract.

A Watch should not duplicate Lens filters, source routes or Recipe tool/method definitions.

### No silent precedence

There is no generic “last object wins” rule. If two inputs attempt to own the same non-overrideable concern, compilation fails before external work begins. Any supported override must be explicit, typed, recorded, and visible in the resulting RunSpec.

## Immutable compiled `RunSpec`

Before a command performs acquisition/research, the application compiles the selected versions into an immutable execution snapshot:

```text
RunSpec
  run_id
  lens_id + lens_version
  recipe_id + recipe_version
  source_policy_id + version
  selected source_route_ids + versions
  tool/capability bindings + versions
  method/model versions
  resolved semantic time window
  data-freshness requirement
  concrete acquisition windows
  budgets/limits
  explicit overrides
  watch_id + watch_version (when triggered by a watch)
  compiled_at
```

Historical comparison should use the stored RunSpec rather than reconstructing effective configuration from whatever the current Lens/Recipe/Watch happens to contain later. A compile error is preferable to an ambiguous run.

## Result-set history

A Run can produce one or more immutable `ResultSet`s containing `ResultOccurrence`s. This records “what this execution returned” even when every returned item already existed in the Bank and no new external Observation was created. Result history may retain rank, profile/method version, scores/dimensions, why-match features and origin/lineage.

This supports questions such as:

> What exactly did the 5 October run return, in what order, and why was item A ranked first at that time?

without re-running a newer embedding/ranker.

## Search modes

The bank/search layer should eventually support multiple independent modes.

### Exact / structured
Fields, ranges, tags, types, dates and domain filters.

### Full text
Lexical search over stored text/OCR/captions/transcripts.

### Semantic
Natural-language meaning rather than literal words.

### Similarity / example-based
Use one or more saved items as seeds.

### Image/media similarity
Visual, style, object, perceptual-duplicate and semantic image similarity are different profiles.

### Domain-structural similarity
Example: games similar by mechanics/core loop rather than marketing description.

### Relation/graph
Search through typed relationships.

### Temporal/historical
Search by release/creation/first-seen/active period or “what did we know then?”.

### Change-based
Items whose metrics, status or relationships changed in a specified way.

### Evidence/research lineage
Everything used by or produced by a research run, claim, result or interpretation.

### Hybrid
Combine similarity + metadata + time + analytics + personal relevance.

Example:

> Find games mechanically similar to these saved games, released after 2020, with low combat weight and rapidly growing player interest in the last 60 days.

## Multi-aspect similarity

Never reduce every domain to one opaque similarity number.

For games, possible dimensions:

- mechanics;
- core loop;
- player verbs;
- progression;
- systemic/emergent behavior;
- theme;
- visual style;
- audience;
- monetization;
- session structure.

For images:

- perceptual near-duplicate;
- visual composition;
- objects/content;
- style;
- color/texture;
- semantic caption meaning.

A query may choose a profile or weighted combination. UI should explain why two items are considered similar.

## Search/similarity evaluation contract (future design requirement)

Central probabilistic/vector retrieval should eventually have versioned quality evaluation rather than only technical “index built” checks. Candidate concepts:

- `SearchEvaluationSet` — versioned benchmark queries/seeds and scope;
- `RelevanceJudgment` — human/domain-approved relevance labels or graded judgments;
- `SearchEvaluationRun` — ranker/representation/profile version + produced metrics.

Possible metrics depend on the search mode: Precision@K, Recall@K, nDCG/MRR where appropriate, diversity/novelty measures, and ranking/profile stability. No single metric should become universal.

Example regression: mechanics embedding v3 indexes successfully but retrieves games by theme/marketing wording rather than mechanics; a mechanics-specific evaluation set should expose that change.

This is a future production-quality requirement, not a claim that the current note archive failed its original task.

## Watch examples

- watch a game’s price, player count, reviews and updates;
- watch a company for news, jobs, funding and products;
- every day find new games similar to a saved collection;
- alert when a freelance demand cluster grows materially;
- alert when an image or related original appears elsewhere;
- watch source health separately from the research target.

## Bank-first discovery policy

Useful default SourcePolicies:

```text
1. bank only
2. saved/trusted sources
3. saved sources + selected external connectors
4. broad external discovery, if explicitly allowed
```

The user should be able to choose the source boundary without redefining the Lens semantics.

## Query must not silently refresh

Preserve the accepted v1.11 command/query boundary. A query over current/historical bank state should be able to say `refresh_recommended` rather than silently launching expensive acquisition/research unless user intent explicitly requests fresh data or product policy authorizes it.

## Retrieval and verification pipeline (current vNext direction)

For serious tracked research, external discovery should be decomposable into explicit stages rather than one opaque “research” call:

```text
Lens + SourcePolicy
        ↓
RetrievalRun(s)
        ↓
merge / dedupe / classify sources
        ↓
provisional observations / claims
        ↓
counter-search where material
        ↓
claim ↔ evidence verification
        ↓
accepted / disputed / insufficient result state
        ↓
Run ResultSet / projections
```

### `RetrievalRun`

A retrieval execution records, where available:

- provider/capability executor;
- query/query variant;
- source policy/boundary;
- provider parameters/version where exposed;
- returned candidate URLs/items;
- timestamp;
- relation to the parent ResearchRun/RunSpec.

This allows the system to evaluate retrieval quality instead of assuming a second provider automatically adds independent evidence.

### Retrieval diversity analytics

Potential later metrics:

- overlap between providers;
- unique domains;
- unique primary sources;
- unique useful sources;
- marginal independent evidence;
- counterevidence found;
- duplicate/low-quality rate;
- cost and latency.

### Counter-search

A counter-search task intentionally searches for evidence that can contradict, narrow, re-scope, or offer alternative explanations for a material provisional claim. “No counterevidence found” must not be interpreted as proof.

### Claim verification

Canonical verification statuses (master §7.2 / TGT-014) are:

```text
SUPPORTED
PARTIALLY_SUPPORTED
CONTRADICTED
INSUFFICIENT
MISSCOPED
SOURCE_DOES_NOT_SUPPORT
```

`PARTIAL` is the former Claim-status spelling and a scoped legacy read/import alias for `PARTIALLY_SUPPORTED`; canonical writes use the full name. Preserve the original imported value and normalization provenance. This documentation does not implement runtime compatibility or change unrelated `PARTIAL` classifications.

Verification should inspect whether a source actually entails the claim, including scope, geography, period, actual-vs-forecast, measurement definition, and dependency on upstream sources.

### Source genealogy

Where important, preserve source-to-source relations such as:

```text
cites
derived_from
syndicated_from
republishes
reports_on
based_on_dataset
```

This helps distinguish many pages from many independent evidence origins.
