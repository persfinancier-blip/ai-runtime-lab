# LAB-099 exact orchestration import-closure audit

Date: 2026-09-13

## Scope

Source-audit the smallest repository byte closure required to execute the test-only `lab099_confirmed_orchestration_witness.execute_frozen_confirmed_orchestration()` gate at PR #186 head `766434563a5ad82a88156687c84de9c9e17b14c6`.

No production LAB-099 implementation is introduced by this note.

## Runtime observation

The GitHub connector can read exact files/blobs at the pinned head, but this run still did not expose a supported byte-preserving route from those connector reads into the local execution filesystem. A direct archive/raw fallback was probed and could not be materialized through the supported download path. Therefore no exact branch import or file-backed SQLite end-to-end PASS is claimed.

## Exact closure manifest

The source-audited execution closure is the following set of repository Python blobs. A future executable runtime should materialize these exact paths from the pinned head and verify every Git blob SHA before import/execution.

### LAB-099 test-owned orchestration layer

- `experiments/provider_generation_history/tests/lab099_confirmed_orchestration_witness.py` — `71a50df5b5d8c3cece33274d5263f1c4fe0ec27a`
- `experiments/provider_generation_history/tests/lab099_shared_anchor_prefix_witness.py` — `079d42b61836294d433170d4aace867e1c03b106`
- `experiments/provider_generation_history/tests/lab099_confirmed_execution_witness.py` — `454e76cb3059353d041ba83f81dc11b9eec45b5c`
- `experiments/provider_generation_history/tests/lab099_confirmed_fixture_row_verifier.py` — `b1324194ef0f9c251ccdc747394d63b7b0a9d68a`
- `experiments/provider_generation_history/tests/lab099_confirmed_ledger_reference.py` — `69b1bfeda67c43fbf2a7ed3361c08495a94a8a5e`
- `experiments/provider_generation_history/tests/lab099_cutover_storage_reference.py` — `89c796b6dd59d5ca9490cfa0b8e7803a76cf7b1f`
- `experiments/provider_generation_history/tests/lab099_precursor_fixture_adapter.py` — `671ace9ed879a0a1d0c06786b11d2e46fb746de3`
- `experiments/provider_generation_history/tests/lab099_precursor_fixture_vectors.py` — `73406169990849327774fc46682747a14222bd9d`
- `experiments/provider_generation_history/tests/lab099_prepared_cross_binding_reference.py` — `1979346f2372f7daf8a0a2dcc31743ab22e50c1a`
- `experiments/provider_generation_history/tests/lab099_precursor_reference_vectors.py` — `d1757fa667b8ab7ce4ea1b6ae27136f594716511`
- `experiments/provider_generation_history/tests/lab099_precursor_relation_reference.py` — `41f1fa650fa4554d44710fc1e717090e620e533b`

### Existing production/test substrate imported by the witness

- `experiments/anchor_attestation/protocol.py` — `15d8b7cf8ff093490ccb75679030d3a0fe41e401`
- `experiments/provider_generation_history/activation.py` — `fbc8cb4f581221c8b8755a43c436e4d6be74c7a7`
- `experiments/provider_generation_history/integration.py` — `bd3f093637b4c619709bdc2d289af17417202697`
- `experiments/provider_generation_history/protocol.py` — `c2077635aa2ecebf9a3072d97efeacb37cb0d478`
- `experiments/provider_generation_history/supported.py` — `8140d6e180c3e97085830b872cea7d87f8433144`
- `experiments/shared_anchor_intent_ledger/protocol.py` — `fd22bc30f6aacdfd157557c8b458d9f7b0b3bda8`
- `experiments/shared_anchor_intent_ledger/supported.py` — `22a05c04831f65c1d7fe9077df3bb780c4008e09`

## Audited import edges

Observed exact source imports establish these critical edges:

1. orchestration -> provider-generation `HistoricalReceipt` + confirmed-row verifier + confirmed ledger reference + storage oracle + precursor adapter + legitimate-prefix witness;
2. legitimate-prefix witness -> anchor attestation + supported historical ledger + execution witness + confirmed ledger reference + shared-anchor `Intent`;
3. execution witness -> anchor attestation + provider-generation protocol + confirmed ledger reference + storage oracle;
4. confirmed-row verifier -> storage oracle + PREPARED cross-binding oracle;
5. PREPARED cross-binding oracle -> storage oracle + precursor reference authority;
6. fixture adapter dynamically imports precursor relation reference + executable fixture vectors;
7. fixture vectors -> confirmed bridge + storage oracle + precursor authority + relation reference;
8. supported historical ledger -> anchor attestation + activation + integration + provider-generation protocol + shared-anchor protocol/supported;
9. integration -> anchor attestation + provider-generation protocol + shared-anchor protocol/supported.

The listed closure is intentionally source-level and minimal for this gate; repository-wide tests, README files and unrelated expected-failure seeds are not part of this exact orchestration execution closure.

## Required executable gate

On the first runtime that can materialize the exact blobs above:

1. verify each file with `git hash-object` against this manifest;
2. run `python -m compileall` over the materialized closure;
3. import `lab099_confirmed_orchestration_witness` from the exact closure;
4. call `validate_orchestration_contract_shape()`;
5. create a fresh file-backed SQLite database and call `execute_frozen_confirmed_orchestration(path)`;
6. require exact result identities:
   - request `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`;
   - receipt `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`;
   - confirmed position `42`;
   - confirmed head `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`;
   - final `HistoricalSharedAnchorLedger.verify_durable()` success;
7. only after that observed executable gate may LAB-099 production RED/GREEN work begin.

## Decision

`LAB099_EXACT_ORCHESTRATION_IMPORT_CLOSURE_V1_FROZEN`.

This manifest is a reproducibility aid, not execution evidence. Production `activation_reservation_provenance` remains forbidden until the exact closure executes and an actual RED is observed.
