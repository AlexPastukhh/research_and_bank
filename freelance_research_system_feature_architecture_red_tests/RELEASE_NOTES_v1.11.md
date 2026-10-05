# Release Notes v1.11.0 — Stage 2

## Phase 2 — Result/query use cases and command/query boundary

- Added UC21 Get Current State → CurrentStateSnapshot.
- Added UC22 Get Changes → ChangeSet.
- Added UC23 Get Trend → TrendSeries.
- Added UC24 Get Interpretation → InterpretationRecord.
- Added UC25 Get Research Health → ResearchHealthSnapshot.
- Query UCs are explicitly read-only: they do not silently run monitoring, measurement, evidence collection, repair, or system audit commands.
- Added English/Russian command-vs-query routing fixtures, including state-sensitive `what changed / что изменилось` cases.
- Integrated result-product contracts and UI screen map into the release.
- Deliberately expanded architecture budget from 20 to 25 top-level UCs and to six semantic groups.
- Result projection builders remain Phase 3; query UCs can report projection capability unavailable rather than fabricate results.
- No new Golden Paths are added in Phase 2; query-side Golden Paths remain Phase 4.

## Acceptance

Phase 2 acceptance A2.1–A2.8 is PASS. All 47 v1.10 routing fixtures are preserved; UC21–UC25 are implemented nodes in the generated map; projection builders remain explicitly Phase 3.

Release integrity: `SYSTEM VALIDATION: OK — 1.11.0`.


## Acceptance Q&A model 1.1

- Added persistent phase execution records under `AUDIT/PHASE_EXECUTION_RECORDS/`.
- Every phase now captures pre-execution questions; emergent questions are append-only; accepted phases require post-execution answers/decisions/evidence for every blocking question.
- Added `REFERENCE/PHASE_ACCEPTANCE_QA.md` generated view, schema, validator, parity check and release-gate integration.
- Phase 0–2 records were reconstructed retrospectively from actual design/acceptance decisions; Phase 3–7 question sets are captured prospectively before implementation.
- System Map now displays question/answer status per development phase.
- Corrected the high-level System Map diagram to show UC21–UC25 as implemented query UCs while the projection backend remains planned.
