# LAB-100 — caller-owned ActivationState can bypass exact-provider fencing authority

Date: 2026-09-02

## Scope

Strengthening of LAB-100 / issue #185. This is not a separate issue because it is the same activation-provider implementation/capability authority boundary.

## Source observation

On PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`, `FencedActivationProvider.__init__()` accepts an optional caller-supplied `activation_state` and retains that exact mutable object as public `self.activation_state`.

`ActivationState` is a mutable dataclass with public authority-bearing fields:

- `next_fence`
- `pending`
- `committed`
- `lock`

All activation lifecycle methods (`prepare_activation`, `activation_status`, `commit_activation`, `release_activation`, `abort_activation`, and the `increment` fence check) directly trust this retained object.

Therefore even if LAB-100 eventually requires `type(provider) is FencedActivationProvider`, the fence-state authority can still remain caller-owned and externally mutable if the caller supplied the `ActivationState` or later reaches `provider.activation_state`.

## Concrete consequence

A valid provider-side pending reservation is represented only by `activation_state.pending != None` in this in-process model. An external holder of the same state object can assign `pending = None` directly, bypassing `release_activation()` / `abort_activation()` and causing `increment()` to stop observing the activation fence.

Likewise, direct mutation of `committed` or `next_fence` can fabricate/remove provider lifecycle evidence or disturb monotonic fence allocation without traversing the audited methods.

## Isolated semantics probe

Executed a minimal dataclass/reference probe mirroring the relevant ownership semantics:

1. create mutable shared state;
2. install one pending ticket;
3. retain a second reference to the same object;
4. assign `pending = None` through that external reference;
5. observe the provider-visible state is now unfenced.

Observed result: pending existed before mutation and was absent afterward (`True, True`).

This is semantics evidence, not an exact PR behavioral PASS.

## Design constraint

LAB-100 must bind not only the provider implementation type but the provider-owned activation-state authority.

Minimal coherent options:

1. For the in-process audited provider, construct activation state internally, keep it private, and expose no mutable raw state object through the supported capability surface.
2. If restart tests need durable shared state injection, inject through an explicitly trusted provider-store abstraction whose mutation API enforces the same lifecycle invariants; do not accept an arbitrary mutable dataclass as authority.
3. If real providers are adapters to an external service, treat the adapter as a least-capability client and independently authenticate/reconcile provider-side state rather than trusting a caller-mutable Python object.

Exact-type enforcement alone is therefore insufficient.

## Required regression-first addition

- construct an exact `FencedActivationProvider` with caller-retained activation state;
- establish a valid PREPARED ticket;
- mutate the retained state out-of-band (at minimum clear `pending`; also cover committed/fence rebinding where meaningful);
- pre-fix: demonstrate the supported coordinator/provider surface can observe an unfenced or fabricated lifecycle state;
- post-fix: prove the supported activation authority cannot be changed through a caller-owned/raw mutable state reference.

Compose this with the existing LAB-100 regressions for fake provider subclasses and inherited identity/generation rotation.

## Execution limitation

Direct Git transport in this run failed before repository execution with `Could not resolve host: github.com`. No exact repository RED/GREEN or production mutation is claimed.
