# LAB-099 legitimate shared-anchor prefix witness

Date: 2026-09-13

## Scope

This note records the source audit and test-only fallback used after the required LAB-086 materialization probe again failed before repository execution with `Could not resolve host: github.com`.

No LAB-086 PASS and no LAB-099 repository RED/GREEN PASS is claimed.

## Source audit

Pinned LAB-092 base: `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.

`SharedAnchorLedger.execute()` first reserves one exact contiguous position, advances the attested provider using `catch_up_one`, reauthenticates the resulting request via `RECONCILE`, and only then changes the durable row from PREPARED to CONFIRMED with a stable receipt binding.

`HistoricalSharedAnchorLedger.verify_durable()` additionally requires:

- `len(shared_anchor_intents) == shared_anchor_meta.reserved_position`;
- positions to be contiguous from 1 through the durable tail;
- every CONFIRMED row to have a corresponding authenticated historical provider receipt;
- at most one PREPARED row, and only at the tail.

Therefore setting only `reserved_position=41` or inserting raw synthetic rows would fabricate history and is not an acceptable fixture path.

## Selected mechanism

A legitimate non-authoritative prefix can be built through the supported APIs:

1. install the existing fixture-only provider history g1..g8 using `DurableProviderHistory.rotate()`;
2. instantiate the g8 provider at position 0 using the same deterministic execution-witness key;
3. construct `SupportedHistoricalSharedAnchorLedger` over that durable current g8 head;
4. execute 41 deterministic `archive_checkpoint` intents through `ledger.execute()`;
5. require every row to finish CONFIRMED and contiguous;
6. require `ledger.verify_durable()` to succeed;
7. require durable tail=41, row count=41, PREPARED count=0, and an authenticated provider read at position 41.

The 1..41 prefix payloads are execution mechanics only. They do not derive or alter the frozen LAB-099 PREPARED/CONFIRMED semantic authority. The frozen position-42 request id depends on position plus the position-42 intent identity/content, not on the content of earlier rows.

## Implementation

Added test-only:

`experiments/provider_generation_history/tests/lab099_shared_anchor_prefix_witness.py`

Branch commit: `d810fae3b2c47d0f733bfb23d5cc1dcf4b20fcde`.

Published blob: `079d42b61836294d433170d4aace867e1c03b106`.

Observed local checks before publication:

- `python -m py_compile` PASS;
- local `git hash-object` = `079d42b61836294d433170d4aace867e1c03b106`, exactly matching the published GitHub blob.

The full builder was not imported/executed because the exact repository import closure is not locally materialized in this runtime. Accordingly, there is still no persisted CONFIRMED end-to-end execution claim.

## Audit boundary

The builder performs no raw insertion into `shared_anchor_intents` and no direct mutation of `shared_anchor_meta`. It uses fixture-only provider keys solely to exercise existing mechanics and never exports them as LAB-099 semantic authority.

## Next prerequisite

After the next mandatory LAB-086 materialization probe, if the exact closure is still unavailable, source-audit and stage one test-only orchestration helper that composes:

`legitimate prefix 1..41 -> frozen atomic PREPARED at 42 -> existing provider increment/RECONCILE -> frozen confirmed_event_plan -> persisted CONFIRMED verifier`

The helper must not synthesize request/receipt/head authority and must refuse any divergence from the already frozen position-42 identities. Execute it only when the complete exact import closure can be materialized. Production LAB-099 remains forbidden until executable RED is observed.
