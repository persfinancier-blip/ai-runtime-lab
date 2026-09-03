# LAB-100 — inherited provider rotate bypasses activation fencing

Date: 2026-09-03

## Scope

Source audit of draft PR #175 (`LAB-090`) while LAB-086 exact publication remains tool-limited.

This finding strengthens existing LAB-100/#185 rather than creating a duplicate issue.

## Source evidence

`FencedActivationProvider` extends `SignedAnchorProvider` but does not override or disable the inherited `rotate(provider_id, generation, key)` method.

LAB-090 activation lifecycle state is stored separately in `ActivationState` and guarded by `activation_state.lock`. `prepare_activation()` creates a ticket bound to the provider's current `provider_id` and `generation`; later `activation_status()`, `commit_activation()`, `release_activation()`, and `abort_activation()` all call `_ticket_matches_runtime()` and therefore require the runtime identity to remain equal to the ticket identity.

The inherited `SignedAnchorProvider.rotate()` directly mutates `provider_id`, `generation`, `key`, and `_request_results` without consulting `ActivationState`, without acquiring `activation_state.lock`, and without rejecting a live pending/committed activation fence.

## Concrete schedule

1. provider identity is `(P, g)` and position is `N`;
2. coordinator calls `prepare_activation(expected_position=N, activation_id=A)` and receives ticket `T=(P,g,N,A,fence)`; provider now owns `ActivationState.pending=T`;
3. another holder of the same provider object/capability calls inherited `rotate(P, g+1, key2)` before coordinator commit/recovery;
4. the pending ticket remains stored unchanged in `ActivationState`;
5. every later lifecycle call on `T` fails `_ticket_matches_runtime()` because runtime generation is now `g+1` while ticket generation is `g`;
6. ordinary increment remains fenced because `pending` is still non-null, but coordinator cannot status/commit/release/abort the exact reservation through the supported LAB-090 lifecycle.

This can strand the external provider in a fail-closed but unrecoverable state without any matching durable coordinator transition proving the identity mutation.

## Why this is not a new issue

LAB-100 already asks whether the nested activation provider is the exact audited implementation or an independently verifiable trusted capability. The inherited mutation surface is part of that same implementation/capability authority boundary. LAB-093 also tracks caller-owned mutable provider capability exposure. The correct action is to strengthen those contracts rather than create LAB-101 for the same authority graph.

## Regression-first extension

Add an exact-provider RED once source execution is available:

- create `FencedActivationProvider` at generation g;
- prepare exact activation ticket T;
- invoke inherited provider `rotate()` before SQL/provider activation commit;
- pre-fix: prove runtime identity changes while `ActivationState.pending == T`, then lifecycle reconciliation of T fails and ordinary increment remains fenced;
- post-fix: supported provider authority must prevent identity/key rotation while any activation reservation/commit state is unresolved, or move identity/key/position/request-results/activation state under one atomic provider authority that defines a safe transition protocol;
- verify no caller-overridable/inherited mutation method can bypass that authority boundary.

Do not fix only by swallowing `ActivationTicketMismatch` or clearing `pending`: that would discard provider-owned activation evidence. The identity transition itself must be serialized/authorized with the same durable provider authority.

## Validation status

Source-proved from exact PR #175 activation implementation and inherited `SignedAnchorProvider` source. Exact branch execution remains unavailable in this run, so no behavioral PASS/FAIL is claimed.
