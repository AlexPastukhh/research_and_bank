# Proposed golden scenarios for universalization

These are acceptance-oriented scenario drafts. They should eventually map to explicit use cases/capabilities and executable architecture tests if the direction is accepted.

## GSU01 — Freelance longitudinal intelligence

Goal: prove legacy domain still works after generalization.

```text
saved Lens: work relevant to user
→ discover from saved + external sources
→ observe opportunities/tasks
→ resolve identities
→ measure payout/demand/requirements/lifetime
→ update shared bank
→ Current State
→ Changes since previous run
→ Trend
→ Research Health
→ personal relevance projection
```

Key invariant: freelance-only metrics live in its domain pack, not the universal core.

## GSU02 — Game mechanics discovery

```text
save/analyze several games
→ generate/version mechanics representations
→ ask for mechanically similar recent games
→ search bank first
→ external discovery via game sources
→ explain multi-aspect similarity
→ save selected candidates
→ create Watch on collection/similarity neighborhood
```

Proves: bank, domain representations, example-based discovery, collections, external search and watch.

Target extension — `OPP-017` (`TARGET_REQUIRED`, outside MVP): supply positive game examples and, when desired, negative examples with the unwanted mechanics/core-loop dimensions. Compare soft negative preference (lower rank) with explicit hard exclusion; explain the effect on candidates and compare human relevance judgments with the positive-only baseline. The same example contract may be used in other supported domains. This note records intended acceptance; it does not claim an implemented similarity engine or demonstrated quality gain.

## GSU03 — App longitudinal analysis

```text
save app/category Lens
→ repeated observations of price/rating/reviews/rank/releases
→ entity identity across stores/sources
→ current state
→ cohort/lifecycle/trend/change-point views
→ compare with prior periods
```

Proves: generic metrics/time-series, domain events and repeated observation.

## GSU04 — News/event intelligence

```text
saved topic + trusted source group
→ ingest stories
→ cluster duplicate coverage into underlying events/stories
→ maintain source provenance/divergence
→ distinguish event time from discovery time
→ current state + changes + trend/volume + interpretation
```

Proves: bitemporal need, clustering, source diversity and evidence-bound interpretation.

## GSU05 — Save arbitrary image → similarity → research

```text
user saves image without a project
→ Asset stored with provenance
→ image/text/style representations created
→ later find similar items
→ selected results become collection
→ collection becomes research seed
```

Proves: bank independence from research and multimodal reuse.

## GSU06 — Saved sources and reusable tools

```text
user saves source group
→ registers routes/access methods
→ saves research recipe using registered tools
→ reruns recipe on schedule
→ results preserve source/tool/method lineage
```

Proves: Source != Tool != Route != Recipe.

## GSU07 — Historical truth and backfill

```text
system knows state at T1
→ later discovers older evidence valid at T0
→ stores valid time and system time separately
→ historical queries distinguish “true then” from “known then”
```

Proves temporal correctness.

## GSU08 — Identity correction

```text
two records initially separate
→ resolver suggests same entity
→ user confirms merge
→ raw observations remain intact
→ canonical identity/history updates
→ indexes/projections rebuild deterministically
→ split can reverse if later evidence contradicts merge
```

Proves repairability and no destructive evidence loss.

## GSU09 — Bank-first / source-scoped search policy

User asks the same query in three modes:

1. bank only;
2. saved sources only;
3. saved sources + broad external discovery.

Results and provenance must clearly reflect the chosen boundary.

## GSU10 — ChatGPT + UI collaboration

```text
user selects several UI items
→ asks ChatGPT to compare/explain/find similar
→ ChatGPT references stable bank IDs
→ application runs deterministic queries/tools
→ UI updates table/chart/current selection
→ user saves result/lens/watch
```

Proves chat is an orchestration/explanation layer and UI is the persistent state surface.


## GSU11 — Configuration authority and immutable RunSpec

```text
Lens defines semantic intent
+ SourcePolicy defines allowed/preferred sources
+ SourceRoutes define concrete access
+ Recipe defines tools/methods/steps
+ Watch defines cadence/alerts
→ compile immutable RunSpec
→ execute
```

If conflicting ownership remains unresolved, compilation must fail rather than silently override. A later historical inspection must show exactly which versions/configuration the run used.

Proves: deterministic repeated execution and comparability.

## GSU12 — Historical result-set reproducibility

```text
run R1 searches existing bank
→ returns A #1, B #2 under similarity profile v2
→ no new external observation is required
→ ResultSet/ResultOccurrences are stored
→ representation/profile later changes to v3
→ historical query still returns R1 membership/rank/reasons as produced then
```

Proves: research-result history is not reconstructed from current ranking logic.

## GSU13 — Search-quality regression check

```text
versioned mechanics-similarity evaluation set
→ evaluate representation/ranker v2
→ evaluate proposed v3
→ compare mode-appropriate relevance/diversity/stability metrics
→ block or flag materially worse mechanics retrieval
```

Proves: search quality is testable rather than inferred from index health.

## GSU14 — Epistemic reuse without evidence loops

```text
source evidence S
→ AI summary A derived_from S
→ A saved in Bank
→ later research retrieves A
→ A may provide context but is not independent confirmation of S
→ claim support graph preserves dependency
```

Proves: save-anything semantics do not corrupt evidence independence.

## Universality acceptance heuristic

A useful architecture test: the same universal kernel should support at least freelance, games, apps and news by swapping domain packs/adapters rather than adding domain-specific fields to core. If each new domain forces core-schema changes, the abstraction is not yet reusable enough.

## GSU15 — Problem / algorithms / theory / solution evolution

User-confirmed universality example (2026-10-07; SCE-20261007-01). Target acceptance scenario over existing INT-001/002/003, MVP-001/002/005–008, TGT-001/007/012–019/020/024 and COND-001; no new requirement ID or promotion into the first working version.

Save a problem/context, algorithms/implementations, theory/assumptions and supporting materials → retain stable IDs/versions and author/source lineage → use the problem/collection/Lens as the seed of a later scoped research run → combine LLM candidate reasoning with available external primary-source research → search separately for alternatives, limitations, errata, corrections and new techniques → compare applicability under explicit inputs/constraints/objectives/metrics → save findings, uncertainty and evidence/result history → add conditional reassessments without erasing the former account → repeat on request or via a supported Watch.

Required acceptance distinctions:

- R1 can represent problem/algorithm/theory as Entity kinds and details as Asset/Annotation/Collection; richer structured domain fields/types are not silently supported by the closed schema.
- LLM-authored ideas/own knowledge are not independent source evidence or proof of freshness. Unknown model/publication/coverage remains unknown. Formal correctness or performance may need proof/experiments.
- New-to-Bank differs from newly published/invented; a source correction differs from a real change in an algorithm. Missing results do not prove absence of better methods.
- “Better” has a declared context and metric; retain both strengths and counterexamples/limitations. No single universal superiority score.
- Previous theory/assessment/results and exact cited revisions remain available after correction. A retrieved AI summary cannot self-confirm its underlying claim.
- Manual repeat/policy is distinct from unattended automation; COND-001 gates scheduler/executor/retry/alerts. No recurring task is created by this scenario note.

Evidence/limits: PLANNING/SOLUTION_EVOLUTION_SCENARIO_2026-10-07.json and its independent8-case static fixture/checker demonstrate minimal generic shape and boundaries. Full algorithm reasoning, web research, importer/UI and Watch acceptance remain staged. This example extends the reusable-core heuristic beyond the four original domain proof packs.
