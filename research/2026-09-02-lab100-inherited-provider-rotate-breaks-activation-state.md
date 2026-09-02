# LAB-100 — exact provider type is still identity-mutable through inherited `rotate()`

Date: 2026-09-02

## Scope

Follow-up audit of LAB-100/#185 on draft PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`). This note does **not** create a new issue: it strengthens LAB-100's design constraint.

## Source fact

`FencedActivationProvider` subclasses `SignedAnchorProvider` and does not override or disable the inherited `rotate(provider_id, generation, key)` method.

`SignedAnchorProvider.rotate()` mutates `provider_id`, `generation`, and `key`, and clears request results. It does not inspect or migrate `FencedActivationProvider.activation_state`.

LAB-090 activation tickets are bound to `(provider_id, generation)`. `FencedActivationProvider._ticket_matches_runtime()` rejects a ticket whenever its provider identity/generation no longer equals the provider object's current identity/generation. `activation_status()`, `commit_activation()`, `release_activation()`, and `abort_activation()` all pass through that runtime-ticket identity check.

Therefore the exact audited implementation remains internally identity-mutable after an activation reservation exists.

## Concrete schedule

1. Construct exact `FencedActivationProvider` for provider A generation 2 with durable/shared `ActivationState`.
2. `prepare_activation(expected_position=7, activation_id=...)` installs a PREPARED ticket for `(A,2)` in `activation_state.pending`.
3. Before coordinator reconciliation, call inherited `provider.rotate("A", 3, key3)` on the same exact provider object.
4. `activation_state.pending` still contains the generation-2 ticket.
5. `activation_status(ticket)` now raises `ActivationTicketMismatch` because the provider runtime generation is 3.
6. `abort_activation(ticket)` also raises the same mismatch, so the pending reservation cannot be cleared through the ordinary exact-ticket API while the object remains rebound.
7. `increment()` remains fenced because it checks only whether `activation_state.pending` is non-`None`.

The result is a stranded provider-side reservation caused by the exact class itself, not by a malicious subclass.

## Isolated semantics probe

A small in-memory probe mirroring the relevant inherited-rotate + ticket-runtime checks produced:

- before identity rotation: status `PREPARED`;
- after generation 2 -> 3 rotation on the same object: both `status(ticket)` and `abort(ticket)` raised `ActivationTicketMismatch`;
- the original pending ticket remained installed.

This is a semantics probe, not exact repository behavioral execution. Direct git transport in the same run failed before repository execution with `Could not resolve host: github.com`.

## Why this matters to LAB-100

LAB-100 currently considers exact implementation identity as the minimal contract if custom providers are unsupported. This finding shows that **exact type alone is insufficient** unless the exact provider's authority/identity is construction-bound for the lifetime of any activation state, or provider identity rotation is made activation-aware and proven atomic with pending/committed state.

This is also adjacent to LAB-093 capability exposure, but the defect here is narrower: even with no subclass substitution, the trusted implementation exposes an inherited mutation that violates its own activation-ticket/runtime invariant.

## Regression-first contract addition

Add to LAB-100 pre-fix REDs:

- exact `FencedActivationProvider`, not a subclass;
- prepare a valid activation ticket;
- invoke inherited provider identity/generation rotation while the ticket is pending;
- prove the pending ticket becomes unreconcilable and remains installed;
- post-fix: either reject identity/key rotation while activation state is non-quiescent, or provide a formally defined activation-aware generation transition that preserves ticket reconciliation semantics;
- ensure no path silently clears or rebinds a pending ticket to a different generation.

## Design constraint

Do not solve LAB-100 only by replacing `isinstance(...)` with `type(...) is ...`. The trusted provider primitive must also have a lifetime-stable identity/capability contract while activation reservations exist. If provider identity rotation is required, it needs an explicit state-machine transition rather than the inherited generic mutable `rotate()`.
