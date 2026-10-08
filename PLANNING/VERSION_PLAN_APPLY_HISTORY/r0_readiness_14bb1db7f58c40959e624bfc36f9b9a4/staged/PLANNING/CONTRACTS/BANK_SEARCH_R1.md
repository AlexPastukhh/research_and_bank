# R1 lexical search — scoped design 1.0.0

2026-10-06; OPEN-010/OPEN-018, MVP-003/MVP-009. Proposal suitable for autonomous implementation within the existing R1 exact/full-text scope. Semantic/similarity, graph ranking, R5 clustering and R6 profile evaluation are later tasks; their mandatory targets are preserved.

## Corpus and fields

Only accepted revisions of R1 Asset/Entity/Annotation/Collection enter the corpus. `current` selects the newest revision per object at snapshot S; `all_revisions` selects every retained revision accepted by S. This is commit/system history, not bitemporal/event-time reconstruction or a frozen ResultSet. Unaccepted packages and Source design fixtures are excluded.

| Field key | Exact source | Unsupported/absent handling |
|---|---|---|
| title | document.title for all supported types | Complete retained title, not renderer text |
| filename | Asset bytes storage.original_filename | Null gives no terms; file_path is not an original display filename |
| uri | Asset locator storage.uri | Literal retained URI tokens; do not fetch/percent-decode/rewrite URL |
| aliases | Entity data.aliases entries | Each alias tokenized independently; no identity merge |
| body | Annotation data.body (plain_text or literal markdown) | No HTML execution or semantic interpretation |
| content | Verified retained Asset bytes with media_type=text/plain, strict UTF-8, at most 4 MiB | Other MIME, invalid UTF-8 or oversize retained bytes excluded from content only; originals and metadata still available |

No provenance source_locator, author identity, embedded links, external-ID values, Collection member text or Entity-linked Asset text are searched implicitly. Selected fields are explicit, nonempty, unique; absent fields contribute zero tokens. PDF/DOCX/image/OCR/video/HTML/JSON extraction and fetch are unsupported in this profile. A stored document/media type never promises searchable body or renderer support. The text/plain size cap is an extraction limit separate from the 64 MiB original-file intake cap: retain original unchanged, mark size_limit, never index a truncated prefix.

Content coverage per corpus revision: indexed, locator_only, unsupported_media, invalid_utf8, size_limit or not_applicable. Coverage is returned as counts for the selected type/mode corpus regardless of matches; sum equals corpus revisions. `invalid_utf8` does not reject an otherwise valid accepted binary original. Missing/hash-invalid original is INTEGRITY_ERROR, not an extraction exclusion. A selected content query with zero hits can be complete for supported content while exclusions remain visible; do not claim full-media coverage. Strict UTF-8 BOM, if present, remains in original and acts as a separator in tokenization.

## Query semantics and limits

Profile `r1-lexical/1`: apply NFC, Unicode casefold, then NFC. Token = maximal Unicode L*/N* characters with M* combining marks only following an existing token. Punctuation, whitespace, symbols and control characters separate tokens; no accent folding, stemming, stop words, prefixes, wildcards, phrase/boolean syntax or fuzzy/embedding search. CJK sequences are literal maximal tokens, not dictionary segmentation. ASCII SQL/FTS-looking syntax is ordinary input data; never interpolate it into SQL. Values from different fields/alias entries are tokenized independently, then their term sets unioned; AND across all unique query terms. Thus title='alpha' and body='beta' can match 'alpha beta'; adjacent values must not create 'alphabeta'.

Query is 1..1024 UTF-8 bytes, <=32 distinct nonempty normalized terms; no terms => INVALID_REQUEST, oversize => LIMIT_EXCEEDED. Matching metadata/body uses complete schema-validated values; tokenization must stream within bounded intake/document policy, not copy unbounded strings. Request requires supported object_types, fields, revisions_mode, nullable snapshot_sequence, limit 1..100 and offset 0..10000. Unknown fields/modes/duplicate selectors are invalid. Larger corpus/response needs pagination, not silent top-N claims.

Snapshot S is one resolved durable commit sequence (0 for an empty initialized Bank) chosen at read start when null. An explicit S must be <= durable max; query snapshot prevents later commits appearing during pagination. For subsequent pages reuse returned S and offset+limit. Hits ordered by commit_sequence descending, object_id ascending, revision_id ascending; return total_matches before page limit, has_more, pinned type/object/revision, matched_fields and extraction state. No numeric relevance score is asserted. Exact ID retrieval uses bank.get, not string search. A changed current head never changes an old pinned hit.

Unicode data version is part of concrete profile identity: include `unicode_data_version` from the runtime and normalization_version=1 in the cache and response. Reusing a cache with a different identity yields INDEX_PROFILE_MISMATCH. Rebuild under the new identity; old query results do not silently claim identical token semantics. Fixture expected IDs must pass on supported Windows Python; whole-Unicode cross-version parity is not established by this fixture.

## Minimal local index choice

Use one disposable app-owned local SQLite `search-cache.sqlite3`, separate from canonical `bank.sqlite3`; no external service/vector store or modification of canonical physical format v1. Canonical SQLite owns originals/history and always wins. The derived cache has its own version=1, never accepted receipt authority, and can be deleted/rebuilt without deleting Bank objects. This avoids changing the already selected canonical schema to accommodate a mutable cache. Revisit combined/separate advanced stores before R6 only if justified.

Candidate derived records: generation(profile identity, complete_through_sequence); corpus(ref,type,commit_sequence,coverage); terms(ref,field,term). Queries intersect selected term postings, then filter refs using the canonical read snapshot/head set and explicit types. Metadata/coverage for every corpus revision is required even when there are no tokens. All prepared SQL binds user values. The production index adapter must prove this relational algorithm agrees with the independent control-query oracle.

Publish a complete generation atomically only after retained document/original validation and extraction for a fixed canonical snapshot; never publish a watermark on partial work. A generation through W>=S may serve S with canonical visibility filtering; W<S returns INDEX_NOT_READY. Appended commits during build remain outside its watermark. Rebuild happens as an explicit maintenance/background application action, never a hidden research/URL refresh inside a read. Lost/corrupt cache => INDEX_UNAVAILABLE until rebuilt, never empty successful results. Profile mismatch and integrity problems are visible. Storage/index atomicity is intentionally separated: receipt acceptance does not wait for search, and UI shows pending indexing until its watermark catches up.

## Control evidence and remaining implementation

`BANK_QUERY_EXAMPLES.json` contains real schema-shaped synthetic revisions, retained payload bytes, explicit commit sequences and manually specified expected pinned refs. `check_bank_queries.py` independently tokenizes corpus and checks queries plus invalid requests, current/history, limits, integrity and stale-cache errors. It is a read-only oracle, not the production index/endpoint/importer. Exact expected-ID equality is the R1 lexical correctness criterion for these scoped fixtures; this does not establish relevance for semantic profiles or actual-media extraction.

Runtime acceptance still requires SQLite postings parity against the oracle, restart/rebuild, concurrent snapshot/pagination, exact originals/pinned reads, Windows environment and UI/error coverage. No benchmark, real-data exposure, whole-Unicode guarantee, R0/release acceptance or search service is delivered in this task.
