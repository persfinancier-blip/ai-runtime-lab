# LAB-090 pre-SQL activation-ticket validation

Date: 2026-08-31

## Problem

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` previously trusted the `ActivationTicket` returned by the candidate provider's `prepare_activation()` and entered the coordinator SQL transaction before proving that the returned ticket was exactly bound to the requested generation, observed shared-anchor tail, activation identity, and provider-owned PREPARED reservation.

A malformed provider response could therefore supply inconsistent ticket fields that were persisted into `provider_generation_activations` and used during generation-head rotation before later reconciliation rejected the inconsistency.

The deterministic regression already published on PR #175 is `experiments/provider_generation_history/tests/test_activation_ticket_binding.py` (blob `05b11e7549a051ee5c09d77b3571aa8123e95e3d`). It returns a ticket with the wrong provider identity and requires that the durable generation remain G1 and that no G2 activation row be written.

## Fix published

PR #175 branch `lab-090-provider-activation-fencing` commit:

- `8aa12d35e3dc397543193e098ab51017cf09ffc8`
- resulting `supported.py` blob `f9f4975001fa691b415cbbd488897d8c44499c49`

Immediately after `prepare_activation()` and before opening the coordinator `BEGIN IMMEDIATE`, the implementation now requires:

- exact `ActivationTicket` type;
- `provider_id == new.provider_id`;
- `generation == new.generation`;
- `expected_position ==` the coordinator-observed tail;
- exact deterministic `activation_id`;
- integer positive fence;
- `provider.activation_status(ticket) == "PREPARED"` for that exact ticket.

Any binding failure raises `HistoricalVerificationError` before coordinator SQL mutation.

## Audit evidence

GitHub's returned commit diff shows one source file changed and exactly one guard block inserted immediately after `prepare_activation()` and before `sql_committed = False` / the SQL transaction. No generation-history SQL mutation was moved ahead of validation.

The Contents API write used the exact previously fetched `supported.py` blob `6aee4eaec6d34563ea82c2a3216a82fb1d157c00` as the optimistic-concurrency precondition. GitHub accepted it and returned the new content blob above.

A newline-at-EOF normalization also appears in the commit diff; it is semantically irrelevant but recorded rather than hidden.

## Validation limits in this run

Direct Git/raw transport was probed again and remained unavailable due DNS resolution failure. Therefore no exact branch-local behavioral GREEN or full activation integration/restart/downstream unittest gate is claimed for this commit in this run.

The pre-existing regression source remains the intended behavioral gate. Exact execution remains mandatory before PR #175 can leave draft status.

## Security/correctness note

For an invalid returned ticket, the coordinator deliberately does not attempt SQL mutation. It also does not guess or synthesize some other provider ticket to clear provider-owned state: if a provider violated its own prepare contract, fail-closed provider-side fencing is safer than aborting an unverified reservation.
