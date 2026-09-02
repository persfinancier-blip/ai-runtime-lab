# LAB-098 follow-up — surplus bootstrap activation row is accepted structurally

Date: 2026-09-02

## Context

PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`) verifies rows already present in `provider_generation_activations`, but the verification relation is activation-row -> provider-generation only. It does not derive the exact activation-row set from authenticated provider-generation transitions.

LAB-098/#183 already records the missing-row direction: a required activation row can be deleted and omission is not detected. This note records the dual surplus-row direction.

## Source observation

`SupportedHistoricalSharedAnchorLedger._verify_activation_records()` accepts an activation row when:

- `new_generation_id` resolves to an existing provider generation;
- the row's provider/generation/key reconstruct the same `GenerationDescriptor` identity;
- `expected_position` is a non-negative exact int;
- `activation_id == provider-activation:<generation_id>:<expected_position>`;
- `fence` is a positive exact int;
- status is `SQL_COMMITTED` or `COMMITTED`;
- only historical `SQL_COMMITTED` rows are additionally rejected.

There is no predicate requiring that `new_generation_id` is the target of an authenticated provider-generation transition. Therefore the bootstrap generation, which by definition has no predecessor transition and should not have a LAB-090 handoff activation, can carry a structurally valid `COMMITTED` activation row.

## Isolated relational probe

A file-backed SQLite probe mirrored the current verifier predicates:

1. Insert one valid bootstrap provider generation `g1`.
2. Insert no provider-generation transition.
3. Insert activation row:
   - `new_generation_id = g1`;
   - `provider_id/generation` matching g1;
   - `expected_position = 0`;
   - deterministic activation id `provider-activation:<g1>:0`;
   - `fence = 1`;
   - `status = COMMITTED`.
4. Evaluate the current structural predicates.

Observed result: every current predicate evaluated true.

This is an isolated relational/query reproduction, not an exact PR behavioral PASS/FAIL claim.

## Why this matters

The activation table is not merely passive history. Constructor recovery consults the current generation's activation row. A surplus current-generation row can therefore alter restart behavior despite there being no authenticated provider-generation transition that required that handoff evidence. At minimum this creates an unauthenticated fail-closed/availability surface; depending on matching provider-side activation state, recovery paths can also attempt release/reconciliation operations for evidence that was never authorized by provider-generation history.

This is the set-completeness dual of the deleted-row flaw: accepting exactly all transition-governed activations requires both no omissions and no extras.

## Regression-first contract extension for LAB-098

Add a surplus-row case before production changes:

- construct a legitimate bootstrap-only history g1 with no provider-generation transition;
- inject a structurally valid `COMMITTED` activation row for g1;
- pre-fix: demonstrate `_verify_activation_records()` does not reject the surplus row;
- post-fix: fail closed before provider/SQLite mutation.

Also cover a surplus activation row for any provider-generation record that is not the target of the LAB-090-governed transition relation used to derive activation provenance.

## Design constraint

Derive the expected activation relation from authenticated provider-generation transition history and require a bijection:

- every LAB-090-governed transition has exactly one activation record; and
- every activation record corresponds to exactly one such authenticated transition.

The bootstrap generation must not acquire activation provenance merely because a syntactically valid row references its generation descriptor.

This composes with LAB-099: after set completeness/bijection is established, exact ticket contents still need independent authenticated binding.
