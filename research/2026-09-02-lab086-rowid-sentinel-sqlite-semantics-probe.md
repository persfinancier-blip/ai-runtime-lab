# LAB-086 rowid sentinel SQLite semantics probe

Date: 2026-09-02

## Question

The retained LAB-086 hidden-rowid patch (`61841b58be42b01b97ca223567cbf9f428f7f0ce`) relies on a two-stage SQLite trigger pattern:

- BEFORE INSERT rejects an explicit rowid collision except when `NEW.rowid == -1`;
- AFTER INSERT rejects a stored row whose final rowid is exactly `-1`.

The `-1` exception is needed because SQLite exposes `NEW.rowid == -1` in a BEFORE INSERT trigger when no explicit rowid has yet been assigned. The security question is whether that exception accidentally permits `INSERT OR REPLACE` to destroy authenticated history through explicit hidden-rowid collisions.

## Exact repository state observed

Draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Its current `experiments/asymmetric_break_glass_history/strict_fence.py` blob is still predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.

The retained patch blob is still `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target remains `b78e7c98e35138719f77c482c7f1aab36b702de7`. The target blob is not currently present through GitHub's blob endpoint (404).

Direct git transport was probed in this run and failed before repository execution with `Could not resolve host: github.com`; therefore this is an isolated SQLite semantic probe, not an exact branch behavioral gate.

## Probe

A file-independent in-memory SQLite test recreated the retained patch's relevant trigger shape on a rowid table with an existing authenticated row at rowid 5.

Observed results:

1. Ordinary insert with no explicit rowid succeeded and SQLite assigned a fresh rowid.
2. `INSERT OR REPLACE` with explicit `rowid=5` and a fresh content key was rejected by the BEFORE trigger; the original row remained unchanged.
3. `INSERT OR REPLACE` with explicit `rowid=-1` was rejected by the AFTER sentinel trigger; the attempted row was rolled back.
4. `INSERT OR REPLACE` colliding on both rowid and content key was rejected; the original row remained unchanged.
5. A genuinely new explicit `rowid=0` succeeded, confirming the trigger does not collapse all explicit rowid use into a blanket denial.

## Conclusion

The retained two-stage `NEW.rowid != -1` + AFTER `NEW.rowid == -1` sentinel pattern behaves as intended for the core SQLite ambiguity it is designed to resolve: implicit rowid allocation remains usable, explicit collisions are blocked before REPLACE can remove history, and explicit storage of the reserved `-1` sentinel is rolled back after insertion.

This does not replace the required LAB-086 exact branch subgate. In particular, publication must still be byte-preserving from predecessor + retained patch, and the real-schema tests must still cover hidden-rowid collisions, NULL identities, alternate UNIQUE collisions, thaw scope, receipt history, and compileall.

No new blocker was found in this specific trigger mechanism.
