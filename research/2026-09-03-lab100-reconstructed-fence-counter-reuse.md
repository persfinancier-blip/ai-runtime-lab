# LAB-100 — reconstructed activation fence counter can reuse an old fencing token

Date: 2026-09-03

## Scope

Source audit of draft PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`) while LAB-086 exact publication remains blocked by the absence of a supported byte-preserving connector-to-machine patch pipeline.

This note strengthens existing LAB-100/#185; it does not create a new issue.

## Finding

`ActivationState` contains three pieces of provider-owned lifecycle state:

- `next_fence: int = 0`
- `pending: ActivationTicket | None`
- `committed: dict[str, ActivationTicket]`

`FencedActivationProvider.prepare_activation()` allocates a new fencing token solely as:

```python
self.activation_state.next_fence += 1
...
fence=self.activation_state.next_fence
```

There is no constructor- or prepare-time invariant requiring `next_fence` to be at least the maximum fence represented by `pending` and `committed` durable tickets.

The class documentation explicitly treats supplying a shared/reconstructed `ActivationState` as the model for provider-side durability. Therefore a reconstructed state can be internally inconsistent while still being accepted by the implementation. For example:

1. historical activation T1 was committed with `fence=7` and remains in `committed`;
2. reconstruction supplies the committed map but accidentally/defaults `next_fence=0`;
3. after no live pending reservation remains, a new prepare increments `next_fence` to `1` and issues T2 with `fence=1`;
4. the provider has now reused/regressed its fencing-token epoch relative to already durable provider evidence.

A fencing token whose monotonicity can regress across reconstruction does not safely order old and new holders in a real external-service implementation. The coordinator currently checks only that a returned fence is a positive integer; historical activation verification also checks only `fence >= 1`, not continuity/monotonicity.

## Why this belongs to LAB-100

LAB-100 already requires the activation lifecycle, position/CAS authority, identity/key state, request idempotency and synchronization primitive to form one coherent trusted provider authority. The fence allocator is another part of exactly that authority. Persisting tickets without binding/recovering the allocator epoch is the same reconstruction/implementation-boundary problem, not a separate coordinator-table issue.

## Regression-first contract

When exact source execution becomes available, add a provider-level RED before production changes:

1. construct durable activation state containing a committed/released historical ticket with fence `N > 1`;
2. reconstruct the same provider identity/generation with that durable ticket evidence but `next_fence < N` (including the default zero case);
3. request a new activation;
4. pre-fix: demonstrate a newly issued fence `<= N`;
5. post-fix: reconstruction or prepare must fail closed, or recover an allocator epoch that provably yields a fence `> max(all durable provider fence evidence)`.

Also cover a live `pending` ticket with a fence greater than `next_fence` and ensure no second reservation or post-release allocation can regress the epoch.

## Design constraint

Do not "fix" this only by taking `max()` over caller-supplied mutable ticket collections at each prepare unless those collections themselves are part of the authenticated/atomic provider authority. A real provider must persist the fence allocator epoch atomically with reservation/commit state, or derive it from durable provider state whose integrity and completeness are independently guaranteed.

The coordinator-side SQLite activation table must not be promoted into the provider's fencing-token source of truth: LAB-090's purpose is precisely to retain an external linearization authority independent of coordinator SQLite.

## Evidence classification

Source-proved invariant gap on PR #175. No exact behavioral repository execution is claimed in this run.
