# LAB-099 confirmed execution witness boundary

Date: 2026-09-13

## Context

LAB-099 has an independently frozen CONFIRMED semantic bridge for `provider-alpha`, generation 8, predecessor position 41, confirmed position 42, request id `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`, stable receipt binding `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`, and confirmed-entry digest `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`.

The prior prerequisite audit correctly found that authenticated execution also needs a complete provider-history chain and provider-side request-result state. This note decides how those mechanics may be supplied without turning fixture material into LAB-099 semantic authority.

## Source audit

`GenerationDescriptor` identity and transition proofs bind provider id, generation, verification-key identity and old/new MACs. `DurableProviderHistory.verify_durable()` requires the bootstrap plus every contiguous generation and transition through the current head.

`SignedAnchorProvider.increment()` retains a request result in `_request_results`; `reconcile_increment()` later emits a fresh authenticated `RECONCILE` observation for that retained result. `AttestationVerifier` authenticates the observation with the current `(provider_id,generation)` key.

Critically, the historical receipt `stable_binding` and shared-anchor `_stable_receipt` do **not** include the fixture key, signature, challenge, or observation kind. They are SHA-256 over exactly:

- provider id;
- generation;
- position;
- request id.

Therefore the already frozen stable receipt is reproducible with arbitrary deterministic test-only keys **without those keys becoming semantic authority**, provided the witness only asserts equality to the independent frozen receipt/head and never derives replacement LAB-099 vectors from its keys.

## Decision

Add a test-only, non-authoritative execution witness in PR #186:

`experiments/provider_generation_history/tests/lab099_confirmed_execution_witness.py`

The witness:

1. deterministically derives fixture-only keys for `provider-alpha` generations 1..8;
2. constructs the complete g1..g8 descriptor/transition chain using the existing `GenerationDescriptor` / `DurableProviderHistory.make_transition` contract;
3. can install that chain through normal `DurableProviderHistory.rotate()` operations and verify it with `verify_durable()`;
4. instantiates the existing `SignedAnchorProvider` at generation 8 / position 41;
5. executes the frozen request id through existing increment then reconcile mechanics;
6. requires the resulting historical stable binding to equal the independently frozen receipt `ead923...30b4`;
7. requires the already frozen CONFIRMED entry to hash to `45c53d...0dda`.

The witness exports no new LAB-099 semantic bytes and is not production code.

## Validation actually executed in this run

- direct repository clone/materialization was probed first and failed before repository execution with `Could not resolve host: github.com` (exit 128);
- the newly authored witness source passed local `python -m py_compile` before publication;
- local `git hash-object` of the exact authored file was `454e76cb3059353d041ba83f81dc11b9eec45b5c`, exactly matching the GitHub blob after publication;
- an independent local calculation reconfirmed that `(provider-alpha, 8, 42, frozen request id)` hashes to the frozen stable receipt `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`.

No exact repository import/execution of the published witness occurred, so this is not a LAB-099 repository RED/GREEN claim.

## Next prerequisite discovered

The execution witness solves provider-history/key/request-result mechanics, but a full `HistoricalSharedAnchorLedger.verify_durable()` reference database at predecessor position 41 also requires a legitimate contiguous shared-anchor prefix for positions 1..41. Merely setting `shared_anchor_meta.reserved_position=41` would fail the ledger's invariant `len(rows) == reserved` and would fabricate durable history.

The next safe fallback is therefore to source-audit and, if coherent, add a **test-only prefix builder** that uses existing supported shared-anchor execution mechanics to create positions 1..41 under the witness provider, rather than inserting synthetic history rows. The frozen LAB-099 intent remains position 42 and must still reproduce the exact frozen request/receipt/head identities.

Production LAB-099 behavior remains forbidden until an actual executable RED is observed.
