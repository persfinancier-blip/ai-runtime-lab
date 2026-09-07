# Provider-fence attestation / external-provider non-equivocation / cross-region monotonicity v1

Date: 2026-09-07
Status: FROZEN DESIGN EVIDENCE
Contract id: `PROVIDER_FENCE_ATTESTATION_EXTERNAL_PROVIDER_NON_EQUIVOCATION_CROSS_REGION_MONOTONICITY_V1_FROZEN`
Related: LAB-093/#178, LAB-090/#169, LAB-100/#185

## Question

The previous issuer-handoff contract assumes a provider/broker enforcement point can reject stale issuer epochs. For an external or multi-region provider, that assumption is not enough. A local coordinator can be correct while the provider serves stale regions, accepts two epochs concurrently, loses replication, or equivocates between readers.

This note defines the minimum evidence needed before treating an external provider fence as authoritative for `HANDOFF_CLOSED`.

## Primary-source donors

1. Google Cloud Spanner external consistency / TrueTime: external consistency gives one serial order consistent with observed commit order across regions; strong reads observe effects of all transactions committed before the operation. This is a positive donor for a provider that can expose one globally ordered authority state rather than region-local observations.
   - https://docs.cloud.google.com/spanner/docs/true-time-external-consistency

2. Azure Cosmos DB consistency documentation: under strong consistency, writes are committed across regions; weaker session consistency uses session tokens and asynchronous cross-region replication. Session tokens are therefore useful causal evidence, but not by themselves a universal global-fence proof.
   - https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels
   - https://learn.microsoft.com/en-us/azure/cosmos-db/multi-region-writes

3. AWS DynamoDB global tables documentation: MREC accepts writes locally while remote regions can be offline and resolves simultaneous updates with last-writer-wins; strongly consistent reads in one region can still be stale relative to writes in another region in MREC. This is a negative donor: convergence/LWW is not equivalent to monotonic fencing or non-equivocation.
   - https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html
   - https://docs.aws.amazon.com/prescriptive-guidance/latest/dynamodb-global-tables/overview.html

## Threat model

A provider fence is consequential authority. The adversarial/failure cases include:

- stale region accepts epoch `e` after cutover to `e+1`;
- two regions independently accept renewals for `e` and `e+1`;
- read-after-write returns the new epoch in one region but an old epoch in another;
- replication lag hides an accepted stale renewal until after local closure is declared;
- active/active conflict resolution silently chooses one of two accepted epochs;
- provider failover restores an older control-plane snapshot;
- API endpoint routing changes consistency level or read semantics;
- provider acknowledges a write but cannot later prove which globally ordered state accepted it;
- provider returns inconsistent fence state to independent verifiers;
- credential/signing-root rotation succeeds while an old regional issuer remains usable.

The contract must distinguish **availability**, **eventual convergence**, **session monotonicity**, and **global monotonic enforcement**. Only the last one can directly close a D2 handoff without an additional drain horizon.

## Core rule

`HANDOFF_CLOSED` MUST NOT depend on a provider's prose claim that it is "strongly consistent", "multi-region", "HA", or "eventually consistent".

Closure requires an authenticated, replay-resistant `ProviderFenceAttestationV1` proving that every consequential renewal/use path is bound to one monotonic provider fence domain, or else an explicit fallback mode whose residual authority is bounded by finite expiry.

## ProviderFenceAttestationV1

Minimum fields:

- `provider_authority_id`: stable logical provider/fence domain identity;
- `provider_implementation_id`: product/API/adapter generation actually enforcing the fence;
- `account_or_tenant_scope`: exact administrative scope;
- `resource_scope`: canonical set/range of resources protected;
- `fence_generation`: monotonic issuer/provider generation;
- `predecessor_attestation_digest`;
- `cutover_event_id`;
- `write_ack_id` or transaction/commit id supplied by the provider;
- `commit_order_token`: provider-native globally ordered revision/timestamp/version where available;
- `consistency_mode`: exact mode used for the write and readback;
- `write_region_or_endpoint`;
- `required_readback_domains`: independent region/endpoint set that must witness the cutover;
- `readback_observations[]`: authenticated endpoint/region, observed fence, observed commit token, time window;
- `stale_epoch_rejection_probe[]`: safe negative checks proving old epoch is rejected on required consequential paths;
- `replication_or_resolved_frontier`: if the provider exposes one;
- `maximum_uncertainty_or_lag_bound`: only when contractually/mechanically enforced, not a measured average;
- `issuer_root_epoch` / credential generation;
- `evidence_expiry`;
- `adapter_semantics_digest`;
- canonical signature/MAC by the local trusted adapter plus any provider-native receipt signature available.

A provider-native request id or HTTP 200 alone is not a fence attestation.

## Acceptance classes

### P1 — GLOBAL_LINEARIZABLE_FENCE

Requirements:

- one globally ordered write domain for the fence;
- acknowledged update to `e+1` linearizes after `e`;
- strong/global readback from any supported consequential endpoint cannot return an earlier committed fence;
- stale-epoch consequential request is rejected by the enforcement point, not merely detected later;
- failover preserves the same monotonic order.

This class may support immediate `HANDOFF_CLOSED` after attested cutover and independent readback.

Spanner-style external consistency is the positive donor shape: one serial order across regions is materially stronger than region-local session guarantees.

### P2 — BOUNDED_PROPAGATION_FENCE

Requirements:

- provider has an explicit mechanically enforced maximum propagation/lease horizon `H`, not merely an SLO percentile;
- new epoch is accepted only after cutover; old epoch may remain usable in bounded replicas until `H`;
- no renewal can extend old authority beyond `H`;
- every stale endpoint has finite expiry or server-side epoch checking;
- closure waits through `H` plus uncertainty and then performs readback/rejection checks.

Result before horizon: `HANDOFF_PENDING_DRAIN`.
Result after complete evidence: `HANDOFF_CLOSED_BOUNDED`.

### P3 — SESSION_OR_CAUSAL_ONLY

Examples: session-token systems where the client can force its own subsequent reads/writes to observe a causal frontier, while unrelated clients/regions may lag.

These tokens are useful for reconciliation but do not prove all provider endpoints reject the old epoch.

Result: cannot close global revocation without additional broker mediation or finite-expiry drain.

### P4 — EVENTUAL_OR_LWW

Active/active eventual replication, last-writer-wins conflict resolution, or local-region acceptance during remote outage is not a monotonic fence.

DynamoDB MREC is the canonical negative donor shape: local writes continue while another region is unavailable and conflicts converge later via LWW. That property is valuable availability, but insufficient to prove that stale authority was never accepted.

Result: `REVOCATION_UNENFORCEABLE_GLOBALLY` unless all consequential use is mediated by a stronger local broker or credentials have a finite non-renewable expiry.

## Non-equivocation requirement

A provider is non-equivocating for fence generation `e` only if two independently authenticated verifiers querying the required authority domain cannot obtain mutually valid states that authorize incompatible epochs for overlapping resource scope.

Required verifier rule:

1. Collect observations from at least the configured independent endpoint/region set.
2. Bind each observation to a provider-native commit/revision token if available.
3. Require monotonic relation to the accepted predecessor attestation.
4. If two valid observations are incomparable or authorize overlapping epochs, emit `PROVIDER_FENCE_EQUIVOCATION_SUSPECTED`.
5. Do not choose `latest timestamp wins` locally unless the provider contract itself guarantees that timestamp is the single global serialization order.
6. Persist both contradictory observations as fraud/incident evidence.

## Attested readback is necessary but not sufficient

A readback that says `e+1` only proves what that read path observed. It does not prove an unqueried stale endpoint rejects `e`.

Therefore `ProviderFenceAttestationV1` must carry both:

- **positive evidence**: new fence is committed and visible at the required frontier;
- **negative enforcement evidence**: old epoch can no longer perform consequential renewal/use on every material path, or remaining paths are covered by a proven finite horizon.

This mirrors the descendant-revocation contract: enumeration/readability of current state is weaker than proof that no live descendant can still act.

## Cross-region monotonicity rule

For each material region/endpoint `r`, define `frontier(r)`.

Closure requires one of:

- provider guarantees all supported endpoints participate in one linearizable/global order and a strong read is sufficient to observe it; or
- `frontier(r) >= cutover(e+1)` for every material region plus stale-epoch rejection at each material enforcement path; or
- region `r` is formally drained/disabled and cannot receive consequential traffic; or
- region `r` remains outside closure and the result is `UNKNOWN` / pending drain.

A traffic-router configuration is not itself proof that a stale region is unable to accept direct/API traffic unless access control also fences it.

## Failover continuity

Provider failover from region/provider implementation A to B is safe only if at least one holds:

1. A and B share the same monotonic fence authority and B proves its frontier includes cutover `e+1` before it serves consequential requests.
2. A emits an authenticated terminal checkpoint consumed by B, and B rejects all epochs below that checkpoint.
3. Old capabilities have a finite non-renewable expiry, A is fully drained, and B starts only after the drain horizon.

If B can start from a stale snapshot and issue/renew before catch-up, failover is not fence preserving.

## Provider API / adapter binding

The local adapter is part of the trusted computing base. `ProviderFenceAttestationV1` must bind the exact adapter semantics used to interpret provider receipts and consistency modes.

A provider SDK/API upgrade is consequential if it changes:

- endpoint selection;
- default consistency level;
- retry behavior after timeout;
- multi-region routing;
- conflict resolution;
- request idempotency;
- version/ETag/precondition semantics;
- credential refresh path.

Such a change requires a new `provider_implementation_id`/adapter generation and re-attestation before it may support closure.

## Timeout and UNKNOWN

Timeout-after-send remains `UNKNOWN_PENDING_RECONCILIATION`.

The coordinator must not infer from timeout that the fence update failed. It must reconcile through provider-native request/commit identity or a monotonic readback that can distinguish:

- not committed;
- committed as `e+1`;
- conflicting/incomparable provider state.

If the provider cannot provide enough evidence to distinguish these states safely, closure is blocked.

## Fraud / contradiction proofs

Freeze these proof forms:

### `StaleRegionAcceptanceProofV1`
Evidence that a material endpoint accepted consequential authority for epoch `< current_fence` after cutover.

Verdict: `STALE_REGION_ACCEPTED_REVOKED_EPOCH_PROVEN`.

### `ProviderFenceEquivocationProofV1`
Two authenticated provider observations/receipts for overlapping scope that authorize incompatible epochs and cannot both exist under the declared consistency contract.

Verdict: `PROVIDER_FENCE_EQUIVOCATION_PROVEN`.

### `FailoverRollbackProofV1`
Post-failover provider frontier is below the previously attested terminal/cutover frontier and consequential service resumed.

Verdict: `PROVIDER_FAILOVER_ROLLBACK_PROVEN`.

### `ConsistencyModeDowngradeProofV1`
A consequential operation was acknowledged under a weaker consistency mode than the active attestation permits.

Verdict: `PROVIDER_CONSISTENCY_DOWNGRADE_PROVEN`.

Any proven contradiction invalidates dependent `IssuerHandoffClosureProofV1`, descendant-closure proof, finalization certificate, and destructive-GC eligibility for the affected scope until repaired.

## Repair

Repair is additive:

1. quarantine affected provider scope;
2. preserve contradictory receipts/observations;
3. advance to a new provider/issuer epoch;
4. establish a stronger provider fence or broker-mediated path;
5. re-root all potentially affected live descendants/leases;
6. repeat closure attestation;
7. never rewrite old attestations to pretend the contradiction did not occur.

## RED-first matrix (80 cases)

Freeze an 80-case matrix across these groups, 8 each:

1. single-region monotonic acceptance;
2. two-region replication lag;
3. stale-region direct traffic;
4. concurrent old/new issuer renewals;
5. timeout-after-send and reconciliation;
6. failover / stale snapshot restore;
7. active-active conflict/LWW behavior;
8. consistency-mode/API/SDK downgrade;
9. independent-verifier equivocation detection;
10. closure/GC invalidation and additive repair.

Representative mandatory RED cases:

- write `e+1` acknowledged in region A, region B still accepts `e`;
- A and B both return success for incompatible renewal epochs;
- strong read from A shows `e+1`, eventual read from B shows `e`, closure incorrectly trusts only A;
- provider fails over to stale replica and old issuer renews;
- local adapter retries an UNKNOWN request against another region and creates dual acceptance;
- API upgrade silently changes strong read to session/eventual mode;
- LWW convergence ends at `e+1` after both `e` and `e+1` were consequentially accepted;
- route removes stale region from normal traffic but direct credential still reaches it;
- provider-native commit token rolls backward across failover;
- two independent verifier domains receive mutually incompatible valid receipts.

GREEN must demonstrate fail-closed behavior or bounded-drain semantics, not merely eventual convergence.

## Composition decisions

- LAB-090 owns the provider-side activation/fencing transition.
- LAB-100 owns which provider implementation/capability may be trusted.
- LAB-093 capability-envelope/lease/handoff work consumes this contract when claiming external D2 revocation closure.
- An in-process leader election, local consensus generation, or local issuer epoch is insufficient unless the external provider enforces or faithfully reflects the same monotonic fence.
- If a provider cannot meet P1/P2, route consequential authority through a broker that can, or downgrade the security claim to finite-expiry/best-effort and keep closure `UNKNOWN` until expiry.

## Frozen verdict

`EXTERNAL_PROVIDER_FENCE_CLOSURE_REQUIRES_NON_EQUIVOCATING_MONOTONIC_ENFORCEMENT_V1`.

A third-party/multi-region provider is authoritative for handoff closure only when evidence proves one monotonic fence across every material consequential path, or when all residual stale authority is mechanically bounded by a finite non-renewable horizon. Eventual convergence, LWW conflict resolution, one-region readback, session monotonicity, health/HA, or traffic routing alone are insufficient.
