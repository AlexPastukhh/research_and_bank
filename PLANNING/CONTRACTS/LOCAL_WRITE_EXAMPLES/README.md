# Synthetic envelope fixtures

Do not place these packages in production intake: bank-example-item/1 is not a production Bank schema.
First transaction d855b9d5-3caa-46c3-86bf-a4978ef64f21 creates object 0b5f4b93-7be4-4bb4-b793-a0ae5f423aa7.
Second transaction 1d83c3cb-900b-4d3a-bcb2-9e5e0cd2686d updates it against the first revision.
Exact replay keeps transaction IDs and byte-for-byte manifests.
Hashes and lengths apply to UTF-8 bytes with LF; changing CRLF/BOM requires a new prepared package, not editing a published one.
No producer/importer, committed Bank state or application receipt is included.
Validation of these static fixtures proves envelope consistency only. Runtime acceptance LW01–LW13 remains pending.
