# LAB-086 rowid sentinel regression — 2026-08-28

## Scope

Follow-up to the hidden-rowid `INSERT OR REPLACE` hardening candidate. The saved patch deliberately treats SQLite `NEW.rowid == -1` as the pre-insert auto-rowid sentinel, excludes that value from the BEFORE INSERT collision lookup, and adds an AFTER INSERT guard that refuses a genuinely stored `rowid=-1`.

The existing `test_thaw_rowid_collision_regression.py` covered replacement via an already-existing positive hidden rowid but did not directly exercise the sentinel branch.

## New regression

Published on `lab/086-asymmetric-break-glass-history`:

- `experiments/asymmetric_break_glass_history/tests/test_thaw_rowid_sentinel_regression.py`
- commit `ee210a47221b6df53f3518aa3af74f76c5b0122b`
- Git blob `4c3c41426e4ff26ba53ba3ba088d6eb7bd75be33`

The authored local file passed `python -m py_compile` and `git hash-object` returned the same GitHub blob `4c3c41426e4ff26ba53ba3ba088d6eb7bd75be33`.

The regression requires both:

1. explicitly inserting `rowid=-1` into thawed authenticated history is rejected and leaves no row behind;
2. omitting rowid still permits a genuine successor and SQLite assigns a non-`-1` rowid.

No PASS is claimed for this regression against the branch runtime yet because the rowid hardening patch itself is not published and the full executable dependency closure is not available in the current shell.

## Independent SQLite semantic probe

A standalone in-memory SQLite probe using the exact proposed trigger shape was executed in this run.

Observed:

- ordinary insert with omitted rowid succeeded and received rowid `1`;
- explicit `rowid=-1` raised `IntegrityError` from the sentinel trigger and did not persist;
- an `INSERT OR REPLACE` collision expressed through `_rowid_` was rejected by the collision guard;
- the same collision expressed through `oid` was rejected;
- the original row remained unchanged.

This is mechanism evidence, not a substitute for executing the exact branch candidate.

## Decision

Retain the AFTER INSERT sentinel guard in the rowid-only candidate. Add the new sentinel regression to the focused LAB-086 rowid gate after exact candidate materialization.

The publication blocker for `strict_fence.py` is unchanged: exact branch bytes are available via GitHub, but no supported byte-preserving response/download path into the current execution filesystem has yet succeeded. Direct `urllib`/git transport still fails DNS, and `container.download` requires a web-view precondition that the raw GitHub URL could not satisfy in this run.
