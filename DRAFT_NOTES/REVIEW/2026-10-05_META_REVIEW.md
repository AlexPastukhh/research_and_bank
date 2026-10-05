# 2026-10-05 — Meta-review of the Universal Bank draft review

## Object

The object is the preceding review of `freelance_research_system_with_universal_bank_vnext_drafts.zip`, not the archive in isolation.

The meta-review independently re-checked the baseline, draft content and the mechanisms behind RV-001 through RV-004.

## Confirmed review conclusions

- baseline preservation was correctly assessed;
- accepted-v1.11 vs draft-vNext separation was correctly assessed;
- main user-intent coverage was high;
- the need to preserve historical result membership/ranking is a legitimate future contract question;
- explicit censoring semantics are worth retaining when lifecycle/survival analysis is implemented.

## Reclassified review findings

### RV-001 — downgraded from current defect to important future design clarification

The drafts already retain `research_result` roles, `run_id` provenance, backlinks, and lineage to runs/claims/results. Therefore the need was not omitted entirely.

What remains unresolved is the stronger contract: whether exact historical retrieval membership/rank/score/reason must be immutable and independently queryable.

This is important before implementation, but the original task was to preserve design notes, not to fully specify every persistence entity. It should not be called a failure of that task.

### RV-002 — not confirmed as a current defect; retain as possible future integrity risk

The problematic evidence loop requires assumptions that the drafts do not make: that arbitrary bank items are evidence-eligible and that AI-derived items count as independent evidence.

Existing notes already distinguish AI/user Annotation from raw truth, and the accepted baseline already has dependency/independence evidence concepts.

Keep the issue as a hardening/design question, not a confirmed defect.

### RV-003 — future requirement/opportunity, not failure of the reviewed work

Search-quality evaluation is valuable before production use of probabilistic/embedding retrieval, but it was not an original requirement of the note-preservation task.

The drafts already keep testing of probabilistic/LLM components as an open architecture decision. Add a concrete retrieval-evaluation design later.

### RV-004 — mostly optional future analytics ideas

Forecasting, hierarchical estimation and multiple-testing controls are useful candidates, not current defects.

Multiple-testing/FDR is specifically conditional on the chosen alert/anomaly mechanism and should not be mandated prematurely.

Explicit censoring/missingness remains a particularly useful note because it protects the existing `not_seen != disappeared` temporal invariant during future survival/lifecycle implementation.

## Newly confirmed design problem missed by the first review

### MR-001 — configuration authority overlap: Lens / Recipe / Watch / SourceRoute

The drafts deliberately separate:

```text
Source = where
Tool = how
Lens = what
Run = execution
Recipe = reusable execution design
Watch = repeated observation rule
```

But later sections assign overlapping execution concerns:

- `ResearchLens` can own source policy, metrics, freshness, ranking and can be scheduled;
- `ResearchRecipe` can own sources, tools, steps, metrics and schedule;
- `Watch` can own source routes, cadence, freshness and observation rules.

Reachable ambiguity example:

```text
Lens:   my-sources-only, player_growth, weekly
Recipe: Steam+Reddit, review_velocity, daily
Watch:  Steam route, hourly
```

There is no declared authority/precedence/compilation rule for the resulting run.

**Causal chain:** reusable/reproducible repeated research -> overlapping configuration ownership -> Lens+Recipe+Watch combined -> conflicting valid settings -> run semantics are not deterministic -> comparability/reproducibility can become ambiguous.

**Current classification:** confirmed design problem in the vNext proposal, significant before implementation.

One candidate resolution is to give each concern a single owner and compile all resolved versions into an immutable `RunSpec`, but the exact design remains open.

## Newly confirmed planning omission missed by the first review

### MR-002 — build-vs-buy evaluation misses the personal knowledge / AI workspace class

The drafts evaluate crawling/data/search infrastructure and enterprise intelligence platforms well, but the replacement/partial-replacement survey is weaker for products closest to the desired `save anything -> organize -> retrieve/search -> AI-assisted workspace` layer.

Examples to evaluate as references or partial substitutes include products/classes such as:

- Fabric-style AI personal knowledge/workspace products;
- Zotero-style durable source/reference banks;
- other personal knowledge/reference managers and media libraries as appropriate.

The finding does **not** claim any one product replaces the full system. It says the comparison set is incomplete for the specific Universal Bank/UI question.

**Current classification:** confirmed planning omission / future evaluation requirement; it does not invalidate the draft architecture.

## Uncertain point

### MR-003 — Article vs Story vs Event terminology

The drafts sometimes use `article/story` as an Entity example while the news scenarios also require clustering many source publications into underlying stories/events.

Before formal schema work, evaluate an explicit distinction such as:

```text
Publication/Article
Story/Narrative
Event
```

Current evidence is insufficient to call this a confirmed defect; it is a terminology/modeling ambiguity to resolve.

## Overall meta-review result

The original review was strong on baseline preservation and intent coverage but over-classified several newly invented future requirements as defects of the already completed note-preservation task.

The most important confirmed design issue after meta-review is MR-001. The most important planning omission is MR-002.
