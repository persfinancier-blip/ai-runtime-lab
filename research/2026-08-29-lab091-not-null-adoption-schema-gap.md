# LAB-091 — weakened NOT NULL adoption schema gap

Date: 2026-08-29

## Finding

`CREATE TABLE IF NOT EXISTS` does not repair field-domain constraints on a preexisting legacy table. LAB-091 had begun validating identity PK/UNIQUE structure and existing row values, but a clean legacy database could still omit canonical `NOT NULL` declarations on non-identity fields and be accepted at first adoption.

The concrete case is `shared_anchor_intents.component_id`. The canonical LAB-080 schema declares it `TEXT NOT NULL`. On a legacy table where that declaration is weakened to plain `TEXT`, a crafted one-shot `intent-insert` permit can exactly match the row token for `component_id=NULL`; the v3 current-tail/provider trigger does not reject the NULL component, and the v4 deterministic request-id UDF deterministically hashes JSON `null`. Therefore the current v2/v3/v4 trigger stack can accept a PREPARED row containing a state that the canonical schema itself forbids.

## Executed reproduction

A local SQLite mechanism probe reproduced the exact relevant semantics from the published LAB-091 trigger/UDF code:

- one-shot permit consumption bound to the exact intent row token;
- v2 exact intent-insert guard;
- v3 current-tail/current-provider guard;
- v4 deterministic request-id guard;
- canonical provider head/generation and metadata tail;
- only `component_id NOT NULL` removed from the intent table.

The insert of `intent-null-component` with `component_id=NULL` succeeded and persisted as PREPARED inside the transaction when its request ID was computed over the same NULL value. This demonstrates a future-state gap, not merely a schema-text difference.

## Fix

Added `experiments/mutable_shared_anchor_writer/adoption_schema_domains.py` and wired it into `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._install_guards()` before existing-row adoption validation. The new admission check requires canonical `NOT NULL` declarations for the mutable shared-anchor fields whose canonical schemas require them:

- `shared_anchor_meta.reserved_position`;
- intent `component_id`, `intent_type`, `payload_digest`, `provider_id`, `provider_generation`, `predecessor_position`, `position`, `request_id`, `status`;
- `component_anchor_watermarks.position`.

Identity TEXT PRIMARY KEY columns are intentionally not included in this first slice because SQLite rowid-table `TEXT PRIMARY KEY` reports `notnull=0` even for the canonical schema; their NULL identity behavior is separately constrained by exact permit identity handling and the identity-contract validator.

## Validation

Focused regression executed locally before publication:

- canonical schema accepted;
- clean database with only `component_id NOT NULL` removed rejected;
- 2/2 unittest methods PASS.

The locally executed files were Git-blob hashed before publication, and post-publication re-fetch matched exactly:

- `adoption_schema_domains.py`: `1abef5360fc57f5a863e8665556cbdb9dee6f012`;
- `test_adoption_schema_domain_regression.py`: `4b00c0953f1c8095b7432aa78a1c2cb8041d0350`.

Published commits on `lab/091-mutable-shared-anchor-writer`:

- helper: `620fda8a0c022d1d0074fbd4cc1b4f7fa3f61664`;
- regression: `ff3134924ebd020fa19713bf90d5eecf42a756a6`;
- final supported-class wiring: `5b720fba666d8e412d04ae77ad7e7dc640a93637` (`history_bound_operation_scoped.py` blob `69c6b1070b1f65bb7c00b31a5c3cfce1c5d4a51f`).

This is focused mechanism/regression evidence, not the complete LAB-091 real-stack acceptance gate.

## Next gate

Re-run the prior adoption identity/index/collation suites together with this new schema-domain regression against the new branch head, then resume the exact real LAB-080/LAB-082 timeout-after-commit/UNKNOWN and two-worker/crash supported-surface gate.
