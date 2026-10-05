# Freelance Opportunity Research System v1.11

Reusable system for researching **what people pay other people to do**, where that work is found, how much it pays, how much effort it requires, and how those markets change over time.

It is designed for two situations:

1. **new project** — start from a decision question and build a baseline;
2. **clean-chat continuation** — provide a previous research repo/archive plus this system, reconstruct state, reuse valid methods/sources, create a minimal DeltaPlan, and continue one atomic task at a time.

## Core question

The system can ultimately compare combinations such as:

`service unit × client segment × channel × skill level × economics/effort`

It explicitly supports the full work spectrum: programming/software, creative work, operations/admin, microtasks, testing/feedback/research participation and specialist services. Cheap tasks are retained rather than filtered out automatically.


## Canonical action routing

Top-level actions are now routed through one canonical registry: `CORE/USE_CASE_REGISTRY.json`.

`request → complete use-case contract → Task Manifest/capabilities → execute → typed outputs → acceptance → outcome → transition`

This replaces duplicated routing logic previously spread across START_HERE, decision trees, bootstrap instructions and AtomicPlan. Those files may explain or visualize flows, but they are no longer independent routers. See `CORE/USE_CASE_ARCHITECTURE.md`, `REFERENCE/USE_CASE_REGISTRY.md`, and the generated `REFERENCE/SYSTEM_MAP.md`.

## Pipeline

`Define → Discover → Verify → Observe → Normalize → Clean → Measure → Triangulate → Filter → Practical Test → Market Test → Decide → Monitor → Rediscover`

For an existing project, prepend:

`Bootstrap → Reconcile → Staleness Scan → DeltaPlan`

## v1.6 operational core

v1.6 makes reuse deterministic rather than dependent on chat memory:

- `CORE/SYSTEM_SPEC.json` — machine-readable system contract;
- `PROJECT_INDEX.json` — canonical pointer map inside each project;
- `RUN_STATE.json` — compact execution state;
- Task Manifests — exact atomic question, method/version, inputs, forbidden work, outputs and acceptance tests;
- `METHOD_REGISTRY.json` — versioned reusable methods and SearchRecipes;
- `DEPENDENCY_GRAPH.json` — change propagation without rerunning everything;
- `HANDOFF.json` + `SESSION_CHECKPOINT.md` — portable clean-chat checkpoint;
- system/project validation + smoke-test tools;
- opportunity-economics schema for payout, delivery effort, acquisition effort, costs and effective hourly economics.


## Temporal + configurable runtime

- policy values live in `CORE/SYSTEM_DEFAULTS.json` and project-local `PROJECT_CONFIG.json`; changing TTLs, cadence, timezone, priorities or interesting-item rules does not require code changes;
- every research pass can be recorded as a dated Daily Run;
- observations are append-only and linked to stable entities;
- daily diffs distinguish `new`, `changed`, `confirmed closed`, `reopened` and merely `not seen`;
- `not seen` never means `closed` by default;
- interesting items can be viewed by the day they appeared/changed;
- test suite uses deterministic clocks, semantic invariants, idempotency, mutation tests and metamorphic/refactor-resilience checks.


## v1.6 audit remediation (retained in v1.9)

v1.6 closes the AX01–AX20 findings discovered in the v1.5 self-audit. In particular it adds confined project paths, unified JSON Schema validation, gap-safe temporal identity, source-route comparability, recoverable multi-file transactions, explicit migration support, executable measurement/economics checks, dependency impact propagation, repair tooling and release-manifest verification.

Release checks are split into a short critical contract gate (`python TOOLS/run_tests.py`) and the full regression suite (`python TOOLS/run_tests.py --full`). The persistent AX01–AX26 audit remains the higher-level release criterion.

## Source management

Research sources are reusable project objects:

`SourceInbox → SourceRegistry → SourceReviews → SourceUsePlan`

Keep separate:
- **source category** — what it is;
- **source role** — `discovery / evidence / both / archive`;
- **priority** — mutable general priority;
- **task priority** — task-specific override;
- **discovered via / discovery route** — how the source was found.

Search engines, Reddit, forums and curated lists may be discovery routes; they do not automatically become final evidence for the claim they helped discover.

## Clean-chat start

The new agent reads:

1. `START_HERE_AGENT.md`
2. `CORE/SYSTEM_SPEC.json`
3. previous project `PROJECT_INDEX.json` when available
4. `STATE.json` + `RUN_STATE.json` + last checkpoint
5. only then the files needed by the next task

It should not ask the user to restate recoverable history.

## Main directories

- `CORE/` — stable machine/human system contract.
- `BOOTSTRAP/` — ingest previous research and build DeltaPlan.
- `METHOD/` — research methodology.
- `TEMPLATES/` — project/runtime/schema templates.
- `TOOLS/` — initialization, validation, checkpoint and change-propagation helpers.
- `WORKBOOK/` — spreadsheet template.
- `REFERENCE/` — decision trees, cadence and lessons.
- `EXAMPLE/` — clean-chat and pilot walkthroughs.
- `GOLDEN_PATHS/` — executable end-to-end release scenarios and run history.

## Start a new project

```bash
python TOOLS/init_project.py /path/to/new_project my-project-id
python TOOLS/validate_project.py /path/to/new_project
```

Then fill `PROJECT_BRIEF.md`, create the first Task Manifest and execute `M01`.

## Continue a previous project

```bash
# preferred: accepts repo/folder, ZIP, standalone file(s), or a mixture
python TOOLS/bootstrap_cycle.py -o /path/to/new_cycle /path/to/old_project_or_zip [more_artifacts...]

# simpler pointer-only initializer when baseline is one directory
python TOOLS/init_baseline_cycle.py /path/to/old_project /path/to/new_cycle
```

Then follow `START_HERE_AGENT.md` / BOOT-01…BOOT-06.

## Checkpoint

```bash
python TOOLS/checkpoint_project.py /path/to/project
python TOOLS/validate_project.py /path/to/project
```

## System self-check

```bash
python TOOLS/validate_system.py
python TOOLS/smoke_test.py
```

## Hard rules

- One atomic task at a time.
- Discovery is not measurement.
- A stratified discovery sample is not a demand-frequency sample.
- Historical snapshots are append-only.
- Reuse exact method versions when comparability matters.
- Never silently resolve state conflicts.
- Never simulate unavailable capabilities or inaccessible sources.
- Preserve negative/counter evidence.
- Do not discard cheap/simple work merely because higher-paying work exists.
- Do not create a master ranking before the underlying dimensions have been measured.

System version: **1.11.0** — 2026-10-01.


## System self-audit

The system carries its own persistent audit framework under `AUDIT/`. `AUDIT/AUDIT_AXES.json` is the canonical AX01–AX26 contract. Release audits preserve their reports under `AUDIT/RUNS/`. Green unit tests do not imply audit clearance; critical-axis failures remain release blockers.

Quick baseline audit: `python AUDIT/run_system_audit.py --target .`. Full release audits additionally execute the adversarial cases in `AUDIT/TEST_CASES.md`.


## v1.8 use-case routing hardening

Use-case routing is now verified by multilingual/state-sensitive fixtures, explicit use-case kinds, outcome-guarded transitions, route lineage in Task Manifests, and an enforceable architecture complexity budget. Mutable routing metadata is owned only by `CORE/USE_CASE_REGISTRY.json`; workflow Markdown no longer duplicates it.


## Golden Paths

Release-gate end-to-end workflows are defined in `CORE/GOLDEN_PATH_REGISTRY.json` and documented under `GOLDEN_PATHS/`. Run them with `python TOOLS/run_golden_paths.py`. They are hermetic and exercise request routing, use-case transitions, persistence, temporal monitoring, source management, migration, and checkpointing through public contracts.


## v1.10 Stage 1 — Complete Use Case Contract v3

All 20 implemented use cases now declare group/interaction type, actor intent, typed inputs/outputs, reads/writes/capabilities, freshness/comparability requirements, acceptance/failure contracts, side effects, idempotency, capability requirements, UI/API hooks, and Golden Path membership. Workflow Markdown owns procedure ordering only. The system map is generated and release-gated. At the v1.10 Stage-1 release, UC21–UC25 were still planned for Phase 2; they are implemented in v1.11 Stage 2.

## v1.11 Stage 2 — Result/query boundary

The registry now contains **25** top-level use cases across six semantic groups. UC21–UC25 are read-only result/query intents returning `CurrentStateSnapshot`, `ChangeSet`, `TrendSeries`, `InterpretationRecord`, and `ResearchHealthSnapshot`. Their backend projection builders remain Phase 3; queries never silently perform refresh/measurement/evidence/repair commands. The System Map shows implemented query UCs separately from the planned projection backend and maps future UI surfaces as compositions rather than routers.

## Phase acceptance

Development phases use explicit acceptance contracts **plus a persistent question/answer record**. Before work, blocking design questions are captured under `AUDIT/PHASE_EXECUTION_RECORDS/`; during work, material emergent questions are appended; after work, every blocking question requires an answer, decision and evidence before `accepted`. `REFERENCE/PHASE_ACCEPTANCE_QA.md` is the generated human view. `STAGE_STATUS.json` records acceptance state and links each phase to its question record. Tests are evidence, not acceptance by themselves.

