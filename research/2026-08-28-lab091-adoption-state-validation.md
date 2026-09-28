# LAB-091 — adoption-time validation of preexisting mutable state

Date: 2026-08-28

## Finding

The final LAB-091 v2/v3/v4 trigger stack constrains future SQL statements, but triggers cannot retroactively prove that rows already present before first LAB-091 adoption were created by the supported state machine.

The inherited LAB-082 durable verifier already proves ledger continuity, current-provider binding for PREPARED state, Ed25519 receipt authenticity, confirmed receipt binding and basic watermark bounds. Two LAB-091-specific invariants were not covered at adoption time:

1. existing `shared_anchor_intents.request_id` must equal the deterministic LAB-080 request identity derived from `(position,intent_id,component_id,intent_type,payload_digest)`;
2. every existing `asymmetric_provider_receipts.request_id` must be owned by some shared-anchor intent. A legitimate crash window may leave `PREPARED + matching receipt`, so receipt presence for PREPARED state is allowed; orphan receipts are not.

Without adoption validation, a preexisting non-deterministic PREPARED request could be grandfathered when LAB-091 guards are installed, and a preexisting orphan authenticated receipt could remain outside the new receipt state machine.

## Fix

Added `experiments/mutable_shared_anchor_writer/adoption_validation.py` with `validate_existing_mutable_state_locked(q)`.

The helper is invoked from the final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._install_guards()` inside the same `BEGIN IMMEDIATE` transaction that installs the v2/v3/v4 persistent triggers. Guard installation therefore commits only if the preexisting mutable state already satisfies the LAB-091 adoption invariants.

The helper deliberately does not duplicate LAB-082 verification. It adds only invariants introduced by LAB-091 that persistent triggers cannot enforce retroactively.

## Exact evidence

Published blobs used in the focused execution:

- `operation_permit.py` — `637784a5cb61a024a1df3e0e983887b6d0a838be`
- `state_machine_udfs.py` — `8c1d6d0cd075285aed3a90ac337b60b60c1d608b`
- `adoption_validation.py` — `d96c5656273cdfd42250ccd55456c10110eb4a20`
- `test_adoption_validation.py` — `1a5b397a05d61845ca183cf476ee32db5e8def3c`
- final wiring `history_bound_operation_scoped.py` — `4bdf64fa714cbe0d5598ac9a702dd60edd97a112`

Local `git hash-object` matched all four executed files exactly. Focused regression result: **5/5 PASS**. `compileall` for `experiments/mutable_shared_anchor_writer` also passed.

Covered cases:

- valid existing deterministic PREPARED state is adoptable;
- non-deterministic existing request ID is rejected;
- orphan existing provider receipt is rejected;
- legitimate crash-state `PREPARED + matching request receipt` remains adoptable;
- adoption validation requires an active transaction.

## Boundary

This is focused exact-published evidence for the adoption validator and its wiring. It does not replace the still-required full LAB-080/LAB-082 supported-surface concurrency/UNKNOWN/restart gate for PR #173.
