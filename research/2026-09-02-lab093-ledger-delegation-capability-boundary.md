# LAB-093 — supported-ledger delegation capability boundary

Date: 2026-09-02
Issue: #178

## Question

Does public `ledger.attested` create a concrete security/correctness property violation beyond the fact that the constructor caller originally supplied and therefore already owns the same `AttestedCatchup` object?

## Source facts

1. `SharedAnchorLedger.__init__()` retains the caller-supplied exact `AttestedCatchup` as public mutable `self.attested`.
2. The supported LAB-080 wrapper inherits that attribute unchanged; its additional contract is restart-time durable-state verification, not a narrower capability surface.
3. Normal supported ledger operations intentionally mediate external-anchor effects through durable SQLite intent state:
   - `execute()` first reserves a durable intent, then invokes `self.attested.catch_up_one(...)`, then reauthenticates and confirms the durable row;
   - `verify_component()` reads/authenticates the external anchor and advances only a verified durable watermark.
4. A holder of the supported ledger object can instead recover the raw retained capability through `ledger.attested` and call `catch_up_one()` directly. The same holder can reach `ledger.attested.provider` and invoke provider methods without first creating the matching durable shared-anchor intent.
5. In LAB-090 the concrete provider can be `FencedActivationProvider`, whose reachable public methods additionally include `prepare_activation`, `commit_activation`, `release_activation`, and `abort_activation`.
6. LAB-081/LAB-090 integration itself needs the mutable handle internally: runtime/provider identity is read from `self.attested`; normal execution uses it; provider rotation eventually swaps the internal runtime handle to `new_attested`.

## Concrete incremental violation

The earlier observation "the constructor caller already owns the provider" is insufficient once the supported ledger is delegated to another component.

Capability set comparison:

- Constructor caller: already owns `attested`; no new authority is created by storage in the ledger.
- Ledger-only recipient: nominally receives a durable shared-anchor capability whose consequential external advance path is `reserve -> external increment/reconcile -> durable confirmation`. Because `attested` is public, that recipient also receives the raw external-anchor capability and can bypass the durable intent protocol entirely.

A minimal reproduction does not require concurrency or provenance tamper:

1. Owner constructs a valid `SupportedSharedAnchorLedger(path, attested)` and passes only the ledger reference to a worker/component.
2. Worker calls `ledger.attested.catch_up_one(db_sequence=1, request_id="out-of-ledger")` (or reaches the provider directly with a valid challenge/request where applicable).
3. External anchor advances while `shared_anchor_meta.reserved_position` and `shared_anchor_intents` have not recorded the corresponding durable intent.
4. Subsequent ledger verification/operation observes an unexplained external advance and fails closed, creating an availability/correctness failure outside the mediated ledger protocol.

LAB-090 broadens the same leakage: a ledger-only recipient can recover activation mutation methods from `ledger.attested.provider`. Those methods are not part of the ordinary shared-anchor ledger API and can manipulate provider activation state outside `HistoricalSharedAnchorLedger.rotate_provider()` ordering.

This is an incremental delegation violation even though it is not an authority escalation for the original constructor caller.

## Relationship to LAB-087

LAB-087 already adopted the same architectural principle for SQLite: workers must not receive the broker's raw writable handle merely because the broker itself owns it. Connection authorizers are defense-in-depth; the process/filesystem boundary keeps the mutable capability private.

LAB-093 is the analogous external-provider capability boundary. It should not be implemented as a LAB-092 provenance wrapper.

## Required internal capabilities

The current implementation needs a mutable internal `AttestedCatchup` handle for:

- current provider descriptor extraction through verifier/expected/keyring;
- `challenge()` and `authenticated_read()`;
- mediated `catch_up_one()` during `execute()`;
- provider `reconcile_increment()` during reauthentication;
- LAB-081/LAB-090 runtime handle replacement after successful provider rotation.

LAB-090 rotation also needs activation methods on the candidate `new_attested.provider`, but those calls belong inside the coordinator's rotation method, not on a public ledger property.

Therefore a read-only facade over the current public object is not sufficient if it still exposes `.provider` or a method equivalent to `catch_up_one()`.

## Least-capability contract

Preferred contract for a future implementation:

1. Retain the exact mutable runtime object privately (`_attested`).
2. All internal mediated methods use `_attested`.
3. Do not expose the raw mutable `AttestedCatchup` or raw provider through a public ledger attribute.
4. If compatibility/introspection requires a public surface, expose immutable identity/status only (for example provider id, generation, authenticated current descriptor), never `catch_up_one`, raw `.provider`, activation mutation methods, verifier keyring mutation, or handle replacement.
5. Provider rotation replaces `_attested` only after the existing durable/provider activation protocol reaches its documented commit boundary.
6. Keep constructor ownership semantics explicit: this does not revoke capabilities already retained independently by the original caller; it prevents accidental authority amplification when the ledger itself is delegated.

## Regression required before production change

Regression should model a ledger-only recipient rather than the constructor caller:

- construct supported ledger with a valid provider;
- intentionally retain no external reference in the simulated worker/delegate;
- assert the supported public ledger surface cannot recover an object that offers direct external increment/reconcile/activation mutation;
- prove ordinary `execute`, `verify_component`, and provider rotation still work through their mediated paths;
- for LAB-090, prove activation prepare/commit/release remain reachable internally through `rotate_provider()` but not recoverable from the delegated ledger public surface.

A simple `hasattr(ledger, "attested") == False` check is not enough by itself; the audit must inspect all public return values/properties for an equivalent raw provider escape.

## Scope decision

LAB-093 is now justified as a concrete capability-encapsulation issue. It is not a LAB-092 provenance bug and does not supersede LAB-086 publication/execution priority.

No production code was staged in this run because exact branch execution is unavailable. The correct next implementation slice is a regression-first delegated-ledger capability test on the LAB-080/LAB-090 supported surfaces, then the minimal private-handle/read-only-introspection change if the pre-fix reproduction executes as specified.
