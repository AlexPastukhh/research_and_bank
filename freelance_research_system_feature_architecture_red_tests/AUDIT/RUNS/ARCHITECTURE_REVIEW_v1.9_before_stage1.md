# Current System Review — v1.9 → next architecture

## Executive result

**v1.9 control plane is internally consistent, but it is not yet complete for the planned user-facing result/UI layer.**

### Verified green checks

- `validate_use_cases.py`: PASS — 20 use cases.
- `validate_architecture.py`: PASS under the current v1.9 budget.
- Golden Paths GP01–GP06: 6/6 PASS.
- Quick regression gate: PASS.
- Smoke test: PASS.
- 100,000-observation benchmark: PASS (~0.29s in this run; limit 10s).
- Manifest: 128 tracked files, 0 missing, 0 mismatches.
- Workbook contains 33 named sheets.

### Important caveat

The combined `validate_system.py` and `AUDIT/run_system_audit.py` launchers timed out under the current execution environment, while their independent short gates passed. Treat this as a test-orchestration weakness to harden, not as evidence that every underlying check failed.

## Findings

### F-NEXT-01 — Use-case coverage is write-side heavy
- Severity: **high**
- v1.9 has 20 lifecycle/research/maintenance/governance UCs but no first-class query/result UCs for Current State, Changes, Trends, Interpretations, or Research Health.

### F-NEXT-02 — Use-case contracts are not yet complete
- Severity: **high**
- All 20 UCs have routing/preconditions/references/outcomes/transitions, but 0/20 have explicit first-class inputs, outputs, writes, failure modes, side effects, UI/API bindings, freshness/comparability requirements.

### F-NEXT-03 — Result Projection / Query layer is missing
- Severity: **high**
- The attached result contracts define five canonical user-facing products, but v1.9 has no canonical builders/stores/query interface for them.

### F-NEXT-04 — Current grouping is insufficient for UI/query architecture
- Severity: **medium**
- Current `kind` values are orchestration/research/maintenance/governance; there is no separate semantic `group` and `interaction_type` (command/query/orchestration).

### F-NEXT-05 — Architecture budget blocks justified query expansion
- Severity: **medium**
- `max_top_level_use_cases` is 20; adding five genuinely new query intents requires a versioned budget change with AX26 evidence.

### F-NEXT-06 — Golden Paths cover command-side but not result/query-side
- Severity: **medium**
- GP01–GP06 exercise lifecycle/research/maintenance/migration, but none exercises CurrentStateSnapshot/ChangeSet/TrendSeries/Interpretation/Health or query→refresh→query loops.

### F-NEXT-07 — No generated whole-system map in the release
- Severity: **medium**
- v1.9 has architecture docs and registries, but no canonical generated dependency map or parity gate tying them together.

### F-NEXT-08 — Audit axes are broad but their concrete result/UI/map checks are not yet encoded
- Severity: **medium**
- AX01–AX26 can cover the new layer without AX27, but pass criteria/evidence maps need explicit checks for projection correctness, query/command boundaries, map parity and UI-derived views.

### F-NEXT-09 — Monolithic validate_system/audit launchers remain timeout-prone in this environment
- Severity: **low**
- Independent validators/gates pass, while the combined launcher timed out externally; release tooling should have internal per-check timeouts and machine-readable partial results.

## Use-case contract completeness

| Field needed for full UC contract | Present in v1.9 UCs |
|---|---:|
| `group` | 0/20 |
| `interaction_type` | 0/20 |
| `actor_intent` | 0/20 |
| `inputs` | 0/20 |
| `reads` | 0/20 |
| `writes` | 0/20 |
| `capabilities` | 0/20 |
| `outputs` | 0/20 |
| `freshness_requirements` | 0/20 |
| `comparability_requirements` | 0/20 |
| `acceptance` | 0/20 |
| `failure_modes` | 0/20 |
| `side_effects` | 0/20 |
| `idempotency` | 0/20 |
| `capability_requirements` | 0/20 |
| `ui_surfaces` | 0/20 |
| `api_queries` | 0/20 |
| `golden_paths` | 0/20 |

## Axis recommendation

**Do not add AX27 yet.** The new risks fit the existing framework:
- **AX01**: user-result fitness — required result products answer declared user questions.
- **AX05/AX06**: current state/trends/changes must respect freshness and comparability.
- **AX19**: query-side Golden Paths and projection regressions.
- **AX20**: generated System Map and UI/result-contract artifacts are release-integrity requirements.
- **AX21/AX22**: command vs query routing and boundary coverage.
- **AX23**: query→gap→command→query composition must close deterministically.
- **AX24**: system map/UI maps are generated/derived, never second authorities.
- **AX25**: request→query UC→projection→source result lineage.
- **AX26**: justified budget increase and dependency-count limits.

## Current conclusion

v1.9 is a sound base for the next step. The correct next architecture change is not more research primitives; it is to complete the UC contract model, add a result/query side, implement projection products, and make the whole-system map a generated release artifact.
