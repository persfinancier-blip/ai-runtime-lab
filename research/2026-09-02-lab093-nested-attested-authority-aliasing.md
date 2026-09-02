# LAB-093 — nested AttestedCatchup authority aliasing audit

Date: 2026-09-02
Issue: #178 / LAB-093
Scope: source-level audit only; no behavioral execution claimed in this run.

## Question

Would LAB-093 be fixed by moving `HistoricalSharedAnchorLedger.attested` to private storage and exposing a read-only `attested` property that returns the original `AttestedCatchup` object?

## Finding

No. The raw `AttestedCatchup` is itself a mutable authority graph.

`SharedAnchorLedger.__init__()` currently retains the exact caller-supplied object as `self.attested`. Supported ledger methods later derive provider identity from `self.attested.verifier.expected`, invoke `self.attested.catch_up_one()`, call `self.attested.provider.reconcile_increment()`, and verify observations with `self.attested.verifier.verify()`.

In LAB-036, `AttestedCatchup` publicly stores both `provider` and `verifier`. `AttestationVerifier` publicly stores mutable `keyring` and `expected`. None of these are frozen/value-only views.

Therefore, making only the outer ledger slot non-rebindable while returning the raw object through a read-only property would still permit delegated code to mutate nested authority state, for example:

1. obtain the raw `ledger.attested` object;
2. replace `attested.provider` with provider B;
3. replace `attested.verifier.expected` with B's identity;
4. add/replace B's key in `attested.verifier.keyring`;
5. subsequent supported ledger operations consume the mutated graph through `_provider()`, `_descriptor_from_attested()`, `_reauthenticate()`, or `execute()`.

This is an aliasing/capability problem, not merely Python attribute rebinding. A read-only property that returns a mutable authority object is not a least-capability view.

## Security/correctness implication

The construction-time exact-type check (`type(attested) is AttestedCatchup`) does not establish lifetime identity or immutability of the nested provider/verifier/keyring graph. A delegated holder that is intended to receive only ledger authority can recover and mutate the stronger external provider/verifier authority if the raw object remains reachable.

This composes with the already-proved LAB-093 findings:

- direct raw-provider capability exposure (`ledger.attested.provider`);
- public outer `ledger.attested` slot rebinding.

The nested-aliasing case matters because it defeats an incomplete fix that merely changes `self.attested` to `_attested` plus `@property attested: return self._attested`.

## Required LAB-093 contract refinement

A safe fix must satisfy both:

1. the active internal attested capability is construction/lifecycle-bound in private state and cannot be replaced except through the validated provider-rotation transition; and
2. public introspection must not return the raw mutable `AttestedCatchup`, provider, verifier, keyring, or any alias from which those objects can be recovered or mutated.

If introspection is required, expose immutable value data only (for example provider id/generation/status snapshots), not a wrapper that forwards mutable nested objects.

Internal code may retain the raw capability privately because it must perform authenticated reads/reconciliation/catch-up. The boundary is delegation: possession of the supported ledger must not automatically amplify into possession of the raw external mutation/verifier configuration capabilities.

## Regression-first requirement

Before production change, add a regression that demonstrates the incomplete-fix hazard explicitly:

- construct ledger against provider A;
- obtain the public introspection surface;
- attempt nested retargeting of provider/verifier/keyring to valid provider B without assigning a new object to the outer ledger slot;
- pre-fix/raw-alias surface should demonstrate that supported authority can be redirected or that the stronger raw capability is recoverable;
- post-fix least-capability view must make the nested mutable objects unreachable, while normal execute/reconcile/validated rotation behavior remains intact.

The regression should not rely only on `AttributeError` for `ledger.attested = ...`; it must prove absence of nested authority recovery/mutation.

## Source evidence

- `experiments/shared_anchor_intent_ledger/protocol.py`: `SharedAnchorLedger.__init__()` retains `self.attested = attested`; `_provider()`, `_reauthenticate()`, and `execute()` consume it later.
- `experiments/provider_generation_history/integration.py`: historical integration repeatedly consumes `self.attested`, and provider rotation assigns a new raw attested object after durable rotation.
- `experiments/anchor_attestation/protocol.py`: `AttestedCatchup.__init__()` stores public mutable `provider` and `verifier`; `AttestationVerifier.__init__()` stores public mutable `keyring` and `expected`.

## Decision

Do not create a new issue. This is a concrete refinement of LAB-093/#178 and should be part of its acceptance criteria. Do not accept an outer-slot-only fix or a read-only property returning the raw mutable object.
