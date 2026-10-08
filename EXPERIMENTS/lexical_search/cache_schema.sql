-- Synthetic disposable lexical cache v1; never canonical Bank/receipt authority.
BEGIN IMMEDIATE;
PRAGMA application_id=1380078385;
PRAGMA user_version=1;
CREATE TABLE corpus (
 rid TEXT PRIMARY KEY NOT NULL CHECK(length(rid)=36),
 oid TEXT NOT NULL CHECK(length(oid)=36),
 object_type TEXT NOT NULL CHECK(object_type IN ('Asset','Entity','Annotation','Collection')),
 seq INTEGER NOT NULL CHECK(seq>=1),
 coverage TEXT NOT NULL CHECK(coverage IN ('indexed','locator_only','unsupported_media','invalid_utf8','size_limit','not_applicable')),
 commit_id TEXT NOT NULL CHECK(length(commit_id)=36),
 document_sha256 TEXT NOT NULL CHECK(length(document_sha256)=64)
) STRICT;
CREATE INDEX corpus_visible ON corpus(object_type,seq DESC,oid,rid);
CREATE TABLE terms (
 rid TEXT NOT NULL REFERENCES corpus(rid),
 field_id INTEGER NOT NULL CHECK(field_id>=0 AND field_id<=5),
 term TEXT NOT NULL CHECK(length(CAST(term AS BLOB))>=1 AND length(CAST(term AS BLOB))<=4194304),
 PRIMARY KEY(rid,field_id,term)
) STRICT;
CREATE INDEX terms_posting ON terms(field_id,term,rid);
CREATE TABLE generation (
 id INTEGER PRIMARY KEY CHECK(id=1),
 watermark INTEGER NOT NULL CHECK(watermark>=0),
 profile_id TEXT NOT NULL CHECK(length(profile_id)<=64),
 unicode_version TEXT NOT NULL CHECK(length(unicode_version)<=64),
 normalization INTEGER NOT NULL,
 digest TEXT NOT NULL CHECK(length(digest)=64),
 revision_count INTEGER NOT NULL CHECK(revision_count>=0),
 posting_count INTEGER NOT NULL CHECK(posting_count>=0)
) STRICT;
COMMIT;
