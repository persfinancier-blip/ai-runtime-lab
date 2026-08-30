# LAB-090 — durable activation-ticket integration

Date: 2026-08-30

## Objective

Close the provider-generation handoff race where a candidate external provider could advance after an authenticated read but before the durable SQLite generation-head rotation.

## Implemented on draft PR #175

Branch: `lab-090-provider-activation-fencing`

Current implementation extends the earlier provider-owned activation primitive with coordinator durability:

1. Read the current durable shared-anchor tail only to choose the candidate expected position.
2. Call provider-side `prepare_activation(expected_position, activation_id)` before the authoritative SQLite rotation. This is the external linearization point and fences ordinary provider increments while PREPARED.
3. Enter `BEGIN IMMEDIATE` and re-check shared-ledger conditions. If a PREPARED shared-anchor intent exists or the tail changed, roll back SQL and abort the provider reservation.
4. In the same SQL transaction, persist the exact activation ticket (`activation_id`, new generation id, provider id/generation, expected position, fence) and rotate provider-generation history/head. Durable activation status is `SQL_COMMITTED` at this point.
5. A SQLite trigger rejects new `shared_anchor_intents` inserts while any activation remains `SQL_COMMITTED`, closing the post-SQL/pre-provider-commit writer window for every coordinator using the database.
6. Commit/reconcile the provider activation. `UnknownOutcome` is reconciled by exact ticket status. Only after provider status is COMMITTED is the durable activation row advanced to `COMMITTED` and the runtime provider swapped.
7. On restart with the new durable generation, an unresolved `SQL_COMMITTED` ticket is reconstructed from SQLite and reconciled against provider-owned activation state before normal work continues.

The integration intentionally requires `FencedActivationProvider` for provider rotation. Existing provider-generation integration tests on the branch were changed to exercise rotations through that fenced provider rather than silently falling back to the old read-before-SQL behavior.

## Regressions added

`experiments/provider_generation_history/tests/test_activation_integration.py` covers:

- provider prepare fences an attempted external advance before SQL rotation;
- a stale candidate is rejected at provider prepare before generation-head commit;
- SQL-side failure / existing PREPARED intent aborts the provider reservation and leaves generation unchanged;
- provider commit with lost acknowledgement reconciles as COMMITTED;
- post-SQL provider outage leaves a durable `SQL_COMMITTED` ticket;
- while that ticket is unresolved, new shared-anchor reservation is blocked;
- restart with the same provider-owned activation state reconciles the ticket and marks it COMMITTED.

The older integration suite was updated so rotation paths use `FencedActivationProvider`.

## Audit findings fixed during this run

Two issues were found after the first coordinator implementation and corrected before handoff:

1. **Post-SQL writer race.** After SQL generation-head commit but before provider commit, another writer could otherwise reserve an intent for the new generation. A DB-level trigger now blocks inserts while activation status is `SQL_COMMITTED`; the exception is translated to `PendingRotationBlocked` on the supported API.
2. **Over-strong fence uniqueness.** The first validator incorrectly required fence values to be globally unique across provider generations. Fence is already bound to provider generation/ticket, so only positive validity is enforced; a new provider-owned generation may legitimately restart its local fence sequence.

## Validation actually executed

Direct exact-branch execution was attempted via:

`git clone --depth 1 --branch lab-090-provider-activation-fencing https://github.com/persfinancier-blip/ai-runtime-lab.git`

and failed before repository execution with:

`Could not resolve host: github.com`

Therefore no byte-for-byte branch unittest result is claimed in this run.

A focused local SQLite mechanism check was executed independently and passed:

- with one activation row in `SQL_COMMITTED`, the trigger rejected a new shared-anchor insert with `provider activation unresolved`;
- after changing the activation row to `COMMITTED`, the same insert succeeded.

This confirms the trigger/transaction mechanism itself, not the whole branch.

## Source audit

The current PR changes are limited to:

- `experiments/provider_generation_history/activation.py`
- `experiments/provider_generation_history/supported.py`
- `experiments/provider_generation_history/tests/test_activation.py`
- `experiments/provider_generation_history/tests/test_activation_integration.py`
- `experiments/provider_generation_history/tests/test_integration.py`

No GitHub Actions or background workers were used for execution.

## Remaining acceptance work

PR #175 should remain draft until a runtime with direct branch transport can run the exact published branch tests, including the provider-generation history suite and relevant downstream shared-anchor suites. The source-level protocol now covers the requested stale-candidate, SQL-failure/abort, UNKNOWN, restart, and unrelated-writer windows; exact behavioral execution remains the missing evidence.
