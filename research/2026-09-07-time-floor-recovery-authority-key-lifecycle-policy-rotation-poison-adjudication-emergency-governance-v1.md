# Time-floor recovery authority: key lifecycle, policy rotation, poison adjudication, and emergency governance v1

Date: 2026-09-07
Status: DESIGN FROZEN — executable RED/GREEN still required
Parent: LAB-093 / #178

## Why this exists

The previous secure-time contract established that a poisoned far-future `TrustedTimeFloorV1` cannot be lowered by ordinary time samples, local clock reset, VM rollback, cache deletion, or routine resynchronization. Recovery therefore needs a distinct higher-order authority.

That creates a new root-of-trust problem: if `TimeFloorRecoveryAuthorityV1` can be self-bootstrapped, self-rotated, cheaply compromised, or invoked on merely surprising clock evidence, the recovery mechanism becomes a universal anti-rollback bypass.

This note freezes the governance/security contract for that authority.

## Primary conclusion

`VALID_RECOVERY_SIGNATURE != AUTHORIZED_RECOVERY_POLICY != PROVEN_POISONING != SAFE_REPLACEMENT_FLOOR`.

A time-floor recovery is valid only when all four independent questions close:

1. **Authority** — did the artifact satisfy the currently trusted recovery policy and key history?
2. **Continuity** — was any policy/key transition authorized by both predecessor and successor generations rather than self-authorized?
3. **Adjudication** — is there independently reproducible evidence that the current trusted floor is actually poisoned, rather than merely surprising?
4. **Replacement safety** — is the proposed replacement interval/floor supported by independent evidence and conservative enough not to create a new rollback or fast-forward condition?

Failure of any one yields fail-closed recovery status, not an inferred lower clock.

---

## Donor mechanisms and facts

### TUF root-key rotation: continuity must cross old and new trust sets

The Update Framework requires each next root metadata generation to be signed by a threshold of keys from both the previously trusted root and the new root. Clients walk intermediate root versions in order; a new root generation cannot bootstrap its own authority. TUF also treats rollback/fast-forward recovery as a special trust-transition problem rather than ordinary metadata acceptance.

Reusable mechanism here: recovery-policy generation `R(n+1)` MUST be authorized by both the predecessor recovery policy `R(n)` and the successor policy `R(n+1)`, with a monotonic generation and archived intermediate lineage.

Source: TUF specification v1.0.26, sections 5.3 and 6.1.

### NIST key-management lifecycle: compromise is a state transition, not deletion of history

NIST SP 800-57 Part 1 Rev. 5 requires compromised keys to be revoked/replaced and the transition recorded. It also notes that metadata should be retained for audit and that historical verification after compromise may still be meaningful under controlled conditions when trustworthy timing/evidence bounds the signature to a pre-compromise period.

Reusable mechanism here: key status is append-only and time/generation scoped. `RETIRED`, `COMPROMISED`, `DESTROYED`, and `UNKNOWN_COMPROMISE_ONSET` do not erase prior signatures; they change which historical signatures remain authority-valid.

Source: NIST SP 800-57 Part 1 Rev. 5.

### RFC 3628 TSA compromise: stop issuing and publish affected-history information

RFC 3628 requires a TSA that suffers key compromise, suspected compromise, or loss of calibration to stop issuing timestamps until recovery steps are taken, and where possible publish information allowing relying parties to identify affected timestamp tokens. It also recommends dual control for backed-up TSA signing keys.

Reusable mechanisms here:
- recovery authority goes `NO_RECOVERY_SIGN` on suspected compromise;
- publish compromise/calibration-loss boundaries and affected decision IDs;
- no silent key replacement;
- emergency key custody must not collapse into one operator merely because the event is urgent.

### RFC 5905 NTP panic behavior: a huge offset is evidence of abnormality, not permission to step blindly

NTPv4 defines a panic threshold (default 1000 seconds in the reference algorithm): an offset beyond it is treated as probably bogus and should cause diagnostic/operator intervention rather than ordinary clock correction.

Reusable mechanism here: a very large discrepancy is a **poison suspicion trigger**, not sufficient proof of poisoning and not automatic authorization to lower `TrustedTimeFloorV1`.

---

## Frozen objects

### `TimeFloorRecoveryPolicyV1`

Fields:

- `policy_lineage_id`
- `generation`
- `previous_policy_digest`
- `key_set[]` with immutable key IDs/public keys
- `signature_threshold`
- `independence_thresholds` by required failure/control domains
- `adjudicator_set[]`
- `adjudication_threshold`
- `emergency_policy_digest` or explicit `NONE`
- `permitted_recovery_reasons[]`
- `max_single_recovery_delta`
- `required_evidence_classes[]`
- `required_publication_witness_policy_digest`
- `activation_frontier`
- `created_at_evidence_digest`
- canonical digest

A policy is not current merely because it is numerically newest. It is current only if there is an authenticated monotonic chain from the locally trusted predecessor to this generation.

### `TimeFloorRecoveryKeyStatusV1`

Append-only status statement:

- `policy_lineage_id`
- `key_id`
- `status = ACTIVE | RETIRED | SUSPECTED_COMPROMISE | COMPROMISED | DESTROYED`
- `effective_from_frontier`
- `known_compromise_start` or `UNKNOWN`
- `detected_at_frontier`
- `replacement_key_id` or `NONE`
- `reason_code`
- authorizing recovery-policy generation
- publication checkpoint/witness proof

Unknown compromise onset is never rounded optimistically to detection time.

### `TimeFloorPoisonEvidenceBundleV1`

Contains only evidence; it is not itself a verdict.

Required classes:

1. poisoned `TrustedTimeFloorV1` decision and its exact provenance;
2. exact routine time quorum samples that caused the floor advance;
3. source/key status history for every contributing source;
4. independent time evidence obtained after suspicion;
5. publication/activation frontier evidence;
6. relevant VM/snapshot/suspend/RTC continuity evidence;
7. network/operator/control-domain provenance for contributing and recovery sources;
8. divergence analysis and uncertainty bounds;
9. reproducible classification transcript.

### `TimeFloorPoisonAdjudicationV1`

Verdicts:

- `POISONING_PROVEN`
- `POISONING_NOT_PROVEN`
- `UNKNOWN_INSUFFICIENT_EVIDENCE`
- `UNKNOWN_CONFLICTING_EVIDENCE`
- `UNKNOWN_ADJUDICATOR_INDEPENDENCE`

Includes:

- exact evidence-bundle digest;
- exact policy generation;
- each adjudicator's signed individual verdict + rationale code;
- independence grouping;
- threshold closure;
- dissent artifacts;
- publication checkpoint.

No majority vote over implementation outputs substitutes for this adjudication.

### `TimeFloorRecoveryDecisionV1`

Only valid following `POISONING_PROVEN`.

Fields:

- poisoned floor digest/generation;
- adjudication digest;
- predecessor recovery-policy digest;
- proposed successor `TrustedTimeFloorV1` generation;
- conservative replacement interval `[lower, upper]`;
- chosen replacement floor and derivation rule;
- recovery signatures;
- independence proof;
- old/new policy authorization if policy transition is simultaneous;
- publication/witness checkpoint;
- supersedes relation, never deletion/rewrite.

---

## Key bootstrap and lifecycle

### Bootstrap

`TimeFloorRecoveryAuthorityV1` MUST originate from an out-of-band authenticated root or an already trusted higher-order governance root. A recovery policy discovered only from the same repository/log whose time state it may later revise is insufficient bootstrap evidence.

`TOFU` may exist for experimental/local deployments, but must be labelled `TOFU_LOCAL_RECOVERY_ROOT`; it is not equivalent to independently established authority.

### Ordinary rotation

For policy generation `R(n) -> R(n+1)`:

1. `R(n+1)` has generation exactly `n+1` and commits to `digest(R(n))`.
2. The transition payload is canonical and binds the complete new key set, thresholds, independence rules and activation frontier.
3. A threshold valid under **old `R(n)`** signs the exact transition.
4. A threshold valid under **new `R(n+1)`** signs the same exact transition.
5. Both threshold closures satisfy their own independence requirements.
6. The transition is appended to the transparency/publication history and witnessed before activation.
7. Intermediate policy generations remain retrievable forever for historical verification.

A successor policy cannot authorize itself if predecessor authorization is absent.

### Retirement

Normal retirement is prospective. A retired key may remain valid for historical decisions made while it was active, provided no compromise statement intersects that decision's authority frontier.

### Compromise

On suspected or confirmed compromise:

- affected keys immediately leave new-decision eligibility;
- recovery signing freezes if the remaining independent threshold cannot be met;
- a status statement is published append-only;
- if compromise onset is known, authority can be classified relative to that boundary;
- if onset is unknown, any historical decision whose safety depends on the key gets `UNKNOWN_HISTORICAL_RECOVERY_AUTHORITY` until independently re-adjudicated;
- replacing a compromised key still requires valid predecessor governance unless the predecessor threshold itself is compromised, in which case the explicit emergency path below is required.

---

## Poisoning adjudication: surprising is not poisoned

The following are **suspicion triggers only**:

- floor jump beyond configured operational expectations;
- RFC-5905-style panic-sized offset;
- one or more routine time sources later classified as compromised/falseticker;
- abrupt VM/snapshot restore anomaly;
- large disagreement with current local wall clock;
- operator assertion that "the year is obviously wrong".

`POISONING_PROVEN` requires evidence that defeats the original authority basis, not merely evidence that a different time is plausible.

Minimum proof shape:

1. Reconstruct the exact original floor-advance decision and show which inputs/keys/control domains caused it.
2. Establish at least one material defect in that authority basis, e.g.:
   - source key compromised before the sample;
   - source lost calibration before the sample;
   - quorum independence was false because enough sources shared one hidden control/upstream domain;
   - accepted packet/sample provenance does not match the signed authority;
   - implementation/classification bug deterministically accepted an excluded outlier;
   - publication/activation rollback caused stale authority to be treated as current.
3. Independently obtain replacement time evidence from a recovery set that does **not** share the defeated control domains.
4. Bound replacement uncertainty conservatively.
5. Obtain independent adjudicator threshold closure.

If the original decision looks bizarre but its authority basis cannot be disproven, result is `UNKNOWN_CONFLICTING_EVIDENCE`, not an automatic downward correction.

---

## Emergency governance

Emergency authority exists only for the case where ordinary recovery policy itself cannot safely authorize transition, such as compromise of enough recovery keys to break or capture the normal threshold.

### `EmergencyTimeRecoveryPolicyV1`

It MUST be separately bootstrapped before the emergency. It cannot be invented after the incident by the same actors requesting the correction.

Required properties:

- distinct key custody from ordinary recovery threshold;
- explicit organizational/control-domain independence requirements;
- higher or at least non-weaker effective threshold than routine recovery;
- mandatory recusal/conflict declarations;
- mandatory transparency publication before effect where system safety permits, otherwise immediate post-event publication with a bounded emergency window;
- narrow scope: only restore recovery governance and/or correct a specifically adjudicated poisoned floor;
- no authority to rewrite historical artifacts;
- activation produces a new generation and invalidates stale emergency attempts by monotonic generation/fencing.

### No "break glass = one admin" rule

Urgency is not a reason to collapse threshold security. NIST/RFC dual-control principles are used as donors: an emergency may change *which* independent authorities participate, but it must not convert a multi-party root of trust into unilateral operator authority.

### Correlated approvers

Numerical `k-of-n` is insufficient. At minimum record and threshold over:

- employer/organization;
- reporting/control chain;
- key/HSM custody;
- identity provider/account recovery domain;
- cloud/hosting/provider;
- network/jurisdiction where relevant;
- software/build lineage of signing clients;
- common legal/administrative authority capable of compelling all approvers simultaneously.

If the configured independence threshold cannot be proven, verdict is `UNKNOWN_RECOVERY_GOVERNANCE_INDEPENDENCE`.

---

## Conflicting valid recovery artifacts

Two signature-valid recovery artifacts can both satisfy their cryptographic thresholds yet disagree.

Define a stable slot:

`RecoverySlotV1 = (policy_lineage_id, poisoned_floor_digest, poisoned_floor_generation, adjudication_generation)`.

If two distinct recovery decisions occupy the same slot:

- same signer signs conflicting artifacts -> `RECOVERY_SIGNER_EQUIVOCATION_PROVEN`;
- two independent full quorums authorize incompatible decisions -> `RECOVERY_THRESHOLD_EQUIVOCATION_PROVEN`;
- verifier MUST NOT pick the lower floor, higher floor, newest timestamp, highest generation, or first-seen artifact automatically;
- both branches are preserved and published;
- current authority becomes `RECOVERY_FORK_DISPUTE_NO_MUTATION` until a later appeal/reconciliation generation resolves the fork under a policy whose authority is itself unambiguous.

The appeal/reconciliation result creates a new generation and explicit supersession edge. It never deletes the losing branch.

---

## Replacement-floor rule

Recovery is not permission to set arbitrary wall time.

The replacement must be derived from an independently supported interval. Default safe rule:

- compute an authenticated recovery interval `[L, U]` after uncertainty and transport bounds;
- ensure the interval is consistent with all retained monotonic publication/activation evidence that survived the poisoning event;
- choose a floor no lower than the strongest independently authenticated historical lower bound and no higher than the defensible recovery interval;
- encode the derivation in the recovery artifact;
- bump `TrustedTimeFloorV1.generation` even if the numeric floor decreases.

Thus monotonicity moves from raw numeric time to authenticated **generation/history**, allowing explicit correction without opening routine rollback.

---

## Fail-closed decision table

| Condition | Result |
|---|---|
| routine quorum says current floor is too high | no recovery authorization |
| local wall clock disagrees | suspicion only |
| panic-sized discrepancy | `POISON_SUSPECTED`, no mutation |
| original quorum defect proven but replacement quorum correlated | `UNKNOWN_RECOVERY_TIME_INDEPENDENCE` |
| poisoning proven, recovery signatures below threshold | `RECOVERY_UNAUTHORIZED` |
| signatures valid but policy generation not chained from predecessor | `RECOVERY_POLICY_CONTINUITY_FAILURE` |
| old policy signs rotation, new policy does not | `RECOVERY_POLICY_TRANSITION_INCOMPLETE` |
| new policy signs itself, old policy absent | `RECOVERY_POLICY_SELF_AUTHORIZATION` |
| key compromise onset unknown and decision depends on key | `UNKNOWN_HISTORICAL_RECOVERY_AUTHORITY` |
| two full valid recovery decisions conflict | `RECOVERY_FORK_DISPUTE_NO_MUTATION` |
| emergency policy created after incident with no prior authenticated root | `EMERGENCY_POLICY_UNTRUSTED` |
| valid recovery completed | new generation + explicit supersession; old poison record retained |

---

## Fraud / contradiction proof classes

1. `RecoveryPolicySelfAuthorizationProofV1`
2. `RecoveryPolicyRollbackProofV1`
3. `RecoveryKeyPostCompromiseUseProofV1`
4. `RecoveryKeyUnknownCompromiseDependencyProofV1`
5. `PoisonAdjudicationSelfOracleProofV1`
6. `PoisonEvidenceOmissionProofV1`
7. `RecoveryQuorumCorrelationProofV1`
8. `EmergencyGovernanceCaptureProofV1`
9. `RecoverySignerEquivocationProofV1`
10. `RecoveryThresholdEquivocationProofV1`
11. `UnsafeReplacementFloorProofV1`
12. `HistoricalRecoveryRewriteProofV1`

Each proof is append-only evidence; detection never authorizes an implicit state repair.

---

## RED-first executable matrix

Minimum exact executable suite before production integration:

### Policy/key lifecycle
1. valid old+new rotation succeeds;
2. new-only self-rotation fails;
3. old-only transition fails;
4. skipped intermediate generation fails;
5. replayed older policy fails;
6. retired key cannot sign new recovery;
7. pre-retirement historical signature remains classifiable;
8. known pre-decision compromise invalidates authority;
9. known post-decision compromise preserves bounded historical classification;
10. unknown compromise onset yields UNKNOWN where threshold depends on key.

### Poison adjudication
11. bizarre offset alone does not prove poisoning;
12. panic-sized offset alone does not mutate floor;
13. compromised original source + independent corroboration can prove poison;
14. correlated original sources are collapsed to one failure domain;
15. implementation bug reproduction can defeat original decision;
16. incomplete original provenance yields UNKNOWN, not poison proven;
17. replacement evidence sharing defeated domain is rejected;
18. conflicting independent evidence yields UNKNOWN;
19. adjudicator below threshold fails;
20. correlated adjudicators fail independence closure.

### Replacement safety
21. routine sample cannot lower trusted floor;
22. VM rollback cannot lower trusted floor;
23. cache/state deletion cannot lower trusted floor;
24. adjudicated recovery creates new generation;
25. old poisoned decision remains retrievable;
26. replacement below surviving authenticated lower bound fails;
27. replacement above evidence upper bound fails;
28. uncertainty omitted from replacement proof fails;
29. recovery generation replay fails;
30. stale verifier cannot reinterpret older poison generation as current.

### Emergency governance
31. pre-bootstrapped emergency policy can recover captured ordinary threshold;
32. incident-time invented emergency root fails;
33. one-admin break glass fails threshold;
34. same HSM/account domain masquerading as multiple approvers fails;
35. recused approver cannot count;
36. emergency action outside enumerated scope fails;
37. emergency generation replay fails;
38. emergency rotation that weakens threshold without predecessor authorization fails;
39. post-event publication omission fails finality;
40. emergency recovery retains all displaced policy/key history.

### Fork/equivocation
41. same signer signs two slot-conflicting recoveries -> signer equivocation proof;
42. two full conflicting quorums -> threshold equivocation proof;
43. verifier must not choose minimum timestamp;
44. verifier must not choose maximum timestamp;
45. verifier must not choose newest wall-clock timestamp;
46. verifier must not choose first-seen branch;
47. appeal creates new generation, does not rewrite either branch;
48. stale appeal policy fails continuity;
49. recovered branch must be transparency-published/witnessed;
50. losing branch remains independently verifiable.

### Crash/atomicity/publication
51. crash after adjudication before recovery leaves floor unchanged;
52. crash after recovery record before trusted-floor update reconciles deterministically;
53. crash after floor update before publication finality fails current-authority until reconciled;
54. duplicate identical recovery is idempotent;
55. duplicate different recovery in same slot becomes fork evidence;
56. publication rollback after recovery is rejected;
57. missing key-status history fails verification;
58. missing predecessor policy fails verification;
59. partial compromise notice cannot silently restore key authority;
60. decommissioned recovery infrastructure remains historically verifiable.

---

## Security decisions frozen

1. Recovery authority is a separate trust lineage, not another time source.
2. Recovery-policy rotation uses predecessor+successor authorization; successor self-authorization is forbidden.
3. Key compromise/revocation is append-only historical status with explicit uncertainty about compromise onset.
4. Large time disagreement is suspicion, not proof.
5. `POISONING_PROVEN` requires reconstruction and defeat of the original authority basis plus independent replacement evidence.
6. Routine and recovery quorums must not be controlled by the same failure domains when that shared control is material to the incident.
7. Emergency governance must be pre-bootstrapped and multi-party; urgency does not permit unilateral authority.
8. Conflicting valid recovery artifacts produce a fork/dispute state, never automatic min/max/LWW selection.
9. Recovery changes authenticated generation/history; it never rewrites the poisoned evidence.
10. Exact executable RED/GREEN proof is required before any production integration.

## Sources

- The Update Framework Specification v1.0.26, sections 5.3 and 6.1: root rotations require threshold signatures from both old and new root metadata, with sequential intermediate versions.
- NIST SP 800-57 Part 1 Rev. 5 (2020): key lifecycle, compromise/revocation/replacement, audit metadata and controlled historical verification.
- RFC 3628 (2003): TSA private-key lifecycle, compromise/loss-of-calibration handling, affected-token information, dual-control recovery for backed-up signing keys.
- RFC 5905 (2010): NTPv4 panic threshold; extremely large offsets are treated as probably bogus and trigger intervention rather than ordinary adjustment.

## Next evidence task

If LAB-086 exact source remains unavailable, research **recovery-policy transparency bootstrap / offline root custody / disaster loss of all ordinary+emergency recovery keys and governance-root reconstitution semantics**. The key question is whether total loss of every pre-authorized recovery signer can be recovered without silently inventing a new root of trust, and what evidence can distinguish legitimate organizational reconstitution from takeover.