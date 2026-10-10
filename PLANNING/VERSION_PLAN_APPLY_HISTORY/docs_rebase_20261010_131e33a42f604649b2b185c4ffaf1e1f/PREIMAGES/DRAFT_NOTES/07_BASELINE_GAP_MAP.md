# Existing baseline → universal-bank vNext gap map

## Important interpretation rule

The limitations below are **not retroactive defects in accepted v1.11**. v1.11 was explicitly designed for freelance-opportunity research. They become gaps only relative to the newly expanded product goal.

The current red architecture suite is also explicitly a changeable `PROPOSAL` while red. If universalization is accepted, proposed red contracts should be amended before implementation rather than implemented and immediately refactored.

## Existing pieces to preserve/generalize

### Canonical use-case routing
Keep the accepted `request → UC contract → capability/workflow → typed output → acceptance → outcome` discipline.

### Command/query boundary
Keep queries read-only; do not silently refresh/research unless user intent/policy calls a command/orchestration.

### Execution ownership
Keep `research_agent`, `application`, `mixed`, `internal`, `development`. Add product interaction scenarios separately from system UCs.

### Sources
Current source inbox/registry/reviews/use-plan model is reusable. Generalize sources beyond freelance channels and strengthen route/tool separation.

### Temporal observations
Append-only observations, stable entity history, `not_seen != closed`, method/scope/source-route comparability are highly reusable.

### Result products
`CurrentStateSnapshot`, `ChangeSet`, `TrendSeries`, `InterpretationRecord`, `ResearchHealthSnapshot` should remain first-class.

### Evidence/provenance
Claims, counterevidence, method versions, source lineage, checkpoints/audit remain core strengths.

## Concepts currently too freelance-specific for universal core

| Current concept | vNext treatment |
|---|---|
| primary unit = `service unit` | move to Freelance domain pack; core uses typed `Entity`/domain unit |
| `UC06 Observe Paid Work` | generalize to observe entities/events/signals; paid-work observation becomes domain specialization |
| opportunity economics schema | move to domain analysis pack/plugin |
| payout/delivery/acquisition effort as universal assumptions | metric registry/domain metrics |
| practical delivery test | Freelance domain use case/capability |
| market acquisition test | Freelance domain use case/capability |
| `Direction Detail` terminology | generic Entity/Segment/Lens detail surface |
| daily run naming | consider `ResearchRun`/`ObservationRun`; cadence is configuration |

## Major missing capabilities relative to new goal

### Universal bank ownership
Data should survive and be reusable across projects/research runs.

### Asset/media storage
Images/files/snapshots/videos/etc. need first-class storage/provenance independent of Entity.

### Cross-research canonical identity
One game/app/company/etc. should not be duplicated for every research run.

### Collections
Mixed user-curated groups that can become search/research/watch seeds.

### Relations / knowledge graph layer
Typed links between entities/assets/claims/events/etc.

### Representations
Versioned embeddings/features/OCR/captions/domain vectors for multimodal and domain similarity.

### Similarity engine
Multiple similarity profiles/dimensions and explainable results.

### Historical bank search
Current-state query is not enough. Need first-class search over all saved/historical objects and observations.

### Source routes
The same saved source can have many reusable query/access configurations.

### Tool/connector registry
Reusable acquisition/processing/analytics capabilities separated from source identity.

### Research lens / recipe / compiled run semantics
Persistent “what to look for/how” specifications that can be reused. After review, concern ownership is clarified: Lens = semantic intent, SourcePolicy/SourceRoute = source boundary/access, Recipe = execution method, Watch = repetition/alerts, and each execution receives an immutable compiled RunSpec.

### Generalized watch
Entity/query/collection/similarity/metric/relation watches, not only known-scope daily monitoring.

### Bitemporal/history semantics
Separate event/valid time from system/capture time where needed.

### Personal projection
Personal relevance/fit/taste should be a projection layer.

### Historical result-set occurrence
A repeated-search/research system needs to preserve not only observed facts but also what a specific run returned (membership/rank/profile/reason), especially for bank-only retrieval that creates no new external Observation. Draft concepts `ResultSet` / `ResultOccurrence` now capture this requirement.

### Evidence eligibility for arbitrary bank material
Storage role is not epistemic authority. User notes, AI annotations, derived metrics and source captures need explicit derivation/independence semantics when used as evidence. The draft now records this as a future integrity guardrail rather than assuming every saved item is evidence.

### Retrieval quality evaluation
Similarity/search representations are versioned, but production implementation should also version evaluation sets and relevance judgments so important modes such as game-mechanics similarity can detect quality regressions.

### External-tool integration
Commodity acquisition/search/analytics infrastructure should be pluggable.

## Existing 25 UC treatment hypothesis

This is a draft mapping, not a final registry amendment.

- UC01 Start New Project → consider Start Research Space/Lens while Bank exists independently.
- UC02 Continue Baseline → keep/generalize.
- UC03 Execute Atomic Task → keep.
- UC04 Discover Candidates → keep/generalize.
- UC05 Verify Channel/Source → keep/generalize.
- UC06 Observe Paid Work → generalize; keep paid-work specialization in Freelance pack.
- UC07 Normalize/Clean → keep + identity resolution hooks.
- UC08 Measure One Dimension → keep + generic metric registry.
- UC09 Monitor Known Scope → generalize to Watch.
- UC10 Rediscover Novelty → keep/generalize.
- UC11 Triangulate Claim → keep.
- UC12 Practical Delivery Test → Freelance pack.
- UC13 Market Acquisition Test → Freelance pack.
- UC14 Filter/Compare/Decide → keep/generalize.
- UC15 Manage Sources → keep + SourceRoute/tool integration.
- UC16 Change Method/Policy → keep.
- UC17 Checkpoint/Handoff → keep.
- UC18 Repair/Reconcile → keep + bank identity/index repair.
- UC19 Audit/Modify System → keep.
- UC20 Migrate Project → keep/generalize to bank/workspace migrations.
- UC21 Current State → keep.
- UC22 Changes → keep.
- UC23 Trend → keep.
- UC24 Interpretation → keep.
- UC25 Research Health → keep.

Potential new first-class user intents/capabilities to evaluate:

- Save/import arbitrary item;
- Search historical bank;
- Find similar / example-based discovery;
- Manage collections/relations;
- Create/modify Research Lens;
- Create/modify Watch;
- Import/backfill historical dataset;
- Correct/merge/split entity identity;
- Manage tools/connectors;
- Compare cohorts/segments.

Not all need top-level UCs; some may be application features/capabilities under existing intents.

## Architectural dependency direction

Preferred:

```text
Universal Bank
  ↑ used by Search/Discovery
  ↑ used by Research Kernel
  ↑ used by Watch/Temporal Engine
  ↑ used by Analysis/Projection
  ↑ exposed through Application API/UI/ChatGPT
```

Avoid making the Bank a child owned by a Research Project.

## Implementation sequencing warning

If the expanded goal is accepted, do not blindly make all current red architecture assertions green first. Perform an explicit universalization amendment:

1. freeze accepted v1.11 baseline as historical truth;
2. classify current red assertions as `keep`, `generalize`, `move-to-domain-pack`, `replace`, `defer`;
3. define Universal Bank + Domain Pack + Source/Tool contracts;
4. rewrite affected red tests explicitly;
5. add multi-domain golden scenarios;
6. only then implement the new architecture.
