# Release Notes — v1.4.0

## Focus

v1.4 is an operational-reuse release. It reduces dependence on chat history and makes continuation from previous artifacts deterministic.

## Added

- machine-readable `CORE/SYSTEM_SPEC.json` and human `CORE/SYSTEM_CONTRACT.md`;
- canonical `PROJECT_INDEX.json` template;
- compact `RUN_STATE.json` runtime;
- atomic Task Manifest schema/template;
- versioned `METHOD_REGISTRY.json` with comparability/capability fields;
- `DEPENDENCY_GRAPH.json` and change-propagation helper;
- machine `HANDOFF.json` plus checkpoint tooling;
- clean bootstrap from directory/repo, ZIP, standalone file(s), or mixed artifacts;
- project/system validators and end-to-end smoke test;
- workbook runtime sheets: SystemControl, ProjectIndex, RunState, TaskManifests, MethodRegistry, DependencyGraph;
- `OpportunityEconomics` schema/sheet for payout, effort, acquisition cost and effective-rate analysis;
- source role/discovery-route fields separated from category/priority;
- S05 measurement stage for observable economics/effort inputs.

## Changed

- init scripts use `VERSION.json` rather than hard-coded old version strings;
- project state templates upgraded to v1.4 runtime pointers;
- SearchRecipe schema now behaves as a versioned method contract;
- bootstrap requires explicit runtime construction before market research;
- workbook structure is now checked by system validator.

## Tested

- system validation passes;
- new-project initialization passes;
- project checkpoint/handoff generation passes;
- refresh-cycle initialization passes;
- multi-artifact bootstrap passes;
- ZIP member inventory passes;
- workbook formula scan passed during build;
- required workbook sheet validation passes.
