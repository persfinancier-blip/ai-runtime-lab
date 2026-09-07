# Lease / enforcement quorum handoff, issuer-epoch transition, and provider-fence continuity — V1

Date: 2026-09-07
Status: `LEASE_ENFORCEMENT_QUORUM_HANDOFF_ISSUER_EPOCH_PROVIDER_FENCE_CONTINUITY_V1_FROZEN`
Scope: LAB-093 follow-on architecture research; composes with the frozen D2 lease/revocation contracts. No production-code or behavioral PASS is claimed by this note.

## Problem

The previous D2 lease contract requires renewal, revocation, and consequential use-time enforcement to be bound to one authenticated monotonic lease/root generation. That still leaves a dangerous transition problem: a live system must eventually replace replicas, consensus membership, brokers/providers, signer sets, or verification roots.

A naive handoff can create a split-authority interval where both old and new issuers can renew the same logical capability. If a partitioned old issuer remains able to mint an extension while the new issuer has already begun serving, the previously proved finite revocation horizon is false.

The handoff therefore needs a stronger invariant than ordinary availability-oriented leader election:

> At every consequential instant, every accepted renewal or use must be attributable to exactly one currently authoritative issuer epoch, and an issuer retired from epoch N must be physically unable to extend authority into epoch N+1 or later.

`no two active leaders observed` is not sufficient. The property is about accepted effects, including delayed/replayed renewal paths and external providers.

## Donor mechanisms

### Raft / etcd membership transition

etcd runtime reconfiguration is a useful donor for membership safety. Current documentation recommends serialized changes and adding a replacement as a learner until it has caught up before promotion. Reconfiguration requires a functioning quorum and strict reconfiguration checks reject transitions that would make the reconfigured cluster lose quorum.

Useful mechanism: **catch up before granting voting/issuing authority; serialize authority-membership changes through the authoritative log.**

Not inherited automatically: consensus membership safety alone does not revoke an external provider credential already held by an old process.

Sources:
- https://etcd.io/docs/v3.8/op-guide/runtime-configuration/
- https://etcd.io/docs/v3.7/op-guide/runtime-configuration/

### TUF root rotation

TUF root update gives a strong trust-root handoff pattern: version N+1 root metadata is accepted only when signed by a threshold trusted under root N and by the threshold declared by root N+1; versions advance monotonically and clients retrieve every intermediate root.

Useful mechanism: **old-authority + new-authority overlap signs the transition object, but operational authority is still versioned and monotonic.**

This overlap must not be confused with allowing both generations to mint leases concurrently. The overlap authorizes the handoff record; it does not authorize dual post-cutover issuance.

Source:
- https://theupdateframework.github.io/specification/ — root update workflow and key migration.

### Kubernetes Lease / coordinated leader election

Kubernetes Lease objects identify a current holder and track renewals / transitions. Coordinated leader election uses a shared Lease so one candidate acquires the role while others remain followers; loss of renewal allows another candidate to take over.

Useful mechanism: **persisted holder identity and transition generation at the coordination authority.**

Negative boundary: a Lease record by itself is not a fencing token. If an old holder can still mutate the protected external resource after losing the Lease, the resource remains vulnerable to stale-holder effects.

Sources:
- https://kubernetes.io/docs/concepts/architecture/leases/
- https://kubernetes.io/docs/reference/kubernetes-api/coordination/lease-v1/

### Short-lived workload credentials / SPIFFE

SPIFFE Workload API streams rotating short-lived SVIDs and trust bundles to workloads. Rotation shows a practical separation between identity credential refresh and durable identity continuity.

Useful mechanism: **short-lived issuer credentials reduce stale-authority exposure, but expiry is only a bound when the enforcing peer/provider actually checks the rotated trust state and old credentials cannot be refreshed.**

Sources:
- https://spiffe.io/docs/latest/deploying/svids/
- https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/

## Frozen authority model

### 1. `IssuerEpochV1`

Every lease authority generation has an authenticated immutable record:

- `authority_id`
- `epoch`
- `predecessor_epoch_digest`
- `issuer_membership_root`
- `renewal_policy_digest`
- `enforcement_policy_digest`
- `provider_fence_binding`
- `signing_root_digest`
- `activation_frontier`
- `retirement_frontier` (unset while active)
- `max_lease_horizon`
- `handoff_nonce`

Epoch identifiers are monotonic and never reused after rollback/recovery.

### 2. Three transition states

A handoff is not a single boolean switch. It has three authenticated states:

1. `PREPARED(N->N+1)` — successor has caught up and can verify history, but cannot issue or renew.
2. `CUTOVER_COMMITTED(N->N+1)` — the authoritative log chooses N+1 as the only epoch allowed to issue new leases/renewals.
3. `OLD_EPOCH_FENCED(N)` — independent evidence proves epoch N can no longer cause a provider-accepted extension or consequential use beyond the allowed residual horizon.

`CUTOVER_COMMITTED` without `OLD_EPOCH_FENCED` is not closure. It is a transitional state with residual-risk obligations.

### 3. Handoff authorization

The transition object must be authenticated by:

- the currently trusted authority for epoch N;
- the successor authority/root for epoch N+1;
- any root/recovery coauthorization required by the existing LAB-086/090 authority model.

This is analogous to TUF dual-threshold root transition: both sides authenticate the handoff object. It does **not** grant both sides simultaneous renewal authority after the cutover frontier.

## Issuance and renewal linearization

### Single issuance frontier

Every issuance/renewal request is bound to:

- exact `authority_id`;
- exact `issuer_epoch`;
- monotonically unique request id;
- capability/descendant identity;
- previous lease generation;
- requested expiry/horizon;
- provider fence token or provider-side equivalent.

The authority log linearizes the request before an external provider effect is considered committed.

After `CUTOVER_COMMITTED(N->N+1)`, any newly linearized renewal under N is invalid even if an old issuer process still has network access or a signing key.

### Crash/timeout result

If the authority does not know whether an external renewal committed before cutover, the result is `UNKNOWN_PENDING_RECONCILIATION`, not retry-as-new and not success.

Reconciliation must query or otherwise attest the provider-visible generation/fence before closure.

## Stale-issuer fencing

The preferred construction is provider-enforced fencing, not merely issuer-local state.

For each consequential provider operation, the provider/broker must reject a request whose epoch/fence is older than the highest accepted epoch/fence for that authority/resource.

Required properties:

- monotonic compare at the actual enforcement point;
- persistence across issuer restart;
- no reset on provider failover;
- no acceptance based only on client wall clock;
- no hidden alternate API that bypasses the fence;
- idempotent replay for the same exact request, but rejection of stale semantic replays.

If the provider cannot enforce epochs/fences, D2 can only remain bounded by the immutable maximum expiry of already-issued credentials. The system must record `PROVIDER_FENCE_UNAVAILABLE`; it may not claim immediate old-issuer revocation.

## Provider implementation migration

Changing provider A to provider B is more dangerous than changing consensus replicas because B may have no knowledge of A's highest accepted fence.

Safe migration requires one of these constructions:

### A. Shared monotonic fence authority

Both providers validate a fence derived from a shared authoritative monotonic store. B begins accepting only after it has synchronized at least the cutover fence.

### B. Provider-side handoff checkpoint

A emits an authenticated final checkpoint containing its highest accepted epoch/fence and outstanding ambiguous operations. B imports and verifies that checkpoint before activation. A is then placed into a state that rejects all post-checkpoint renewals.

### C. Finite-expiry drain

When neither cross-provider fence nor authenticated checkpoint is possible, stop new N renewals, wait through the maximum immutable N horizon using provider-authoritative time, prove there are no refresh paths, then activate B. This sacrifices availability but preserves the safety claim.

There is no safe `best effort` fourth mode for consequential D2 authority.

## Quorum / membership handoff

Replica membership changes are allowed only through the same authority log and must preserve quorum intersection or an equivalent serialized consensus reconfiguration mechanism.

Preferred operational sequence:

1. Add successor replica as non-issuing learner/observer.
2. Catch it up through the current authority log frontier.
3. Verify its policy/root/provider-fence state.
4. Commit membership transition.
5. Only after commit may the successor participate in issuance quorum.
6. Removed replica's issuer epoch is fenced at the provider/broker layer.

A removed replica retaining old keys is not a safety problem only if those keys cannot make a provider accept a renewal under a stale epoch.

## Signing-root rotation

Signing-root rotation and issuer-epoch rotation are separate axes and must not be conflated.

- Root N+1 authenticates new issuer identities/keys.
- Old root/root policy authenticates continuity into N+1.
- Lease acceptance is bound to the issuer epoch carried by the signed request.
- A cryptographically valid signature from a retired issuer/root remains historically verifiable but cannot authorize a new renewal.

Historical verification mode is therefore `VERIFY_ONLY`; it does not restore issuance authority.

## Partition semantics

### Old partition, new quorum live

After committed cutover:
- new epoch may serve;
- old partition may continue local computation but all renewal/effect attempts must be provider-fenced;
- if provider fencing is unproven, closure remains `UNKNOWN` until old maximum horizon expires or the old path is physically disabled and verified.

### New partition before cutover

N remains authoritative. N+1 cannot issue merely because it believes it is healthier.

### Authority-log partition without quorum

No epoch transition and no renewal requiring a new linearized authority decision. Fail closed for consequential operations.

### Provider partition

Timeout after sending a renewal is `UNKNOWN_PENDING_RECONCILIATION`; do not mint a replacement renewal whose combined effects could extend the horizon.

## Crash and recovery

Recovery must persist or reconstruct:

- current epoch;
- committed handoff state;
- highest issued/accepted lease generation per consequential capability or canonical aggregate frontier;
- provider highest fence / attested checkpoint;
- ambiguous external effects;
- retired issuer list;
- signing-root generation.

A restored snapshot with a lower epoch/fence is rollback evidence, not an invitation to reissue from the old generation.

If durable state and provider-observed state disagree, the system enters `RECOVERY_RECONCILIATION_REQUIRED` and cannot claim closure until monotonicity is re-established.

## Closure proof

`IssuerHandoffClosureProofV1` requires all of:

1. authenticated N->N+1 handoff object;
2. quorum-safe membership transition proof;
3. N+1 catch-up/frontier proof;
4. exact cutover log position;
5. provider/broker proof that N cannot extend authority past the permitted residual horizon;
6. complete renewal-path inventory for both epochs;
7. resolution of timeout/UNKNOWN effects crossing the cutover;
8. root-transition continuity proof when signing roots changed;
9. historical verification material for retired N retained according to evidence policy.

Verdicts:

- `HANDOFF_CLOSED`
- `HANDOFF_OPEN_RESIDUAL_LEASES`
- `HANDOFF_UNKNOWN_PROVIDER_FENCE`
- `HANDOFF_UNKNOWN_AMBIGUOUS_EFFECT`
- `HANDOFF_REJECTED_SPLIT_AUTHORITY`
- `HANDOFF_REJECTED_ROLLBACK`

Only `HANDOFF_CLOSED` can support a claim that epoch N has no remaining renewal authority.

## Fraud / contradiction proofs

Freeze compact evidence forms for:

- `PostCutoverOldEpochRenewalProofV1`
- `StaleProviderFenceAcceptanceProofV1`
- `UnrecordedIssuerMembershipProofV1`
- `ProviderCheckpointRollbackProofV1`
- `DualEpochConcurrentIssuanceProofV1`
- `RetiredRootNewRenewalProofV1`
- `HiddenRenewalPathAfterHandoffProofV1`

A proven contradiction invalidates dependent D2 closure/finalization/GC proofs and re-roots the affected descendant closure. Repair is additive: new epoch + explicit incident/repair evidence; historical bytes are not rewritten.

## RED-first matrix (80 cases)

### A. Quorum/membership transition (1-10)
1. learner caught up before promotion
2. learner behind at promotion -> reject
3. remove member while quorum unsafe -> reject
4. two membership changes concurrently -> serialize/reject
5. removed member restarts -> no issuance authority
6. old quorum partition after cutover -> provider rejects N
7. new minority before cutover -> cannot issue
8. membership epoch rollback -> reject
9. duplicate transition request -> idempotent
10. transition with unknown member identity -> reject

### B. Issuer epoch linearization (11-20)
11. N renew before cutover -> allowed
12. N renew after cutover -> reject
13. N+1 renew before cutover -> reject
14. N+1 renew after cutover -> allowed
15. concurrent N renew / cutover, renew linearizes first -> bounded residual
16. concurrent N renew / cutover, cutover first -> reject renew
17. retry same request after timeout -> exact idempotent result
18. retry with changed expiry -> reject semantic replay
19. stale issuer key valid cryptographically -> reject by epoch
20. epoch reuse after recovery -> reject

### C. Provider fencing (21-30)
21. provider accepts higher fence
22. provider rejects lower fence
23. equal fence exact replay -> idempotent
24. equal fence different request -> reject
25. provider restart preserves highest fence
26. provider failover preserves highest fence
27. alternate provider API omits fence -> closure blocked
28. hidden SDK refresh without fence -> closure blocked
29. provider accepts stale fence -> fraud proof
30. fence reset during migration -> rollback proof

### D. Provider A->B migration (31-40)
31. shared fence synchronized before B activation
32. B activates below A checkpoint -> reject
33. A checkpoint has unresolved UNKNOWN -> B closure blocked
34. A continues renewing after final checkpoint -> fraud proof
35. no shared fence, finite-expiry drain complete -> allowed
36. drain incomplete -> B activation cannot claim closure
37. provider-authoritative clock unavailable for drain -> UNKNOWN
38. B restore from stale checkpoint -> reject
39. A and B both accept same logical renewal after cutover -> split-authority proof
40. migration rolled back to A without new epoch -> reject

### E. Signing-root handoff (41-50)
41. handoff signed by old+new required thresholds
42. only old root signs -> reject
43. only new root signs -> reject
44. root version rollback -> reject
45. retired root verifies history -> allowed
46. retired root signs new renewal -> reject
47. intermediate root generation missing -> reject catch-up
48. issuer epoch unchanged but root rotated safely
49. issuer epoch rotates with root atomically bound
50. stale trust bundle accepts retired issuance -> contradiction

### F. Partition / timeout / recovery (51-60)
51. provider timeout before response -> UNKNOWN
52. cutover while UNKNOWN exists -> closure blocked
53. reconciliation proves N renewal committed pre-cutover -> residual horizon tracked
54. reconciliation proves no commit -> close obligation
55. old issuer partitioned beyond cutover -> provider fence rejects
56. authority quorum unavailable -> no transition
57. restored authority snapshot below epoch -> rollback detected
58. restored provider fence below checkpoint -> rollback detected
59. crash between cutover commit and old fence -> transitional OPEN, not CLOSED
60. crash after fence before proof persistence -> reconstruct from authoritative evidence

### G. Renewal-path completeness (61-70)
61. SDK auto-refresh bound to epoch
62. provider session refresh bound to epoch
63. queue visibility extension bound to epoch
64. child/plugin renewal bound to epoch
65. admin/manual renewal bound to epoch
66. disaster-recovery credential recreation bound to epoch
67. unknown refresh endpoint discovered -> invalidate closure
68. scheduled job created under N runs after cutover -> must reauthorize under N+1 or reject
69. cached bearer credential cannot outlive immutable horizon
70. imported external handle without epoch -> not D2-closable

### H. Historical verification / audit / GC (71-80)
71. historical N proof verifies after retirement
72. historical verification cannot issue
73. GC keeps handoff/root/checkpoint dependencies
74. GC before provider ambiguity resolved -> reject
75. fraud proof after closure reopens affected closure
76. additive repair preserves original N evidence
77. offline verifier catches up root chain generation-by-generation
78. missing handoff generation -> fail closed
79. conflicting handoff records for same epoch -> equivocation / block
80. exact replay of closed proof against different provider root -> reject context mismatch

## Security conclusions

1. Consensus leader election is necessary but not sufficient; external effect acceptance must be fenced by issuer epoch at the actual enforcement point.
2. Dual old/new signatures authenticate a transition record; they must not imply dual post-cutover renewal authority.
3. Provider migration is safe only with shared monotonic fencing, authenticated checkpoint handoff, or a full finite-expiry drain.
4. Short-lived credentials reduce exposure but do not prove revocation unless refresh paths are closed and the verifier/provider enforces the current epoch/root.
5. A stale issuer that can still reach a provider is harmless only when the provider rejects its stale epoch/fence.
6. Timeout/partition ambiguity is `UNKNOWN`; successful closure cannot be inferred from absence of observed renewals.
7. Historical verification authority is intentionally weaker than live issuance authority after retirement.

## Next distinct research question

**Provider-fence attestation / external-provider non-equivocation / cross-region monotonicity semantics**: define how the lab can *prove* a third-party or multi-region provider really enforces one monotonic fence when the provider itself is not part of the local consensus domain; specify attested readback, equivocation detection, regional replication lag, stale endpoint behavior, and what evidence is sufficient before `HANDOFF_CLOSED` can be trusted.