# LAB-100 — reconstructed ActivationState can reuse/decrease fencing tokens

Date: 2026-09-02
Scope: PR #175 (`lab-090-provider-activation-fencing`, observed head `d9a381dd4607a928cd1315adef6431e239995bc1`)
Related issue: #185 / LAB-100

## Finding

`FencedActivationProvider` accepts a caller-supplied `ActivationState` and treats `next_fence` as the sole allocator cursor. `prepare_activation()` increments that integer and emits it as the next ticket fence. The provider does not validate that `next_fence` is at least the maximum fence already present in `pending` or `committed` state.

Therefore a reconstructed/persisted state can be internally inconsistent while still being accepted. Example: `next_fence=0` with an already committed ticket at `fence=7`. The next fresh prepare increments the cursor to `1` and issues fence `1`, which is lower than a historical fence that the same provider state already claims to have issued.

This is a different facet of LAB-100's state-authority boundary from subclass overriding, inherited identity rotation, or external mutation after construction. Even if ownership is fixed and the exact provider class is enforced, reconstruction must validate the internal monotonic-fence invariant before the state becomes authoritative.

## Source evidence

PR #175 `experiments/provider_generation_history/activation.py` currently defines:

- `ActivationState.next_fence: int = 0`;
- `ActivationState.pending` and `ActivationState.committed` independently;
- constructor assignment `self.activation_state = activation_state or ActivationState()` with no consistency validation;
- fresh prepare allocation as `self.activation_state.next_fence += 1`, followed by `fence=self.activation_state.next_fence`.

No constructor or pre-allocation check proves `next_fence >= max(ticket.fence for pending/committed tickets)` or rejects malformed numeric fence/cursor relationships in reconstructed provider state.

## Deterministic semantics probe

Mirroring only the allocator relation is sufficient to expose the invariant failure:

1. reconstructed state contains committed ticket fence `7`;
2. reconstructed `next_fence` is `0`;
3. fresh allocation executes `next_fence += 1`;
4. new ticket receives fence `1`.

Observed relation: historical fence `7`, newly allocated fence `1`.

This is a semantics probe, not an exact-branch behavioral PASS.

## Security/correctness consequence

A fencing token is useful only if its ordering is monotonic within the authority that issues it. Reuse or regression can make stale/older work appear newer to any downstream component that relies on token ordering, and it makes restart/reconstruction semantics depend on an unvalidated caller field rather than durable ticket history.

The current prototype may not yet expose a downstream `fence > previous_fence` consumer, but LAB-090 explicitly models a monotonically fenced provider reservation. The provider therefore must establish that invariant itself rather than assume a well-formed caller state.

## Required RED/GREEN contract

Add a LAB-100 pre-fix RED using the exact PR source:

- construct/reconstruct provider state with `next_fence` below the maximum fence in `pending` or `committed`;
- demonstrate that pre-fix fresh prepare emits a non-monotonic/reused fence;
- require post-fix construction or first authoritative use to fail closed, or canonicalize the cursor from authenticated/durable provider-owned state before issuing any new ticket.

Also cover:

- `next_fence` equal to max historical fence: next allocation must be strictly greater;
- duplicate fence values across distinct historical tickets;
- invalid/negative/non-integer reconstructed cursor values;
- pending and committed copies of the same exact ticket without false duplicate rejection;
- restart after a released committed ticket, where historical max still constrains the next token.

## Design constraint

Do not repair this only by setting `next_fence = max(...)` from arbitrary caller-owned mutable objects. LAB-100 already requires provider-owned/attested authority for activation state. The monotonic cursor and the tickets from which it is derived must belong to that same trusted state-machine boundary.

No production code was changed in this step.