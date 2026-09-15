# LAB-090 pre-ack SQL transition port — 2026-09-15

## Runtime observation

LAB-086 was probed first with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`. The command failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Donor audit

PR #175's `rotate_provider()` establishes the required pre-ack ordering: read the reserved tail, obtain an exact provider-owned activation ticket, then under one `BEGIN IMMEDIATE` re-check unresolved activation state, PREPARED shared-anchor intent state, and the unchanged reserved tail; persist `SQL_COMMITTED` and rotate provider history in the same transaction. Pre-commit failure aborts the exact provider ticket; post-SQL provider acknowledgement is a separate phase.

PR #187 already has the construction-bound private provider-history strategy and the post-SQL `ActivationCoordinatorMixin`. Wholesale copying PR #175 `supported.py` would regress those authority boundaries, so only the transition primitive was ported.

## Implemented

PR #187 now contains `experiments/provider_generation_history/activation_transition.py`.

The new `ActivationTransitionMixin`:

- derives activation identity from exact new generation identity plus reserved position;
- validates exact `ActivationTicket` type, provider/generation, position, activation id, and positive fence;
- requires provider status exactly `PREPARED` before SQL mutation;
- uses one `BEGIN IMMEDIATE` for the authoritative SQLite transition;
- re-checks no unresolved `SQL_COMMITTED` activation;
- re-checks no PREPARED shared-anchor intent;
- re-checks the reserved tail still equals the provider ticket position;
- inserts the exact `SQL_COMMITTED` activation row and calls private `self._history()._rotate_locked(q, new, proof)` before the same commit;
- on failure, checks durable activation state before deciding whether the provider ticket may be aborted, avoiding an abort when SQLite already records the ticket.

Production commit: `47543fb8566040c3837d0f2de261103abf59866c`.

Focused regression source was added as `tests/test_activation_transition_ordering.py` in commit `bdcdb51bfb96ea09226f68c9d53e61c36fbbe1bd`. It freezes private-history use, insert/rotate/commit ordering, activation identity binding, and ticket mismatch rejection.

## Validation boundary

The exact branch could not be materialized into the execution filesystem in this run. A local `py_compile` attempt against `/tmp/activation_transition.py` failed because no byte-preserving connector-to-filesystem materialization exists and that file was therefore absent. This is an execution-environment limitation, not a source test result. No pytest, compile, or repository GREEN is claimed.

## Audit / remaining composition

The transition primitive is intentionally not yet wired into `SupportedHistoricalSharedAnchorLedger`; doing so should be a separate small change so the MRO and existing LAB-092 provenance/startup layers can be audited explicitly.

Next step after the mandatory LAB-086 probe: compose `ActivationTransitionMixin` and `ActivationCoordinatorMixin` into the PR #187 supported ledger and replace only the rotation path with `prepare -> pre-ack SQL transition -> post-SQL acknowledgement`. Preserve existing retry behavior and construction-bound `_history()` authority. Then add focused regressions for changed-tail abort, PREPARED-intent abort, unresolved-activation abort, SQL rotation failure abort, and successful SQL_COMMITTED-to-RELEASED ordering before moving to restart/historical recovery.
