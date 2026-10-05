# System Map Changelog — v1.9 → v1.10 Stage 1

## Implemented

- Added canonical `CORE/SYSTEM_MAP_SPEC.json`.
- Added generated `REFERENCE/SYSTEM_MAP.md`, `.json`, `.mmd` plus parity gate.
- Use Case Registry upgraded from v2 routing contract to v3 complete contract.
- Existing 20 UCs now expose explicit groups and interaction types.
- Resource edges are now explicit `reads`, `writes`, and `capabilities` rather than legacy `references.read/use`.
- Workflow Markdown now owns procedure ordering only; acceptance/outcomes live only in the registry.
- AX20/22/23/24/25/26 evidence strengthened; no new audit axis added.

## Still planned

- UC21–UC25 query/result use cases.
- Result Projection Layer and five canonical result products.
- Query-side Golden Paths GP07–GP12.
- UI composition backed by real query products.

## Acceptance revision

- Added explicit acceptance contracts for Phases 0–7.
- Added development-phase acceptance state to the generated System Map.
- Phase 0 and Phase 1 acceptance reviews are release artifacts.
- Corrected `REFERENCE/MIGRATION_SUPPORT.md` current target from stale v1.9.0 wording to v1.10.0 after acceptance review detected the contradiction.

