# LAB-092 attested/provider capability-boundary audit — 2026-09-01

## Question
After LAB-092 migration provenance becomes incomplete post-construction, can a publicly reachable object from the live ledger still mutate a durable authority surface without passing through the four existing provenance guards?

## Source facts
- `SharedAnchorLedger.__init__` stores the exact caller-supplied `AttestedCatchup` as `self.attested`.
- `AttestedCatchup.catch_up_one()` may call `provider.increment()` and therefore advance the external monotonic anchor.
- `attested.provider` is directly reachable. Under LAB-090 it may be a `FencedActivationProvider`, which exposes `prepare_activation`, `commit_activation`, `release_activation`, `abort_activation`, and inherited anchor mutation methods.
- The same `attested` / provider object is already held by the caller before constructing any ledger.

## Decision
Do **not** classify this as a new LAB-092 provenance bypass and do not add a LAB-092-only wrapper regression/fix.

Reason: provenance deletion does not grant or amplify the capability. A caller capable of invoking `ledger.attested.catch_up_one()` could already invoke `attested.catch_up_one()` directly before construction. LAB-092 currently owns the provenance requirements on ledger-mediated durable state transitions; it does not establish revocation of caller-owned external-provider capabilities.

Adding a provenance wrapper only inside LAB-092 would silently strengthen the authority model at the wrong layer and risks breaking LAB-080/LAB-090 exact `AttestedCatchup` and `FencedActivationProvider` composition semantics without first defining whether exposure of `self.attested` itself is supported.

## Follow-up
Opened #178 / LAB-093 to define the capability-encapsulation boundary explicitly: whether supported ledgers should retain a private mutable provider handle while exposing only a least-capability/read-only view, and how that composes with LAB-087's sole-writable-handle/process boundary.

## LAB-092 implication
No production or regression mutation is justified from this audit alone. Continue searching only for paths where provenance loss permits a *new ledger-owned durable mutation* through a supported/publicly reachable handle. Current guarded surfaces remain:
1. shared-anchor `reserve()` / inherited `execute()`;
2. `rotate_provider()`;
3. mutation-capable `verify_component()` watermark updates;
4. public `provider_history.store_receipt()`.

## Validation limitation
This was a source/contract audit. No branch execution is claimed in this run.