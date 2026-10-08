# Windows secure intake — synthetic implementation in progress

Task R1-SECURE-INTAKE-001. Code is a prototype, not an installed Bank, canonical writer or production security release. SI1–SI6 and native U-1 still require evidence.

- win32_io.py: native non-inheritable no-follow handles, directory leases, single-link files, fixed local NTFS roots; private current-user/SYSTEM ACL for owned fixtures.
- reader.py: transport-only complete bounded snapshot, strict JSON/envelope/inventory/hashes, protected staging; never domain/CAS/receipt/DB acceptance.
- capability.py: real Windows private-root/link/sharing checks, only own temporary objects.
- ISSUES.json: open/resolved problems with history; CAPABILITY_RESULTS.json and TEST_RESULTS.json are actual native results when created. An absent result is not PASS.

Trusted configuration includes authorized root parents, current owner/SYSTEM and protocol/policy bytes. No protection from an administrator or hostile fully authorized in-process owner is claimed. Remote/removable/ReFS roots are unsupported. Real-data deployment, producer READY publication and full importer are future tasks.

Official references checked 2026-10-06:
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew
- https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights
- https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo

Next: native capability checks, synthetic acceptance/fault tests; record concrete failures, resolve/retest, and mark task complete only with mandatory scope evidence.
