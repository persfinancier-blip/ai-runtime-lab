# Emergency-root custody, promise compaction, multi-beacon sampling, copy-domain reconciliation, and PQ attestation recovery v1

Date: 2026-09-09
Status: FROZEN DESIGN EVIDENCE — not executable proof
Issue family: LAB-093/#178 follow-up; LAB-086 remains priority #1

## Scope and boundary

This note executes the exact distinct fallback recorded in `state/CURRENT.md` while the LAB-086 exact-source executable gate remains unavailable in the current runtime. A direct `git clone --no-checkout` was re-probed before this work and failed before repository execution with `Could not resolve host: github.com` (exit 128). GitHub connector read/write remains available.

This design freeze does **not** replace LAB-086 real-schema RED/GREEN execution, the unsafe expected-failure seed, compileall, security/reconciliation audit, or branch/main conflict audit. No new behavioral/compile PASS is claimed here.

Frozen contract name:

`EMERGENCY_ROOT_PROMISE_COMPACTION_MULTIBEACON_COPYDOMAIN_PQ_ATTESTATION_V1_FROZEN`

The contract extends the retained evidence architecture across five boundaries:

1. emergency-root custody-domain independence and dormant-key liveness;
2. promise-frontier compaction/renewal without obligation loss;
3. multi-beacon composition, selective abort, and last-revealer bias;
4. reconciliation of mutually inconsistent copy-domain topology authorities;
5. PQ provenance-attestation key compromise/revocation and negotiation-transcript anti-equivocation.

## Primary donors checked

### Key custody, recovery, and compromise

- NIST SP 800-57 Part 1 Rev. 5, final: key lifecycle, backup/archive/recovery, compromise recovery, and the availability-vs-compromise tradeoff created by extra key copies.
  - https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
  - https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf
- Sigstore threat model: TUF-based root material supports offline/threshold root keys, rotation, revocation with compromise time, and freshness against rollback; Sigstore explicitly treats root/key-distribution compromise as a separate failure domain.
  - https://docs.sigstore.dev/about/threat-model/

### Transparency / outstanding promises

- RFC 9162, Certificate Transparency Version 2.0: signed tree heads, inclusion/consistency proof semantics, append-only auditability, and bounded signed inclusion promises.
  - https://www.rfc-editor.org/rfc/rfc9162

### Public randomness

- NIST IR 8213 draft: randomness pulses are timestamped, signed, hash-chained; a pulse can pre-commit to the randomness released in a later pulse, specifically enabling secure combination of randomness from different beacons.
  - https://csrc.nist.gov/pubs/ir/8213/ipd
- NIST Randomness Beacon v2 project: pulse sequencing, signatures and previous-pulse hash make retroactive pulse rewriting detectable.
  - https://csrc.nist.gov/Projects/interoperable-randomness-beacons/beacon-20
- drand protocol/security documentation: a beacon output is a threshold BLS signature; for a fixed distributed group public key/round, future outputs are determined after DKG, and post-DKG bias requires compromising the group-key assumption rather than choosing among individual partial signatures.
  - https://docs.drand.love/docs/specification/
  - https://docs.drand.love/docs/cryptography/

### Provenance, revocation, and PQ transition

- SLSA Dependency Provenance draft: stronger levels authenticate provenance and use transparency logging so verifiers can detect signing-key compromise; provenance records what a platform claims, while verifiers separately apply policy.
  - https://slsa.dev/spec/draft/dependency-provenance
- Sigstore threat model: TUF distributes trusted key material, supports threshold root signing, rotation and revocation, and can attach compromise time so legitimate pre-compromise signatures remain separately evaluable.
  - https://docs.sigstore.dev/about/threat-model/
- NIST IR 8547 initial public draft: migration states distinguish acceptable, deprecated, disallowed, and legacy-use algorithms; historical verification and authorization for new consequential operations are not the same policy decision.
  - https://csrc.nist.gov/pubs/ir/8547/ipd
- NIST crypto-agility work: algorithm replacement is an operational lifecycle capability and must preserve interoperability and security rather than becoming an implicit downgrade path.
  - https://www.nist.gov/news-events/news/2025/03/considerations-achieving-crypto-agility-nist-releases-cswp-39-public

## Facts vs lab inference

### Facts from donors

- Key recovery/availability creates additional custody and compromise surface; compromise recovery requires revocation/replacement and does not erase the historical compromise event.
- Transparency-style promises retain meaning through authenticated checkpoints and consistency evidence; failed lookup is not positive proof that an obligation vanished.
- A public randomness pulse can be authenticated and chained; interoperable beacon designs can pre-commit and combine values from multiple sources.
- Threshold-signature beacon protocols can eliminate a classic single-party last-revealer choice for a fixed round once the threshold key/group and message are fixed, but an application can still bias its **use** of beacons through selective source/round inclusion, timeout/fallback choice, or abort policy.
- Provenance/signature verification authenticates a binding under a key and policy. It does not by itself prove that the signer/build system was uncompromised or that the semantic claim is correct.
- PQ transition policy may allow legacy historical verification while disallowing the same legacy algorithm for new protection/authorization.

### Lab inference / design decision

Evidence assurance is defined by authenticated historical policy plus independently survivable authority, completeness, anti-rollback and anti-equivocation state. A clean successor may restore future eligibility; it cannot silently strengthen, erase, compact away, or reinterpret predecessor evidence.

---

# 1. Emergency-root custody-domain independence and dormant-key liveness

## Required object

`EmergencyRootGeneration` MUST bind at least:

- `root_generation_id` and predecessor;
- exact public-key/member identities and threshold/denominator;
- custody-domain identities and independence claims;
- storage mode per member: offline/HSM/removable/etc.;
- authenticated activation/recovery policy;
- anti-rollback floor and successor rule;
- liveness-test policy and maximum accepted test age;
- liveness challenge transcript digest(s);
- compromise/revocation records and effective times;
- break-glass activation boundary and required independent approvers;
- canonical serialization/version.

## Frozen rules

1. **`N_KEYS != N_INDEPENDENT_CUSTODY_DOMAINS`.** Multiple root keys held by the same organization, HSM cluster, administrator plane, vault tenancy, backup system or disaster domain count as correlated for independence claims unless separately evidenced.
2. **Emergency authority must pre-exist the incident.** An emergency root first introduced after incumbent compromise cannot bootstrap trust for that same incident.
3. **Dormant does not imply live.** A never-used offline key may be uncompromised yet unusable, corrupted, inaccessible, algorithmically unsupported or operationally unrecoverable.
4. **Liveness proof is challenge-bound and non-authorizing.** A scheduled liveness exercise proves that the exact key/custody path could authenticate a harmless challenge under the then-current policy; it MUST NOT itself authorize a recovery or production mutation.
5. **Liveness tests need freshness policy.** A five-year-old successful test is not automatically sufficient evidence that the dormant path is available now. Maximum age is authenticated policy.
6. **No secret reconstruction for routine liveness.** Threshold/offline custody should test via member-local signature/share/proof where possible; do not centralize private material merely to prove availability.
7. **Backup root copies expand the denominator of destruction/compromise accounting.** Backup/archive copies that can recover root authority are part of custody topology and cannot be hidden from the independence claim.
8. **Compromise/revocation is monotonic history.** Rotation to a clean root restores future authority but does not make evidence created during a compromised generation clean.
9. **Freshness resists rollback.** Recovery verification MUST reject old but correctly signed root metadata below the accepted monotonic floor/current root generation.
10. **Recovery quorum must be independent of the compromised plane.** If the same control plane that is being recovered can rewrite the root policy, liveness records, or denominator, the recovery path is not independent.

Canonical states:

- `EMERGENCY_ROOT_READY`
- `EMERGENCY_ROOT_LIVENESS_STALE`
- `EMERGENCY_ROOT_CUSTODY_CORRELATED`
- `EMERGENCY_ROOT_UNAVAILABLE`
- `EMERGENCY_ROOT_COMPROMISED`
- `EMERGENCY_ROOT_ROLLBACK`
- `EMERGENCY_ROOT_POSTINCIDENT_BOOTSTRAP_REJECTED`

---

# 2. Promise-frontier compaction and renewal without obligation loss

## Problem

A growing authenticated outstanding-promise frontier cannot remain forever as an unbounded flat set, but compaction itself is a dangerous authority operation: an omitted unresolved promise can disappear while the compacted root still looks internally valid.

## Required object

`PromiseFrontierCompactGeneration` MUST bind:

- predecessor frontier generation/root;
- exact covered promise-ID namespace/range or canonical partition map;
- predecessor accepted-count and disposition counts;
- commitments for fulfilled, outstanding, explicitly voided/adjudicated classes;
- all unresolved deadline classes;
- compaction algorithm/version;
- carry-forward commitment/root for still-outstanding promises;
- authenticated proof that every predecessor member has exactly one successor disposition;
- witness/checkpoint policy epoch;
- successor frontier generation and anti-rollback floor.

## Frozen rules

1. **Compaction is a successor generation, never destructive mutation.** Keep the predecessor commitment/checkpoint sufficient to audit the transformation.
2. **Conservation law:** every predecessor promise MUST map to exactly one authenticated disposition: `FULFILLED`, `OUTSTANDING_CARRIED`, or an explicitly policy-valid terminal disposition such as `VOID_ADJUDICATED`.
3. **`OLD_COUNT == NEW_COUNTS` is necessary but insufficient.** Counts alone permit substitution. The transform must be bound to exact promise identities or an authenticated set/accumulator relation.
4. **Outstanding promises cannot be summarized away before their deadlines/terminal adjudication.** A compact archive that retains only aggregate counts is insufficient for later omission proof.
5. **Fulfillment must bind the exact original promise.** A fulfillment row/proof for promise B cannot satisfy promise A merely because they share subject/deadline fields.
6. **Compaction cannot reset deadline age.** Carrying an old promise into a new frontier does not grant a new MMD/deadline unless the original promise policy explicitly allowed authenticated renewal accepted by the claimant.
7. **Renewal is bilateral/authorized where semantics change.** If a promise deadline or scope changes, the successor must bind claimant/issuer approvals required by the old policy; unilateral log-side renewal is not allowed.
8. **Anti-omission verification spans generations.** A verifier can start from a historical accepted promise and follow a deterministic authenticated chain through each compaction to fulfillment/outstanding/terminal disposition.
9. **No proof by failed lookup.** If the compaction archive cannot answer membership/path evidence for a historical promise, status is `PROMISE_COMPACTION_UNVERIFIABLE`, not “fulfilled/expired.”
10. **Same predecessor, conflicting compacted roots are equivocation unless an authenticated fork-adjudication rule exists.**

Canonical states:

- `PROMISE_COMPACTION_VALID`
- `PROMISE_COMPACTION_OMISSION`
- `PROMISE_COMPACTION_DUPLICATE_DISPOSITION`
- `PROMISE_COMPACTION_SUBSTITUTION`
- `PROMISE_DEADLINE_RESET_REJECTED`
- `PROMISE_COMPACTION_EQUIVOCATION`
- `PROMISE_COMPACTION_UNVERIFIABLE`

---

# 3. Multi-beacon composition, selective abort, and last-revealer bias

## Required object

`MultiBeaconSamplingGeneration` MUST bind before outputs are decision-selectable:

- exact beacon/source population and source identities;
- source key/group epochs;
- fixed round-selection rule per source;
- minimum required source set/threshold;
- timeout/deadline policy;
- missing-source handling;
- composition function/version and domain separator;
- fallback/abort policy;
- precommit/chaining expectations;
- authenticated transcripts of all source pulses/absence evidence;
- final composed seed and deterministic sample algorithm/version.

## Frozen rules

1. **`MULTI_SOURCE != MULTI_SOURCE_INDEPENDENT`.** Source count is not independence; common operators, DKG participants, infrastructure, upstream entropy or administration may correlate failures.
2. **Composition policy commits before reveal.** The evaluator cannot choose which beacon outputs to combine after seeing them.
3. **Do not use “first favorable subset wins.”** Trying subsets/rounds until the selected audit sample is convenient is post-output grinding.
4. **Selective abort is part of the threat model.** Even if every individual pulse is unbiased, a party that may decide after seeing partial outputs whether to wait, abort, retry, or fall back can bias the final application outcome.
5. **A fixed-threshold BLS beacon reduces classic last-share reveal choice for its own fixed round.** Once group key/message are fixed, partial signers do not get to choose among many valid aggregate signatures; however availability withholding remains possible and application-level fallback can reintroduce bias.
6. **Precommit helps cross-beacon composition.** Where a beacon commits in pulse r to material released later, composition can require those commitments before another source's corresponding value is usable, reducing adaptive source selection.
7. **Fallback is pre-policy.** A local RNG or alternate beacon is permissible only if the exact fallback trigger and composition semantics were committed before observing decision-relevant outputs.
8. **Missing source is not silently zero.** `H(A || 0)` after B disappears is a new composition rule and must be precommitted; otherwise status is `MULTIBEACON_INCOMPLETE`.
9. **At least-one-good-source claims require a combiner with stated assumptions.** The lab will not assert “unbiased if any source is honest” unless the exact combiner, independence assumption, precommit/availability model, and adversarial scheduling model support that statement.
10. **Historical beacon compromise degrades dependent samples.** A later clean beacon epoch cannot retroactively strengthen a sample whose source epoch is proven compromised or adaptively selectable.

Canonical states:

- `MULTIBEACON_SAMPLE_VALID`
- `MULTIBEACON_SOURCE_CORRELATED`
- `MULTIBEACON_POSTREVEAL_SUBSET_SELECTION`
- `MULTIBEACON_SELECTIVE_ABORT_BIAS`
- `MULTIBEACON_INCOMPLETE`
- `MULTIBEACON_FALLBACK_REBOUND`
- `MULTIBEACON_SOURCE_EPOCH_COMPROMISED`

---

# 4. Copy-domain topology discovery reconciliation across inconsistent authorities

## Problem

The retained `CopyDomainUniverse` design allows multiple topology/configuration/inventory/audit sources. Those sources can disagree. Blind union overstates active domains; blind intersection hides possible copies. A “preferred CMDB wins” rule lets one compromised authority erase negative-space obligations.

## Required object

`CopyDomainReconciliationGeneration` MUST bind:

- predecessor universe/reconciliation generation;
- exact participating authority/source identities and trust/failure domains;
- signed/authenticated source snapshots with observation intervals;
- normalized domain identity mapping rules;
- per-domain source assertions (`PRESENT`, `ABSENT`, `UNKNOWN`, `RETIRED`, `POSSIBLE`);
- conflict set and provenance;
- reconciliation policy/version;
- domain activation/retirement evidence;
- unresolved negative-space cells;
- adjudicator/quorum identity where human/authority adjudication is required.

## Frozen rules

1. **Source conflict is evidence, not noise.** Contradictory authenticated topology assertions are retained and surfaced as `COPY_TOPOLOGY_CONFLICT` until resolved.
2. **For destruction/completeness claims, unresolved `PRESENT` or `POSSIBLE` dominates an `ABSENT` claim.** This is a fail-closed coverage rule, not a declaration that the copy definitely exists.
3. **Absence needs source authority over the relevant domain and interval.** A compute inventory cannot prove that an offline backup vault has no copy unless its authenticated scope actually covers that vault.
4. **Retirement needs closure evidence.** A domain marked retired by one source remains relevant until the policy-required sources/adjudication prove the copy path was closed and historical retained copies were handled.
5. **No silent ID aliasing.** Two names/ARNs/paths may be the same physical/control domain or distinct domains. Identity reconciliation itself is versioned evidence.
6. **Reconciliation is interval-aware.** Sources sampled at different times cannot be compared as if simultaneous; topology transition events may legitimately explain differences.
7. **Authority compromise is scoped and monotonic.** A compromised topology authority degrades claims depending uniquely on it for the affected interval; successor clean authority does not retroactively observe the past.
8. **Union/intersection are not universal policies.** The chosen rule depends on claim type. Destruction negative-space defaults to fail-closed superset coverage; replica-independence requires proven distinct control/destructive domains, not union count.
9. **Adjudication produces a successor generation.** Do not rewrite the losing source snapshot; preserve conflict provenance.
10. **Completeness requires coverage of unknown cells.** A reconciled universe with unresolved `UNKNOWN`/uncovered domain×time cells cannot support `ALL_COPY_DOMAINS_ACCOUNTED_FOR`.

Canonical states:

- `COPY_UNIVERSE_RECONCILED`
- `COPY_TOPOLOGY_CONFLICT`
- `COPY_DOMAIN_IDENTITY_AMBIGUOUS`
- `COPY_DOMAIN_RETIREMENT_UNPROVEN`
- `COPY_TOPOLOGY_AUTHORITY_COMPROMISED`
- `NEGATIVE_SPACE_RECONCILIATION_INCOMPLETE`

---

# 5. PQ provenance-attestation key compromise/revocation and negotiation anti-equivocation

## Required object

`PQAttestationTrustGeneration` MUST bind:

- predecessor trust generation;
- provenance-attestation signer/build-platform identities and key epochs;
- attestation transparency-log identity/checkpoint policy where used;
- exact compromise/revocation records with effective/known times;
- trusted root/TUF-style metadata generation and anti-rollback floor;
- builder/parser/canonicalizer/crypto/verifier provenance requirements;
- hybrid/PQ algorithm policy and effective boundaries;
- exact local offer, peer offer, selected suite and fallback reason;
- negotiation transcript commitment and peer/local transcript signatures where available;
- verifier implementation/failure-domain requirements;
- canonical serialization/version.

## Frozen rules

1. **A valid provenance signature from a later-compromised key is not automatically clean.** Evaluation is time/epoch/policy scoped; compromise time and transparency evidence determine whether historical attestations remain eligible, degraded, or rejected.
2. **Revocation metadata itself needs freshness and anti-rollback.** An attacker cannot restore a revoked provenance key by replaying an older correctly signed trust-root snapshot.
3. **Transparency preserves detection evidence but not semantic correctness.** A logged malicious attestation is still malicious; log inclusion proves public commitment/existence, not trustworthiness.
4. **`SBOM_PRESENT != BUILD_TRUSTED`.** The SBOM/attestation must bind the exact executable/build and trusted builder identity; a compromised builder can honestly describe a malicious build.
5. **Re-attesting unchanged bytes with a clean successor key does not repair compromised build provenance.** A fresh rebuild/reverification under independently trusted provenance is needed where policy requires semantic/build recovery.
6. **Negotiation has two views.** A complete transcript binds what each party claims it offered/received plus the selected suite. A single endpoint's self-authored transcript is insufficient to prove that the peer offered no stronger algorithm.
7. **Conflicting authenticated transcripts are positive equivocation evidence.** If one session identity/nonce has two incompatible offer/selection transcripts, fail closed as `NEGOTIATION_EQUIVOCATION` pending adjudication.
8. **Transcript completeness is explicit.** Hashing only the selected cipher/signature suite cannot detect stripping of stronger offers; offers, policy epochs, fallback/error paths and binding session context must be committed.
9. **Deprecated/disallowed boundaries affect new authorization, not necessarily historical verification.** Policy may continue to verify archived classical signatures as legacy evidence while forbidding them from authorizing a new migration.
10. **Verifier diversity remains by implementation/failure domain.** Multiple processes sharing the same parser/crypto build are one correlated verifier for diversity claims.
11. **Revocation cannot erase already observed equivocation.** A clean successor signer or transcript policy restores future eligibility only.
12. **Crypto agility must be monotonic against downgrade.** Unknown/unsupported stronger options do not silently authorize selection of a weaker suite unless authenticated policy explicitly permits the fallback for that context.

Canonical states:

- `PQ_ATTESTATION_TRUST_VALID`
- `PROVENANCE_SIGNER_COMPROMISED`
- `PROVENANCE_REVOCATION_STALE`
- `PROVENANCE_ROOT_ROLLBACK`
- `BUILD_REATTESTED_NOT_REBUILT`
- `NEGOTIATION_TRANSCRIPT_INCOMPLETE`
- `NEGOTIATION_EQUIVOCATION`
- `NEGOTIATION_DOWNGRADE_DETECTED`
- `VERIFIER_FAILURE_DOMAIN_CORRELATED`

---

# Cross-domain invariants

1. **Independence is evidence, not a count.** Root custodians, beacons, topology sources, builders and verifiers are independent only when their relevant control/failure domains are independently evidenced.
2. **Dormant authority needs liveness evidence.** Long-unused recovery material is neither assumed dead nor assumed usable.
3. **Compaction must conserve obligations.** Authenticated summaries may reduce storage/lookup cost but cannot make unresolved identities or deadlines disappear.
4. **Commit before observe.** Source populations, rounds, retry/fallback rules, combiners and negotiation policies are frozen before decision-relevant outputs become selectable.
5. **Selective abort is a decision surface.** Availability failure can become bias/downgrade if the post-failure behavior is chosen after seeing partial outcomes.
6. **Conflicts are durable evidence.** Authority/transcript disagreement is never resolved by overwriting one side in place.
7. **Freshness protects revocation/recovery.** Correctly signed stale root/trust metadata below an accepted floor is rejected.
8. **Historical compromise is monotonic.** Clean successors restore future eligibility; they do not erase affected intervals.
9. **Positive completeness beats absence.** Destruction, promises and transcript completeness require authenticated coverage/frontiers, not failed lookup.
10. **Binding is not semantic truth.** Valid signatures, provenance, randomness proofs and transparency inclusion prove particular bindings/claims under assumptions; policy must separately decide whether those claims are sufficient for consequential action.

---

# RED-first matrix (40 cases)

## A. Emergency root / dormant liveness (8)

1. 3-of-5 root keys but four keys share one HSM admin/destructive domain -> reject 3-independent-domain claim.
2. emergency root first published after incumbent compromise -> reject recovery bootstrap.
3. pre-authenticated emergency root; fresh harmless challenge signed by required independent threshold -> liveness eligible.
4. last successful liveness proof older than frozen max age -> `EMERGENCY_ROOT_LIVENESS_STALE`.
5. liveness exercise requires exporting/reconstructing all private shares centrally -> reject as policy violation.
6. old root metadata correctly signed but below accepted anti-rollback floor -> reject rollback.
7. one root member compromised and revoked; successor root generation independently authorized -> future eligible, predecessor compromise retained.
8. root public metadata survives but required custody members are inaccessible/corrupted -> `EMERGENCY_ROOT_UNAVAILABLE`, no silent threshold shrink.

## B. Promise frontier compaction (8)

9. predecessor 100 promises -> successor dispositions cover same exact 100 IDs once each -> accept conservation proof.
10. counts still total 100 but promise A dropped and B duplicated -> reject substitution/duplicate disposition.
11. unresolved promise omitted from compacted root because deadline is near -> reject omission.
12. carried promise receives new later deadline without old-policy-authorized renewal -> reject deadline reset.
13. historical promise can be followed across two compactions to exact fulfillment proof -> accept lineage.
14. compact archive keeps only aggregate counts, cannot prove disposition for one historical ID -> `PROMISE_COMPACTION_UNVERIFIABLE`.
15. same predecessor frontier produces two different compacted roots with overlapping authority -> equivocation.
16. terminal `VOID_ADJUDICATED` binds wrong promise identity -> reject.

## C. Multi-beacon composition (8)

17. evaluator commits A+B fixed rounds and `H(domain||A||B)` before either output; both arrive -> reproducible composition succeeds.
18. evaluator computes A+B and A+C then chooses sample it prefers -> reject post-reveal subset selection.
19. B missing; evaluator substitutes zero despite no precommitted missing-source rule -> `MULTIBEACON_INCOMPLETE`.
20. B missing; precommitted policy says abort with no sample -> valid fail-closed abort, no fallback sampling claim.
21. B missing after A revealed; evaluator switches to local RNG although fallback was not precommitted -> reject fallback rebound.
22. three named beacons actually share one operator/control plane -> reject independence claim.
23. threshold-BLS beacon fixed round produces one verifiable aggregate output; a participant withholds shares below availability threshold -> classify availability failure, not “chosen alternate random value.”
24. one source epoch later proven compromised -> dependent historical sample assurance degraded; successor sample under clean epoch may be eligible separately.

## D. Copy-domain reconciliation (8)

25. CMDB says backup domain absent; backup controller authenticated snapshot says present -> retain `COPY_TOPOLOGY_CONFLICT`, include possible domain in destruction coverage.
26. compute inventory says absent for offline vault outside its scope -> cannot support vault absence.
27. one source says domain retired but snapshot catalog shows retained copy in interval -> retirement unproven.
28. two aliases proven same destructive domain -> merge identity for independence counting while retaining alias provenance.
29. two authorities sampled months apart with authenticated creation/retirement transition between them -> reconcile interval-correctly, no false equivocation.
30. sole historical topology authority later proven compromised and no independent retained evidence covers interval -> historical negative-space assurance degraded.
31. adjudication chooses canonical successor mapping but preserves both conflicting source snapshots -> acceptable successor generation.
32. unresolved `UNKNOWN` archive domain remains -> cannot assert `ALL_COPY_DOMAINS_ACCOUNTED_FOR`.

## E. PQ provenance / negotiation (8)

33. provenance key compromised at T2; attestation has authenticated transparency timestamp T1 and policy allows pre-compromise evidence -> evaluate under historical policy, do not blanket rewrite.
34. same attestation first observed only after compromise with no trustworthy pre-compromise timestamp -> fail/degrade per policy.
35. attacker serves stale trust metadata that re-enables revoked key -> reject via anti-rollback/freshness.
36. malicious build has valid signed SBOM from compromised builder -> signature/SBOM valid but build trust rejected/degraded.
37. clean successor key re-signs exact malicious bytes without independent rebuild -> `BUILD_REATTESTED_NOT_REBUILT`.
38. local transcript says peer offered PQ+classical; peer-authenticated transcript for same session says classical-only -> `NEGOTIATION_EQUIVOCATION`.
39. transcript stores only selected classical suite, omitting authenticated offer sets despite policy requiring downgrade detection -> `NEGOTIATION_TRANSCRIPT_INCOMPLETE`.
40. archived classical signature remains valid for legacy historical verification after deprecation, but is used to authorize a new post-boundary migration -> reject new authorization.

---

# Implementation implications for LAB-093..100

When exact-source execution becomes available, implementation should remain regression-first and minimally invasive:

- introduce authenticated generation objects rather than mutable status flags;
- encode exact denominators/populations/policies in canonical serialization;
- preserve predecessor roots and conflict/compromise records;
- make anti-rollback floors explicit at every root/trust rollover;
- add conservation-set proofs/tests before allowing promise compaction;
- make multi-beacon composition/fallback deterministic from a precommitted policy;
- keep copy-domain conflict/unknown states fail-closed for destruction/completeness claims;
- bind PQ provenance trust generation and full algorithm offer/selection transcript before treating a migration signature as consequential authority.

Do **not** implement these design freezes as production refactors ahead of the retained LAB-086 exact executable gate unless repository priority changes or exact-source access becomes available for the downstream work first.

## Next distinct evidence task if exact execution remains blocked

Freeze:

**emergency-root liveness challenge secrecy/denial-of-service and quorum-member replacement under partial loss + authenticated accumulator/proof design for promise compaction and archive survivability + multi-beacon independence/correlation evidence and commit/reveal timeout fairness + copy-domain conflict-adjudicator authority/appeal and topology-source completeness proofs + provenance transparency-log survivability, attestation rekor/TUF-style root rollover, and PQ negotiation replay/cross-session binding.**
