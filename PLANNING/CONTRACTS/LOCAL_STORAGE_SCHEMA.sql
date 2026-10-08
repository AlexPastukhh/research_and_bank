-- Candidate R1 SQLite physical schema v1; not production Bank initialization.
-- Every writable connection must independently enforce configured pragmas.
BEGIN IMMEDIATE;
PRAGMA application_id=1380076337;
PRAGMA user_version=1;
CREATE TABLE commits (
 commit_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
 transaction_id TEXT NOT NULL UNIQUE,
 commit_id TEXT NOT NULL UNIQUE,
 manifest_sha256 TEXT NOT NULL CHECK(length(manifest_sha256)=64),
 manifest_blob BLOB NOT NULL,
 ready_blob BLOB NOT NULL,
 accepted_at TEXT NOT NULL,
 policy_version TEXT NOT NULL,
 policy_blob BLOB NOT NULL,
 FOREIGN KEY(commit_sequence) REFERENCES accepted_receipts(commit_sequence) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE TABLE files (
 file_id INTEGER PRIMARY KEY,
 commit_sequence INTEGER NOT NULL REFERENCES commits(commit_sequence),
 path TEXT NOT NULL,
 byte_length INTEGER NOT NULL CHECK(byte_length>=0),
 sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 file_blob BLOB NOT NULL CHECK(length(file_blob)=byte_length),
 UNIQUE(commit_sequence,path)
) STRICT;
CREATE TABLE revisions (
 revision_id TEXT PRIMARY KEY NOT NULL,
 object_id TEXT NOT NULL,
 object_type TEXT NOT NULL,
 schema_ref TEXT NOT NULL,
 base_revision_id TEXT REFERENCES revisions(revision_id) DEFERRABLE INITIALLY DEFERRED,
 commit_sequence INTEGER NOT NULL REFERENCES commits(commit_sequence),
 operation_index INTEGER NOT NULL CHECK(operation_index>=0),
 document_path TEXT NOT NULL,
 UNIQUE(commit_sequence,object_id),
 UNIQUE(commit_sequence,operation_index),
 FOREIGN KEY(commit_sequence,document_path) REFERENCES files(commit_sequence,path)
) STRICT;
CREATE INDEX revisions_object_history ON revisions(object_id,commit_sequence DESC);
CREATE TABLE accepted_receipts (
 commit_sequence INTEGER PRIMARY KEY REFERENCES commits(commit_sequence),
 receipt_blob BLOB NOT NULL
) STRICT;
CREATE TABLE attempt_receipts (
 attempt_id TEXT PRIMARY KEY NOT NULL,
 transaction_id TEXT,
 manifest_sha256 TEXT,
 recorded_at TEXT NOT NULL,
 receipt_blob BLOB NOT NULL
) STRICT;
CREATE VIEW object_heads AS
 SELECT object_id,object_type,revision_id,commit_sequence FROM (
  SELECT object_id,object_type,revision_id,commit_sequence,
   ROW_NUMBER() OVER(PARTITION BY object_id ORDER BY commit_sequence DESC) AS position
  FROM revisions
 ) WHERE position=1;
-- Canonical rows are append-only. Explicit migration uses a new DB, not disabled triggers.
CREATE TRIGGER commits_no_update BEFORE UPDATE ON commits BEGIN SELECT RAISE(ABORT,'immutable_commit'); END;
CREATE TRIGGER commits_no_delete BEFORE DELETE ON commits BEGIN SELECT RAISE(ABORT,'immutable_commit'); END;
CREATE TRIGGER files_no_update BEFORE UPDATE ON files BEGIN SELECT RAISE(ABORT,'immutable_original'); END;
CREATE TRIGGER files_no_delete BEFORE DELETE ON files BEGIN SELECT RAISE(ABORT,'immutable_original'); END;
CREATE TRIGGER revisions_no_update BEFORE UPDATE ON revisions BEGIN SELECT RAISE(ABORT,'immutable_revision'); END;
CREATE TRIGGER revisions_no_delete BEFORE DELETE ON revisions BEGIN SELECT RAISE(ABORT,'immutable_revision'); END;
CREATE TRIGGER accepted_receipts_no_update BEFORE UPDATE ON accepted_receipts BEGIN SELECT RAISE(ABORT,'immutable_receipt'); END;
CREATE TRIGGER accepted_receipts_no_delete BEFORE DELETE ON accepted_receipts BEGIN SELECT RAISE(ABORT,'immutable_receipt'); END;
CREATE TRIGGER attempt_receipts_no_update BEFORE UPDATE ON attempt_receipts BEGIN SELECT RAISE(ABORT,'immutable_attempt'); END;
CREATE TRIGGER attempt_receipts_no_delete BEFORE DELETE ON attempt_receipts BEGIN SELECT RAISE(ABORT,'immutable_attempt'); END;
COMMIT;
