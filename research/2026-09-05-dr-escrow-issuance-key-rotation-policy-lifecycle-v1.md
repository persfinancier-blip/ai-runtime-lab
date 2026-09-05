# DR_ESCROW_ISSUANCE_KEY_ROTATION_POLICY_LIFECYCLE_V1_FROZEN

Date: 2026-09-05
Status: FROZEN design contract; executable RED/GREEN pending
Scope: LAB-093 composition with LAB-086 public-only break-glass history and the previously frozen DR checkpoint-escrow/root-recovery protocol.

## Problem

The prior DR contract requires independently retained pre-disaster checkpoint evidence and a cross-domain quorum before a lost local root/checkpoint can be restored. That leaves a lifecycle question: how are escrow packages, witness keys, custodians, and quorum policies created and changed over time without making rotation itself a rollback, threshold-downgrade, or second mutable root-of-trust plane?

## Primary evidence

1. TUF Specification v1.0.36 (2026-08-05) requires a trusted line of root continuity through intermediate root metadata and uses threshold trust for top-level roles. Root key compromise below threshold is handled by normal rotation; compromise of a threshold requires out-of-band recovery. The key point for this contract is overlap/continuity: a new trust configuration is accepted through the already-trusted configuration, not merely because it is newer.
2. C2SP Transparency Log Witness Protocol v1.0.0 requires witnesses to verify checkpoint signatures and append-only consistency against the latest checkpoint they previously persisted; the witness must atomically persist the new checkpoint before returning a cosignature. This is the donor mechanism for monotonic escrow observations and anti-rollback state.
3. NIST SP 800-57 Part 1 Rev. 5 treats key lifecycle, compromise, backup/recovery, trust anchors, split knowledge, and key-management policy as explicit management concerns rather than ad-hoc operational details.

## Non-goals

- No private LAB-086 break-glass signing material is escrowed in this protocol.
- No online worker/provider/admin credential becomes DR authority.
- No independent DR database is allowed to become a second mutable root-of-trust plane.
- No policy change may silently make previously insufficient signatures sufficient for an already-created historical checkpoint.

## Canonical authority objects

### `DR_ESCROW_POLICY_V1`

Immutable canonical object, committed into the existing global provenance chain before it can authorize future escrow issuance:

- `policy_version`
- `policy_generation` (strictly monotonic)
- `parent_policy_digest`
- `effective_after_checkpoint`
- ordered `custodian_set[]` containing stable custodian IDs and public verification keys
- `threshold`
- `minimum_failure_domains`
- allowed signature algorithms / encoding version
- maximum package age / drill interval policy
- `emergency_human_ceremony_required_if[]`
- `policy_digest`

`policy_generation` is an ordering aid, never independent authority. The parent digest and provenance transition establish continuity.

### `DR_ESCROW_PACKAGE_V1`

Immutable pre-disaster package:

- global provenance history ID
- escrow policy digest and generation
- source checkpoint identity (position/size/root/digest as applicable)
- manifest/root verification material required by the frozen DR recovery protocol
- issuer identity
- issuance time as informational metadata only
- canonical package digest
- qualifying custodian/witness signatures

A package is usable only if its checkpoint was already authenticated under the runtime trust chain when issued, its policy was current for issuance, and qualifying signatures met that policy at issuance.

## Issuance protocol

1. Broker verifies the current global provenance head and current DR policy.
2. Candidate checkpoint is verified as a descendant of the currently trusted checkpoint/history.
3. Canonical escrow package bytes are produced exactly once.
4. Independent custodians/witnesses verify package identity and checkpoint continuity before signing/retaining it.
5. Issuance is considered COMPLETE only after the required threshold and minimum failure-domain count are satisfied and the resulting package digest/receipt is appended to the existing global provenance chain.
6. An incomplete package is staging evidence only and cannot be used for automatic DR.

Timestamp recency or replica count never substitutes for authenticated continuity/quorum.

## Key rotation contract

Key rotation is a policy transition, not a side-channel configuration edit.

### Normal rotation

To replace custodian/witness key `K_old` with `K_new`:

1. Create `policy_{n+1}` with parent `digest(policy_n)`.
2. `policy_{n+1}` MUST be authorized under `policy_n`'s currently trusted quorum and recorded as a parent-linked global provenance transition.
3. `K_new` becomes eligible only for escrow packages issued after the transition's effective checkpoint.
4. `K_old` remains valid for verification of historical packages that were validly issued while its policy was authoritative.
5. Historical packages are never re-signed merely to make them appear issued under the new policy.

This mirrors the TUF principle that trust-root migration requires a trusted continuity path; a newly presented key cannot bootstrap itself.

### Rotation overlap

A policy change that removes one or more custodians MUST NOT create a period in which fewer than the old policy's required independent domains can authenticate the transition itself. Operationally, new keys should be provisioned and proven retrievable before old keys are retired.

A failed new-key activation leaves `policy_n` authoritative. No partial policy is accepted.

## Quorum-policy change contract

### Threshold increase

Allowed through a normal parent-linked policy transition authorized by the current policy.

### Threshold decrease / failure-domain decrease

Security-sensitive and fail-closed by default. It MUST satisfy all of:

- authorized by the existing stronger policy, not the proposed weaker policy;
- explicit `THRESHOLD_DOWNGRADE` transition type in global provenance;
- independent evidence that the remaining custodian set still satisfies the configured failure-domain constraint;
- no retroactive effect: historical escrow packages retain the acceptance rule from their issuance policy;
- fresh post-transition escrow issuance and recovery drill before the weaker policy may authorize automatic disaster recovery.

A policy file with a lower threshold appearing in storage is never sufficient authority.

## Lost custodian replacement

Loss of one custodian below threshold is an availability incident, not authority to rewrite history.

Replacement procedure:

1. Prove current policy and surviving quorum.
2. Add replacement custodian/key in `policy_{n+1}` through the normal parent-linked transition.
3. Require retrieval/signing drill from the replacement domain.
4. Issue a fresh escrow package under `policy_{n+1}`.
5. Only then retire the lost custodian for future issuance.

If surviving independent authority is below the current threshold, automatic policy mutation stops and the frozen human security ceremony path is required.

## Compromise handling

- Suspected key compromise below threshold: revoke for future issuance via an old-policy-authorized transition; historical packages remain valid only as historical evidence when the recovery decision can still establish an uncompromised qualifying quorum under their issuance policy.
- Compromise at or above threshold: no automatic key rotation can restore trust, because the compromised policy could authorize its own successor. Enter `DR_ROOT_COMPROMISED` and require out-of-band human security ceremony.
- Rotation is not allowed to erase compromise evidence or change the issuance policy attached to historical packages.

## Periodic drills

A DR configuration that is cryptographically correct but operationally unretrievable is not sufficient.

Each policy defines a maximum drill interval. A drill MUST verify, without performing recovery side effects:

- each required failure domain can retrieve its retained package/checkpoint evidence;
- package bytes match the authenticated package digest;
- signatures still verify with the historical policy snapshot;
- enough independent domains can form the configured quorum;
- append-only consistency to the current trusted checkpoint can be proven or the expected historical checkpoint can be supplied for the frozen DR protocol;
- no private production root/break-glass secret is exposed during the exercise.

Drill results are append-only provenance evidence. A missed/failed drill degrades `DR_AUTOMATIC_RECOVERY_READY` to false; it does not authorize weaker quorum or key reuse.

## Policy activation state machine

`DRAFT -> QUORUM_AUTHORIZED -> PROVENANCE_COMMITTED -> DRILL_VERIFIED -> ACTIVE`

Only `ACTIVE` policy may authorize automatic DR or issuance of packages considered current. Failures before `PROVENANCE_COMMITTED` leave the previous policy authoritative. Failures after commit but before `DRILL_VERIFIED` leave the new policy recorded but automatic DR disabled until drill success; they MUST NOT silently fall back to treating an older policy as current for newly issued packages.

## Anti-rollback and split-view rules

- Policy selection follows authenticated parent continuity, never timestamp or storage freshness.
- A lower-generation policy after a higher authenticated generation is rollback and fails closed.
- Two different children of the same parent that each carry apparently sufficient signatures are `DR_POLICY_SPLIT_VIEW`; automation stops until consistency is resolved by the existing root-recovery/human ceremony protocol.
- Custodians/witnesses retain their latest accepted policy/checkpoint observation and reject inconsistent rollback, borrowing the monotonic-state mechanism from the C2SP witness protocol.

## Crash consistency

Every authority transition uses the existing global provenance atomic-append/recovery mechanism. Minimum ordering:

1. prepare canonical transition under current policy;
2. gather qualifying signatures;
3. persist all immutable transition evidence;
4. append/anchor the global provenance transition atomically;
5. re-read and verify the committed head;
6. only then expose the new policy as current;
7. run required drill before setting automatic-recovery readiness.

A crash may leave redundant staged evidence, but MUST NOT leave an unanchored policy authoritative.

## Acceptance / RED-first matrix (60 cases)

### Issuance (1-10)
1. valid current-policy issuance succeeds;
2. insufficient signatures rejected;
3. threshold met but insufficient failure domains rejected;
4. unknown custodian key rejected;
5. duplicate signatures from same custodian count once;
6. package digest mutation rejected;
7. checkpoint identity mutation rejected;
8. untrusted/non-descendant checkpoint rejected;
9. incomplete staged package not DR-usable;
10. provenance receipt missing => issuance not COMPLETE.

### Rotation (11-22)
11. valid old-policy-authorized key replacement succeeds;
12. new key self-authorizing its own policy rejected;
13. old key remains valid for historical package verification;
14. old key not valid for post-effective issuance;
15. partial rotation crash keeps old policy authoritative;
16. committed-but-undrilled new policy not automatic-DR-ready;
17. new-key retrievability failure blocks readiness;
18. policy parent digest mismatch rejected;
19. skipped generation with valid parent allowed only if canonical policy permits monotonic generation; parent continuity remains decisive;
20. rollback to prior policy rejected;
21. two divergent successors => split-view fail closed;
22. re-signing historical package under new key does not rewrite issuance policy.

### Quorum changes (23-34)
23. threshold increase under old quorum accepted;
24. threshold decrease signed only by proposed weaker quorum rejected;
25. threshold decrease signed by current stronger quorum but without explicit downgrade transition rejected;
26. downgrade reducing minimum failure domains below floor rejected;
27. authorized downgrade remains non-retroactive;
28. fresh package required after downgrade;
29. fresh drill required before automatic DR after downgrade;
30. storage-only threshold edit rejected;
31. custodian-set shrink without old-policy authorization rejected;
32. threshold=0 rejected;
33. threshold greater than custodian count rejected;
34. duplicate failure-domain labels do not satisfy diversity.

### Custodian loss/compromise (35-44)
35. single lost custodian below threshold triggers replacement path;
36. replacement without surviving quorum rejected;
37. replacement key must pass retrieval/signing drill;
38. retirement before fresh package blocked;
39. suspected compromised key revoked for future issuance;
40. revoked key cannot sign new package;
41. historical package policy remains immutable;
42. threshold compromise enters DR_ROOT_COMPROMISED;
43. compromised quorum cannot authorize successor automatically;
44. ordinary admin/provider/worker credential cannot perform custodian replacement.

### Drills/recovery readiness (45-52)
45. all-domain drill success sets readiness;
46. one required domain unavailable => readiness false;
47. digest mismatch => readiness false;
48. historical-policy signature failure => readiness false;
49. insufficient quorum during drill => readiness false;
50. missed drill interval => readiness false without weakening policy;
51. drill must not expose private production break-glass/root secrets;
52. successful drill appends provenance evidence without changing history authority.

### Crash/restart/anti-rollback (53-60)
53. crash before signature quorum leaves old policy current;
54. crash after signatures but before provenance commit leaves old policy current;
55. crash after provenance commit reconstructs committed policy from chain;
56. restart cannot infer current policy from newest timestamped file;
57. stale custodian observation rejects lower policy/checkpoint;
58. divergent authenticated policy views block automatic DR;
59. policy deletion does not cause first-install/self-bootstrap behavior;
60. no rotation/drill/storage-pressure path can make a previously used application-idempotency key become MISS.

## Implementation boundary

Production implementation waits for exact executable RED/GREEN on the retained authority stack. When implementation begins, do not introduce a new standalone escrow trust DB. Reuse the frozen global provenance encoder/chain/atomic-append/storage/verifier and LAB-093 broker startup state machine.

## Decision

`DR_ESCROW_ISSUANCE_KEY_ROTATION_POLICY_LIFECYCLE_V1_FROZEN` is the required lifecycle contract for DR escrow. Automatic recovery authority is established before disaster, evolves only through the already-authenticated provenance chain, and cannot be weakened by storage edits, self-authorizing new keys, policy rollback, or post-disaster convenience.