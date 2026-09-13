# LAB-099 — exact CONFIRMED seed prerequisite audit

Date: 2026-09-13

## Scope

Source-audit the smallest exact SQLite/reference fixture needed to make the frozen LAB-099 `provider-alpha` / generation 8 / `41 -> 42` CONFIRMED bridge mechanically executable end-to-end without adapting or synthesizing authority.

This run first re-probed LAB-086 exact materialization. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128), so no new LAB-086 executable/security gate is claimed.

## Frozen LAB-099 bridge already available

PR #186 freezes:

- provider id `provider-alpha`;
- provider generation `8`;
- predecessor position `41`;
- confirmed position `42`;
- exact shared-anchor request id `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`;
- stable RECONCILE receipt binding `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`;
- confirmed entry digest `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`;
- PREPARED digest and exact cutover materialization contracts.

Those values are sufficient to validate the semantic binding of a CONFIRMED ledger row. They are not sufficient to construct an authenticated live provider/history fixture without introducing new authority material.

## Existing source contracts inspected

### Provider generation history

`experiments/provider_generation_history/protocol.py` requires every durable generation descriptor to include `verification_key_hex`. `verify_durable()` reconstructs every generation, verifies every gN -> gN+1 transition using HMACs under both adjacent keys, requires the first generation to equal the construction bootstrap, and requires the terminal descriptor to match `provider_generation_head`.

Therefore an exact generation-8 provider-history seed requires either:

1. an already frozen exact g1..g8 descriptor/key/transition chain, or
2. a separately declared test execution credential chain.

The LAB-099 frozen bridge contains neither. A lone `provider-alpha/g8` head row would not satisfy the existing durable-history verification contract.

### Shared-anchor / attestation

`experiments/shared_anchor_intent_ledger/protocol.py` reauthenticates a CONFIRMED row by calling `attested.provider.reconcile_increment()` for the stored request id and then verifying the returned `RECONCILE` observation against the current provider identity/key.

`experiments/anchor_attestation/protocol.py` shows that `SignedAnchorProvider.reconcile_increment()` returns evidence only when the provider already retains `_request_results[request_id]`; that result is created by a prior authenticated increment. Its MAC is generated from the provider's current secret key. The stable receipt binding deliberately omits the key and challenge, so the frozen stable receipt cannot reconstruct the missing provider-side authenticated observation or its signing key.

Thus exact execution also requires a seeded provider-side request result for the frozen request id under an exact generation-8 verification key. Neither prerequisite is present in the frozen LAB-099 vectors.

## Repository-wide check

A repository code search for `provider-alpha` returned no existing default-branch fixture or authority chain that could supply those missing generation keys/provider request-result state. No existing exact seed was found to reuse.

## Decision

Do **not** add an `exact seeded reference database` in this slice.

Doing so now would require inventing at least one of:

- generation-8 verification/signing key material;
- the complete g1..g8 descriptor/transition chain needed by `verify_durable()`;
- provider-side `_request_results` state / a corresponding authenticated observation for the frozen request id.

Those are execution credentials/evidence, not derivable consequences of the current frozen semantic bridge. Silently generating them inside the seed would blur the boundary between a semantic test vector and the authority used to prove it.

This is a prerequisite gap, not a product blocker and not permission to generalize the bridge.

## Safe next slice

Define and freeze a **test-only execution witness contract** that is explicitly non-authoritative for LAB-099 semantics but supplies the missing mechanics:

- deterministic g1..g8 `provider-alpha` fixture keys and exact `GenerationDescriptor` chain;
- transitions generated/validated only through the existing provider-history contract;
- generation-8 `SignedAnchorProvider` initialized at position 41;
- the frozen request id executed through the existing increment path to create provider-side request-result state at position 42;
- assert that the resulting stable receipt equals the already frozen LAB-099 receipt binding before any persisted CONFIRMED test is allowed to proceed.

The witness must be rejected if it changes any frozen LAB-099 request/position/receipt/head value. It must not become a second source of LAB-099 authority.

Do not add production `activation_reservation_provenance` code until actual repository RED is observed.
