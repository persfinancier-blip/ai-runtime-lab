# LAB-019 — Cross-version kernel migration and rolling-upgrade conformance

Date: 2026-08-19

## Donors

1. Protocol Buffers schema evolution: field numbers are durable wire identity, must not be reused, and evolution is classified as wire-safe, conditionally compatible, or unsafe. Compatible-but-lossy changes require managed rollout. Primary: https://protobuf.dev/programming-guides/proto3/
2. Kubernetes API deprecation/versioning: simultaneously served versions must round-trip without information loss; preferred/storage version does not advance until a release supports both old and new representations. Persisted older versions remain decodable/convertible. Primary: https://kubernetes.io/docs/reference/using-api/deprecation-policy/
3. SQLite application schema metadata: `PRAGMA user_version` is application-owned, while SQLite's internal `schema_version` is maintained by SQLite and should not be repurposed. Primary: https://www.sqlite.org/pragma.html

## Policy

Compatibility outcomes are explicit: **ACCEPT / MIGRATE / TRANSLATE / REJECT**.

Four independent version axes must not be collapsed: storage schema version; action/protocol version; artifact/evidence version; worker/migration epoch.

A compatible V1→V2 migration preserves work identity, phase semantics, idempotency/effect key, external receipt, evidence identity and artifact version. It atomically advances migration epoch, worker epoch, fence and generation. Unknown future versions hard-reject. Old action traces require explicit deterministic translation; removed actions without mapping reject.

## Unsafe baseline

The seeded unsafe migrator rewrites `effect_key` and `evidence_id` and does not advance migration epoch/fence. The retained expected-failure test demonstrates semantic corruption even though the structure appears successfully upgraded.

## Observed local evidence

- unsafe migration test: FAIL as intended because durable external identities changed;
- corrected reference + SQLite conformance suite: **15/15 passed**;
- `python -m compileall -q experiments/versioned_kernel`: passed.

Scenarios include V1→V2 preservation, future rejection, rolling overlap, old-worker fencing, transactional crash/retry, identity preservation, action translation/rejection, and reference/SQLite post-migration conformance.

## Production implications

New workers may consume old durable state only through an explicit compatibility/migration layer. Migration epoch/fence must be committed atomically with authoritative schema transition. Rolling upgrades need an overlap window in which new code understands old state before new storage semantics become authoritative. Stored first-divergence/action traces require their own protocol version and deterministic translator; never reinterpret old action names under new semantics.

## Non-goals

No general migration framework, deployment controller, distributed consensus protocol, or claim that SQLite represents PostgreSQL locking behavior. PostgreSQL-specific migration/locking validation remains deferred until a representative runtime exists.
