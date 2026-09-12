# LAB-100 — provider/verifier pairing must be validated before activation prepare

Date: 2026-09-12
Status: source-audit finding; exact behavioral RED/GREEN still pending
Scope: draft PR #175 (`lab-090-provider-activation-fencing`) at head `d9a381dd4607a928cd1315adef6431e239995bc1`

## Finding

`AttestedCatchup` accepts an arbitrary `provider` object and `verifier` object and does not itself prove that they describe the same provider identity/generation/key. On PR #175, `SupportedHistoricalSharedAnchorLedger.rotate_provider()` derives `runtime_new` only from `new_attested.verifier`, checks that verifier-derived descriptor against the requested `new` descriptor, then obtains `provider = new_attested.provider` and only checks `isinstance(provider, FencedActivationProvider)` before calling `provider.prepare_activation(...)`.

The exact `FencedActivationProvider` can therefore be paired with a verifier for a different provider generation. The coordinator reaches the provider mutation first:

1. verifier-derived `runtime_new` matches requested generation `new`;
2. exact `FencedActivationProvider` belongs to a different provider identity/generation but passes the `isinstance` gate;
3. `prepare_activation()` installs `ActivationState.pending` and allocates a fence using the provider object's own identity/generation;
4. only after that mutation does `rotate_provider()` validate the returned ticket against `new.provider_id/new.generation`;
5. mismatch raises `HistoricalVerificationError` before the SQL-phase cleanup/abort scope is entered;
6. the provider reservation remains installed with no durable `provider_generation_activations` row from which restart can reconcile it.

This is a stronger exact-provider instance of the existing rejected-ticket cleanup finding: it does not require `WrongTicketProvider` or any overridden activation lifecycle method. The authority split is already present in the ordinary `AttestedCatchup(provider, verifier)` construction boundary.

## Source evidence

At PR #175:

- `experiments/anchor_attestation/protocol.py`: `AttestedCatchup.__init__()` stores `provider` and `verifier` without a pairing check.
- `experiments/provider_generation_history/supported.py`:
  - `_descriptor_from_attested()` derives the runtime descriptor from `attested.verifier.expected` and `keyring`, not from the provider object;
  - `rotate_provider()` validates that verifier-derived descriptor against `new`, then accepts any `isinstance(..., FencedActivationProvider)` provider;
  - `provider.prepare_activation()` occurs before ticket identity validation;
  - malformed/mismatched ticket rejection occurs before the `sql_committed=False` / SQL try/except block whose failure path calls `provider.abort_activation(ticket)`.
- `experiments/provider_generation_history/activation.py`: exact `FencedActivationProvider.prepare_activation()` mutates `ActivationState.next_fence` and `ActivationState.pending` before returning the ticket.

## Required regression

Use only exact audited classes; no malicious subclass:

1. construct valid g1 ledger;
2. create exact `FencedActivationProvider` whose provider identity/generation is not g2;
3. pair it with an `AttestationVerifier` whose expected identity/keyring correctly describe g2;
4. call `rotate_provider(g2, valid_transition_proof, mismatched_attested_pair)`;
5. pre-fix expectation: coordinator rejects the ticket but the provider has a live `ActivationState.pending` reservation and no durable g2 activation row;
6. post-fix expectation: fail closed before `prepare_activation()` or any provider/SQLite mutation; provider state and durable history remain unchanged.

Also cover provider-id mismatch, generation mismatch, and key/identity mismatch where representable by the supported provider implementation.

## Design implication

LAB-100's trusted construction boundary must bind the verifier identity/key material to the exact provider authority before invoking any mutating provider lifecycle method. A post-prepare ticket check is necessary but too late for fail-before-mutation semantics.

This composes with, but does not replace:

- the trusted/sealed provider implementation requirement;
- caller-owned `ActivationState` removal/confinement;
- activation-aware provider identity rotation;
- monotonic fence reconstruction;
- authenticated retained activation-ticket provenance;
- restart verification before recovery side effects.

## Execution caveat

Direct exact repository materialization was re-probed in this run and failed before repository execution with `Could not resolve host: github.com`. This note records source-level proof and a RED-first regression contract only. No exact behavioral RED/GREEN, compileall, or integration PASS is claimed.
