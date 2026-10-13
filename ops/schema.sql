-- Owned append-only synthetic assessment ledger and indexed derived findings. Created by Jason Stys.
-- BEGIN CODE MAP (generated; python scripts/code_map.py)
-- table: snapshots — line 18
-- column: seq — line 19
-- column: assessment_id — line 20
-- column: as_of — line 21
-- column: payload — line 22
-- column: previous_hash — line 23
-- column: hash — line 24
-- table: findings — line 26
-- column: snapshot_seq — line 27
-- column: control_id — line 28
-- column: state — line 29
-- END CODE MAP
PRAGMA application_id = 1380795905;
PRAGMA user_version = 1;
PRAGMA foreign_keys = ON;
CREATE TABLE snapshots (
    seq INTEGER PRIMARY KEY,
    assessment_id TEXT NOT NULL UNIQUE,
    as_of TEXT NOT NULL,
    payload TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    hash TEXT NOT NULL UNIQUE
);
CREATE TABLE findings (
    snapshot_seq INTEGER NOT NULL REFERENCES snapshots(seq),
    control_id TEXT NOT NULL,
    state TEXT NOT NULL,
    PRIMARY KEY (snapshot_seq,control_id)
);
CREATE INDEX finding_state_sequence ON findings(state,snapshot_seq);
CREATE TRIGGER snapshots_no_update BEFORE UPDATE ON snapshots BEGIN SELECT RAISE(ABORT,'append-only snapshots'); END;
CREATE TRIGGER snapshots_no_delete BEFORE DELETE ON snapshots BEGIN SELECT RAISE(ABORT,'append-only snapshots'); END;
CREATE TRIGGER findings_no_update BEFORE UPDATE ON findings BEGIN SELECT RAISE(ABORT,'append-only findings'); END;
CREATE TRIGGER findings_no_delete BEFORE DELETE ON findings BEGIN SELECT RAISE(ABORT,'append-only findings'); END;
