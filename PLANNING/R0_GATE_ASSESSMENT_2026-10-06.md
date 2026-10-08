# R0 contract readiness assessment — 2026-10-06

R0-GATE-READINESS-001. Object: the 20-gate readiness checklist plus the scoped R1 operations/search/ownership/retention contract. This is development decision evidence, not an application release.

## Result

Minimal R1 ownership, navigation, read operations, lexical fields/query semantics, original retention and expected-ID controls now have explicit design contracts. The three user choices are recorded verbatim and no longer pending. The current work item is completed in that bounded scope. No requirement wording/classification, milestone/feature delivery, baseline schema or canonical physical store is changed.

R0 remains not fully accepted. The R0 milestone's two criteria require integrated acceptance of the complete contract set, not only this checkpoint. Existing Source/Entity/types/compatibility checkpoints and vNext UC-to-contract mapping remain partial at their own scope; full gate acceptance must reconcile them together with inventory before marking the milestone accepted. Native query-fixture tests do not prove that integration. Runtime LW gates are separate R1/R2 acceptance and are not treated as unanswered R0 design questions.

| Gate group | This checkpoint | Remaining / when required |
|---|---|---|
| OPEN-001/002/003/004 | R1 navigation and single Bank identity/ownership recorded; future Project/Lens roles bounded | UI implementation R1; actual research UX/types R2; richer alternatives separately |
| OPEN-005 | Existing R1 pinned minimal reference contract preserved | Runtime pinned reopen R1; full registry R4 |
| OPEN-007 | No silent expiry/delete, unaccepted package visibility, explicit staging/cleanup boundary | Disk-full/retention/export/restore runtime tests before corresponding R1 use; deletion policy if requested |
| OPEN-009 / PLAN-SOURCE-ENTITY | Existing strict allowlist/type-schema matrix and Source boundary preserved | Integrated actual-type/UC compatibility evidence before full gate acceptance; Source runtime R2 and future converters explicitly separate |
| OPEN-010/018 | Versioned lexical fields, strict UTF-8 extraction/cap, snapshots/modes, 22 manual expected-ref queries | Production postings/cache parity, restart/rebuild/pagination R1; relevance profiles R6/R7 |
| OPEN-011 / PLAN-LOCAL-WRITE | Existing SQLite canonical format/limits/durability design unchanged | Safe Windows intake and serialized importer/CAS/recovery, actual LW runtime gates; no full app delivered |
| OPEN-012 | Closed query request schema, semantic outputs/errors, command/query separation | Actual local callable adapter and response/byte-transfer conformance before R1; names here are contract names |
| OPEN-015 | PC-on sufficient, local-first unchanged | Local transport/unavailable UI runtime R1 |
| PLAN-CLAIM-ENUM / PLAN-CLUSTERING-PARITY | Existing documentation resolutions retained | Runtime enum normalization R4; supported clustering inputs/evaluation R5 |
| PLAN-INVENTORY | 115 requirements/classes and phased obligations preserved; no blanket proposal adoption | Integrated gate acceptance and affected-contract traceability only, 41 proposals still pending |
| PLAN-WINDOWS-PARITY | Accepted legacy tree untouched; new tests independent of affected baseline validators | Maintenance copy/patch and parity before reliance on those validators; not inferred from this query oracle |
| COND-003 / OPEN-017 | User scope explicit; ideas/analysis not presumed public, extra AI providers not planned | Applicable access/exposure/retention/export controls before nonpublic real use |
| COND-005/006/007 | No strict-claims/ranker/bitemporal waiver introduced | Re-evaluate actual trigger before implementing corresponding capability |

## Evidence and limits

Contracts: CONTRACTS/BANK_OPERATIONS_R1.md, BANK_SEARCH_R1.md, BANK_QUERY.schema.json, BANK_QUERY_EXAMPLES.json.
Tests: TOOLS/check_bank_queries.py (read-only corpus oracle), test_bank_queries.py (8 counterexample groups); Windows execution/exit codes and all hashes are recorded by WORK_ITEMS/R0_GATE_READINESS_RECEIPT.json only after successful checks and writes.
Expected IDs are manually specified, independent of the matching algorithm. Synthetic corpus is schema-shaped; original hashes and extraction exclusions checked. Tests include current vs retained history, pinned get with no latest fallback, snapshot paging, cache-not-ready/unavailable/profile errors, Unicode and query limits. Oracle uses no production index or network.

No service/CLI, live Bank, UI, real research, power-loss/confinement acceptance, whole-Unicode parity, migration or private-data deployment is tested here. No background provider exposure, scheduling, cloud, new workspace scope or auto-deletion is introduced.

## Review log — R0-RC-20261006

- Confirmed new contract defects after native successful verification: none within this checkpoint's tested scope. The receipt is authoritative for execution success, not this prose.
- U-RC1: full R0 integrated gate and UC/type compatibility acceptance remains incomplete; retain original partial findings and gate state. Does not block bounded synthetic development, blocks announcing R0 accepted.
- U-RC2: actual query adapter, response/byte-transfer semantics, SQLite postings and Windows importer remain unimplemented; runtime parity and LW checks are required before corresponding release/use.
- D-RC1: measured index/storage growth and large-media extraction; revisit on real workload/limit change. Retention without expiry consumes disk; ignored growth can cause backpressure.
- D-RC2: profile Unicode identity must be reevaluated on runtime upgrade and cache rebuild. Ignoring version changes can alter matching while appearing identical.
- D-RC3: explicit deletion/privacy/backup destination policy; revisit on deletion/nonpublic-use/provider-exposure request. Never silently reclaim retained originals or publish ideas.
- Q-RC1 Proposal: start an isolated Windows secure-intake reader probe before a full importer. High suitability for autonomous decision: unchanged user need/scope, bounded implementation complexity; non-blocking user clarification. Safe intake evidence is blocking the later production write path.
- Q-RC2 Proposal: use a disposable local SQLite term cache, no canonical schema change or external service. High suitability for autonomous decision, non-blocking; revisit OPEN-010 at R6 or measured performance failure.
- User assistance: no new answer/access request needed for the present synthetic task. Prior user choices remain canonical; no request to repeat them.

Next bounded work: WORK_ITEMS/R1_SECURE_INTAKE.json. It collects Windows safe-read evidence in temporary synthetic directories, not production Bank commits or R0/R1 release acceptance.
