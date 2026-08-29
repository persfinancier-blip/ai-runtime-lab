# LAB-091 — non-BINARY identity collation first-adoption gap

Date: 2026-08-29

## Finding

The first-adoption schema validator previously treated a UNIQUE/PRIMARY KEY as canonical when its indexed column names matched the required identity, without checking SQLite collation semantics.

That admits legacy schemas such as `UNIQUE(id COLLATE NOCASE)`. Such a constraint is not equivalent to the canonical LAB-080/LAB-082 BINARY identity contract: byte-distinct identifiers such as `Intent-A` and `intent-a` are both valid exact strings at the protocol layer, but a NOCASE unique index rejects the second row.

This is a compatibility/availability gap in adoption, not an authority escalation. A clean legacy snapshot could be accepted even though future otherwise-valid supported operations could fail because the inherited schema implements a different identity equivalence relation.

## Executed reproduction

A fresh SQLite probe observed:

- `PRAGMA index_info` for `UNIQUE(id COLLATE NOCASE)` reports the same single column `id` as a canonical unique index;
- `PRAGMA index_xinfo` exposes the key-term collation as `NOCASE`;
- inserting `Intent-A` then `intent-a` raises `sqlite3.IntegrityError` under NOCASE;
- the canonical BINARY unique constraint accepts both byte-distinct values.

After applying the fix logic, an executed focused probe observed:

- canonical BINARY schema: accepted;
- `shared_anchor_intents.intent_id` with NOCASE PK: rejected;
- `shared_anchor_intents.request_id` with NOCASE UNIQUE: rejected;
- `component_anchor_watermarks.component_id` with NOCASE PK: rejected;
- `asymmetric_provider_receipts.request_id` with NOCASE PK: rejected;
- Python compile of the focused probe: PASS.

A second combined index-semantics probe checked the new collector against the prior partial/expression cases as well as the new collation case:

- canonical `TEXT UNIQUE`: accepted;
- canonical `TEXT PRIMARY KEY`: accepted through its BINARY backing index;
- canonical `INTEGER PRIMARY KEY`: accepted directly despite having no backing index;
- partial UNIQUE: rejected as a table-wide identity guarantee;
- expression UNIQUE: rejected as a canonical identity guarantee;
- NOCASE UNIQUE: rejected;
- NOCASE text PRIMARY KEY: rejected;
- `UNIQUE(id DESC)` with BINARY comparison: accepted, because sort direction does not change uniqueness equivalence.

This is focused mechanism evidence; it is not a claim that the complete PR #173 real-stack gate has passed. The previous exact published adoption-index suites must still be re-executed against validator blob `1731648b...` before the branch-wide regression gate can be called green.

## Fix

Branch `lab/091-mutable-shared-anchor-writer` now uses `PRAGMA index_xinfo` key terms when accepting non-partial UNIQUE indexes and requires BINARY collation for every identity key term. Expression terms remain rejected. `INTEGER PRIMARY KEY` is accepted directly because it is the rowid identity and has no backing index; text/composite primary keys are accepted through their backing unique index so their collation is auditable.

Published branch artifacts:

- `experiments/mutable_shared_anchor_writer/adoption_validation.py`
  - commit `4d509c028c8b32f36011674cb868374223538069`
  - blob `1731648b4e65b1c5984d4f93b78c45d5a066dd95`
- `experiments/mutable_shared_anchor_writer/tests/test_adoption_collation_regression.py`
  - commit `715bebe7172e738b15ce126bb2f132645010e9d5`
  - blob `ad2b3b80bf848f874e300acf6304cb57997f5bca`

A post-write fetch confirmed the validator branch blob and the regression blob above.

## Audit boundary

Index sort direction does not change uniqueness equivalence, so ASC/DESC is not rejected. Expression and partial indexes were already handled separately. Custom/NOCASE/RTRIM collations are rejected for canonical identity keys because they do not preserve the protocol's exact-string identity relation.

## Next action

LAB-086 remains priority #1. If its byte-preserving Contents publication path remains unavailable, continue LAB-091 by executing the final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` against the real LAB-080/LAB-082 dependency closure, starting with timeout-after-commit/UNKNOWN and two-worker/crash tests that currently use stubs rather than the final supported class. Before counting the collation change as branch-wide safe, re-run the prior expression/partial/missing-constraint adoption suites against validator blob `1731648b...`.
