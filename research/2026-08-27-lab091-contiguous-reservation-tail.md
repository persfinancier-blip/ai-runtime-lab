# LAB-091 — contiguous reservation/tail invariant

Date: 2026-08-27

## Finding

The v3 cross-table state-machine guard bound a new PREPARED intent to the current `shared_anchor_meta.reserved_position`, but did not require the new `position` to be exactly one greater than its `predecessor_position`.

This left a fail-closed correctness/availability gap even with a perfectly matching one-shot permit:

1. durable tail is `0`;
2. insert PREPARED intent with `predecessor_position=0`, `position=999`, current provider/generation and an exact permit;
3. the v3 intent guard accepted it because the predecessor matched the current tail;
4. update `shared_anchor_meta.reserved_position 0 -> 999`;
5. the v3 meta guard accepted it because a matching PREPARED row existed.

A focused SQLite counterexample reproduced the durable jump to `999`.

## Fix

Defense is enforced independently at both state transitions:

- intent insert requires `NEW.position = NEW.predecessor_position + 1` in addition to current-tail/current-provider binding;
- meta update requires `NEW.reserved_position = OLD.reserved_position + 1` in addition to the matching PREPARED row.

The second check is intentionally redundant. Even if a gap intent is present out-of-band, the tail cannot jump across it through the supported guarded DML surface.

## Evidence

Published commits on PR #173:

- code: `01c8fd697171fb2a2b330991cc159e0432a51ab7`;
- regression follow-up: `5bf96d36d4b2ee40ba516ee7d7804cb5b614218d`.

Exact published blobs used for execution:

- `operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be`;
- `row_tokens.py` `801eb0fbdb915bb31f40069d087bf3ce56d659a8`;
- `cross_table_guards.py` `aff3ef5f8a49db119f86b074a8d6684beac7ab0c`;
- `test_cross_table_state_machine_guards.py` `d1ad01e68621c504c70eabddb709679c8583de93`.

Exact published-source regression: **8/8 PASS**. `compileall` also passed. The unrelated artifact-tool spreadsheet warmup warning was emitted during Python startup and did not affect unittest/compileall return codes.

## Scope

This closes the LAB-091 reservation-contiguity invariant. It does not expand LAB-091 into a same-privilege SQLite sandbox; LAB-087 remains the outer single-writable-process/filesystem boundary. The full LAB-080/LAB-082 restart/concurrency/crash/UNKNOWN integration gate remains required before PR #173 can merge.
