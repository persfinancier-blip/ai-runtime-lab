# LAB-099 — historical activation rows are structurally valid but not transition-bound

Date: 2026-09-02

## Context

Source audit target: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`.

LAB-090 persists `provider_generation_activations` with `activation_id`, `new_generation_id`, `provider_id`, `generation`, `expected_position`, `fence`, and `status`. Startup `_verify_activation_records()` validates each row structurally, but for historical `COMMITTED` rows it has no external provider state to compare against and no authenticated transition payload that commits to the original activation ticket fields.

This is distinct from LAB-098, which covers a row being deleted entirely. LAB-099 covers a row remaining present while its ticket evidence is coherently rebound.

## Source finding

Current `_verify_activation_records()` proves only that:

- `new_generation_id` resolves to an existing provider generation;
- provider/generation/key reconstruct that generation id;
- `expected_position` is a non-negative exact integer;
- `activation_id == provider-activation:<generation_id>:<expected_position>`;
- `fence` is a positive exact integer;
- status is `SQL_COMMITTED` or `COMMITTED`;
- historical rows are not left `SQL_COMMITTED`.

It does **not** prove that the persisted `expected_position`, `fence`, or derived `activation_id` are the exact values returned by the provider when that generation transition was prepared. Provider-generation transition proofs authenticate generation continuity, but their payload does not contain the LAB-090 activation ticket fields.

For the current generation a rewritten ticket will normally be exposed when recovery asks the live `FencedActivationProvider` for `activation_status(ticket)`. Historical `COMMITTED` rows receive no equivalent check; after rotation moves past them, the original provider reservation state is no longer the durable verifier for those fields.

## Isolated relational probe

A file-backed SQLite probe mirrored the current `_verify_activation_records()` predicates:

1. create valid provider generations g1 and g2;
2. retain durable head g2;
3. create a legitimate g2 `COMMITTED` activation row with `expected_position=7`, `fence=4` and the matching deterministic activation id;
4. rewrite the same row coherently to `expected_position=999`, `fence=12345`, and recompute `activation_id` from the new position;
5. re-run the current structural predicates.

All predicates evaluated true:

- generation identity: true;
- expected position exact/non-negative: true;
- activation id matches the rewritten fields: true;
- fence exact/positive: true;
- status allowed: true.

This is isolated query/semantic evidence, not claimed exact repository behavioral execution.

## Security / correctness consequence

The activation row is intended to be durable evidence for the provider-owned fencing handoff. If historical rows can be rewritten to another internally consistent ticket, durable history proves only that *some syntactically valid ticket-shaped row* exists, not that the recorded ticket is the one that authorized the transition.

That weakens LAB-098's future completeness check: requiring exactly one activation row per authenticated provider-generation transition is insufficient unless the contents of that row are also authenticated/bound to the transition.

## Regression-first contract

Establish a valid g1 -> g2 -> g3 sequence under LAB-090, then while g3 is current:

- mutate historical g2 `COMMITTED` activation `expected_position`;
- recompute its deterministic `activation_id` so the row remains internally consistent;
- mutate `fence` to another positive integer;
- leave provider generation descriptors, transition proofs, head, shared-anchor history, and row status intact.

Pre-fix: demonstrate restart/history verification accepts the coherently rebound historical ticket.

Post-fix: fail closed before provider or SQLite mutation, leaving the tampered row unchanged.

Also test one-field mutations independently and the fully coherent multi-field rewrite.

## Design constraint

Activation ticket provenance must be authenticated by authority independent of the mutable activation row itself. Candidate designs should bind the exact activation ticket (or a canonical digest containing `new_generation_id`, provider/generation, `expected_position`, `activation_id`, and fence/provenance) into the authenticated provider-generation transition/handoff evidence at creation time.

Do not fix this by hashing fields into another column in the same activation row: that remains self-asserted and rewritable. Do not reconstruct historical ticket contents from current runtime state.

Compose with:

- LAB-090/#169 — provider-owned activation fencing and ordering;
- LAB-092/#176 — activation schema provenance;
- LAB-097/#182 — provider-history deletion/rebootstrap provenance;
- LAB-098/#183 — activation-record completeness/deletion.

## Status

READY — source-proved and isolated relational semantics reproduced. Exact repository RED/GREEN pending. LAB-086 remains priority #1.
