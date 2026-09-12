# LAB-099 CONFIRMED ledger-reference bridge

Date: 2026-09-13

## Context

`state/CURRENT.md` froze `LAB099_CONFIRMED_LEDGER_REFERENCE_BRIDGE_REQUIRED_V1`: the test-owned CONFIRMED provenance vector had a synthetic resulting provenance-head digest, while `lab099_cutover_storage_reference.confirmed_head_digest(entry)` derives authority from a concrete CONFIRMED shared-anchor ledger entry including the reauthenticated receipt binding. No byte-exact bridge existed between those surfaces.

LAB-086 remains priority #1. In this run direct `git clone --no-checkout` failed before repository execution with `Could not resolve host: github.com` (exit 128), so no new LAB-086 executable evidence is claimed. The supported fallback was therefore limited to PR #186 test-owned LAB-099 work.

## Source audit

Pinned LAB-092 `experiments/shared_anchor_intent_ledger/protocol.py` already defines all CONFIRMED receipt authority needed by LAB-099:

- request identity is SHA-256 over canonical JSON of `position`, `intent_id`, `component_id`, `intent_type`, and `payload_digest`;
- `_stable_receipt()` is SHA-256 over canonical JSON of `provider_id`, `generation`, `position`, and `request_id` from a verified `RECONCILE` observation;
- CONFIRMED reauthentication requires the current provider generation, exact position/request identity, and equality with persisted `receipt_binding`.

Therefore LAB-099 must not invent another receipt/authenticator mechanism.

## Frozen reference bridge

Added test-only `lab099_confirmed_ledger_reference.py` on PR #186.

Exact reference CONFIRMED ledger entry:

- provider: `provider-alpha`, generation `8`;
- predecessor position `41`, position `42`;
- intent id: `migration:provider-activation-reservation-precursor-cutover:v1:77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e`;
- payload digest: `8aee140ac30142fac83fe03f95f36e56be94583b4ef100060610bb9ec59089e9`;
- request id: `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`;
- stable RECONCILE receipt binding: `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`;
- `confirmed_head_digest(entry)`: `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`.

### Mapping decision

`LAB099_CONFIRMED_LEDGER_REFERENCE_BRIDGE_V1_FROZEN`:

1. CONFIRMED provenance field 7 equals `confirmed_head_digest(entry)` **directly**. There is no second deterministic provenance-head transform.
2. Resulting provenance epoch is predecessor epoch + 1. The frozen reference maps `7 -> 8`.
3. The previous `c0..df` field-7 value in `lab099_precursor_reference_vectors.py` is retained only as a historical synthetic vector until the executable CONFIRMED fixture/event layer is switched to the bridged vector; it is not authority.
4. The bridged CONFIRMED canonical bytes are frozen separately in the new oracle, with digest `e7f7083876141f73cc7e8adc88b39c5e6da7f9c10a83433d2a067588c54ae157`.

This choice minimizes authority surfaces: a verified CONFIRMED ledger row plus its existing RECONCILE receipt is the single head input. Adding a second transform would add semantics without independent security value.

## Validation actually executed

- local `python -m py_compile /tmp/lab099_confirmed_ledger_reference.py`: PASS;
- locally recomputed request id, stable receipt, confirmed-head digest, bridged CONFIRMED canonical bytes and SHA-256 digest;
- post-publication local `git hash-object` of the exact authored file: `69b1bfeda67c43fbf2a7ed3361c08495a94a8a5e`, equal to the GitHub blob;
- PR #186 remains draft/test-only; after the write it is ahead 20 / behind 0 relative to pinned PR #177 head and all changed files remain under `experiments/provider_generation_history/tests/`.

The module was not imported against the complete repository closure in this run, so this is reference-oracle evidence, not repository RED/GREEN.

## Next engineering slice

With the bridge frozen, the next safe fallback is test-only:

1. add `confirmed_event_plan()` using the exact reference entry/receipt/head/epoch bridge;
2. add a non-discoverable persisted CONFIRMED RED-intent suite;
3. isolate mutations for receipt binding, confirmed position, confirmed head, and exact PREPARED-digest ancestry;
4. keep production `activation_reservation_provenance` forbidden until exact repository execution is available and an actual RED is observed.
