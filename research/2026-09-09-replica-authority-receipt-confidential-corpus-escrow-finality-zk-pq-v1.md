# Replica authority, ingress receipts, confidential corpus, escrow finality, and ZK/PQ renewal v1

Date: 2026-09-09
Status: FROZEN DESIGN EVIDENCE; RED/GREEN executable proof still required
Contract: `REPLICA_AUTHORITY_RECEIPT_CONFIDENTIAL_CORPUS_ESCROW_FINALITY_ZK_PQ_V1_FROZEN`
Parent: LAB-093 / #178

## Why this slice exists

The preceding freezes established independent destructive-domain counting, positive time-source censorship evidence, immutable canonical semantic-corpus generations, escrow epoch-fork detection, and ZK transcript/proof-renewal downgrade detection. This slice closes five remaining ways those assurances could be laundered without breaking a signature:

1. an operator relabels two replicas as two independent destructive domains, or two authorities concurrently assign incompatible domain topology;
2. a time source and collector collude about whether a challenge was actually accepted/delivered;
3. confidential corpus cases are omitted from a selective-disclosure audit while the visible subset still passes;
4. an escrow fork is adjudicated but losing-branch shares/ciphertexts remain usable or disposal is falsely inferred;
5. a ZK proof is re-proved under a new/PQ scheme without independently freezing semantic equivalence, exact parameters, and migration provenance.

The objective is not stronger rhetoric. It is to define what evidence is sufficient to count each assurance and what must remain UNKNOWN when positive evidence is missing.

## Primary donors and exact reusable mechanisms

### RFC 9162 — Certificate Transparency v2
Source: https://www.rfc-editor.org/rfc/rfc9162.html

Reusable mechanisms:
- an accepted submission receives a signed SCT;
- the SCT is a positive promise by a particular log to append a particular accepted submission;
- the promise is bounded by that log's Maximum Merge Delay;
- append-only state is independently checkable with signed tree heads and consistency proofs.

Donor boundary: an SCT proves a log made a promise. It does not prove an arbitrary network ingress accepted a request unless the ingress receipt is itself authenticated and bound to the exact request.

### IETF Roughtime
Source: https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/

Reusable mechanisms:
- client-chosen nonce binds a response to a request;
- chaining observations from multiple servers can expose inconsistent time assertions;
- authenticated responses support provenance and ordering evidence.

Donor boundary: silence is not self-authenticating. A missing Roughtime response does not by itself distinguish source withholding from failed delivery, collector loss, censorship, or observation omission.

### NIST SP 800-57 Part 1 Rev. 5 + Rev. 6 draft
Sources:
- https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
- https://csrc.nist.gov/pubs/sp/800/57/pt1/r6/ipd

Reusable mechanisms:
- key lifecycle transitions are explicit and recorded;
- all secret/private-key copies must be destroyed when no longer required;
- metadata may need to remain for audit even after key destruction;
- compromised key material does not become trustworthy again merely because a new key exists.

Donor boundary: a signed declaration saying `destroyed` is evidence of an assertion, not cryptographic proof that all physical/electronic copies are unrecoverable.

### NIST SP 800-88 Rev. 2
Source: https://csrc.nist.gov/pubs/sp/800/88/r2/final

Reusable mechanism: sanitization/zeroization is a concrete operational control; crypto erase is safe only when all relevant target key copies can actually be sanitized and the assumptions of the storage design hold.

### RFC 9901 — Selective Disclosure for JWTs (SD-JWT)
Source: https://www.rfc-editor.org/rfc/rfc9901.html

Reusable mechanism: disclosed claims remain cryptographically bound to an authenticated larger object while undisclosed claims can remain hidden.

Donor boundary: selective disclosure proves binding of what is disclosed; it does not prove that hidden claims are irrelevant, that a hidden case population is complete, or that no decision-relevant case was omitted.

### NIST PQC standards and migration work
Sources:
- FIPS 203/204/205 publication: https://csrc.nist.gov/News/2024/postquantum-cryptography-fips-approved
- PQC project: https://csrc.nist.gov/Projects/post-quantum-cryptography
- NIST IR 8547 draft transition plan: https://csrc.nist.gov/pubs/ir/8547/ipd

Reusable mechanisms:
- ML-KEM, ML-DSA, and SLH-DSA are standardized PQ primitives;
- transition is an explicit lifecycle problem, not an implicit algorithm swap;
- cryptographic agility requires knowing exactly which algorithm/parameter epoch protects which artifact.

Donor boundary: migrating an attestation signature to ML-DSA/SLH-DSA does not establish semantic equivalence of the statement being attested, nor does it repair an already-broken predecessor binding.

## Frozen decision 1 — replica-domain authority is separate from replica count

Define an immutable `ReplicaDomainEpoch`:

```text
ReplicaDomainEpoch {
  topology_id,
  generation,
  predecessor_digest,
  effective_boundary,
  authority_policy_digest,
  replica_id -> destructive_domain_id mappings,
  control_domain metadata,
  storage/provider/failure-domain claims,
  evidence_manifest_digest,
  signatures[],
  transparency_checkpoint
}
```

### Rules

1. Replica independence is evaluated against the exact historical `ReplicaDomainEpoch` that was effective when the survivability claim was made.
2. A replica operator MAY report topology facts but MUST NOT be the sole authority that converts its own labels into counted independence.
3. `replica_count` and `independent_destructive_domain_count` are different metrics.
4. Two replicas sharing a destructive root — same credential root, same storage account, same administrator, same KMS root, same physical failure domain when that matters — MUST NOT be counted as independent merely because names/providers/regions differ.
5. Domain relabeling creates a successor topology generation; it never rewrites the denominator of historical claims.
6. Two different authenticated mappings for the same `(topology_id, generation)` are `REPLICA_DOMAIN_EQUIVOCATION`.
7. Concurrent successor epochs from the same predecessor are `REPLICA_DOMAIN_SPLIT_BRAIN` until adjudicated. No last-write-wins.
8. A later proof that two previously distinct labels actually shared one destructive root can downgrade current reliance on the historical survivability assertion. The original bytes/signatures remain historical evidence; the assurance classification changes through a separately authenticated adjudication record.
9. Losing topology branches remain retained as conflict evidence.

### Positive independence evidence

A counted domain requires an authenticated evidence bundle sufficient for the policy, for example independent control-plane identity, storage account/tenant identity, KMS/trust-root identity, recovery authority, physical/provider placement claims, and a current non-overlap adjudication. The policy must state which dimensions matter. Merely having different strings in `region` or `provider` fields is not sufficient.

Frozen boundary:

`TWO_AUTHENTICATED_REPLICA_LABELS != TWO_INDEPENDENT_DESTRUCTIVE_DOMAINS`.

## Frozen decision 2 — challenge ingress receipt authority and collector anti-collusion

Positive censorship/withholding proof needs a separate delivery fact before it can reason about silence.

Define:

```text
ChallengeReceipt {
  challenge_digest,
  source_id,
  source_key_epoch,
  ingress_id,
  ingress_key_epoch,
  accepted_at_interval,
  response_deadline,
  collector_population_digest,
  collector_policy_digest,
  nonce,
  receipt_signature,
  publication_checkpoint
}
```

### Rules

1. A source's own unsigned log line `received` is not sufficient positive delivery evidence.
2. A collector's statement `I sent it` is not sufficient positive acceptance evidence.
3. The strongest ordinary path is an authenticated ingress/source receipt bound to the exact challenge digest, nonce, source identity, deadline and observation population.
4. If source and ingress are the same administrative/key-control domain, the receipt proves that domain made an assertion; it does not create independent evidence against that same domain.
5. Positive malicious-withholding attribution requires at least one receipt/acceptance authority whose compromise is not already assumed by the attribution claim, plus a precommitted collector denominator whose complete post-deadline observations are authenticated.
6. Collector population is fixed before the response deadline. Dropping collectors that saw a timely response is denominator laundering.
7. Same collector identity/generation with two different complete observation roots is `COLLECTOR_EQUIVOCATION`.
8. Missing ingress receipt yields `DELIVERY_NOT_PROVEN`, not `SOURCE_WITHHOLDING_PROVEN`.
9. Authenticated acceptance plus incomplete collector observations yields `POST_ACCEPTANCE_OBSERVATION_INCOMPLETE`.
10. Authenticated acceptance plus a complete collector population showing no valid timely response can establish `TIMELY_RESPONSE_NOT_OBSERVED_BY_COMMITTED_COLLECTORS`; malicious intent remains a separate policy/adjudication question unless the protocol contract makes timely response mandatory.

Frozen boundaries:

`SEND_ATTEMPT != ACCEPTANCE_RECEIPT`.

`ACCEPTANCE_RECEIPT + COMPLETE_NO_RESPONSE_OBSERVATION != INTENT_PROVEN`.

## Frozen decision 3 — confidential semantic corpus must preserve anti-omission auditability

A corpus may contain confidential or regulated cases. Confidentiality must not permit the evaluator to choose only favorable visible cases.

Define an immutable public `CorpusCommitmentManifest` and access-controlled case objects:

```text
CorpusCommitmentManifest {
  corpus_id,
  generation,
  predecessor_digest,
  case_count,
  ordered_case_commitments[],
  classification_labels_commitment,
  policy_digest,
  completeness_root,
  authority_signatures[],
  transparency_checkpoint
}
```

Evaluation produces:

```text
CorpusEvaluationEvidence {
  corpus_manifest_digest,
  evaluator_build/provenance,
  evaluated_case_commitments[],
  per-case result commitments[],
  aggregate result,
  disclosure_profile,
  auditor/zk evidence,
  signatures[]
}
```

### Rules

1. The full case population is committed before evaluation.
2. `evaluated_case_commitments` MUST equal the authenticated required population for a full-corpus PASS, even when plaintext cases remain confidential.
3. A selective-disclosure view may hide case contents but MUST NOT silently hide case existence/count unless the policy explicitly defines a weaker privacy-preserving assurance class.
4. Hash/commitment equality proves binding, not semantic correctness of a hidden case or hidden result.
5. Decision-relevant hidden predicates require either authorized auditor review of the plaintext, an approved ZK predicate over the committed case/result, or a weaker explicit assurance classification.
6. Auditor access is least privilege and creates a durable access/decision record without publishing confidential plaintext.
7. Two manifests with the same corpus id/generation and different completeness roots are `CORPUS_EQUIVOCATION`.
8. A later declassification may reveal case bytes and verify them against the old commitments without changing the historical evaluation generation.
9. Redaction must preserve the ability to distinguish `CASE_EXISTS_BUT_HIDDEN` from `CASE_NOT_IN_CORPUS`.

Frozen boundary:

`SELECTIVELY_DISCLOSED_PASS != COMPLETE_CONFIDENTIAL_CORPUS_PASS` unless authenticated commitments and the required confidential-case audit predicate cover the complete population.

## Frozen decision 4 — escrow fork adjudication is not safe disposal

Define immutable adjudication and retirement records:

```text
EscrowForkAdjudication {
  fork_id,
  common_predecessor_epoch,
  branch_digests[],
  winner_digest,
  losing_branch_digests[],
  decision_policy_digest,
  evidence_digest,
  authority_signatures[],
  effective_boundary,
  finality_state
}

EscrowRetirementRecord {
  branch_digest,
  member/share identifiers,
  ciphertext/KEK references,
  retirement_boundary,
  required destruction/sanitization actions,
  observed action evidence[],
  residual exposure classification,
  authority signatures[]
}
```

### Rules

1. Fork adjudication decides which epoch may be used prospectively. It does not erase exposure from losing branches.
2. Losing branch shares MUST be explicitly retired from future protocol use.
3. A share marked retired but still accepted by a verifier/decryptor is a security defect.
4. Disposal claims distinguish `RETIREMENT_AUTHORIZED`, `SANITIZATION_REPORTED`, and `DESTRUCTION_ASSURANCE_SATISFIED`.
5. A signed operator statement saying a share was deleted is not, by itself, proof that every copy is unrecoverable.
6. When cryptographic erasure is used, the evidence must cover the key hierarchy and all wrapped/exported/backup copies assumed by the policy.
7. Previously emitted valid partial decryption shares remain historical exposure evidence even after local key destruction.
8. If losing and winning branch shares can still be mixed to satisfy a threshold, reconfiguration is incomplete and the successor MUST NOT be considered safe.
9. Rejoin after partition must first prove the node's accepted epoch and retired-epoch set before it may contribute shares.
10. Final adjudication may be superseded only by the previously frozen appeal/new-evidence authority model; disposal evidence is never rewritten.

Frozen boundaries:

`FORK_ADJUDICATED != LOSING_BRANCH_CRYPTOGRAPHICALLY_DISPOSED`.

`DELETION_ATTESTED != ALL_COPIES_UNRECOVERABLE`.

## Frozen decision 5 — ZK renewal semantic-equivalence authority and PQ attestation migration

Define a migration object that separates statement semantics from cryptographic wrapper:

```text
ZKProofMigration {
  migration_id,
  predecessor_proof_system,
  predecessor_circuit_digest,
  predecessor_public_input_schema_digest,
  predecessor_parameter_epoch,
  successor_proof_system,
  successor_circuit_digest,
  successor_public_input_schema_digest,
  successor_parameter_epoch,
  source_statement_manifest_digest,
  semantic_equivalence_policy_digest,
  semantic_diff_corpus_digest,
  semantic_attester_provenance[],
  equivalence_verdict,
  migration_attestation_algorithms[],
  signatures[],
  transparency_checkpoint
}
```

### Semantic authority rules

1. The circuit author/prover MUST NOT be the sole authority deciding semantic equivalence of its own successor circuit.
2. Equivalence is against an exact statement specification + canonical semantic corpus, not against matching names or matching success on a hand-picked sample.
3. Byte-reproducible circuit builds help bind source/build/artifact; they do not prove semantic equivalence.
4. A successor proof that merely verifies `old_verifier(old_proof) == true` is a wrapper and inherits the old proof-system/parameter assumptions.
5. Full renewal requires re-proving the original authenticated statement (or a separately proven semantically equivalent statement) under successor assumptions.
6. If source witness material is unavailable, the system must expose that only wrapper/legacy validation is possible; it must not label the result full renewal.

### PQ migration rules

1. Attestation signature algorithm is versioned independently from ZK proof system, circuit, SRS/parameters and statement semantics.
2. A PQ successor attestation uses an exact algorithm/parameter identifier (for example ML-DSA or SLH-DSA under the applicable FIPS profile) and a new key epoch.
3. Adding a PQ signature to an old artifact does not repair a predecessor signature that was already untrustworthy before the new binding was created.
4. Migration must bind the exact predecessor artifact while its predecessor authenticity is still acceptable under policy, or bind independently authenticated source evidence.
5. Hybrid/classical+PQ periods must state combination semantics explicitly: `both-required`, `either-accepted`, or another frozen policy. Verifiers MUST NOT infer semantics from the presence of two signatures.
6. Algorithm downgrade is detected by authenticated policy epoch. A verifier may not silently fall back to a deprecated classical-only path after the PQ-required boundary.
7. PQ key compromise/revocation remains a key-lifecycle event; PQ algorithms do not remove the need for effective-time, revocation, transparency and provenance controls.
8. Crypto-agility metadata and migration attestations themselves must be archived under the same proof-closure rules as other consequential evidence.

Frozen boundary:

`PQ_SIGNED_SUCCESSOR != SEMANTICALLY_EQUIVALENT_RENEWAL`.

## Cross-cutting authority separation

For consequential reliance, model at least these roles separately even when policy permits some controlled overlap:

- replica-topology claimant;
- replica-domain adjudication authority;
- challenge ingress/acceptance authority;
- collectors/observers;
- semantic-corpus authority;
- confidential-case auditor/ZK predicate authority;
- escrow epoch authority;
- escrow fork adjudicator;
- sanitization/destruction operator;
- ZK circuit/predicate author;
- semantic-equivalence adjudicator;
- attestation key authority;
- PQ migration policy authority;
- transparency/witness layer.

The independence policy must describe which overlaps are permitted. Multiple signatures from one control root do not create multiple independent authorities.

## 40-case RED-first matrix

### A. Replica-domain authority / split brain

1. Two replicas, different names, same storage account/KMS root -> MUST count as one destructive domain when policy treats that root as destructive.
2. Operator self-labels two directories as independent domains with no independent authority -> MUST NOT satisfy two-domain quorum.
3. Authenticated topology epoch maps replicas to two independently evidenced domains -> MAY satisfy two-domain policy.
4. Same topology id/generation, different mapping roots -> `REPLICA_DOMAIN_EQUIVOCATION`.
5. Two successor topology epochs from same predecessor -> `REPLICA_DOMAIN_SPLIT_BRAIN`.
6. Historical two-domain claim followed by ordinary relabel -> historical denominator MUST remain original epoch.
7. Later evidence proves shared destructive root -> current assurance MUST downgrade through adjudication; historical bytes remain immutable.
8. One replica lost but second replica in truly independent domain contains complete checkpoint package -> recovery MAY remain sufficient if policy threshold allows it.

### B. Challenge receipts / collector collusion

9. Collector says `sent`, no ingress receipt -> `DELIVERY_NOT_PROVEN`.
10. Authenticated receipt binds wrong nonce/challenge digest -> MUST NOT count.
11. Receipt accepted after deadline -> MUST NOT establish timely acceptance.
12. Source+ingress same compromised control domain, no independent receipt authority -> receipt MUST NOT alone prove source-malicious withholding under a claim assuming that domain compromised.
13. Valid independent receipt + complete precommitted collectors + no timely response -> positive no-response observation MAY be established.
14. One committed collector omitted from final observation set -> `POST_ACCEPTANCE_OBSERVATION_INCOMPLETE`.
15. Two complete observation roots for same collector epoch -> `COLLECTOR_EQUIVOCATION`.
16. Timely response observed by one committed collector but excluded from aggregate -> censorship attribution MUST fail; denominator laundering detected.

### C. Confidential semantic corpus

17. Public subset 100% passes, confidential committed case unevaluated -> full-corpus PASS MUST fail.
18. Full manifest commits 100 cases, evidence contains 99 case commitments -> anti-omission failure.
19. Hidden case exists with authorized auditor PASS and exact commitment linkage -> MAY count under policy without public plaintext disclosure.
20. Hidden case represented only by unlabeled aggregate count with no membership commitments -> MUST NOT prove complete population.
21. ZK proof demonstrates approved pass predicate over every committed case/result -> MAY satisfy the specific predicate; MUST NOT imply unrelated semantic properties.
22. Same corpus id/generation, different completeness root -> `CORPUS_EQUIVOCATION`.
23. Later declassification bytes match old commitment -> MAY increase inspectability without changing historical generation.
24. Selective disclosure hides existence of failed required case -> MUST be detectable as incomplete population or weaker assurance class.

### D. Escrow fork adjudication / disposal

25. Fork winner selected, losing branch still accepted for partial decrypt -> FAIL.
26. Losing branch marked retired, one offline node rejoins and emits old-epoch share -> share MUST be rejected and exposure recorded.
27. Operator signs `deleted` but backup/export-copy coverage unknown -> `SANITIZATION_REPORTED`, not destruction-assurance satisfied.
28. Crypto erase destroys KEK but policy knows an exported plaintext share existed -> MUST NOT claim all-copy destruction.
29. Losing branch emitted valid partial share before retirement -> exposure record remains monotone after adjudication.
30. Winner and loser shares can be combined to threshold -> successor activation MUST fail.
31. Two competing fork adjudications under same finality generation -> adjudication equivocation/conflict, no LWW.
32. Complete sanitization evidence covers all policy-required copies and verifier rejects retired epoch -> prospective retirement MAY pass; historical exposure remains.

### E. ZK semantic renewal / PQ migration

33. New circuit has same name/version label but different semantics -> MUST require semantic-diff/equivalence evidence.
34. Reproducible successor circuit bytes from two builders, no semantic corpus -> MUST NOT count as semantic equivalence.
35. Recursive proof only verifies old proof acceptance -> classify wrapper/legacy-assumption inheritance, not full renewal.
36. Original authenticated witness re-proved under semantically equivalent successor circuit/parameters -> MAY qualify full renewal when all policy gates pass.
37. ML-DSA signature added after predecessor signature was already known compromised, no independent source binding -> MUST NOT rehabilitate old provenance.
38. Hybrid artifact policy says both-required; verifier accepts classical-only -> downgrade failure.
39. PQ-required boundary effective, verifier silently falls back to deprecated classical key -> downgrade failure.
40. PQ-signed migration object binds exact predecessor/source, exact successor proof/circuit/parameter epochs, semantic-equivalence verdict, and transparent policy epoch -> MAY satisfy migration attestation gate; proof correctness still requires actual successor verification.

## Audit conclusions

1. **Independence is itself an authenticated claim.** Counting replicas, witnesses, collectors, semantic attesters or migration signers without freezing their control/destructive-domain provenance allows denominator laundering.
2. **Positive absence claims need positive admission evidence.** The CT-style pattern is useful: first establish an authenticated acceptance/promise, then compare it against an authenticated complete post-deadline state. A failed request or empty lookup is not equivalent.
3. **Confidentiality must not erase population completeness.** Commit existence/membership first, then selectively reveal content or prove a narrow predicate.
4. **Retirement and destruction are different assurance classes.** Protocol rejection of a retired share is directly testable; universal physical deletion of every historical copy is much harder and must not be inferred from an assertion.
5. **PQC migration protects new cryptographic bindings, not old semantics.** Exact semantic provenance, parameter/circuit lineage, downgrade policy and predecessor validity boundaries remain mandatory.

## Implementation consequence

Do not implement production refactors from this document before executable RED cases exist. The intended next engineering shape for LAB-093+ is immutable epoch/manifest records, explicit assurance enums, fail-closed classification, monotone conflict/exposure evidence, and policy-bound authority denominators. Exact schemas should be chosen only after tests are written against the existing implementation surface.

## Exact next research fallback if executable source remains unavailable

Freeze the next distinct slice around:

**replica-domain challenge/audit freshness and false-independence revocation + ingress-receipt transparency/non-inclusion proof + confidential-corpus auditor compromise and re-audit generations + escrow destruction-evidence retention versus privacy/secrets minimization + PQ hybrid-combiner semantics, algorithm deprecation effective-time and long-term renewal of migration attestations.**
