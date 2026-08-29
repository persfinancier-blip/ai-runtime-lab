# LAB-091 — weakened watermark CHECK gap

Date: 2026-08-29

## Finding

LAB-080 canonically creates `component_anchor_watermarks.position INTEGER NOT NULL CHECK(position>=0)`. LAB-091 first-adoption hardening had started validating identity and selected NOT NULL constraints, but the persistent v2/v4 guard stack still relied on the historical CHECK to reject a newly inserted negative watermark position.

A legacy table retaining `NOT NULL` but lacking `CHECK(position>=0)` can therefore admit `position=-1` if an exact one-shot `watermark-insert` permit is presented. The v4 confirmed-prefix guard is conditioned on `NEW.position>0`, so it does not reject the negative case.

This is a behavioral compatibility gap, not merely textual DDL drift.

## Reproduction

A local SQLite probe reproduced the published semantics with:

- weakened `component_anchor_watermarks(component_id TEXT PRIMARY KEY, position INTEGER NOT NULL)`;
- v2 exact watermark insert guard;
- v4 confirmed-prefix insert guard;
- an exact one-shot permit for `component-a`, new value `-1`.

Observed RED: the row `('component-a', -1)` was inserted.

## Fix

Harden the v2 exact watermark insert guard itself with `NEW.position<0` before permit consumption. This preserves the canonical reachable-state invariant regardless of whether a legacy schema retained the historical CHECK.

Published on `lab/091-mutable-shared-anchor-writer`:

- runtime commit `568011740f743208314ff2e5c464e1b48bcd4781`;
- `full_operation_guards.py` blob `529ee8094d04b0cc9bb208f3fce8f85b2bc6db0f`;
- regression commit `210d51dd15ebfcaf4858bb927e2b729765c176b3`;
- regression: `tests/test_weakened_watermark_check_regression.py`.

## Execution evidence

A local focused supported-path reconstruction using `PermitConnection`, `install_operation_permit_udf`, `one_shot_permit`, and the corrected watermark trigger executed:

- negative watermark insert with exact permit: rejected;
- zero watermark insert with exact permit: accepted;
- result: 2/2 PASS;
- compileall PASS for the focused reconstructed package.

The initial local harness run failed only because the temporary reconstructed harness had an unterminated triple-quoted string; that harness typo was corrected and the gate was rerun successfully. The published branch source did not contain that typo.

## Scope

This does not claim complete CHECK/type-affinity equivalence. It closes one demonstrated future reachable-state gap without requiring brittle textual comparison of `sqlite_master.sql`.

Next: re-run the combined adoption/index/collation/NOT NULL/check focused gates on branch head, then continue the real LAB-080/LAB-082 supported-class UNKNOWN/concurrency/crash gate.
