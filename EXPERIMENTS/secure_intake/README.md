# Windows secure intake — completed synthetic transport prototype

Task **R1-SECURE-INTAKE-001** completed 2026-10-06, SI1–SI6 PASS; native Windows 11 build 26200 / Python 3.14.7. **32/32 mandatory test groups PASS, zero skips.** This is the safe-read component, not an installed Bank or production security/release acceptance.

## Use and lifetime

`read_package(trusted_intake_root, transaction_id, trusted_staging_root)` returns `INCOMPLETE`, `REJECTED`, `IO_ERROR`, `CANCELLED`, or `VERIFIED_TRANSPORT`. Only the last supplies a `Snapshot`. Trusted policy/schema/configuration are supplied by the app/test, never selected by incoming package paths.

On success consume `snapshot.iter_bytes(logical_path)` while holding the snapshot; close it explicitly or use a context manager. It retains exact immutable READY/manifest/policy bytes, transaction/hash and measured file metadata; protected staging is accessible through held handles. Consumption checks integrity before yielding bytes. It never reopens original intake paths. Close invalidates subsequent consumption. Reader does not emit ACCEPTED/REPLAY, access a Bank database or assert domain/accepted-history validity.

Native handles use OPEN_REPARSE_POINT, directory leases, read-only sharing for source and exclusive private output handles; final path/identity/single-link checks, inventory and bounded hashes prevent or reject the tested redirects/replacements. Strict bounded UTF-8 JSON rejects BOM/duplicates/nonfinite constants and numeric overflow; escaped-string-aware depth scan precedes decoding/schema checks.

Missing READY (including only pending marker) is INCOMPLETE; existing invalid/truncated READY is REJECTED. Failure returns no snapshot and retains input. Owned partial staging is reclaimed after handles close; failed reclamation is explicit/quarantined. Process death can leave isolated orphan directories, never usable readiness; fresh retry creates a new attempt with the original producer IDs. The owned test parent records interruption and reclaims only its own orphan. Other snapshots are preserved.

## Evidence and issue history

- `CAPABILITY_RESULTS.json`: actual private-root/NTFS/link/share capability fixtures.
- `TEST_RESULTS.json`: final 32 groups with actual source hashes; tests include real default byte boundaries (16KiB READY, 512KiB manifest, 2MiB document, 64MiB file, 256MiB package), 128 files/operations, sharing/mutations, links/ACL, failure/cancel/owned-child restart, controlled consumption and continuation without Bank history.
- `TEST_HISTORY/`: previous runs, including failures.
- `ISSUES.json`: investigating/open/resolved history, fixes and retest evidence. Floating-point overflow, all-outcome diagnostics and positive-fixture ownership corrected; checkpoint UTF-8/default-code-page failure also fixed with guarded rollback/reapply; no open scoped problem.
- `COMPLETION_REVIEW_LOG.json`: confirmed fixes, remaining uncertainty, follow-up triggers and next proposal.
- `../../PLANNING/WORK_ITEMS/R1_SECURE_INTAKE_RECEIPT.json`: completion, hashes/readback/source/baseline guards.

Run from CMD with the existing validation environment:

```cmd
C:\Users\alexa\research_and_bank\PLANNING\TOOLS\.schema_validation_env\Scripts\python.exe C:\Users\alexa\research_and_bank\EXPERIMENTS\secure_intake\test_reader.py
```

Test runs retain previous report/issue history and generate only their owned temporary roots. They never initialize a live Bank, fill the disk, change global permissions/settings, terminate unrelated processes or power off the PC.

## Boundaries and next step

Configured root parents, current owner/SYSTEM, code and policy/schema/hooks remain trusted. No resistance to administrators or hostile fully authorized in-process owner is claimed. Only fixed local NTFS is supported; network/removable/ReFS need separate acceptance. Existing fixture success does not verify the actual producer's atomic READY publication or real private deployment. D-1–D-3 in Review Log retain these triggers, orphan lifecycle and workload/hardware limitations.

Next: review the separate `R1_SQLITE_IMPORTER.json` card, then whole-command domain/history/CAS/replay validation, bounded BLOB copy and atomic canonical SQLite receipt in owned synthetic DB. R0/R1 gates, UI/search/packaging, real Bank/privacy and hardware durability remain unaccepted. Accepted system 1.11.0 remains untouched.

Official primary API references checked 2026-10-06:
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew
- https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights
- https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo

## Current source follow-up — AWR-FIX-20261007-01

После AWR fixes текущая source-dependent evidence: [native regression](../completed_work_review/implementation_20261007/native/REGRESSION_NATIVE.json), [local regression](../completed_work_review/implementation_20261007/REGRESSION_LOCAL.json), [Review Log](../completed_work_review/implementation_20261007/REVIEW_LOG.json). Local247PASS/5 platform skips; native290PASS/294 with4 original reader Win1314 fixture blockers. Component LOCAL_RESULTS/NATIVE_RESULTS and previous receipts remain historical immutable runs; they are not rewritten to represent changed-source acceptance. Actual mapped UI10 cases PASS. Full reader native/release/real deployment not accepted.
