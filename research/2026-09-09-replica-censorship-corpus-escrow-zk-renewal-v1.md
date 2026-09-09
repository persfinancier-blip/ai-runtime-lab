# Replica independence, censorship evidence, corpus completeness, escrow partition forks, and ZK renewal

Date: 2026-09-09
Status: DESIGN FROZEN / RED-FIRST
Contract: `REPLICA_CENSORSHIP_CORPUS_ESCROW_ZK_RENEWAL_V1_FROZEN`

## Scope

This follow-up extends the LAB-093 evidence/capability architecture while LAB-086 exact executable closure remains blocked by unavailable direct source transport. It does not substitute for LAB-086 RED/GREEN execution.

The contract covers five failure classes:

1. checkpoint-package replica independence and recovery after an archive-domain loss;
2. time-source query/response censorship and positive challenge-delivery completeness;
3. canonical semantic-corpus anti-omission/equivocation authority;
4. escrow refresh/reconfiguration fork detection across partition/rejoin with partial share exposure;
5. ZK transcript chunk recovery and downgrade-resistant proof renewal.

## Donor mechanisms

### RFC 9162 — append-only checkpoints and consistency

Certificate Transparency uses signed tree heads plus Merkle consistency proofs so a verifier can prove that a later tree extends a previously accepted tree. The useful donor property is that historical continuity can be checked from retained authenticated checkpoints/proofs rather than trusting a current server assertion.

Implication here: a surviving archive copy is useful only when it retains enough authenticated material to reproduce the exact historical relation. Replica count alone is not evidence of independence or recoverability.

### IETF Roughtime — nonce-bound, chained time evidence

Roughtime binds responses to client nonces and supports chaining observations across servers. The useful donor property is freshness/order evidence tied to a specific challenge, rather than accepting a free-standing timestamp.

Implication here: absence of a response is not positive evidence that a time authority censored a request unless the system can prove challenge delivery/acceptance under a previously committed observation policy.

### NIST threshold cryptography — proactive refresh and bounded corruption

NIST threshold-cryptography work treats proactive refresh as a way to refresh distributed shares without changing the represented secret/public key, reducing future exposure under bounded compromise. Refresh does not rewrite the fact that an earlier threshold may already have been compromised.

Implication here: partitioned concurrent refresh/reconfiguration epochs cannot be merged with last-write-wins or by mixing shares from different epochs. Exposure history remains monotone.

### Ethereum KZG ceremony — public transcript and verifiable contribution chain

The KZG ceremony publishes a public transcript and records contribution-chain evidence. The useful donor property is that later verification depends on retrievable transcript material and parameter lineage, not only on a remembered digest.

Implication here: transcript chunk replication must preserve a verifiable manifest/ordering and proof-renewal must prove the original statement under successor assumptions, not merely wrap acceptance of an old proof.

## Frozen contract

## 1. Checkpoint-package replica independence

Define a `CheckpointReplicaSet` with:

- logical package id;
- exact signed checkpoint bytes;
- source log id/key epoch/hash suite;
- witness/policy epoch and historical denominator;
- consistency ancestry/material required by policy;
- replica manifests;
- storage/control failure-domain labels;
- independent integrity attestations;
- recovery policy generation.

### Rules

`N_REPLICAS != N_INDEPENDENT_FAILURE_DOMAINS`.

Two copies under the same provider account, operator, encryption key, region-control plane, or deletion authority may count as one destructive domain even when physically distinct.

A package is `RECOVERABLE_AFTER_DOMAIN_LOSS` only if, after deleting every object in one declared destructive domain, the remaining replicas can independently reconstruct and verify the exact package and its historical continuity.

A replica that retains only a digest is not a full recovery replica.

Replica relocation after loss creates a new replica generation. It must not rewrite the historical claim that the previous diversity level had degraded.

### States

- `REPLICA_POLICY_SATISFIED`
- `REPLICA_DIVERSITY_DEGRADED`
- `RECOVERABLE_BUT_DIVERSITY_DEGRADED`
- `PACKAGE_INCOMPLETE`
- `RECOVERY_UNVERIFIABLE`

## 2. Positive evidence for time-source censorship

A missing response is ambiguous among censorship, packet loss, client failure, authority outage, collector failure, and deliberate withholding.

`NO_RESPONSE != CENSORSHIP_PROVEN`.

Define a `TimeChallengeReceipt` bound to:

- challenge nonce/digest;
- target authority/key epoch;
- committed observation population and collectors;
- authenticated acceptance/delivery evidence when supported;
- deadline/window;
- response-or-nonresponse observation commitments;
- collector denominator/policy epoch.

Positive `CHALLENGE_ACCEPTED_BUT_RESPONSE_WITHHELD` requires evidence that the authority or a trusted ingress accepted the exact challenge before deadline and that the committed complete observation set contains no valid response before close.

Without authenticated acceptance, the strongest result is `DELIVERY_OR_RESPONSE_UNKNOWN`.

Collector membership/denominator is frozen before challenge dispatch. Dropping an inconvenient collector after observing outcomes is denominator laundering.

A response received by any committed collector before deadline defeats a claim of complete response censorship even if other collectors observed nothing.

## 3. Canonical semantic-corpus anti-omission and equivocation

A parser/generator migration corpus is an authority-bearing test artifact. Passing a hand-selected subset is not proof of semantic equivalence.

Define immutable `SemanticCorpusGeneration`:

- corpus id/generation;
- exact ordered case manifest;
- case ids and content digests;
- expected canonical interpretations/results;
- policy/schema version;
- authority signatures;
- transparency checkpoint;
- predecessor generation digest;
- completeness rule.

`PASS_ALL_FETCHED_CASES != PASS_COMPLETE_CORPUS`.

A runner must prove that evaluated case ids exactly equal the authenticated generation manifest. Missing cases fail closed.

Two authenticated manifests claiming the same corpus id/generation but different roots are `CORPUS_EQUIVOCATION`.

A successor generation may add/remove/change cases only by explicit versioned supersession; it cannot reinterpret an old migration verdict retroactively.

Corpus authority and parser/generator implementation authority must be separable enough that the implementation under test cannot silently define its own passing corpus.

## 4. Escrow fork detection under partition/rejoin

Refresh and membership/threshold reconfiguration remain distinct operations.

Define `EscrowEpochTransition` with:

- predecessor epoch digest;
- operation class: `REFRESH` or `RECONFIGURE`;
- exact old/new membership and threshold;
- public commitments/verification material;
- activation boundary;
- transition quorum evidence;
- exposure-state summary;
- successor epoch digest.

Two activated successors from one predecessor are not reconciled by last-write-wins.

`same predecessor + two active successors => ESCROW_EPOCH_FORK`.

After partition/rejoin, participants must compare predecessor/successor lineage before producing any new decryption/refresh share. If incompatible active lineages exist, consequential operations fail closed pending adjudication.

Shares from sibling epochs are never mixed to meet a threshold unless the cryptographic scheme explicitly proves cross-epoch compatibility; ordinary refresh semantics do not imply such compatibility.

Partial exposure is monotone. If valid shares from an abandoned sibling were released, abandoning that branch does not erase exposure. Risk accounting includes every released share/commitment that can still contribute to reconstructability or key compromise.

A refresh may restore future resilience after bounded compromise but cannot change historical state from `THRESHOLD_COMPROMISED` back to uncompromised.

## 5. ZK transcript chunk recovery and proof-renewal downgrade detection

Define `ZKTranscriptArchiveManifest`:

- ceremony/proof-system id;
- parameter epoch;
- exact ordered transcript/chunk manifest;
- chunk digests and lengths;
- transcript root/hash;
- contribution-chain metadata;
- verifier/reference implementation versions;
- storage replica/failure-domain metadata;
- recovery policy.

A transcript hash without retrievable authenticated chunks is `TRANSCRIPT_COMMITMENT_ONLY`, not independently re-verifiable archival evidence.

Recovery must prove exact manifest closure: all mandatory chunks, ordering, contribution links and parameter derivation checks reproduce the archived root and verifier-accepted parameters.

### Renewal classes

- `REPROOF_ORIGINAL_STATEMENT`: successor proof re-evaluates the original authenticated witness/statement under successor circuit/proof-system/parameter assumptions.
- `WRAP_OLD_VERIFIER_ACCEPTANCE`: successor proof only proves that an old verifier accepted an old proof.

Only the first is a full cryptographic renewal of the original statement.

`WRAP_OLD_VERIFIER_ACCEPTANCE` inherits the old verifier/SRS assumptions and must be labeled downgrade/inherited-risk evidence, not successor-assumption evidence.

If original witness/source evidence is unavailable, a full re-proof is impossible even if the old proof can be recursively wrapped.

Proof renewal requires exact predicate/circuit semantic lineage. A successor circuit with weaker predicate is a downgrade even when the proof verifies cryptographically.

## Cross-cutting authority rules

1. Historical denominators and policy generations are immutable inputs to historical verification.
2. Loss/recovery events append new evidence; they do not rewrite prior assurance state.
3. Positive omission/censorship claims require a prior promise/acceptance/complete-observation basis. Missing data alone is not proof of malicious omission.
4. Digest preservation is not equivalent to evidence-byte preservation when independent re-verification requires the bytes.
5. Replica diversity, collector diversity, corpus authority, escrow participant independence, and ceremony contributor count are distinct concepts and must not be inferred from raw counts alone.
6. Any recovery/migration that strengthens future assurance must preserve historical compromise/degradation evidence.

## RED-first regression matrix

### Checkpoint replicas

1. two byte-identical replicas in independent destructive domains -> recover after either one is deleted;
2. two replicas under one deletion authority -> denominator counts one destructive domain;
3. surviving replica contains digest only -> recovery fails `PACKAGE_INCOMPLETE`;
4. checkpoint bytes survive but historical policy/denominator missing -> verification fails;
5. checkpoint/policy survive but required consistency ancestry missing -> `RECOVERY_UNVERIFIABLE`;
6. restore new replica after loss -> current diversity can recover but historical degradation remains recorded;
7. replica manifests disagree on package root -> fail closed;
8. stale replica is older generation than required claim -> cannot satisfy claim closure.

### Time censorship/completeness

9. no response and no authenticated challenge acceptance -> `DELIVERY_OR_RESPONSE_UNKNOWN`;
10. authenticated acceptance + complete committed collectors + no response before deadline -> positive withholding state;
11. one committed collector has valid timely response -> complete-censorship claim fails;
12. collector removed after observing inconvenient response -> denominator laundering rejected;
13. collector added after dispatch -> excluded from that challenge denominator;
14. two authorities return incompatible authenticated intervals -> conflict retained, not averaged away;
15. response nonce mismatch -> not evidence for challenged request;
16. collector equivocation on observation commitment -> collector evidence invalid/fail closed.

### Semantic corpus

17. runner executes every authenticated case and all expected results match -> pass;
18. one manifest case omitted locally but all fetched cases pass -> fail incomplete;
19. extra unmanifested case is run -> cannot alter authenticated verdict;
20. same corpus id/generation, different signed roots -> `CORPUS_EQUIVOCATION`;
21. successor corpus changes one expected result -> new generation required;
22. implementation under test supplies unsigned replacement corpus -> reject;
23. corpus case bytes mismatch manifest digest -> reject before semantic run;
24. manifest complete but expected-result schema version unavailable -> fail closed.

### Escrow partition/forks

25. one refresh successor activates normally -> old epoch retired for new operations;
26. two partitions activate siblings from same predecessor -> `ESCROW_EPOCH_FORK`;
27. rejoin attempts LWW based on later wall-clock timestamp -> reject;
28. participant from sibling A + participant from sibling B attempt threshold -> reject cross-epoch mixing;
29. abandoned sibling released one valid decryption share -> exposure remains recorded after adjudication;
30. offline member returns with old epoch and attempts share -> reject until lineage catch-up;
31. refresh after historical threshold compromise -> future epoch may recover resilience but history stays compromised;
32. reconfiguration changes threshold without explicit authorized operation class -> reject.

### ZK transcript/renewal

33. all transcript chunks recover from surviving independent storage and reproduce root -> pass archival recovery;
34. transcript root survives but mandatory chunk missing -> `TRANSCRIPT_COMMITMENT_ONLY`;
35. chunks complete but ordering manifest missing/ambiguous -> fail independent reconstruction;
36. two manifests for same parameter epoch disagree -> parameter/transcript equivocation;
37. successor proof re-proves original authenticated statement under new parameters -> full renewal candidate;
38. recursive wrapper only proves old verifier acceptance -> classify inherited-risk, not full renewal;
39. successor predicate is weaker than predecessor -> downgrade detection rejects full-renewal label;
40. original witness/source bytes unavailable -> full re-proof impossible even if old proof still verifies.

## Security decisions

- Do not use raw replica count as an independence denominator.
- Do not classify silence as censorship without authenticated delivery/acceptance plus committed observation completeness.
- Do not allow corpus discovery at runtime to define completeness; completeness comes from an authenticated immutable manifest.
- Do not merge escrow sibling epochs with last-write-wins, wall-clock recency, or cross-epoch share mixing.
- Do not classify recursive wrapping of an old proof as cryptographic renewal of the original statement.

## Relationship to executable work

This is a design/evidence freeze only. It adds RED targets for LAB-093-follow-on implementation. It does not alter the requirement that LAB-086 PR #165 remain draft until exact branch-local LAB-080→086 dependency closure, unsafe expected-failure seed, compileall, security reconciliation, and conflict audit run on byte-verified source.

## Exact next research fallback if source execution is still unavailable

Freeze the next distinct layer around:

- replica-domain authority and authenticated destructive-domain relabeling/split-brain;
- challenge-ingress receipt authority and anti-collusion between time source and collectors;
- semantic-corpus confidential cases and selective-disclosure auditability;
- escrow fork adjudication finality plus safe disposal/retirement evidence for losing branches;
- ZK proof-renewal semantic-equivalence authority and post-quantum migration of transcript/parameter attestations.
