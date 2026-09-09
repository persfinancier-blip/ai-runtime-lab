# Recovery quorum, receipt frontier, verifiable sampling, copy-domain topology, and PQ supply-chain contract v1

Date: 2026-09-09
Status: FROZEN DESIGN EVIDENCE — not executable proof
Issue family: LAB-093/#178 follow-up; LAB-086 remains priority #1

## Scope and boundary

This note executes the distinct fallback recorded in `state/CURRENT.md` while the exact LAB-086 source gate remains unavailable in the current runtime. It does **not** replace LAB-086 RED/GREEN execution, compileall, unsafe expected-failure validation, or conflict/security audit.

Frozen contract name:

`RECOVERY_FRONTIER_RANDOMNESS_COPYDOMAIN_PQ_SUPPLY_CHAIN_V1_FROZEN`

The contract extends the existing evidence architecture across five boundaries:

1. recovery-quorum membership compromise/rotation and emergency-root survivability;
2. receipt-promise frontier anti-omission across log/key migration;
3. randomness-beacon compromise/bias and verifiable challenge sampling;
4. `CopyDomainUniverse` authority/versioning under topology drift;
5. PQ migration builder/SBOM provenance, negotiation-transcript completeness, and multi-implementation verification.

## Primary donors checked

### NIST key lifecycle / recovery

- NIST SP 800-57 Part 1 Rev. 5 (final): key-management lifecycle, compromise, backup/archive/recovery, trust-anchor and associated metadata protection.
  - https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
- NIST SP 800-57 Part 1 Rev. 6 (initial public draft, 2025-12-05): adds current PQ algorithms and further separates key-storage material/mechanisms.
  - https://csrc.nist.gov/pubs/sp/800/57/pt1/r6/ipd

### Transparency / promise lineage

- RFC 9162, Certificate Transparency Version 2.0: signed tree heads/checkpoints, Merkle inclusion/consistency proof semantics, append-only auditability and signed inclusion promises.
  - https://www.rfc-editor.org/rfc/rfc9162

### Verifiable randomness

- RFC 9381, Verifiable Random Functions: public verification that a VRF output is the unique valid output for the exact `(public key, input)` pair; also distinguishes uniqueness/pseudorandomness from security under malicious key generation.
  - https://datatracker.ietf.org/doc/rfc9381/
- drand documentation: distributed publicly verifiable randomness beacon intended to provide unpredictable/bias-resistant public values.
  - https://docs.drand.love/

### PQ transition

- NIST IR 8547 initial public draft: transition categories include acceptable/deprecated/disallowed/legacy use and describe migration away from quantum-vulnerable algorithms.
  - https://csrc.nist.gov/pubs/ir/8547/ipd
- NIST PQC project/current standards: FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA are final; NIST states organizations should migrate and tracks transition work.
  - https://csrc.nist.gov/projects/post-quantum-cryptography

## Facts vs inference

### Facts from donors

- A valid VRF proof proves the output for the exact key/input; it does not prove that an application chose the input or sampling population without bias.
- RFC 9162-style append-only verification depends on authenticated checkpoints plus inclusion/consistency evidence, not a failed lookup.
- Key-management standards treat compromise/recovery/lifecycle metadata as separate consequential state; replacing a key does not erase historical compromise.
- PQ algorithm approval/transition is lifecycle policy, not merely the presence of a second signature or cipher suite.

### Lab inference / design decision

The lab must preserve the authority, denominator, population, version, and predecessor lineage that gave evidence its meaning at the time it was created. A later clean generation may restore future eligibility but must not retroactively strengthen historical evidence.

---

# 1. Recovery quorum membership compromise and emergency-root survivability

## Required object

`RecoveryAuthorityGeneration` MUST bind at least:

- `authority_generation_id`;
- exact ordered/member-set commitment;
- threshold and denominator policy;
- member key identities + key epochs;
- predecessor generation;
- recovery-rule version;
- emergency-root identity/policy epoch, if used;
- activation boundary and anti-rollback floor;
- compromise/degradation records known at activation;
- authenticated signatures/approvals required by the predecessor policy.

## Frozen rules

1. **A compromised incumbent cannot self-certify recovery.** A successor recovery generation requires authorization independent of the compromised authority according to the predecessor recovery policy or an already-authenticated emergency-root policy.
2. **Historical quorum is immutable.** Later removal of compromised/retired members does not shrink the denominator for an older recovery event.
3. **Membership rotation is a new generation.** Do not mutate a member list in place and reinterpret historical approvals under the new list.
4. **Emergency root is not magic break-glass state.** Its public identity, activation policy, custody assumptions, continuity and anti-rollback floor must already be authenticated before the incident it is expected to recover.
5. **Emergency-root loss is explicit degradation.** If no authenticated surviving path can establish the next authority generation, status is `RECOVERY_ROOT_UNAVAILABLE`, not silent bootstrap.
6. **Compromise is monotonic historical evidence.** A clean successor restores future authority only. It does not erase `COMPROMISED_DURING_GENERATION` from predecessor evidence.
7. **Rollback protection is semantic, not just key-version numeric.** A numerically greater generation is invalid if it descends from an unauthenticated fork or violates the predecessor recovery rule.

Canonical states:

- `RECOVERY_GENERATION_VALID`
- `RECOVERY_GENERATION_COMPROMISED`
- `RECOVERY_SUCCESSOR_UNDERQUORUM`
- `RECOVERY_SUCCESSOR_WRONG_PREDECESSOR`
- `RECOVERY_ROOT_UNAVAILABLE`
- `RECOVERY_GENERATION_ROLLBACK`
- `RECOVERY_GENERATION_FORK`

---

# 2. Receipt promise frontier across key/log migration

## Required object

`PromiseFrontierGeneration` MUST bind:

- log identity and log-generation identity;
- signing key epoch;
- predecessor checkpoint/tree size/root;
- all promise classes covered;
- promise acceptance cutoff/frontier;
- maximum completion deadline semantics;
- outstanding-promise commitment;
- witness policy/denominator epoch;
- successor log/key identity and migration proof;
- exact canonical serialization/version.

## Frozen rules

1. **Key rollover does not orphan old promises.** An acceptance promise signed under K1 remains attributable to K1/log-generation lineage after K2 activates.
2. **Log migration must close or carry the frontier.** A migration cannot claim completeness unless every accepted pre-cutover promise is either proven fulfilled before cutoff or included in an authenticated outstanding-promise frontier carried into the successor.
3. **`NO_ROW != PROMISE_FULFILLED_OR_VOID`.** Absence in the successor log is not proof that a predecessor promise disappeared legitimately.
4. **Positive anti-omission requires a sufficiently late authenticated state.** The verifier needs the promise, its deadline semantics, a post-deadline checkpoint/frontier and canonical non-inclusion/omission evidence over the committed observation domain.
5. **Historical witness denominator remains historical.** Witness retirement/recovery after the checkpoint does not recount the old checkpoint.
6. **Same promise, divergent migration disposition is equivocation.** E.g. one successor frontier marks promise fulfilled while another marks it outstanding/void without authenticated adjudication.
7. **Retiring a log does not retire unresolved obligations.** Archival must retain enough checkpoint/promise/frontier material for independent verification.

Canonical states:

- `PROMISE_FULFILLED`
- `PROMISE_OUTSTANDING_CARRIED_FORWARD`
- `PROMISE_OMISSION_PROVEN`
- `PROMISE_FRONTIER_INCOMPLETE`
- `PROMISE_MIGRATION_EQUIVOCATION`
- `PROMISE_ARCHIVE_UNVERIFIABLE`

---

# 3. Randomness beacon compromise, bias, and verifiable challenge sampling

## Required object

`ChallengeSamplingGeneration` MUST bind **before sampling output is usable**:

- authenticated population/corpus manifest root;
- exact eligible case IDs/count;
- sample size/selection policy;
- deterministic sampling algorithm + version;
- beacon/VRF identity and key/chain epoch;
- randomness round/input/challenge nonce;
- commit ordering proving the population and algorithm predate usable randomness;
- exclusions and stratification rules;
- generator/build provenance;
- resulting selected IDs + reproducibility proof.

## Frozen rules

1. **`VERIFIABLE_RANDOM_OUTPUT != UNBIASED_SAMPLE`.** A beacon/VRF can prove the randomness output yet the application can still bias selection by choosing the population, retrying inputs, selecting among rounds, or changing the algorithm after seeing randomness.
2. **Population commits first.** The eligible population and selection algorithm MUST be authenticated before the beacon round/input becomes selectable by the evaluator.
3. **No post-output grinding.** Repeated beacon-round/input attempts are forbidden unless the retry rule was committed in advance and the transcript proves every attempted round/input.
4. **VRF proof scope is exact.** It proves the output for a particular key/input, not that the key was honestly generated, the input was unbiased, or the population complete.
5. **Beacon compromise is epoch-scoped degradation.** Evidence sampled from a later-proven compromised/biasable beacon epoch becomes `SAMPLING_RANDOMNESS_ASSURANCE_DEGRADED`; a future clean epoch does not rewrite it.
6. **Fallback randomness must be pre-policy.** Do not switch to an easier local RNG after an unfavorable public beacon output unless that fallback was predetermined and transcript-visible.
7. **Sampling reproducibility is mandatory.** An independent verifier given manifest + algorithm + randomness transcript must obtain exactly the same selected IDs.
8. **Confidential challenge secrecy is separate.** Publicly verifiable sampling can coexist with delayed reveal/encrypted selected cases; secrecy and anti-bias are independent properties.

Canonical states:

- `SAMPLING_VALID`
- `SAMPLING_POPULATION_UNCOMMITTED`
- `SAMPLING_POST_OUTPUT_GRINDING`
- `SAMPLING_RANDOMNESS_EPOCH_COMPROMISED`
- `SAMPLING_ALGORITHM_REBOUND`
- `SAMPLING_NOT_REPRODUCIBLE`

---

# 4. CopyDomainUniverse authority, versioning, and topology drift

## Required object

`CopyDomainUniverseGeneration` MUST bind:

- universe generation/version;
- authority/collector identities and policy epoch;
- predecessor universe generation;
- infrastructure topology snapshot or authenticated source references;
- enumerated domain classes: primary, replica, backup, snapshot, archive, cache, export, wrapped-key, removable/offline, disaster recovery, staging/temp, vendor/service copy domains as applicable;
- per-domain owner/control/destructive-failure identity;
- observation time interval;
- source completeness claims and limitations;
- discovered-copy inventory commitments;
- uncovered domain×time cells;
- topology transition events.

## Frozen rules

1. **Universe membership is authority-bearing evidence.** A mutable CMDB/list is not sufficient negative-space authority by itself.
2. **Topology drift creates a new generation or authenticated delta.** New backup products, regions, replication paths, exports or cache layers cannot be silently absent from the historical universe.
3. **Historical claims use historical topology.** A later simplified topology cannot retroactively prove that older copy domains never existed.
4. **Collector compromise degrades dependent negative claims.** A clean new collector may re-establish future coverage but cannot certify historical absence it did not observe unless independent retained evidence closes that interval.
5. **Unknown is first-class.** An uncovered domain×time cell is `NEGATIVE_SPACE_UNCOVERED`, not inferred absence.
6. **False-independence correction is monotonic.** If two domains thought independent are later proven to share one destructive/control domain, historical replica/disposal assurance is degraded for the affected interval.
7. **Universe completeness can be cross-sourced.** Prefer independently governed topology/configuration/inventory/audit sources; one source must not be allowed to define its own complete universe and then prove itself empty.

Canonical states:

- `COPY_UNIVERSE_COMPLETE_FOR_INTERVAL`
- `COPY_UNIVERSE_TOPOLOGY_DRIFT_UNACCOUNTED`
- `COPY_UNIVERSE_AUTHORITY_COMPROMISED`
- `NEGATIVE_SPACE_UNCOVERED`
- `COPY_DOMAIN_FALSE_INDEPENDENCE`

---

# 5. PQ migration builder/SBOM provenance, negotiation completeness, multi-implementation verification

## Required object

`PQMigratedEvidenceGeneration` MUST bind:

- predecessor evidence identity/digest and semantic payload identity;
- successor cryptographic policy epoch;
- exact algorithms/parameter sets and hybrid-combiner semantics;
- migration builder/tool identity + source/build provenance;
- crypto library/module identity/version;
- parser/canonicalizer identity/version;
- SBOM/provenance attestation digest(s);
- verifier implementation identity/version;
- optional independent verifier identities/failure domains;
- complete authenticated negotiation transcript when algorithm negotiation occurred;
- deprecation/effective-time evidence;
- re-verification/re-proof result and degradation carried from predecessor.

## Frozen rules

1. **`VALID_PQ_SIGNATURE != TRUSTED_MIGRATION`.** A correct ML-DSA/SLH-DSA verification does not prove that the migration builder selected the right semantic payload, canonicalized correctly, or was uncompromised.
2. **Builder provenance is consequential.** Migration tooling and crypto dependencies are part of evidence lineage; an unverifiable builder yields `MIGRATION_SUPPLY_CHAIN_UNATTESTED`.
3. **SBOM alone is inventory, not integrity proof.** The SBOM/provenance must itself be authenticated and tied to the exact executable/build used.
4. **Negotiation transcript must be complete enough to detect stripping.** Record both parties' authenticated offered/supported policy sets, selected suite, policy epoch and any downgrade/fallback reason.
5. **`EITHER_ACCEPTED` hybrid semantics are weaker than `BOTH_REQUIRED`.** The combiner rule is authenticated policy, never inferred from presence of two signatures.
6. **Legacy verification is not authorization for new work.** A deprecated/disallowed predecessor signature may remain usable for historical verification where policy permits, but it cannot authorize a new consequential transition after the successor effective boundary.
7. **Verifier diversity is by failure domain, not process count.** Two verifier processes using the same library/build/toolchain are one implementation failure domain for independence claims.
8. **Cross-verification disagreement fails closed.** If independent implementations disagree on the same canonical bytes/policy, status is `VERIFIER_DIVERGENCE`; do not majority-vote unless a prior adjudication policy explicitly defines that authority.
9. **Successor crypto does not repair predecessor semantics.** Preserve predecessor compromise/degradation flags in the renewal lineage.
10. **Algorithm agility cannot become downgrade agility.** Unknown/unsupported stronger offers must not silently force a weaker suite; failure/fallback semantics are authenticated policy.

Canonical states:

- `PQ_MIGRATION_VALID`
- `MIGRATION_SUPPLY_CHAIN_UNATTESTED`
- `MIGRATION_BUILDER_COMPROMISED`
- `NEGOTIATION_TRANSCRIPT_INCOMPLETE`
- `NEGOTIATION_DOWNGRADE_DETECTED`
- `VERIFIER_DIVERGENCE`
- `HYBRID_POLICY_MISMATCH`
- `PREDECESSOR_ASSURANCE_DEGRADED_CARRIED_FORWARD`

---

# Cross-domain invariants

1. **Generation, not mutation.** Recovery membership, promise frontier, randomness authority, copy-domain universe and PQ policy changes create authenticated successor generations.
2. **Denominator laundering is forbidden.** Historical decisions retain historical member/source/witness/verifier denominators.
3. **Commit-before-observe.** Population, retry/fallback and negotiation policy are fixed before seeing decision-relevant randomness/results whenever post-observation choice could bias outcome.
4. **Positive completeness, not failed lookup.** Absence claims require authenticated complete frontier/universe/manifest evidence.
5. **Compromise is monotonic history.** Clean successors restore future eligibility; they do not erase affected historical intervals.
6. **Provenance and semantics are separate.** Valid signatures/build attestations prove particular bindings, not semantic truth unless the semantic mapping itself is included in the authenticated claim.
7. **Independence is an audited topology property.** Member/process/copy/verifier counts do not substitute for independent control/failure domains.

---

# RED-first matrix (40 cases)

## A. Recovery authority (8)

1. incumbent compromised; incumbent alone signs successor -> reject.
2. predecessor 3-of-5 recovery; later policy becomes 2-of-3; historical 2-signature recovery -> reject.
3. valid independent recovery quorum + correct predecessor + monotonic floor -> accept successor.
4. successor signed over wrong predecessor generation -> reject.
5. two independently authorized successors from same predecessor -> `RECOVERY_GENERATION_FORK`.
6. emergency root first introduced after compromise -> reject as unauthenticated recovery root.
7. authenticated emergency root survives incumbent compromise and satisfies frozen policy -> permit successor generation.
8. rollback to earlier valid recovery generation after higher accepted floor -> reject.

## B. Promise frontier / migration (8)

9. K1 promise fulfilled before deadline; K2 rollover retains ancestry -> accept historical fulfillment.
10. K1 promise missing from successor with no carried frontier/non-inclusion proof -> incomplete, not void.
11. K1->K2 migration carries authenticated outstanding-promise commitment -> retain obligation.
12. same promise marked fulfilled in one successor frontier and outstanding in another -> equivocation.
13. log retirement deletes exact old checkpoint bytes but keeps root digest only -> archive assurance degraded.
14. witness set shrinks after old checkpoint; old under-quorum checkpoint recounted -> reject.
15. post-deadline authenticated checkpoint + canonical non-inclusion over complete committed frontier -> omission proven.
16. 404/timeout/partial mirror absence -> omission not proven.

## C. Randomness / sampling (8)

17. population root committed before beacon round; deterministic sampler reproduces exact IDs -> accept.
18. evaluator chooses among three valid beacon rounds after seeing outputs -> grinding/reject.
19. VRF proof valid but population committed after VRF output -> reject unbiased-sampling claim.
20. beacon epoch later proven compromised; historical sample -> degrade randomness assurance.
21. fallback local RNG used despite uncommitted fallback policy -> reject.
22. sample algorithm version changed after beacon output -> reject.
23. VRF key/input/output proof valid, but malicious key-generation assumptions unaddressed where policy requires them -> degrade/reject policy claim.
24. selected case IDs encrypted for delayed reveal but selection reproducible from committed population + public randomness -> anti-bias valid; secrecy assessed separately.

## D. Copy-domain universe (8)

25. all enumerated backups empty but snapshot service omitted from universe -> `NEGATIVE_SPACE_UNCOVERED`.
26. new replication region introduced with authenticated topology delta -> successor universe valid.
27. later topology removes old archive; historical deletion claim evaluated only against new topology -> reject.
28. inventory collector compromised for interval -> dependent negative claims degraded.
29. two replicas later proven same storage/account/control domain -> historical independence degraded.
30. independent topology/config + backup inventory sources jointly cover all domain×time cells -> allow complete-for-interval claim.
31. source returns signed empty inventory but its authenticated scope excludes exports -> exports remain uncovered.
32. late-discovered snapshot proves prior all-copy-destroyed claim false -> historical claim degraded, not rewritten.

## E. PQ migration / supply chain (8)

33. valid ML-DSA signature produced by unattested migration builder -> signature valid, migration assurance insufficient.
34. authenticated builder provenance + exact parser/canonicalizer/crypto versions + successor policy -> provenance gate passes.
35. SBOM names dependencies but is not bound to exact executed build -> insufficient.
36. transcript shows both parties offered required hybrid but selected classical-only without authorized fallback -> downgrade.
37. transcript omits one side's offered algorithms -> negotiation completeness fails.
38. two independent verifier implementations agree on canonical bytes/policy -> satisfy configured diversity gate.
39. two processes use same verifier library/build and are counted as two independent implementations -> reject independence claim.
40. independent verifiers disagree -> fail closed as `VERIFIER_DIVERGENCE`; no ad-hoc majority vote.

---

# Implementation implications for LAB-093+

Do not implement these as one monolithic subsystem. The reusable primitives should be small authenticated generation/lineage types with explicit completeness and degradation states. Likely shared abstractions:

- `AuthenticatedGenerationRef`
- `HistoricalDenominator`
- `CompletenessFrontier`
- `CompromiseRecord`
- `IndependentDomainId`
- `PolicyEffectiveBoundary`

Tests should be written first from the 40 RED cases before production refactors. Exact implementation remains subordinate to the pending LAB-086 executable gate.

## Audit pass

Checked for overlap with prior LAB-093 design freezes. This note adds distinct boundaries rather than renaming prior work:

- explicit recovery-quorum membership rotation/emergency-root survivability;
- migration-time outstanding promise frontier;
- commit-before-randomness population/sampler semantics and anti-grinding;
- versioned copy-domain topology authority;
- authenticated migration-builder/SBOM + complete negotiation + implementation-diversity semantics.

No executable result is claimed. No PR draft/merge state is changed.

## Exact next design fallback if LAB-086 execution remains unavailable

**Emergency-root custody-domain independence and dormant-key liveness proof + promise-frontier compaction/renewal without obligation loss + multi-beacon composition and last-revealer bias/abort semantics + copy-domain topology discovery reconciliation across mutually inconsistent authorities + PQ provenance-attestation key compromise/revocation and canonical negotiation transcript anti-equivocation.**
