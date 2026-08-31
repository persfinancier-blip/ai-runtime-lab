# LAB-090 — activation table schema verification fix

Date: 2026-08-31

## Problem

`SupportedHistoricalSharedAnchorLedger._init_activation_schema()` previously relied on `CREATE TABLE IF NOT EXISTS provider_generation_activations(...)`. SQLite accepts that statement when an object with the same name already exists as a VIEW, so a durable tamper could replace the activation relation with a compatible empty view. The already-canonical activation trigger could then continue to exist while recovery and record verification observed no activation rows.

## Fix

PR #175 branch `lab-090-provider-activation-fencing` commit `ae3a3cf089f7436ea74548ef9fa6cc5242e276e8` introduces canonical activation-table DDL and verifies the persisted object immediately after the idempotent create attempt, before trigger validation or recovery.

Required persisted contract:

- object name is exactly `provider_generation_activations`;
- `sqlite_master.type` is exactly `table`;
- persisted SQL is non-null;
- normalized persisted SQL exactly matches the canonical table DDL, including PRIMARY KEY, UNIQUE, NOT NULL, and status CHECK constraints.

No `DROP`, recreate, migration, or evidence-destructive repair is attempted. Any mismatch raises `HistoricalVerificationError` and restart fails closed.

## Validation actually executed

1. GitHub commit diff inspection: only `experiments/provider_generation_history/supported.py` changed; the patch adds the canonical table definition and pre-recovery schema verification.
2. File-backed SQLite mechanism probe executed locally in this run:
   - fresh canonical table -> exact normalized DDL check PASS;
   - table replaced by same-name VIEW -> `CREATE TABLE IF NOT EXISTS` leaves the VIEW in place;
   - new verification observes `type='view'` and rejects it -> PASS.
3. Direct git clone/exact branch execution was attempted but failed before repository code execution with `Could not resolve host: github.com`.

Therefore no exact-branch behavioral/full-suite GREEN is claimed yet. The existing regression `test_activation_schema_tamper_restart.py` remains the required exact behavioral gate when repository execution transport becomes available.

## Next gate

Run the published-head activation schema tamper regression, trigger tamper regression, activation restart/integration suite, and downstream supported tests. Keep PR #175 draft until those exact-source gates pass and branch integration state is clean.
