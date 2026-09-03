# LAB-093 — delegated-ledger capability exposure is a concrete least-capability violation

Date: 2026-09-04

## Question

LAB-093/#178 deliberately required proof of a concrete property violated *because the ledger exposes the caller-supplied `AttestedCatchup`*, rather than treating ordinary Python attribute reachability as a security finding by itself.

This audit answers that question against the current LAB-090 candidate surface.

## Exact source inspected

- `lab-090-provider-activation-fencing:experiments/shared_anchor_intent_ledger/protocol.py`, blob `fd22bc30f6aacdfd157557c8b458d9f7b0b3bda8`.
- `lab-090-provider-activation-fencing:experiments/provider_generation_history/integration.py`, blob `bd3f093637b4c619709bdc2d289af17417202697`.
- `lab-090-provider-activation-fencing:experiments/provider_generation_history/activation.py`, blob `fbc8cb4f581221c8b8755a43c436e4d6be74c7a7`.
- `lab-090-provider-activation-fencing:experiments/anchor_attestation/protocol.py`, blob `15d8b7cf8ff093490ccb75679030d3a0fe41e401`.
- LAB-087/#166 completed boundary contract: broker retains the only writable SQLite handle; workers are intentionally least-capability/read-only at the storage boundary.

No branch code was executed in this run: direct Git transport again failed before repository access with `Could not resolve host: github.com`. This note is a source-level capability audit only.

## Concrete violated property

Consider two principals:

1. the owner/composition root constructs an `AttestedCatchup` and a supported ledger;
2. a narrower component is delegated **only the ledger object**, not the original provider object.

Today that delegation is not least-capability.

`SharedAnchorLedger.__init__()` stores the exact caller object as public `self.attested`. `HistoricalSharedAnchorLedger` keeps consuming and replacing that same slot. The delegated holder can therefore recover the external mutation capability through the ledger itself:

- `ledger.attested.catch_up_one(...)` performs an authenticated provider increment when the provider is one position behind the requested DB sequence;
- `ledger.attested.provider.increment(...)` is an even more direct external-anchor mutation path;
- on LAB-090 providers, `ledger.attested.provider` can additionally expose provider-side activation state/lifecycle surfaces.

This is materially different from the original constructor caller already owning the provider. The narrower delegated component did **not** possess the provider before delegation; the ledger object graph grants it that capability.

Therefore the concrete property is:

> Delegating the supported ledger must not implicitly delegate authority to mutate or administratively control the external monotonic-anchor provider except through the ledger's own audited operations.

The current object graph violates that property.

## Why this matters with LAB-087

LAB-087 already established a least-capability model at the SQLite boundary: a worker is not handed the broker's writable handle merely because the broker owns one. The same principle applies to the external provider capability.

A component that only needs `reserve/execute/verify` should not gain an independent path around those ledger semantics to advance the anchor or manipulate activation state.

Direct provider mutation can create availability/correctness failures even when it cannot forge authenticated history. For example, an out-of-band increment can make later ledger execution observe an unexplained provider advance and fail closed. That is still an authority leak from the delegated interface: the component can cause an external effect that the ledger API did not authorize as such.

## Important non-fix: `_attested` is not a security boundary

Simply renaming `self.attested` to `self._attested`, freezing a dataclass, or exposing a read-only property is insufficient if mutually untrusted principals execute in the same Python process and can inspect object attributes. Python naming conventions do not provide capability isolation.

There are two coherent supported models:

### Model A — same-trust in-process composition

If every holder of the ledger object is already trusted with the raw provider capability, then LAB-093 is not a security boundary. Document that fact explicitly and classify `attested` exposure as API/encapsulation debt only.

### Model B — least-capability delegation

If a ledger can be delegated to a narrower principal, the supported delegated object must be a façade/proxy whose reachable object graph contains no raw `AttestedCatchup`, `SignedAnchorProvider`, `FencedActivationProvider`, activation-state object, or equivalent mutation handle.

The mutation-capable provider remains owned by the trusted broker/composition root (or a dedicated process). The façade exposes only the audited semantic operations required by the delegate plus immutable/read-only identity/status projections where needed.

For a real trust boundary between principals, process isolation / RPC is the stronger composition and aligns naturally with LAB-087's broker model.

## Regression-first contract

Before implementation, add a regression that models *delegation*, not the original constructor caller:

1. trusted composition code constructs the provider, attestation wrapper, and supported ledger;
2. only the supported delegated ledger/facade is handed to a restricted component;
3. pre-fix, demonstrate that walking the delegated object graph reaches a callable external mutation surface (`catch_up_one`, provider `increment`, or activation lifecycle) and can alter provider state without going through the intended ledger operation;
4. post-fix, the delegated surface still performs required ledger operations but exposes no reachable raw provider/activation mutation capability;
5. prove normal broker-owned execute/reconcile/rotation paths still work;
6. compose with LAB-087 restricted-worker tests so SQLite and provider mutation capabilities obey one least-authority story.

Do not use a test that merely asserts an attribute name starts with `_`; assert absence of a reachable supported mutation capability from the delegated surface.

## Verdict

`LAB093_CONCRETE_DELEGATION_PROPERTY_PROVEN`

LAB-093 is justified **if** the product intends narrower ledger delegation. The right implementation target is a capability-safe façade/process boundary, not cosmetic attribute privacy. If the product instead declares all in-process ledger holders fully trusted with the provider, record that trust model and do not pretend underscore/private fields enforce security.
