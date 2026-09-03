# LAB-090 audit — activation-id collision can be misclassified as this rotation's durable SQL commit

Date: 2026-09-03
Scope: draft PR #175 (`lab-090-provider-activation-fencing`), source audit only

## Finding

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` has an exception-reconciliation path after provider `prepare_activation()` succeeds. If the SQLite transaction fails, the handler re-queries `provider_generation_activations` by only `activation_id` and sets `sql_committed = True` whenever any row with that id has status `SQL_COMMITTED` or `COMMITTED`.

That is weaker than the exact-ticket contract used elsewhere. It does not verify that the recovered row binds all fields of the provider ticket (`new_generation_id`, `provider_id`, `generation`, `expected_position`, `fence`) before concluding that this rotation's SQL commit exists.

Concrete schedule:

1. Candidate generation `G` at durable tail `P` produces deterministic `activation_id = provider-activation:<G>:<P>`.
2. Provider `prepare_activation()` installs an authentic PREPARED ticket `T` with fence `F`.
3. SQLite already contains (e.g. by corruption/tamper or malformed prior state) a row using the same primary-key `activation_id` but with different authority-relevant fields, especially a different `new_generation_id` so the earlier `generation_id=new.generation_id` lookup does not catch it.
4. `INSERT INTO provider_generation_activations ...` fails on the primary-key collision.
5. The exception handler calls `_activation_row(activation_id=T.activation_id)`, sees status `SQL_COMMITTED` or `COMMITTED`, and sets `sql_committed = True` without checking exact row equality to `T`/`G`.
6. The original SQL exception is therefore swallowed and control proceeds to `_commit_or_reconcile_activation(provider, T)` as though the local rotation transaction had durably committed.
7. Provider commitment can now advance to `COMMITTED_FENCED`; only later `_mark_activation_committed(T)` notices that the durable row does not match the exact ticket and fails. This can strand an external committed fence while SQLite never contained this rotation's exact activation evidence.

This is distinct from the already-recorded duplicate-release race: that race has the same exact durable activation and a concurrent idempotent retry. Here the durable row is not this ticket at all, but the exception path mistakes a same-id row for proof of own commit.

It also complements LAB-099/#184 rather than duplicating it. LAB-099 authenticates historical ticket contents; this finding is an immediate coordinator reconciliation bug: exception recovery must not treat a non-exact row as transaction-commit evidence.

## Required regression-first contract

Add a test that seeds a conflicting `provider_generation_activations` row with the deterministic activation id but different authority-relevant fields and a terminal-looking status, then attempts the legitimate rotation.

Pre-fix, demonstrate that the SQL collision is misclassified as `sql_committed` and provider-side commit/reconcile is attempted.

Post-fix:

- the exception-reconciliation row must match the exact ticket and target generation descriptor before it can prove that this rotation committed;
- otherwise fail closed and enter trusted cleanup/recoverable-orphan handling for the authentic provider reservation;
- do not call `_commit_or_reconcile_activation()` from same-id evidence alone;
- preserve the original SQL failure as diagnostic context;
- compose with LAB-099 authenticated ticket binding so a mutable row cannot manufacture exact-commit evidence after the fact.

## Execution evidence / limitations

The source path was inspected directly from PR #175. Direct git transport was re-probed in this run and failed before repository access with `Could not resolve host: github.com`, so no exact branch behavioral RED/PASS is claimed.
