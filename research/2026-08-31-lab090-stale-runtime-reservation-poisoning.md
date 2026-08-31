# LAB-090 stale-runtime reservation poisoning after failed activation release

Date: 2026-08-31

## Context

LAB-090 provider activation uses the ordering:

1. durable provider-generation rotation + activation row `SQL_COMMITTED`;
2. provider `commit_activation()` -> `COMMITTED_FENCED`;
3. durable activation acknowledgement -> `COMMITTED`;
4. exact provider `release_activation()`;
5. swap the live coordinator runtime to the new `AttestedCatchup`.

If step 4 fails with a provider outage, the durable provider head has already advanced and the activation row is `COMMITTED`, but the in-memory ledger still retains the old runtime provider because the swap happens only after release succeeds.

The existing activation trigger blocks new intents only while an activation is `SQL_COMMITTED`. Therefore the `COMMITTED`/release-lost window intentionally allows restart recovery, but the still-live stale object must not be allowed to create new durable intents.

## Defect

`HistoricalSharedAnchorLedger.reserve()` previously acquired `BEGIN IMMEDIATE`, read the durable provider head, and inserted a new `PREPARED` intent using that durable identity without checking that `self.attested` still matched the same durable head inside the transaction.

`execute()` checked `_runtime_matches_entry(entry)` only after `reserve()` had committed.

Concrete failure schedule:

1. G1 runtime is live.
2. G1 -> G2 SQL rotation commits.
3. provider G2 commits activation; SQLite acknowledgement becomes `COMMITTED`.
4. G2 release fails; `rotate_provider()` raises before `self.attested = new_attested`.
5. caller catches the outage and reuses the same ledger object.
6. `execute(intent)` calls `reserve(intent)`.
7. old code inserts a G2 `PREPARED` intent and advances `shared_anchor_meta.reserved_position` while runtime is still G1.
8. only afterward `_runtime_matches_entry()` raises `CurrentGenerationRequired`.

The failed operation has now poisoned durable state with an unresolved PREPARED tail even though no external effect was allowed to execute. Future provider rotation is blocked and recovery requires additional reconciliation/restart work.

This is fail-closed availability/correctness state poisoning, not an authority escalation.

## Fix

Published on draft PR #175 / branch `lab-090-provider-activation-fencing`:

- commit `982bc588be0acc05b4218ce4caf49b214816b86b`
- `experiments/provider_generation_history/integration.py` blob `bd3f093637b4c619709bdc2d289af17417202697`

Inside the existing `BEGIN IMMEDIATE` reservation transaction, immediately after reading `provider_history._current_locked(q)`, the code now derives the live runtime descriptor and requires exact generation-id equality before reading/incrementing the ledger tail or inserting any intent.

This placement matters: a pre-transaction check would still race with a concurrent provider rotation that acquires the SQLite writer lock before reservation.

## Regression

Published:

- commit/head `c09e07c5bf96f9bc1fa12771fd54b0b5567fefb6`
- `experiments/provider_generation_history/tests/test_activation_integration.py` blob `17f8783291efe1b6a4d0cbbf5977694f707a836f`

`test_failed_release_stale_runtime_cannot_poison_next_intent` reproduces a lost activation release, confirms durable head G2 while the live ledger still references G1, then calls `execute()` and requires `CurrentGenerationRequired`. It additionally verifies that `shared_anchor_meta.reserved_position` remains zero and no `must-not-persist` intent row exists.

## Executed mechanism check

Direct git transport was probed first and failed before repository code execution with:

`Could not resolve host: github.com`

A focused SQLite ordering check was executed independently to validate the persistence mechanism:

- old ordering (INSERT/metadata commit, then stale-runtime check): row `[('must-not-persist', 'PREPARED')]`, tail `1`;
- new ordering (runtime-vs-durable check inside `BEGIN IMMEDIATE` before INSERT): no intent rows, tail `0`.

This mechanism check validates the transaction-ordering claim but is **not** an exact PR-head unittest PASS. Exact whole-branch integration/restart/downstream execution remains pending.

## Audit

The change does not alter provider authority, generation transition proofs, activation ticket semantics, thresholds, or external-effect execution. It adds only a missing fail-closed precondition at the transaction boundary where the durable intent is created.

Existing-intent idempotent reads remain before this check. That is intentional: returning an already durable entry is not creation of a new effect; subsequent execution paths still enforce current-generation requirements before any new external effect.

## Next gate

LAB-086 remains priority #1. If its byte-preserving hidden-rowid publication path remains unavailable, reconstruct a broader exact LAB-090 dependency closure and run activation integration/restart/downstream tests from hash-verified published bytes, including this new regression.
