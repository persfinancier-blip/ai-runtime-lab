# LAB-100 — reconstructed provider splits activation state from anchor position authority

Date: 2026-09-03

## Scope

Fallback audit of draft PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`) while LAB-086 exact byte-preserving composition remains blocked by unavailable direct Git transport and no connector-side apply-patch primitive.

No production code is changed and no exact-branch behavioral PASS is claimed.

## Finding

`FencedActivationProvider` treats `ActivationState` as the provider-durable state supplied across reconstructed provider objects. That state persists `next_fence`, `pending`, and `committed`, and its lock serializes activation lifecycle operations.

However the inherited `SignedAnchorProvider` keeps the anchor position (`value`) and request-result map (`_request_results`) directly on each Python provider object. Those fields are not part of `ActivationState` and are not bound to it by an identity/capability check.

Therefore reconstruction can preserve the exact pending activation ticket while replacing the position authority that the ticket was prepared against. A minimal semantics probe gives:

- provider generation 2 at position 10 prepares activation `rotate-2`, expected position 10, fence 1;
- the same `ActivationState` is supplied to a reconstructed generation-2 provider object whose object-local `value` is 3;
- `activation_status(ticket)` is still `PREPARED`, because status only consults identity/generation plus `ActivationState`;
- the reconstructed provider nevertheless exposes a different anchor position authority.

This is a distinct dimension of existing LAB-100, not a new issue. Previous LAB-100 evidence established subclass authority, generic inherited identity rotation, caller-owned mutable `ActivationState`, and non-monotonic fence reconstruction. This finding shows that even a correctly preserved activation-state object is insufficient if the anchor CAS/position/request-result authority can be reconstructed independently.

## Why it matters

The LAB-090 contract says `prepare_activation()` is the external linearization/fence point for the exact observed position. That claim requires the activation ticket and the underlying position/CAS state to belong to one indivisible provider authority. Persisting only the activation half permits a reconstructed object to attest activation status from one state while reads/increments operate on another object-local state.

The in-process concurrency test does not prove this boundary: it uses one `FencedActivationProvider` object, so `prepare_activation()` and `increment()` happen to share the same `activation_state.lock` wrapper around that object's `value`. Reconstruction is the case where the two state domains separate.

## Required RED / post-fix contract

Add a pre-fix RED that:

1. prepares a valid activation ticket against provider position `P`;
2. reconstructs the exact provider identity/generation with the retained activation durability but a different position/CAS state `Q != P`;
3. proves the supported surface currently accepts/reconciles activation status without establishing that both states are one authority.

Post-fix, provider reconstruction must fail closed unless activation lifecycle state, position/CAS state, request-idempotency state, provider identity/key, and their synchronization primitive are bound to one durable provider authority. A caller must not be able to mix retained activation state with independently chosen anchor state.

This should be composed with the existing LAB-100 REDs rather than solved by exact-type checking alone.
