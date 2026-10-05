# 2026-10-05 — Independent review of Universal Bank vNext draft archive

## Reviewed object

`freelance_research_system_with_universal_bank_vnext_drafts.zip`

Scope:

- preservation of the original `freelance_research_system_feature_architecture_execution_owners (1).zip` baseline;
- status separation between accepted v1.11 and vNext exploration notes;
- coverage of the user's desired Universal Bank / Research / Watch / Search / Sources / Tools / ChatGPT+UI direction;
- internal design gaps in the drafts;
- selected claims about external tools/components.

## Baseline result

Confirmed at review time:

- original archive content was preserved and `DRAFT_NOTES/` was additive;
- accepted v1.11 and proposal status were not silently rewritten;
- major user-intent areas were represented in the draft notes;
- baseline validation/smoke evidence remained healthy.

## Findings as originally raised

### RV-001 — Historical result occurrence / result-set membership

**Original classification:** substantial current design problem.

The review argued that Entity + Observation + generic lineage may not be sufficient to preserve exactly which existing bank items were returned by a particular historical search/research run, including rank, retrieval/similarity profile, scores and reasons.

Example concern:

```text
mechanics representation v2:
  run R1 -> A ranked #1, B ranked #2

later mechanics representation v3:
  current search -> B ranked #1, A ranked #4
```

Without a frozen result occurrence/result-set record, answering “what exactly did R1 return and why?” may require reconstruction with newer models.

**Suggested future construct:** `RunResultOccurrence` / `SearchHit` / `ResultMembership` or an equivalent immutable result lineage contract.

### RV-002 — Evidence admissibility for arbitrary bank content

**Original classification:** substantial current design problem.

Concern: arbitrary saved notes, AI annotations, derived summaries and source captures coexist in the bank. The review warned that, without explicit evidence eligibility/derivation rules, a derived AI statement could later be rediscovered and treated as independent evidence.

Potential hardening fields discussed:

```text
epistemic_class
evidence_eligibility
derived_from
independence_group
```

### RV-003 — Search/similarity quality evaluation

**Original classification:** substantial current design gap.

Concern: versioned representations are good, but changing an embedding/ranker can silently worsen a central user-facing function such as “find games similar by mechanics”. Suggested future evaluation artifacts:

```text
SimilarityProfileVersion
SearchEvaluationSet
RelevanceJudgment
SearchEvaluationRun
```

with retrieval metrics such as Precision@K / Recall@K / NDCG / ranking stability where appropriate.

### RV-004 — Additional analytics methods not yet recorded

**Original classification:** local completeness gap in analytics backlog.

Ideas raised:

- forecasting with prediction/credible intervals;
- explicit censoring/missingness semantics for lifecycle/survival analysis;
- multiple-testing / alert calibration considerations for large watch sets;
- sparse-segment / hierarchical estimation / shrinkage.

## Notes

The later meta-review reclassified several of these findings. The current status is authoritative in `FINDINGS.json` and the meta-review record; this file intentionally preserves the original review assessment rather than rewriting it.
