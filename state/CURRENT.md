# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-075 — authenticate and persist the mapping from logical `sink_id` to the concrete adapter/code profile and endpoint/origin used by LAB-074, so a caller cannot satisfy capability binding while substituting a different implementation or destination.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-074.
- Active: Issue #141 / LAB-075 — IN_PROGRESS.
- Active branch: `lab/075-sink-registry-binding-v2` (current with main; original `lab/075-sink-registry-binding` is one commit behind).
- Active PR: none yet.

## Last completed step

Inspected the exact merged LAB-074 `experiments/transactional_broker_journal/capability.py` blob `0cfe0e2e555a234df96393abdf3e14b75ccff2f6`. The unresolved boundary is confirmed: `CapabilityBrokerWorker._assert_sink_binding()` checks only the logical sink string, then `_reconcile()` / `process()` invoke the caller-supplied sink object.

Defined the smallest LAB-075 registry identity: authenticated `(sink_id, registry_generation, adapter_digest, canonical_endpoint_origin, operation_profile, predecessor_entry_digest)` plus issuer identity/generation. New reservations must persist exact entry digest/generation and serialize registry-head verification with request insertion in the same SQLite authority boundary.

The audit found an important design correction before code integration: a free-form `reconciliation_lineage` label is not sufficient authority for historical UNKNOWN reconciliation. An unrelated successor could reuse the label. Compatibility must bind to the exact predecessor entry digest (or an explicit signed historical digest set). Therefore endpoint rotation may reconcile an old UNKNOWN only through a signed successor that explicitly names the historical entry; it may never re-execute that old reservation. CONFIRMED remains receipt-only.

The local execution sandbox reset before the first prototype test run completed, so no code/test success is claimed for this run. Issue #141 records the design evidence and exact limitation.

## Evidence produced

- Exact audited LAB-074 capability blob: `0cfe0e2e555a234df96393abdf3e14b75ccff2f6`.
- Current main: `df007058e0ca765d5b20ed69a628fc3bbee979d7`.
- `lab/075-sink-registry-binding-v2` is identical to current main and is the correct implementation branch.
- Original LAB-075 branch is behind main by one commit.
- Issue #141 updated with the concrete trust-boundary finding, minimal registry schema and predecessor-digest reconciliation rule.

## Known blockers / constraints

- No owner/product blocker.
- Local Python execution reset during prototype execution in this run; treat as transient and retry next run.
- LAB-075 must reuse rather than duplicate LAB-022–025 transport/destination enforcement.
- Python object identity is not production code identity; use stable declared adapter/profile digest in the reference experiment and document production signed artifact/build identity requirement.
- Universal exactly-once external effects and distributed registry consensus remain non-goals.

## Exact next action

Resume Issue #141 on `lab/075-sink-registry-binding-v2`. Implement the authenticated registry with exact predecessor-entry-digest lineage, unsafe string-only baseline, durable registry head and reservation binding. Run the minimum 12-case failure matrix, especially attacker adapter, endpoint substitution, rollback, same-generation substitution, head-change race, old INTENT after rotation, UNKNOWN compatible/incompatible successor, CONFIRMED after rotation and durable relational corruption. Then integrate it behind `CapabilityBoundJournal`, run LAB-074/LAB-073/LAB-072 regressions, perform a separate patch audit, and only then open/integrate a PR.

## Backlog

- #141 / LAB-075 — authenticated sink-adapter and endpoint registry binding — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
