# LAB-086 hidden-rowid REPLACE gap

Date: 2026-08-28

## Finding

The repinned `strict_fence.py` at executable snapshot `05d8e75a636818afcb32e085d464c9fa9171dea5` permanently protects declared history identities while transaction-scoped thaw temporarily removes normal INSERT-deny triggers. That is insufficient for ordinary SQLite rowid tables.

With `recursive_triggers=OFF` (SQLite default), `INSERT OR REPLACE` can conflict on the hidden `rowid` while presenting a fresh declared PK/UNIQUE identity. The existing permanent collision trigger sees no declared-key collision, the implicit REPLACE deletion is not stopped by the ordinary DELETE trigger, and the authenticated row is replaced.

A focused executable SQLite counterexample reproduced:

1. existing row: `rowid=1, history_id='old-id', marker='original'`;
2. permanent declared-key collision trigger + UPDATE/DELETE immutability guards installed;
3. execute `INSERT OR REPLACE INTO history(rowid,history_id,marker) VALUES(1,'attacker-id','tampered')`;
4. statement succeeds and durable row becomes `rowid=1, history_id='attacker-id', marker='tampered'`.

This is the same conflict-algorithm class as the previously fixed declared-PK and alternate-UNIQUE gaps, but through SQLite's hidden physical row identity.

## Affected LAB-086 surfaces

At minimum the mechanism applies to every ordinary rowid table whose INSERT-deny is removed during final-writer thaw, including public recovery authority/transition history, normal root/provider history, threshold proofs and post-cutoff proof creation surfaces. The append-only `asymmetric_provider_receipts` freeze has the same issue because new request IDs intentionally remain insertable and the current no-replace trigger only checks `request_id`.

A RED real-schema regression is now stored as:

- `experiments/asymmetric_break_glass_history/tests/test_thaw_rowid_collision_regression.py`

It covers public history, post-cutoff proof history during thaw, and provider receipts outside thaw.

## Candidate mechanism

A safe fix needs two pieces because SQLite exposes `NEW.rowid == -1` in a `BEFORE INSERT` trigger when the caller did not explicitly provide a rowid:

1. extend each permanent BEFORE INSERT collision trigger with a hidden-rowid collision predicate for explicit rowids:
   - `NEW.rowid != -1 AND EXISTS(SELECT 1 FROM <table> WHERE rowid IS NEW.rowid)`;
2. add a permanent AFTER INSERT guard that aborts if the resulting stored `NEW.rowid == -1`.

The second guard closes the sentinel ambiguity: an ordinary insert has `NEW.rowid == -1` only in BEFORE INSERT, then receives a normal allocated rowid by AFTER INSERT; an explicit stored rowid `-1` reaches AFTER INSERT as `-1` and is rolled back.

Focused candidate execution established all four desired properties on a representative rowid history table:

- hidden-rowid REPLACE of an existing row: BLOCKED;
- declared-PK REPLACE of an existing row: BLOCKED;
- explicit stored rowid `-1`: BLOCKED;
- ordinary fresh insert with automatic rowid: ALLOWED.

## Integration rule

Do not edit the large security-critical `strict_fence.py` by manual whole-file transcription. Apply the fix only from byte-exact pinned source, verify the resulting Git blob, then run the new regression together with the full repinned strict/thaw conflict-algorithm subgate before repinning the executable snapshot again.
