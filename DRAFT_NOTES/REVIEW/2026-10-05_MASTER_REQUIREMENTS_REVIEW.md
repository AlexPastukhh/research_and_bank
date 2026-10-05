# Independent review — master requirements and extension axes

Date: 2026-10-05

## Reviewed object and scope

Object: `freelance_research_system_with_universal_bank_vnext_master_requirements.zip`.

Primary scope:

- `DRAFT_NOTES/11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md`;
- `DRAFT_NOTES/12_REASONING_AND_SCOPE_RULES.md`;
- `DRAFT_NOTES/REQUIREMENTS_MAP.json`;
- consistency with earlier vNext draft notes/review corrections;
- preservation of accepted v1.11 baseline;
- completeness relative to the user goal: exhaustively distinguish what is needed now, needed later, conditionally needed, merely possible, and the axes along which the system may evolve.

No attempt was made to promote these draft requirements into accepted v1.11 implementation contracts.

## Review summary

The overall framing is strong and materially useful. The status taxonomy, product north star, invariants, ChatGPT-first execution strategy, conditional-integration triggers, and 22 extension axes closely match the current product direction. Accepted v1.11 remained byte-for-byte unchanged and its system validation/smoke test still pass.

However, the current master map is not yet reliable enough to be the sole authoritative reasoning registry. Three confirmed issues affect that role:

1. requirement traceability/history/axis linkage is incomplete;
2. some previously preserved potentially important ideas were not normalized into the authoritative map or explicitly delegated to a supplemental backlog;
3. the human and machine-readable maps are not fully equivalent in MVP scope.

There is also an unresolved `Entity` vs `Source` boundary and a conditional privacy/security trigger that must be resolved before a real personal-data MVP deployment.

---

## Confirmed problems

### MRQ-001 — Requirement registry is not traceable enough for its stated role

**Classification:** confirmed problem  
**Impact:** affects main result

**Goal / requirement:** future ChatGPT/architecture work should be able to use stable requirement IDs, statuses and `AX-Vxx` expansion axes without reconstructing intent from chat or re-reading every draft.

**Observed deficiency:**

- `REQUIREMENTS_MAP.json` has 115 stable IDs, but the authoritative human document contains none of those requirement IDs;
- all 115 requirement entries lack explicit `axes` links;
- entries do not carry a human-section reference, requirement origin/source, dependency links, or per-requirement status history;
- the human document says status history should be preserved, but the registry has only the current status.

**Trigger / minimal scenario:** a later review proposes a change on `AX-V04 Search sophistication` and asks which current requirements are affected, or promotes `TGT-010` to MVP. The machine registry cannot answer the first question directly, and overwriting the status cannot preserve the second change's history without relying on external archive/version history.

**Observed problematic situation:** the future agent must infer mappings manually from prose. Different agents can produce different mappings, and a status transition can lose why/when it changed.

**Negative consequence:** the master map can drift from its intended purpose as a durable reasoning baseline, especially after several scope changes.

**Recommended correction later:** give each registry entry at least `human_ref`, `axes`, `origin/rationale` (explicit user requirement vs inferred design requirement vs review-derived), and a status/change-history mechanism or append-only requirement-change log. The human document should expose stable IDs or generated anchors.

---

### MRQ-002 — The authoritative map is not fully exhaustive relative to the already-preserved vNext backlog

**Classification:** confirmed problem  
**Impact:** affects main result (completeness goal), not accepted v1.11

**Goal / requirement:** the new master artifact was explicitly created to preserve comprehensively what is needed, what will be needed, what may be needed, and possible axes of expansion.

**Observed deficiency:** several previously preserved ideas remain only in `08_IDEA_BACKLOG_AND_OPEN_DECISIONS.md` and are neither classified in `REQUIREMENTS_MAP.json` nor explicitly declared out-of-scope/superseded by the master map. Examples include:

- nested collections / saved views;
- favorites / pins / archive states;
- importing browser bookmarks/local folders/exports and import conflict/dedupe handling;
- lens branch/clone/compare workflows;
- watch novelty-suppression behavior;
- explicit offline-mode expectations;
- local recomputation/privacy choice for derived representations;
- Domain Pack/plugin packaging contract;
- explicit reproducibility policy for AI-generated representations/annotations.

Some of these may legitimately remain low-priority `FUTURE_OPPORTUNITY` or `OPEN_DECISION`; the issue is that the supposedly authoritative map does not classify them or state that `08_...` remains a normative supplemental backlog.

**Trigger / minimal scenario:** a future agent follows `11_MASTER...` + `REQUIREMENTS_MAP.json` as instructed and never reads `08_IDEA_BACKLOG...`.

**Observed problematic situation:** a previously captured idea can disappear from planning/review consideration even though the purpose of the new artifact was specifically to prevent such loss.

**Negative consequence:** the map can become authoritative by declaration while being less complete than the draft history it is meant to summarize.

**Recommended correction later:** either normalize every still-relevant backlog item into a classified registry entry, or explicitly define a second-tier supplemental backlog with cross-links and a rule that unnormalized items remain preserved but non-authoritative until triaged.

---

### MRQ-003 — Human and machine-readable requirement maps are not fully equivalent

**Classification:** confirmed problem  
**Impact:** medium; can affect MVP scoping

**Goal / requirement:** the JSON is described as the machine-readable summary of the same current intent, so automated/future reasoning should not get a materially different scope from the human document.

**Observed deficiency / examples:**

1. Human MVP proof domains say games should cover “domain structure and mechanics similarity”; `MVP-011` in JSON weakens this to a “game/mechanics-oriented object flow”. Full versioned representations and explainable similarity are otherwise `TARGET_REQUIRED`.
2. Human MVP Bank explicitly requires “basic relations/links sufficient for provenance/use references” while the JSON MVP entries do not state this; `TGT-001` places the Relation layer in target scope.

These can be resolved either way, but the two authorities must agree about whether these are actual MVP capabilities, design-only/golden-scenario constraints, or post-MVP features.

**Trigger / minimal scenario:** an implementation planner uses only JSON and excludes mechanics similarity/basic relation links; another planner follows the human document and includes them.

**Negative consequence:** both can claim conformance to the “authoritative” requirements while producing different MVPs.

**Recommended correction later:** generate one view from the other or add stable cross-references and automated parity validation between human/JSON statements, classifications and scope qualifiers.

---

## Disputed / uncertain areas

### MRQ-004 — `Source` vs `Entity` canonical identity boundary

The human map lists `source` as an example of `Entity`, while also defining a separate MVP `Source` primitive. It is not clear whether a website/community/provider/channel should:

- be a specialized Entity;
- be a separate Source object linked to an Entity;
- or be Source-only unless independently relevant as an observed-world entity.

No runtime defect exists yet, so this is not a confirmed current problem. It must be resolved before canonical data-model acceptance because otherwise the same site/community can acquire duplicate identity, relations and provenance paths.

---

## What passed review

- Classification vocabulary correctly distinguishes present requirements from target, conditional, experimental and optional work.
- The “new requirements do not retroactively make old work wrong” rule is explicit and appropriate.
- Universal Bank remains independent of Research ownership.
- ChatGPT-first interactive execution and conditional direct integrations match the current strategy.
- `Lens / SourcePolicy / SourceRoute / Recipe / Watch / RunSpec` authority boundaries remain consistent with the prior correction.
- ResultSet/ResultOccurrence, epistemic separation, counter-search/verification and retrieval measurement are retained without being confused with raw truth.
- “complete/current state” remains scope/coverage-relative.
- Domain Packs remain the mechanism for domain expansion.
- 22 extension axes cover the major expansion dimensions: domains, media, retrieval/search/similarity, sources/executors, rigor/time/automation/analytics/identity/personalization, scale/deployment/privacy/collaboration/UI/interoperability/QA/cost/data lifecycle.
- ZIP integrity passed; all 264 original baseline files are present and byte-identical.
- `TOOLS/validate_system.py` passes for v1.11.0 and `TOOLS/smoke_test.py` passes.
- `DRAFT_NOTES/INDEX.json` hashes/sizes matched all 19 indexed files before this review log was added.

---

## Deferred / Follow-up Items

### DF-MRQ-001 — Decide whether COND-003 is already active for the first real personal-bank MVP

**Preserve:** minimal privacy/data-ownership/security boundary for arbitrary personal files/notes/images.  
**Why deferred:** exact deployment is still open (local-first vs cloud-first; test data vs real personal data).  
**Related goal:** personal durable bank; AX-V15/AX-V16/AX-V22; `COND-003`.  
**Return trigger:** before storing real private/sensitive user material outside a strictly local/private prototype.  
**If ignored after trigger:** personal data may be stored/exposed without adequate authorization, encryption, deletion/export or provider-exposure controls.

### DF-MRQ-002 — Add acceptance criteria when requirements become implementation contracts

**Preserve:** many `MVP_REQUIRED`/`TARGET_REQUIRED` entries are intent statements, not yet independently testable acceptance contracts.  
**Why deferred:** the document explicitly says it is a product-intent baseline, not an accepted implementation contract.  
**Related goal:** Phase A → architecture amendment → executable/golden tests; AX-V20.  
**Return trigger:** when promoting any requirement into architecture/implementation scope.  
**If ignored after trigger:** teams/agents can claim completion against vague wording and recreate the human-vs-machine scope divergence seen in MRQ-003.

### DF-MRQ-003 — Version the machine-readable requirements schema

**Preserve:** `REQUIREMENTS_MAP.json` itself should eventually have an explicit schema version and validation/parity checks.  
**Why deferred:** current JSON is readable and internally valid; no consumer contract exists yet.  
**Related goal:** durable machine reasoning / interoperability / QA; AX-V19/AX-V20.  
**Return trigger:** first automated consumer, generator, migration or CI validation of the registry.  
**If ignored after trigger:** format changes can silently break agents/tools or make historical maps difficult to compare.

### DF-MRQ-004 — Triage omitted organization/import/workflow ideas rather than silently dropping them

**Preserve:** the concrete examples listed in MRQ-002.  
**Why deferred:** none has been proven necessary for MVP, and the existing backlog still preserves them.  
**Related goal:** exhaustive product-intent memory and organized bank UX.  
**Return trigger:** next requirements-normalization pass or before declaring the master map exhaustive/final.  
**If ignored after trigger:** useful previously discussed capabilities may disappear from future reasoning simply because agents use only the master registry.

---

## Review limitations

- This review evaluates design/document consistency and the supplied project/archive state; it does not implement or runtime-test the proposed vNext architecture.
- No exhaustive external product/provider benchmark was required or performed here.
- The review did not rerun every long-running legacy test; baseline byte identity plus `validate_system.py` and `smoke_test.py` were independently rechecked.
- User intent was reconstructed from the available conversation/draft history; individual registry entries currently lack explicit origin metadata, which is itself part of MRQ-001.

## Open questions

1. Should the master registry itself be the only authoritative product-intent inventory, or should `08_IDEA_BACKLOG...` remain an explicitly recognized second-tier source until every item is triaged?
2. Is mechanics similarity an actual first-MVP behavior or only a design/golden scenario proving the future architecture can support it?
3. Should `Source` be a specialized Bank entity, a separate research object linked to an Entity, or a distinct object class with its own canonical ID?
4. Will the first real MVP store private/personal data in cloud/shared infrastructure? If yes, `COND-003` is not deferred in practice.

## Compact Review Log

**Object:** `freelance_research_system_with_universal_bank_vnext_master_requirements.zip` — master requirements / reasoning / registry additions plus baseline-preservation check.

**Overall result:** direction and classification model are strong; no accepted v1.11 regression found. The master map is not yet safe as the sole authoritative machine/human reasoning registry because traceability/history/axis linkage is incomplete, previously preserved backlog is only partially normalized, and human/JSON MVP semantics diverge in at least two places.

**Confirmed issues:** `MRQ-001`, `MRQ-002`, `MRQ-003`.

**Uncertain:** `MRQ-004` Source-vs-Entity boundary.

**Deferred/follow-up:** `DF-MRQ-001` privacy-trigger decision; `DF-MRQ-002` acceptance criteria before implementation promotion; `DF-MRQ-003` requirements-schema versioning; `DF-MRQ-004` triage of omitted backlog ideas.

**Limitations:** no vNext runtime implementation exists; no exhaustive provider benchmark; full long-running legacy suite not rerun in this review.
