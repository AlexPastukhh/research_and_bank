# Release Notes — v1.6.0

Date: 2026-09-30

## Purpose

v1.6.0 is the remediation release for the v1.5 AX01–AX20 system audit. The goal is not new market-research scope; it is making the reusable research runtime internally consistent, recoverable, testable and portable.

## Major fixes

- confined all ProjectIndex-resolved paths to the project root; absolute/path-traversal/symlink escapes are rejected;
- gap-day entity history no longer creates false `new`/misses `reopened`;
- method, scope and source-route changes participate in comparability and emit metadata events instead of false market field changes;
- Daily Run finalization is immutable; rejected second runs do not leave orphan run files;
- unified public `*_SCHEMA.json` files on JSON Schema Draft 2020-12 and made project validation schema-driven;
- `done` task state requires required outputs and passed acceptance results;
- manifest-listed missing files fail project validation; release manifest is a system release gate;
- independent source provenance is preserved in observation idempotency;
- source/evidence/claim traceability, frequency-sample rules and economics prerequisites are machine-validated;
- dependency graph references/cycles are validated and downstream impact is attached to change events;
- bootstrap cycles copy their baseline artifacts and point to the actual cycle workbook;
- project mutations use advisory locking; critical multi-file updates use recoverable transaction journals; `repair_project.py` reconciles prepared transactions, finalized runs, orphan runs and entity registry;
- added explicit v1.5→v1.6 migration tool and support matrix;
- added runtime requirements and declared scale targets plus benchmark tooling;
- exposed project configuration is now schema-bounded and actually consumed by runtime tools; low-payout observations are a retention invariant rather than a fake toggle;
- system validation runs a critical contract gate, smoke test and scale benchmark; full regressions remain available with `--full`.

## Compatibility

Projects on system v1.5.0 must run `python TOOLS/migrate_project.py PROJECT --apply` before v1.6 validation. Unsupported older versions fail explicitly rather than being silently reinterpreted.

## Audit policy

The canonical audit framework remains `AUDIT/AUDIT_AXES.json` (AX01–AX20). A release is not audit-clear merely because unit tests are green.
