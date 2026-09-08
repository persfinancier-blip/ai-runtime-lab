# LAB-093 — compromise adjudication transparency, witness quorum, quarantine review, recovery rotation, and adjudicator-compromise recursion v1

Status: `COMPROMISE_ADJUDICATION_TRANSPARENCY_WITNESS_QUORUM_QUARANTINE_REVIEW_RECOVERY_ROTATION_RECURSION_V1_FROZEN`

Date: 2026-09-08

## Scope

This freeze composes with the prior compromise-provenance/onset/false-revocation/recovery-independence contract. It answers four remaining questions:

1. how relying parties detect same-generation or selectively-served adjudication split views;
2. how an emergency quarantine receives bounded independent review without unsafe timer-based trust restoration;
3. how recovery/adjudication roots rotate without collapsing control-domain independence;
4. what happens when the authority that adjudicates compromise or authorizes recovery is itself compromised.

This is a design/evidence freeze only. It is not executable LAB-093 proof and does not relax the LAB-086 exact execution gate.

## Primary donors

- RFC 9162, Certificate Transparency v2: monitors/auditors verify append-only growth, inclusion and consistency; failed audits can yield signed evidence of log misbehavior. A consistency proof does not itself validate leaf semantics.
- transparency.dev witness model: a witness cosigns only checkpoints consistent with its previously accepted checkpoint; a quorum of independently controlled witnesses is used to resist split views. Witnesses attest log consistency, not truth of log contents.
- TUF specification: root metadata is versioned, rollback-protected, threshold-signed, and root rotation requires signatures satisfying both the predecessor root threshold and the successor root threshold. Offline root custody is recommended; threshold-root compromise requires exceptional recovery.
- Sigstore threat model: root-of-trust keys are threshold/offline and geographically/organizationally distributed; key compromise and compromise time are modeled explicitly; clients need freshness and transparency/audit mechanisms rather than assuming a single service is trustworthy.

## Core boundaries

```
VALID_ADJUDICATION_SIGNATURE
  != CURRENT_ADJUDICATION_AUTHORITY
  != GLOBALLY_CONSISTENT_ADJUDICATION_VIEW
  != SEMANTICALLY_CORRECT_ADJUDICATION

WITNESSED_CHECKPOINT
  != TRUE_ADJUDICATION_CONTENT

QUARANTINE_REVIEW_DEADLINE_EXPIRED
  != TRUST_RESTORED

RECOVERY_ROOT_ROTATED
  != RECOVERY_CONTROL_DOMAIN_ROTATED

ADJUDICATOR_COMPROMISED
  != COMPROMISED_ADJUDICATOR_MAY_SELF-RECOVER
```

A witness proves consistency of an authenticated append-only view. It does not prove that the adjudication itself is correct. Semantic appraisal and authority continuity remain separate gates.

## 1. Adjudication transparency and split-view detection

### 1.1 `AdjudicationStatementV1`

Every consequential compromise adjudication MUST have a canonical statement containing at least:

- `adjudication_lineage_id`;
- `generation`;
- `subject_authority_id` and subject generation/key digest;
- `decision`: `NO_COMPROMISE | QUARANTINE | REVOKE | RELIANCE_SCOPE_INVALIDATE | RECOVERED`;
- compromise onset interval and confidence class when applicable;
- evidence digest set and counter-evidence digest set;
- appraisal-policy digest/generation;
- adjudicator-set identity and threshold policy digest;
- decision scope and affected operation classes;
- predecessor adjudication digest;
- issuance time/freshness bounds;
- canonical statement digest and required signatures.

The statement MUST be immutable once accepted. Corrections occur through a successor generation, never by mutation.

### 1.2 `AdjudicationTransparencyReceiptV1`

A transparency receipt binds the exact `AdjudicationStatementV1` digest into an append-only checkpoint. The receipt is historical evidence of publication, not semantic truth.

### 1.3 `AdjudicationWitnessCheckpointV1`

A relying party SHOULD require a policy-defined witness quorum for high-impact adjudications. A witness checkpoint contains:

- log identity and checkpoint tree size/root;
- consistency relation to the witness's previous accepted checkpoint;
- witness identity/key generation;
- witness signature;
- optional witness-control-domain metadata for independence appraisal.

Witness quorum is counted only after independence appraisal. Multiple keys, processes, regions or legal entities under one destructive/control domain do not automatically count as multiple independent witnesses.

### 1.4 Same-generation conflict rule

For one `adjudication_lineage_id` and one generation:

```
same generation + different authenticated statement digest
=> ADJUDICATION_EQUIVOCATION_CONFLICT
=> no positive current reliance
```

Forbidden conflict resolution:

- latest wall-clock timestamp;
- last-write-wins;
- first-seen wins;
- majority CDN endpoint;
- majority copies where copies share one control domain;
- choosing the statement with the larger tree size without proving consistency and semantic succession.

A witness quorum over one branch is useful evidence, but if another independently authenticated same-generation branch is later discovered, the state becomes conflict/equivocation until a higher-generation authorized resolution consumes both branches.

### 1.5 Witness compromise

Witness signatures are themselves authority-bearing evidence and therefore have key lifecycle, freshness, rotation and compromise semantics. A witness compromised inside the quorum policy cannot silently remain counted forever. If post-facto compromise reduces the historically used quorum below the policy threshold for current reliance, the historical checkpoint remains recorded but current reliance is re-appraised.

## 2. Emergency quarantine review liveness

### 2.1 Separation of containment and permanent authority mutation

A credible single detector MAY trigger a scoped fail-closed quarantine when delay would create unacceptable security exposure. This action is deliberately easier than permanent/global revocation.

A quarantine record MUST include:

- trigger evidence digest;
- detector authority/generation;
- exact scope;
- start generation/time;
- review policy and review deadline;
- required independent reviewer set/threshold;
- explicit prohibited and permitted operation classes;
- escape/recovery conditions.

### 2.2 Timer semantics

A review deadline is a liveness obligation, not a trust-restoration timer.

```
review deadline expires without sufficient review
=> QUARANTINE_REVIEW_OVERDUE
=> quarantine remains fail-closed for prohibited operations
```

Trust MUST NOT auto-restore merely because the detector disappeared, the incident ticket aged out, or a wall-clock TTL elapsed.

### 2.3 Anti-permanent-DoS review path

To prevent one malicious detector from creating irreversible global denial of service, the policy MUST provide an independent bounded review path:

- detector cannot be the sole reviewer;
- reviewer threshold/control domains are separate from the triggering detector where feasible;
- reviewer can affirm, narrow, supersede, or convert quarantine into global revocation/recovery;
- reviewer cannot erase the original trigger evidence/receipt;
- failure to achieve review is visible as a degraded governance/liveness state rather than silently becoming trusted.

For essential availability, policy MAY define a restricted degraded mode while quarantine remains unresolved, but the allowed operation classes must be explicitly pre-authorized and must not include the authority-changing action under investigation.

### 2.4 Review freshness

A positive review is valid only against the current evidence/adjudication frontier. New contradiction or compromise evidence appearing after the review invalidates the assumption that the old review closes the case.

## 3. Recovery-authority rotation ceremony

### 3.1 `RecoveryAuthorityGenerationV1`

Recovery/adjudication root generations are versioned and hash-linked. Each generation commits:

- root lineage ID;
- generation number;
- key IDs/public keys;
- signing threshold;
- control-domain/custody declarations;
- permitted recovery scopes;
- predecessor digest;
- activation and expiry/freshness bounds;
- ceremony evidence digest;
- transparency receipt/checkpoint references.

### 3.2 Normal rotation

Normal rotation follows a two-sided continuity rule analogous to TUF root update:

```
valid successor generation
= predecessor-threshold authorization
+ successor-threshold authorization
+ monotonic generation
+ predecessor digest continuity
+ no unresolved same-generation conflict
```

The successor cannot become trusted merely because the new keys sign themselves.

### 3.3 Independence-preserving ceremony

Rotation MUST preserve the required independence properties, not just key count. The ceremony evidence should cover, where applicable:

- which operators/key custodians participated;
- control/destructive domains;
- HSM/offline media identifiers or equivalent custody class;
- threshold achieved;
- old-to-new authorization payload digest;
- confirmation that no one actor controlled enough predecessor and successor shares to defeat the policy;
- publication/transparency checkpoint.

A rotation that moves five keys to five fresh keys all controlled by the same compromised automation account is cryptographically fresh but governance-invalid.

### 3.4 Planned retirement vs compromise recovery

Planned rotation may use normal predecessor+successor continuity. If the predecessor threshold is suspected or proven compromised, predecessor authorization no longer proves safe succession. The process MUST switch to an exceptional recovery path rooted in a separately authorized recovery mechanism established before the incident or, if that continuity is also lost, to the previously frozen external rebootstrap/new-lineage path.

## 4. Adjudicator-compromise recursion

### 4.1 The recursion problem

If adjudicator A decides whether source authority S is compromised, then compromise of A cannot be safely resolved solely by A. Otherwise the compromised authority controls the statement that it is still trustworthy and the statement installing its replacement.

### 4.2 Layered authority model

Freeze these distinct roles:

- `SUBJECT_AUTHORITY`: ordinary source/promise/inventory/etc. authority being judged;
- `COMPROMISE_EVIDENCE_PRODUCER`: produces incident evidence;
- `ADJUDICATION_AUTHORITY`: appraises evidence and authorizes global consequence;
- `RECOVERY_ROOT`: authorizes replacement of adjudication/recovery authority;
- `TRANSPARENCY_LOG`: makes statements auditable/append-only;
- `WITNESS_QUORUM`: protects against inconsistent log views;
- `RELYING_PARTY`: performs local appraisal and current-reliance decision.

No layer alone proves every other layer trustworthy.

### 4.3 Compromised adjudicator response

When adjudicator compromise is credibly signaled:

1. locally quarantine positive reliance on new adjudicator statements inside the affected time/key scope;
2. preserve historical statements and receipts;
3. obtain compromise adjudication from the separately authorized recovery/adjudicator-supervision root or external recovery lineage;
4. determine an evidence-backed compromise-onset interval;
5. re-appraise adjudications whose trust depended on the affected adjudicator during that interval;
6. rotate/recover the adjudication authority through an authorized generation transition;
7. publish the recovery transition and invalidation/re-appraisal statements into transparency;
8. require witness/checkpoint consistency and relying-party frontier catch-up before restoring current positive reliance.

The compromised adjudicator key MUST NOT be sufficient to authorize its own trusted successor.

### 4.4 Recovery-root compromise

If the recovery root itself reaches threshold compromise, there is no safe recursive self-heal inside the same lineage unless an independently established higher/out-of-band recovery anchor exists. The system MUST NOT fabricate continuity. It composes with the previously frozen total-loss/external-rebootstrap contract:

```
recovery-root threshold compromise
+ no independent higher recovery continuity
=> SAME-LINEAGE_RECOVERY_UNPROVEN
=> external rebootstrap / new trust lineage
```

Identity continuity of product name/hostname does not imply cryptographic continuity of authority lineage.

## 5. Relying-party state machine

Minimum current states:

- `ADJUDICATION_CURRENT_VALID`
- `ADJUDICATION_CURRENT_VALID_WITNESSED`
- `ADJUDICATION_QUARANTINE_PENDING_REVIEW`
- `ADJUDICATION_QUARANTINE_REVIEW_OVERDUE`
- `ADJUDICATION_EQUIVOCATION_CONFLICT`
- `ADJUDICATION_CURRENT_STATUS_UNKNOWN_MISSED_INTERVAL`
- `ADJUDICATOR_COMPROMISE_SIGNALLED_LOCAL_QUARANTINE`
- `ADJUDICATOR_COMPROMISE_APPRAISED`
- `ADJUDICATOR_RECOVERY_IN_PROGRESS`
- `ADJUDICATOR_RECOVERED_NEW_GENERATION`
- `RECOVERY_ROOT_COMPROMISE_SAME_LINEAGE_UNPROVEN`

Transitions are monotonic in durable evidence generation. A previously observed higher generation, invalidation or equivocation cannot be forgotten by loading an older cached state.

## 6. Fraud / contradiction classes

Freeze at least these contradiction proofs:

1. `SAME_GENERATION_DIFFERENT_ADJUDICATION_DIGEST`
2. `CHECKPOINT_INCONSISTENT_WITH_PREVIOUS_WITNESSED_PREFIX`
3. `WITNESS_QUORUM_CONTROL_DOMAIN_COLLAPSE`
4. `WITNESS_KEY_COMPROMISE_REDUCES_CURRENT_QUORUM`
5. `UNWITNESSED_HIGH_IMPACT_ADJUDICATION_WHERE_POLICY_REQUIRES_WITNESSING`
6. `QUARANTINE_AUTO_RESTORE_ON_TIMER`
7. `QUARANTINE_TRIGGERING_DETECTOR_SOLE_GLOBAL_REVOKER`
8. `QUARANTINE_TRIGGERING_DETECTOR_SOLE_REVIEWER`
9. `STALE_REVIEW_USED_AFTER_NEW_CONTRADICTION`
10. `RECOVERY_SUCCESSOR_SELF_AUTHORIZED_ONLY`
11. `RECOVERY_ROTATION_GENERATION_ROLLBACK`
12. `RECOVERY_ROTATION_SKIPS_REQUIRED_INTERMEDIATE_GENERATION`
13. `RECOVERY_CONTROL_DOMAIN_COLLAPSE_DESPITE_NEW_KEYS`
14. `COMPROMISED_PREDECESSOR_USED_AS_SOLE_RECOVERY_AUTHORIZATION`
15. `ADJUDICATOR_SELF_ATTESTS_OWN_NON_COMPROMISE_AS_SUFFICIENT`
16. `ADJUDICATOR_SELF_AUTHORIZES_TRUSTED_SUCCESSOR_AFTER_COMPROMISE`
17. `RECOVERY_ROOT_THRESHOLD_COMPROMISE_MISREPRESENTED_AS_NORMAL_ROTATION`
18. `OLD_CACHED_ADJUDICATION_REINTRODUCED_AFTER_HIGHER_INVALIDATION`

## 7. RED-first matrix (48 cases)

### A. Transparency / split view

1. same generation, same digest, valid signatures -> accept one semantic statement;
2. same generation, different digest -> conflict;
3. higher generation with valid predecessor continuity -> eligible for appraisal;
4. higher generation without predecessor continuity -> reject;
5. lower generation after higher trusted frontier -> rollback reject;
6. valid transparency receipt without semantic authority -> reject current reliance;
7. valid semantic authority without policy-required transparency -> fail closed/degraded;
8. one witness signs consistent checkpoint -> append-only evidence only;
9. required quorum of independent witnesses -> witnessed status;
10. quorum numerically satisfied but one control domain -> independence failure;
11. witness signs checkpoint inconsistent with its prior checkpoint -> contradiction;
12. later same-generation alternate branch discovered -> reopen/conflict.

### B. Emergency quarantine / review liveness

13. credible single detector triggers scoped quarantine -> allowed;
14. single detector attempts permanent global revocation without authority -> reject global mutation;
15. review deadline passes unresolved -> remains quarantined + overdue;
16. TTL expires -> no auto restore;
17. detector offline -> no auto restore;
18. independent review affirms quarantine -> remain/narrow as decided;
19. independent review clears based on current evidence -> successor decision may restore permitted reliance;
20. new contradiction arrives after clearing review -> reopen;
21. triggering detector is sole reviewer -> reject review sufficiency;
22. review threshold same nominal identities but shared control domain -> reject independence;
23. degraded-mode operation explicitly pre-authorized and outside affected authority class -> allow restricted mode;
24. degraded-mode attempt includes affected consequential authority mutation -> reject.

### C. Recovery rotation ceremony

25. predecessor threshold + successor threshold + generation continuity -> normal rotation eligible;
26. successor signs itself only -> reject;
27. predecessor only signs new root, successor threshold absent -> reject;
28. generation rollback -> reject;
29. skipped generation when policy requires sequential chain -> reject;
30. five new keys but one compromised custody domain -> independence failure;
31. planned retirement with intact predecessor -> normal rotation path;
32. predecessor threshold compromise known -> normal predecessor authorization insufficient;
33. exceptional independent recovery root authorizes replacement -> recovery eligible;
34. ceremony evidence digest differs across same generation -> equivocation;
35. historical retired public verification material retained -> past verification remains possible subject to compromise scope;
36. rotation deletes unresolved compromise obligations -> reject clean-slate laundering.

### D. Adjudicator compromise recursion

37. adjudicator compromise signal -> local quarantine of affected positive reliance;
38. adjudicator asserts itself healthy using same suspect key -> insufficient;
39. independent recovery root appraises adjudicator compromise -> eligible global consequence;
40. compromised adjudicator self-authorizes successor -> reject;
41. recovered successor with valid exceptional recovery chain -> eligible;
42. late compromise onset overlaps prior adjudication -> current reliance on affected adjudication invalidated/re-appraised;
43. late compromise onset provably after prior adjudication -> preserve unaffected reliance if no other contradiction;
44. compromise onset uncertain around prior adjudication -> current reliance unknown/fail-closed for affected scope;
45. recovery root itself below-threshold compromise -> rotate/revoke compromised shares under intact root threshold;
46. recovery-root threshold compromise with independent higher recovery anchor -> use higher recovery path;
47. recovery-root threshold compromise without independent higher anchor -> same-lineage recovery unproven;
48. external rebootstrap creates new lineage -> do not mislabel as ordinary same-lineage successor.

## 8. Implementation implications for eventual LAB-093 RED/GREEN

The eventual executable implementation should avoid a single god-object for adjudication/recovery. Minimal coherent surfaces should separate:

- canonical statement construction;
- authority-generation verification;
- transparency receipt/checkpoint verification;
- witness quorum/independence appraisal;
- quarantine state/review transitions;
- recovery-root transition verification;
- current-reliance appraisal.

Tests should inject split views, witness/control-domain collapse, stale review, compromised adjudicator and recovery-root loss at the same abstraction level as the corresponding state transition. Do not accept mocked success tokens as sole proof that an external authority transition occurred.

## Decision

Freeze `COMPROMISE_ADJUDICATION_TRANSPARENCY_WITNESS_QUORUM_QUARANTINE_REVIEW_RECOVERY_ROTATION_RECURSION_V1_FROZEN`.

The key security result is that transparency, review liveness and recovery recursion are separate dimensions: witnessing prevents hidden divergent history; independent review prevents emergency quarantine from becoming unilateral permanent governance; two-sided recovery rotation preserves continuity; and compromise of the adjudicator/recovery layer cannot be healed by trusting that same compromised layer. If the final independent recovery root is lost, the truthful result is a new trust lineage rather than fabricated continuity.

## Exact next research fallback if executable LAB-086 remains unavailable

Define **adjudication/recovery authority freshness distribution and offline relying-party catch-up under witness/key rotations**, including witness-set membership authority, quorum-policy rotation, stale witness checkpoint handling, cross-log checkpoint anchoring, and how an offline relying party reconstructs all security-relevant adjudication/recovery transitions without accepting a selectively truncated history.