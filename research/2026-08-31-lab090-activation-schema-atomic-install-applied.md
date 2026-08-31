# LAB-090 activation-schema atomic installation applied

Date: 2026-08-31

## Context

`experiments/provider_generation_history/supported.py::_init_activation_schema()` previously used two separate `sqlite3.Connection.executescript()` calls: one for the activation table and one for the writer-blocking trigger. Because `executescript()` controls transaction boundaries, the method did not hold one writer lock continuously across table creation/verification and trigger creation/verification.

The repository already retained the reviewed minimal candidate patch at `research/patches/lab090-activation-schema-installation-transaction.patch`.

## Safe application

LAB-086 remained first priority, but the current GitHub connector still exposed no supported byte-preserving patch-composition bridge for its exact predecessor + retained patch contract, so LAB-086 was not mutated.

For LAB-090, the current `supported.py` was fetched from branch `lab-090-provider-activation-fencing` with blob SHA `76278dfceff78e2738d7dba73a5c8bcf2c4d3ef6`. The retained patch's old hunk matched the current method exactly. The file was replaced through the normal GitHub Contents API using that blob SHA as the conflict guard.

Published commit:

- commit: `d9a381dd4607a928cd1315adef6431e239995bc1`
- resulting `supported.py` blob: `8140d6e180c3e97085830b872cea7d87f8433144`

Post-write commit inspection shows one file changed and the diff is exactly the retained narrow hunk:

- add `q.execute("BEGIN IMMEDIATE")` before activation table installation;
- replace table `executescript(... + ";")` with single-statement `execute(...)`;
- replace trigger `executescript(... + ";")` with single-statement `execute(...)`;
- retain exact persisted table/trigger definition verification, existing commit, rollback, and close behavior.

A branch re-fetch confirms the resulting method and exact blob SHA above.

## Mechanism validation in this run

A file-backed SQLite two-connection probe exercised the security-relevant state: an existing canonical activation table containing one `SQL_COMMITTED` row, with the trigger initially absent. Connection A began `BEGIN IMMEDIATE`, then installed the trigger before commit. A concurrent Connection B attempted to insert into `shared_anchor_intents` while A held the transaction. After A committed, B resumed against the installed trigger and failed with `IntegrityError: provider activation unresolved`; zero intents were persisted.

This validates the intended lock/installation mechanism. It is not a substitute for exact branch behavioral tests.

## Validation status

Confirmed:

- conflict-guarded Contents API application succeeded;
- published commit diff is exactly the retained source hunk;
- branch re-fetch reports resulting blob `8140d6e180c3e97085830b872cea7d87f8433144`;
- independent file-backed SQLite concurrency mechanism check passed.

Not claimed:

- exact published-branch `test_activation_schema_installation_race.py` GREEN;
- full LAB-090 focused/integration/downstream suite GREEN;
- PR readiness or merge readiness.

Those gates still require a runtime that can execute the exact branch dependency closure.

## Next action

LAB-086 remains first priority if a supported byte-preserving composition bridge appears. Otherwise, when exact source execution is available, run `test_activation_schema_installation_race.py` first, followed by schema/trigger tamper restart regressions, activation restart/integration tests, and downstream gates. Keep PR #175 draft until those behavioral gates are actually observed GREEN.
