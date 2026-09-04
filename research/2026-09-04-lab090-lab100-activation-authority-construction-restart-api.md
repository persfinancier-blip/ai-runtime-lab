# LAB-090 / LAB-100 — ActivationAuthority construction, restart, and upgrade API

Date: 2026-09-04
Status: contract frozen; exact RED/GREEN pending

## Scope

This note freezes the smallest coherent construction/restart API for the LAB-090 activation authority after LAB-100 established that provider-side fencing semantics are an explicit trust root. It composes the LAB-090 draft implementation with the already frozen LAB-093..099 retained-authority/provenance contracts.

No production code is changed here because exact repository execution remains unavailable in this run. Direct Git transport again failed before repository access with `Could not resolve host: github.com`.

## Fresh source evidence

PR #175 branch `lab-090-provider-activation-fencing` currently constructs `SupportedHistoricalSharedAnchorLedger(path, attested, bootstrap)`, then derives the activation provider indirectly from `attested.provider` during rotation/recovery.

Relevant exact source observations:

- `activation.py` blob `fbc8cb4f581221c8b8755a43c436e4d6be74c7a7`: `FencedActivationProvider` is subclassable, accepts caller-owned `activation_state`, exposes that state publicly, and inherits generic provider identity mutation from `SignedAnchorProvider`.
- `supported.py` on PR #175: startup `_recover_pending_activation()` and `rotate_provider()` both fetch `attested.provider` and accept it using `isinstance(provider, FencedActivationProvider)`, then trust lifecycle return values.
- `protocol.py` blob `c2077635aa2ecebf9a3072d97efeacb37cb0d478`: provider generation identity is currently only `(provider_id, generation, verification_key)` through `GenerationDescriptor`; activation implementation identity/version is not retained in that descriptor.

Therefore the activation authority cannot remain an incidental object reachable through `AttestedCatchup`. It must be a separately constructed, retained, verified capability whose implementation identity participates in durable authority reconstruction.

## Frozen V1 API

Conceptual factory:

```text
ActivationAuthorityFactory.create(
    provider_descriptor,
    implementation_id,
    implementation_version,
    protocol_version,
    durable_state_handle,
) -> ActivationAuthority
```

The factory is trusted code. Worker/caller code never supplies a live mutable activation-state object and never chooses an arbitrary implementation class.

Required inputs:

- `provider_descriptor`: exact current `GenerationDescriptor` / successor descriptor identity;
- `implementation_id`: stable registered identifier for the audited authority implementation or explicitly trusted adapter;
- `implementation_version`: exact implementation semantics version, not a display string;
- `protocol_version`: exact activation receipt/ticket protocol version;
- `durable_state_handle`: broker-owned/provider-owned authority-state locator/capability, never exported to restricted workers.

The returned `ActivationAuthority` exposes only the activation lifecycle needed by LAB-090 plus the ordinary anchor operation required to enforce fencing. Its internal state, raw provider object, storage handle, keys, and mutation primitives are not part of the delegated API.

## Construction-bound identity

The LAB-094..096 retained-authority graph must retain an activation-authority descriptor:

```text
ActivationAuthorityDescriptor(
  implementation_id,
  implementation_version,
  protocol_version,
  provider_id,
  provider_generation,
  provider_verification_key_id
)
```

This descriptor is immutable for the lifetime of one retained authority graph. Restart may reconstruct an equivalent capability only if every descriptor field matches durable authenticated provenance.

A same-provider reconstruction under a different implementation/version is **not** ordinary restart. It is an authority replacement/upgrade transition.

## Restart ordering

Broker/provider restart must fail closed in this order:

1. reconstruct and authenticate the LAB-094..096 retained authority graph;
2. reconstruct the exact registered `ActivationAuthority` implementation from its retained descriptor;
3. verify provider identity/generation/key identity against the durable generation head;
4. verify monotonic activation-state invariants (`next_fence`, pending ticket, committed ticket set / provider-native equivalent);
5. verify LAB-097..099 initialization certificate and authenticated activation-ticket provenance;
6. reconcile unresolved LAB-090 activation only after steps 1–5 succeed;
7. run durable ledger/history verification;
8. only then open LAB-093 worker-facing delegation endpoints.

No repair, release, provider increment, generation rotation, or SQLite authority mutation is allowed before the corresponding provenance/authority checks succeed.

## Authority replacement / upgrade

Changing any of these is an explicit authority transition:

- implementation id;
- implementation version when semantics or durable-state interpretation changes;
- protocol version;
- provider identity/generation/key identity outside the already authenticated generation transition.

An upgrade requires a new authenticated `ActivationAuthorityTransition` committed alongside the provider-generation/provenance transition. Minimum binding:

```text
old_authority_descriptor_digest
new_authority_descriptor_digest
provider_generation_transition_digest
activation_state_handoff_digest
protocol_version
```

The handoff must prove one of two states:

- **quiescent**: no pending activation fence exists and the monotonic fence cursor/history is transferred exactly; or
- **explicit unresolved handoff**: the new trusted authority can prove possession/continuity of the exact pending ticket and fence before coordinator recovery proceeds.

A caller may not upgrade by swapping an object reference, subclass, adapter registration, or state handle in memory.

## Factory/registry policy

V1 supports:

1. one exact audited in-process lab implementation; and
2. explicitly registered trusted adapters whose identity/version is known before construction.

Registration is administrative/broker authority, not a worker API. Dynamic import by caller-provided class path, duck typing, `isinstance` acceptance, reflection, or trusting self-reported implementation strings is unsupported.

## Failure semantics

Fail closed without mutating provider or SQLite authority state when:

- retained implementation id/version is unknown;
- implementation binary/code identity does not match its registered semantics version;
- provider descriptor differs from the retained authority descriptor;
- durable activation state is missing, rolled back, or internally inconsistent;
- a pending fence cannot be reconstructed exactly;
- a restart attempts to use a different implementation/version without an authenticated authority transition;
- an authority transition lacks exact state-handoff continuity;
- worker-facing code can obtain the raw authority/state/provider capability.

## RED-first matrix additions

Add these before production implementation:

1. ordinary restart with exact descriptor/state -> succeeds;
2. same provider + different unrecorded implementation id -> fail closed;
3. same implementation id + downgraded version -> fail closed;
4. protocol-version drift without transition -> fail closed;
5. caller-supplied mutable activation state -> rejected at construction;
6. arbitrary subclass/duck-type object -> rejected before mutation;
7. registry alias rebound to different implementation -> fail closed;
8. quiescent authenticated upgrade -> succeeds and preserves fence monotonicity;
9. upgrade with rolled-back `next_fence` -> fail closed;
10. unresolved pending ticket handoff with exact continuity -> recover safely;
11. unresolved handoff with same activation id but changed fence/position -> fail closed;
12. restart with missing provider-owned durable state -> fail closed;
13. provider generation changed without authenticated generation+authority transition -> fail closed;
14. authority reconstruction failure leaves SQLite/provider unchanged;
15. LAB-093 restricted worker cannot obtain factory, registry, state handle, raw authority, or provider.

These extend rather than replace the frozen LAB-100 18-case matrix and LAB-097..099 provenance matrix.

## Decision

`ActivationAuthority` is a first-class construction-bound trust root. LAB-090 must not recover it implicitly from `AttestedCatchup.provider`, and restart must not infer trust from Python type relationships or self-reported lifecycle statuses.

Verdict: `LAB090_LAB100_ACTIVATION_AUTHORITY_CONSTRUCTION_RESTART_API_FROZEN`.

## Exact next engineering step

When exact source execution becomes available, write the construction/restart RED tests first against PR #175 semantics, then implement the smallest factory + retained descriptor boundary. Do not implement production changes before executable RED/GREEN is available.
