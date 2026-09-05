# Post-re-root trust epoch / effect namespace migration V1

Status: `POST_REROOT_TRUST_EPOCH_EFFECT_NAMESPACE_MIGRATION_V1_FROZEN`

Date: 2026-09-05

## Problem

LAB-093's application-idempotency safety contract normally requires exact durable evidence that a historical application key has never been consumed before allowing a new external side effect. The DR contracts already require fail-closed behavior when an authority-required consumed-key/archive epoch is unavailable or cannot be authenticated.

A harder case remains after a human re-root ceremony: the system may have a legitimate operational need to resume future work even though a bounded historical idempotency epoch is provably irrecoverable. Human signatures can establish a new future trust root, but they cannot recreate missing historical non-reuse evidence.

This contract defines the only V1 mechanism by which future execution could be made technically separable from the sealed historical namespace. It does **not** authorize the cutover itself. Activating such a cutover abandons an unprovable portion of historical non-reuse protection and is therefore a genuine product/security decision requiring explicit human-owner authorization.

## Safety thesis

Never reinterpret an old application key under the old effect namespace as `MISS`.

If future effects are deliberately resumed, they occur only in a new one-way trust/effect epoch whose operation identity is cryptographically/domain-separated from every prior epoch. The old namespace remains permanently `SEALED_HISTORY_INCOMPLETE` and continues to fail closed forever.

A new epoch is not a repair of the old one. It is a new authority domain with an explicit, durable discontinuity marker.

## Canonical identities

Every effect-capable request is bound before admission to:

- `principal_id`;
- logical `application_namespace_id`;
- `trust_epoch_id`;
- `effect_namespace_id`;
- caller application idempotency key;
- canonical operation identity / operation digest;
- current authorization/policy generation.

V1 operation/effect identity MUST include `trust_epoch_id` and `effect_namespace_id` in the canonical signed/authenticated payload. A legacy key such as `invoice/123` in epoch E0 and the same text in E1 are therefore not the same runtime idempotency identity.

The API/runtime MUST NOT silently inject a current epoch for callers that omit epoch-aware semantics after a discontinuity. Post-cutover clients must either negotiate the new epoch explicitly or use a protocol version whose canonical identity unambiguously includes it.

## States

Historical namespace states:

`ACTIVE -> SEALED_HISTORY_INCOMPLETE`

There is no transition back to `ACTIVE`, `MISS_CAPABLE`, or an equivalent state.

Migration states:

`PROPOSED -> SECURITY_AUTHORIZED -> CUTOVER_PREPARED -> EXTERNAL_CUTOVER_ANCHORED -> PROVENANCE_COMMITTED -> VERIFIED -> ACTIVE`

Any failure before `ACTIVE` leaves the new epoch non-effect-capable. The old epoch remains sealed throughout.

## Required authorization boundary

Creating draft migration metadata is ordinary maintenance. Transition to `SECURITY_AUTHORIZED` requires a distinct product/security authorization that is not satisfiable by ordinary admin, provider, worker, storage, broker-worker, or DR-recovery credentials alone.

The authorization payload MUST bind at least:

- exact old `trust_epoch_id` and `effect_namespace_id` being sealed;
- exact reason/classification of historical evidence loss;
- strongest surviving authenticated historical checkpoint and all known gaps;
- exact new `trust_epoch_id` and `effect_namespace_id`;
- principal/application namespace scope;
- policy version and canonical encoding version;
- declared external systems/effect classes covered by the cutover;
- rollback prohibition;
- human/security authorization identity and threshold required by policy.

No generic `force`, `repair`, `ignore_history`, or disaster-recovery admin flag is equivalent.

## External side-effect cutover evidence

Namespace separation inside SQLite is insufficient when the external system itself has no epoch-aware idempotency boundary.

Before `EXTERNAL_CUTOVER_ANCHORED`, each effect class MUST have one of:

1. an external provider idempotency namespace/account/version token that includes the new epoch; or
2. a durable broker-controlled request identity passed to the provider whose canonical value includes the new epoch and which cannot collide with prior provider request IDs; or
3. an explicit security-approved adapter proving equivalent domain separation.

If an external effect provider deduplicates only on the raw historical application key and offers no safe epoch/domain separation, that effect class cannot be automatically re-enabled under this contract.

The cutover evidence records exact provider/account/adapter identity and the first admissible new-epoch provider request domain. It is authenticated and parent-linked to the global provenance chain.

## One-way cutover and rollback prevention

Once `PROVENANCE_COMMITTED` is externally anchored:

- the old effect namespace remains permanently sealed;
- startup rejects configuration that selects the old epoch for new effects;
- policy rollback to a pre-cutover configuration fails closed;
- restoring an older database snapshot cannot remove the discontinuity because startup must reconcile against the external/global provenance checkpoint;
- deleting the local migration row cannot make the database appear pre-migration/fresh;
- a later epoch migration creates E2; it never reuses E0/E1 identifiers.

Epoch identifiers are unique random/high-entropy or content-derived authority identifiers, not small counters accepted solely because they are numerically larger.

## Historical lookup behavior

For old epoch E0:

- exact known consumed key -> historical consumed result/tombstone semantics;
- key whose required archive coverage intersects the irrecoverable gap -> `HISTORY_INCOMPLETE`, never `MISS`;
- exact known non-consumption evidence, if such a proof exists, does not reopen E0 for effects; E0 is globally sealed after cutover.

For new epoch E1:

- only keys canonically bound to E1 are looked up in the E1 registry/archive;
- E1 must start with authenticated installation provenance and the normal LAB-093 capacity/retention/archive contracts;
- no E0 row is copied as an E1 `MISS`, `BOUND`, or `COMMITTED` row;
- optional informational cross-epoch indexes may warn that the same human-readable key existed historically, but they cannot substitute for E1 operation identity or authorize effects.

## Crash/restart ordering

Preparation order:

1. authenticate current global provenance and re-root authority;
2. prove old epoch is sealed and classify exact missing-history scope;
3. obtain explicit product/security authorization payload;
4. allocate fresh trust/effect epoch identities;
5. install the new epoch registry in non-effect-capable state;
6. establish external provider/broker cutover domain separation;
7. append/anchor `EXTERNAL_CUTOVER_ANCHORED` and then the migration provenance transition;
8. restart/re-read from durable state and independently verify old-sealed + new-installed + external-cutover evidence;
9. execute a new-epoch dry-run/recovery drill with no external mutation where possible;
10. append a separate activation transition; only then admit E1 effects.

Crash before step 7: E1 is staged/non-authoritative and effects remain disabled.

Crash after step 7 but before activation: the discontinuity is authoritative, E0 remains sealed, E1 remains non-effect-capable until recovery completes.

Crash after activation: startup re-verifies the anchored migration and current E1 registry before effect admission.

At no point is rollback to E0 an allowed recovery action.

## Principal and namespace scope

Migration authorization is scoped. A loss affecting namespace A does not authorize epoch reset for B. Conversely, a global/shared external provider domain may require a broader cutover if provider request IDs or side-effect identity are shared across namespaces.

Cross-principal reuse is forbidden unless the pre-existing product contract explicitly defines those principals as one idempotency authority domain. Migration cannot broaden that domain.

## No automatic loss threshold

V1 deliberately defines no rule such as "after N days of archive loss create a new epoch". Time, business pressure, storage failure, customer urgency, or availability SLOs are not security authorization.

The runtime may prepare evidence and a migration proposal automatically; it may not cross `PROPOSED -> SECURITY_AUTHORIZED` automatically.

## Audit/event requirements

Durable provenance must retain:

- old sealed namespace identity;
- all surviving roots/checkpoints and exact known missing ranges/epochs;
- re-root ceremony transition if applicable;
- authorization payload digest and policy identity;
- new epoch identities;
- external cutover evidence;
- registry installation/checkpoint;
- verification/drill evidence;
- activation transition;
- every later deactivation/supersession.

The discontinuity must be visible in operator/audit output. It must never be normalized into an ordinary rotation.

## RED-first matrix

At minimum implementation tests must cover:

1. old missing-history key never becomes `MISS` before migration;
2. human re-root alone does not enable effects;
3. ordinary admin cannot authorize migration;
4. worker/provider credentials cannot authorize migration;
5. fresh E1 IDs required; reuse of E0 epoch/namespace rejected;
6. raw application key equality across E0/E1 does not imply identity equality;
7. omitted epoch after discontinuity fails closed on legacy protocol;
8. E1 registry installed before authority remains non-effect-capable;
9. provider without epoch-separated request domain blocks activation;
10. provider request identity includes E1 and cannot collide with E0;
11. crash before external cutover anchor leaves all effects disabled;
12. crash after anchor/before provenance commit recovers without enabling effects;
13. crash after provenance commit/before activation leaves E0 sealed/E1 inactive;
14. deletion of local migration row detected from global/external provenance;
15. rollback database snapshot cannot reactivate E0;
16. stale policy cannot authorize cutover;
17. authorization for namespace A cannot reset B;
18. cross-principal widening rejected;
19. E0 records are not copied into E1 as synthesized state;
20. historical E0 exact consumed key remains queryable where evidence exists;
21. E0 gap returns `HISTORY_INCOMPLETE` forever;
22. restoring lost E0 archive after E1 activation improves audit/query availability but does not reactivate E0;
23. E1 ordinary idempotency retry converges normally;
24. E1 `BOUND/UNKNOWN` recovery retains normal fail-closed semantics;
25. E1 capacity exhaustion does not evict E0/E1 historical keys;
26. E1 archival compaction preserves non-reuse;
27. later E2 migration cannot reuse E0/E1 epoch IDs;
28. startup with old config selecting E0 effects fails closed;
29. split-view global provenance blocks activation;
30. missing external cutover evidence blocks activation;
31. corrupt external cutover evidence blocks activation;
32. DR restoration of a pre-migration checkpoint cannot remove cutover;
33. activation is a distinct post-verification transition;
34. audit output identifies the discontinuity as security-authorized migration;
35. no test path permits `force=true`/maintenance mode to bypass authorization.

## Donor/standards rationale

- RFC 6962 consistency proofs model a useful property for this contract: later authenticated state must extend, rather than silently rewrite, the earlier authenticated prefix. The trust-epoch transition is therefore appended as an explicit discontinuity/authority event rather than editing old history.
- NIST SP 800-57 key lifecycle guidance distinguishes active, deactivated, compromised and destroyed states and preserves attributes about historical key status. Analogously, sealing an old effect epoch stops future authorization without pretending its historical verification meaning vanished.
- Existing LAB DR/TUF-derived root-continuity work remains the authority model: a new root/epoch is accepted through an explicit authenticated transition, not simply because it is newer.

## Decision

Freeze the mechanics above for implementation planning and RED-first tests.

**Not authorized by this document:** any actual production transition that resumes side effects when historical application-idempotency non-reuse evidence is unavailable. That activation requires explicit human-owner product/security approval bound to the exact loss scope and new epoch/cutover payload.
