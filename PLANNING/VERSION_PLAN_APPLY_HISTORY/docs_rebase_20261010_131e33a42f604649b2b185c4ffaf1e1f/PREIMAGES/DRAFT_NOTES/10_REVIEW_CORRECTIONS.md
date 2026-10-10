# vNext draft corrections after independent review

## Status

This document records **draft-level corrections** made after the archive review and meta-review. It does not alter accepted v1.11 contracts or claim that all vNext decisions are final.

## Corrections integrated

### 1. Configuration authority made explicit

The previous drafts allowed `ResearchLens`, `ResearchRecipe` and `Watch` to overlap on sources, metrics/freshness and schedule. The corrected draft uses single concern ownership:

```text
Lens         = semantic intent / what qualifies
SourcePolicy = allowed/preferred source boundary
SourceRoute  = source-specific access/query configuration
Recipe       = execution methods/tools/steps
Watch        = cadence/alerts/lifecycle
RunSpec      = immutable compiled effective configuration
```

There is no implicit “last value wins” precedence. Unsupported conflicts fail during compilation; permitted overrides are explicit and stored.

### 2. Historical result output is explicit

`ResultSet` / `ResultOccurrence` are added as draft concepts so an old run can preserve exact membership/rank/profile/reason even when items already existed in the Bank and current ranking models have changed.

### 3. Arbitrary saved content does not automatically become independent evidence

The Bank model now distinguishes epistemic classes and derivation. Saved AI/user/derived material may be useful context, but research methods must decide evidence eligibility and preserve dependency/independence.

### 4. Search/similarity quality becomes testable

The search draft now proposes versioned evaluation sets, relevance judgments and evaluation runs for important probabilistic/vector retrieval modes. This is a future production-quality requirement, not a retroactive defect in the note-preservation task.

### 5. News identity terminology clarified

The draft now distinguishes:

```text
Publication/Article = source-authored content
Story/Narrative     = derived grouping of related coverage
Event               = real-world occurrence
```

This prevents source publications from being accidentally collapsed into one event identity.

### 6. Build-vs-buy survey broadened

The integrations note now includes the personal knowledge / AI workspace / research-source-bank class. Fabric and Zotero are explicit reference/partial-substitute candidates, with comparison axes covering capture, search, provenance, exportability, APIs/MCP, privacy, temporal research semantics and lock-in.

### 7. Analytics backlog hardened without over-promoting optional ideas

Added as explicitly future/conditional topics:

- forecasting with uncertainty;
- censoring/missingness for survival/lifecycle;
- alert calibration/multiple comparisons when statistically applicable;
- sparse-segment/hierarchical estimation.

Only censoring/missingness is treated as particularly important if lifecycle analysis is implemented because it protects `not_seen != disappeared`.

## Review-ledger rule

The original findings are not erased. `DRAFT_NOTES/REVIEW/FINDINGS.json` records their earlier classification and appends correction history/current status.
