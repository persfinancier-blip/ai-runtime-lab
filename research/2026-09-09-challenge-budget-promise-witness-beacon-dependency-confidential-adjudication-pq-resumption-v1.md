# Challenge-budget rollover, promise-GC witnesses, beacon dependency, confidential adjudication, and PQ resumption lifecycle

Date: 2026-09-09
Status: `CHALLENGE_BUDGET_PROMISE_WITNESS_BEACON_DEPENDENCY_CONFIDENTIAL_ADJUDICATION_PQ_RESUMPTION_V1_FROZEN`
Parent: LAB-093 / #178
Execution status: design/research freeze only. This does **not** substitute for LAB-086 or LAB-093 exact RED/GREEN execution.

## Why this slice exists

The previous freeze established challenge anti-amplification, promise GC conservation, versioned beacon membership, confidentiality-aware adjudication, transparency survivability, and the rule `RETRY != AUTHORITY_TO_WEAKEN_CRYPTO_POLICY`.

The remaining ambiguity was one layer deeper:

1. who owns the anti-amplification/rate-limit budget after authority rollover, and what happens when distributed replicas partition;
2. what proves a compacted historical promise set is complete after the original service and accumulator parameters are retired or compromised;
3. what prevents an emergency beacon policy from silently becoming an after-the-fact bias mechanism, especially when nominally separate beacons share dependencies;
4. how an adjudicator can verify confidential evidence without either receiving the whole secret corpus or letting selective opening hide decision-relevant evidence, and how reviewer revocation affects old verdicts;
5. how transparency split-view evidence and TLS/PQ resumption tickets survive trust-root/key/algorithm deprecation without allowing an old ticket to downgrade a new logical operation.

This note freezes those boundaries and a 40-case RED-first matrix.

## Primary donors / mechanisms

### QUIC anti-amplification

RFC 9000, Section 8, limits a server at an unvalidated client address to at most three times the bytes received until address validation. The important reusable mechanism is not the numeric factor; it is **resource expenditure bound to authenticated/validated progress rather than merely to an attacker-controlled request**.

- https://www.rfc-editor.org/rfc/rfc9000.html

### TUF root/key continuity and rollback/freeze resistance

TUF root rotation requires a new root version to satisfy the threshold of both the currently trusted root and the successor root; clients advance roots monotonically one version at a time and reject rollback. Metadata also has explicit expiration/freshness semantics.

- https://theupdateframework.io/spec/
- https://theupdateframework.github.io/specification/

Reusable mechanism: **authority rollover is a lineage transition, not a key replacement event**. Old authority must authorize the transition, successor authority must authorize its own policy, and rollback/freeze state remains observable.

### Certificate Transparency consistency and split-view evidence

RFC 9162 defines signed tree heads, inclusion proofs, consistency proofs, MMD obligations, and explicitly identifies consistency of the view presented to all query sources as an audit property. Gossip is described as the technique by which multiple clients can compare STHs and expose inconsistent views, although a single gossip protocol is not standardized there.

- https://www.rfc-editor.org/rfc/rfc9162.html

Reusable mechanism: **retain conflicting signed checkpoints plus enough ancestry/inclusion/consistency material to prove the conflict later**; do not retain only the adjudicated winner.

### NIST randomness beacon + drand threshold governance

NIST IR 8213 draft specifies signed, hash-chained beacon pulses, including precommitment of the next pulse so outputs from multiple beacons can be securely combined. drand exposes explicit DKG/resharing membership transitions and threshold configuration.

- https://csrc.nist.gov/pubs/ir/8213/ipd
- https://docs.drand.love/operator/drand-cli/

Reusable mechanism: **beacon membership and transition authority are security state**, not deployment metadata.

### Confidential selective disclosure

RFC 9901 (SD-JWT, November 2025) standardizes issuer-signed selectively disclosable claims, including key-binding/lifecycle considerations. W3C Data Integrity BBS Cryptosuites v1.0 (Candidate Recommendation Draft, 7 April 2026) provides selective disclosure and unlinkable derived proofs.

- https://www.rfc-editor.org/rfc/rfc9901.html
- https://www.w3.org/TR/vc-di-bbs/

Reusable mechanism: **selective opening can prove disclosed statements are authentically bound to a committed object; it does not by itself prove that undisclosed statements are irrelevant, absent, or complete**.

### Threshold trust distribution

NIST's Multi-Party Threshold Cryptography project states the core model directly: secret material is shared across parties so compromise of up to a threshold does not reconstruct the key, and cryptographic operations can occur without reconstructing it.

- https://csrc.nist.gov/Projects/threshold-cryptography

Reusable mechanism: **review quorum strength depends on independent compromise domains, not signature count**.

### TLS resumption and PQ transition

RFC 9846 (TLS 1.3, 2026 revision) keeps the TLS 1.3 rule that a session ticket creates a PSK derived from the original resumption master secret and that a ticket can only resume with a cipher suite using the same KDF hash as the original connection. NIST IR 8547 (initial public draft) distinguishes acceptable, deprecated, disallowed, and legacy-use states for cryptographic algorithms.

- https://www.rfc-editor.org/rfc/rfc9846.html
- https://csrc.nist.gov/pubs/ir/8547/ipd

Reusable boundary: a resumption credential is **historical authorization material derived under predecessor policy**. It cannot grant a later operation an exemption from a stricter current minimum cryptographic policy merely because it remains syntactically valid.

## Frozen model A — ChallengeBudgetEpoch

A challenge service has an authenticated budget policy generation:

```text
ChallengeBudgetEpoch = {
  service_id,
  epoch,
  predecessor_epoch,
  authority_set_id,
  authority_threshold,
  unit_definition,
  per_request_limit,
  per_subject_limit,
  global_limit,
  refill_rule,
  partition_rule,
  replay_window,
  effective_from,
  policy_digest,
  signatures
}
```

### A1. Budget authority rollover is a trust transition

A new budget authority/key is not trusted merely because it signs a new epoch. A normal rollover must satisfy predecessor authorization and successor authorization, analogous to TUF root continuity.

If predecessor authority is known compromised, recovery follows the separately authenticated recovery-root path; it must not pretend that compromised predecessor authorization is meaningful.

### A2. Distributed rate limiting is security state

For a consequential expensive challenge, a partitioned replica may not independently reset or mint a full fresh global budget merely because it cannot reach peers.

The system must predeclare one of a small set of partition semantics, for example:

- `FAIL_CLOSED_GLOBAL`: no new globally expensive work without quorum;
- `PREALLOCATED_SHARDS`: each replica/domain receives a signed bounded sub-budget before partition;
- `LOCAL_ONLY_CLASS`: only explicitly low-cost locally bounded challenges continue;
- never `RESET_ON_PARTITION` for authority-sensitive work.

A later merge conserves spent budget across shards. Duplicate/replayed challenge IDs remain spent even if the request landed on different replicas.

### A3. Validation progress, not request authenticity alone, unlocks expenditure

A valid signature on an attacker-replayed request proves origin/authorization but does not justify unbounded repeated work. Expensive response work must be bounded by a one-shot challenge identity, authenticated cost class, replay state, and budget state.

This follows the reusable QUIC pattern: expensive output is gated by validated peer progress and a bounded amplification ratio, not merely by receipt of input.

### A4. Rate-limit exhaustion is not member-loss evidence

If an authority or reviewer has exhausted its challenge budget, its temporary inability to execute another liveness ceremony is `BUDGET_EXHAUSTED`, not `MEMBER_LOST`, `KEY_LOST`, or authority to lower the recovery threshold.

## Frozen model B — PromiseArchiveWitnessGeneration

Promise GC already requires conservation of every predecessor promise into exactly one terminal/carried disposition. This slice adds independent historical witnessability.

```text
PromiseArchiveWitnessGeneration = {
  archive_id,
  generation,
  predecessor_population_root,
  disposition_root,
  mapping_root,
  accumulator_or_tree_scheme,
  parameter_set_id,
  parameter_provenance,
  witness_population,
  witness_threshold,
  archive_locations,
  effective_from,
  signatures
}
```

### B1. GC completion is not self-attested by the compacting service

The service performing compaction cannot be the sole witness that no promise disappeared. A policy-defined independent witness quorum must attest the predecessor root, mapping/disposition root, and archive-generation identity.

`COMPACTOR_SAYS_COMPLETE != INDEPENDENT_COMPLETENESS_EVIDENCE`.

### B2. Historical non-membership needs a historical namespace

After GC, a current accumulator or current database query cannot prove that a promise never existed historically.

`CURRENT_NON_MEMBERSHIP != HISTORICAL_NON_EXISTENCE` remains frozen.

A historical query must name the exact population generation/root and receive a proof relative to that historical root.

### B3. Accumulator parameters are part of the trust root

If a membership/non-membership proof system has parameters, setup material, verifier implementation, or a parameter-generation ceremony, those are authenticated dependencies of the archive generation.

Parameter compromise does not cause old records to be silently reinterpreted as valid or invalid. It creates a degradation event and, when required, a successor archive generation with migrated/rebuilt proofs from the immutable predecessor population/mapping data.

### B4. Migration must preserve proof meaning

A new accumulator/tree generation must preserve:

- exact predecessor namespace;
- exact predecessor population root;
- exact promise-to-disposition mapping;
- exact terminal/carried semantics;
- explicit mapping from old proof identifiers to successor proof identifiers.

A new root over a newly enumerated subset is not a migration; it is a new claim.

## Frozen model C — BeaconDependencyEpoch and emergency policy

```text
BeaconDependencyEpoch = {
  beacon_set_id,
  epoch,
  members,
  dependency_claims,
  independent_domain_classes,
  combiner,
  rounds,
  timeout_rule,
  missing_source_rule,
  emergency_policy,
  emergency_authority,
  effective_from,
  signatures
}
```

### C1. Emergency policy is fixed before reveal

Emergency behavior must be committed before any relevant beacon output is known. It may specify, for example, fail-closed, delayed decision, or a predeclared reduced source set under narrowly defined outage conditions.

It may not say "use any available beacon chosen by the operator" after reveal.

`EMERGENCY != POST_REVEAL_DISCRETION`.

### C2. Emergency authority cannot rewrite the current sample

An emergency governance action can affect only a future decision boundary unless the old policy explicitly precommitted the exact emergency transition for the current decision.

Otherwise an operator could observe unfavorable randomness, declare an emergency, remove a source, and recompute.

### C3. Independence is an evidence claim

Two beacon endpoints can share:

- cloud/region/operator;
- signing/DKG control plane;
- entropy source;
- build artifact/library;
- upstream time source;
- network path/anti-DDoS provider.

Therefore `N_BEACONS != N_INDEPENDENT_BEACONS`.

A dependency attestation records known common domains and the independence policy. Unknown dependency cells are not silently counted as independent.

### C4. Correlated outage is not a license to resample

If several beacons fail because of one shared domain outage, the result follows the precommitted timeout/missing-source policy. Retry, round substitution, source replacement, or emergency enrollment after seeing partial outputs creates a new decision generation.

## Frozen model D — ConfidentialAdjudicationGeneration

```text
ConfidentialAdjudicationGeneration = {
  dispute_id,
  generation,
  committed_evidence_population_root,
  disclosure_policy,
  required_claim_classes,
  reviewer_set_id,
  reviewer_threshold,
  independence_claims,
  selective_opening_scheme,
  revocation_policy,
  verdict,
  verdict_evidence_root,
  predecessor_generation,
  signatures
}
```

### D1. Population commitment precedes selective opening

Before adjudication begins, the party presenting confidential evidence commits to the complete policy-relevant evidence population (or a trusted collector commits it).

Selective disclosure may then reveal only necessary fields/items. But an adjudicator may not infer completeness from the set voluntarily disclosed after the dispute outcome becomes predictable.

`VALID_SELECTIVE_PROOFS != COMPLETE_DECISION_POPULATION`.

### D2. Threshold privacy and threshold judgment are distinct

A threshold of reviewers can be required to reach a verdict without every reviewer seeing all plaintext evidence. For example, evidence can be partitioned by role, selectively disclosed, or evaluated with privacy-preserving proofs.

However, the system must separately state:

- which reviewers saw which claim classes;
- which claim classes were proven without plaintext disclosure;
- which threshold establishes verdict authority;
- which threshold establishes evidence-population completeness.

A quorum of signatures over the final verdict is not automatically a quorum that independently checked every hidden claim.

### D3. Selective opening cannot hide contradiction existence

A proof that disclosed claim X is authentic does not prove that hidden claim Y does not contradict X. Policy must identify decision-relevant claim classes whose existence/commitment must be accounted for even when contents remain secret.

Possible result states include:

- `VERIFIED_DISCLOSED_SUBSET`;
- `POPULATION_COMMITTED_CONTENT_CONFIDENTIAL`;
- `REQUIRED_CLAIM_CLASS_UNOPENED`;
- `ADJUDICATION_EVIDENCE_INSUFFICIENT`.

### D4. Reviewer revocation is monotonic evidence, not history rewrite

If reviewer R is later compromised/revoked, prior verdicts that depended on R are reclassified according to the policy effective when the verdict was issued, for example:

- `HISTORICALLY_VALID_UNDER_THEN_POLICY`;
- `ASSURANCE_DEGRADED`;
- `REAUDIT_REQUIRED`;
- `INVALIDATED` only when the policy and compromise evidence justify it.

A clean successor reviewer cannot simply re-sign the old verdict and call it a re-audit; a re-audit requires fresh independent evaluation of the same committed population or an explicitly equivalent successor population.

## Frozen model E — Transparency split-view retention + PQ resumption lifecycle

### E1. Split-view evidence is never garbage-collected into the winner

If observers possess incompatible signed checkpoints for the same log/time/tree position or possess an unresolvable consistency failure, both views plus observation metadata are durable evidence.

Adjudicating one view as canonical does not authorize deletion of the losing signed checkpoint/evidence.

`SPLIT_VIEW_ADJUDICATED != SPLIT_VIEW_NEVER_HAPPENED`.

Required retained material is policy-dependent but includes, when available:

- exact signed checkpoints/tree heads;
- log/key epoch;
- tree sizes/timestamps;
- consistency/inclusion material;
- observer/witness identities and observation times;
- trust-root lineage needed for later signature verification.

### E2. Mirror count is not witness independence

A mirror that simply copies one operator's view improves availability, not independent split-view detection. Independent witnesses must obtain/retain checkpoints through sufficiently independent observation/control domains to make equivocation observable.

### E3. Resumption tickets are predecessor-policy credentials

A TLS/PQ/hybrid resumption ticket binds to the predecessor session and its derived PSK. It is not a general authorization token to bypass current cryptographic policy.

For every resumed logical operation, evaluate:

```text
current_minimum_crypto_policy
AND ticket/session predecessor policy
AND ticket lifetime/revocation status
AND server/current trust-root status
AND operation replay/idempotency policy
```

The current policy is a floor, not a suggestion.

### E4. Algorithm deprecation has an effective-time boundary

Using the NIST lifecycle vocabulary:

- `acceptable`: new operations may use it subject to policy;
- `deprecated`: explicitly risk-accepted use only if policy permits;
- `disallowed`: must not authorize new use for the disallowed purpose;
- `legacy-use`: may permit processing historical protected material, e.g. verification/decryption, without authorizing new protection.

Therefore an old ticket whose predecessor KEM/signature/authentication suite is now below the current floor can still be retained as historical evidence but cannot force abbreviated resumption. The safe path is a full fresh handshake satisfying the current policy, or fail closed.

### E5. Ticket-key rotation does not erase ticket provenance

If servers rotate ticket-encryption keys, accepted tickets must still map to an authenticated issuing epoch/policy. An unknown or retired ticket key may cause the ticket to be ignored and a full handshake attempted; it must not trigger fallback below the current crypto floor.

### E6. Retry/resumption transcript anti-downgrade

A retry path records:

- initial offer set;
- rejection/retry reason;
- ticket/PSK identity or digest;
- successor offer set;
- selected suite;
- current policy epoch;
- session context.

A retry that removes a policy-required PQ/hybrid option without an authenticated policy-authorized reason is `DOWNGRADE_DETECTED`, even if the resulting classical handshake is otherwise cryptographically valid.

## Cross-cutting frozen invariants

1. **Rollover never resets history.** Budget authority, promise witnesses, beacon governance, reviewers, transparency keys, and ticket keys all transition by authenticated generations.
2. **Partition is not authority.** Loss of coordination does not mint fresh budget, lower quorum, or authorize after-the-fact source selection.
3. **Completeness and validity are different claims.** A valid proof for selected records does not prove the population is complete.
4. **Independence is measured in failure/control domains.** Signature, mirror, reviewer, or beacon count alone is insufficient.
5. **Compromise creates monotonic degradation evidence.** Successor cleanliness does not rewrite predecessor compromise.
6. **Historical verification and new authorization are different operations.** Legacy evidence may remain verifiable while being forbidden for new consequential operations.
7. **Emergency/retry paths inherit the original operation's minimum security floor unless a precommitted authenticated policy explicitly defines a stronger/equivalent transition.**

## 40-case RED-first matrix

### Challenge budget / rollover / partition — A01..A08

| ID | Scenario | Required result |
|---|---|---|
| A01 | Replay exact authenticated expensive challenge to same replica | one execution; replay rejected/no second budget spend |
| A02 | Replay same challenge to different partitioned replica | globally one execution or bounded preallocated shard semantics; no reset |
| A03 | Authority epoch N key signs epoch N+1 without predecessor transition authorization | reject successor epoch |
| A04 | Valid predecessor + successor signatures on monotonic N→N+1 | accept rollover |
| A05 | Partition under `FAIL_CLOSED_GLOBAL` | no new global expensive challenge |
| A06 | Partition under signed preallocated shard budgets | permit only within each shard's remaining allocation; merge conserves spend |
| A07 | Verifier deliberately exhausts member challenge quota then labels member lost | classify budget exhausted; do not lower recovery threshold |
| A08 | Crash/restart loses volatile replay counters but durable budget epoch remains | replay still rejected; quota does not reset |

### Promise GC archive / witnesses / parameter migration — B01..B08

| ID | Scenario | Required result |
|---|---|---|
| B01 | Compactor alone signs "all promises conserved" | insufficient assurance |
| B02 | Independent witness quorum signs exact predecessor/mapping/disposition roots | accept completeness generation |
| B03 | One predecessor promise omitted and another duplicated so counts match | reject exact mapping/conservation proof |
| B04 | Query current accumulator for an ID absent after GC and claim it never existed | reject historical-nonexistence inference |
| B05 | Historical proof names exact predecessor root and proves disposition mapping | accept according to old generation policy |
| B06 | Accumulator parameter set later compromised | mark affected generations degraded; preserve evidence |
| B07 | Successor parameter set recomputes only surviving subset | reject as migration |
| B08 | Successor generation rebuilds from immutable full predecessor population/mapping and preserves lineage | accept migration subject to policy |

### Beacon emergency governance / dependency — C01..C08

| ID | Scenario | Required result |
|---|---|---|
| C01 | Operator sees outputs then invokes unspecified emergency source | reject/post-reveal discretion |
| C02 | Precommitted outage rule activates before reveal conditions are met | reject premature emergency transition |
| C03 | Precommitted fail-closed rule with source outage | no decision/no resample |
| C04 | Two endpoints share same DKG/control/cloud domain but are counted as two independent sources | reject independence count |
| C05 | Dependency cells unknown for required independence threshold | insufficient independence assurance |
| C06 | Correlated outage causes post-reveal source removal then recompute | reject; new decision generation required |
| C07 | Governance enrolls a new beacon effective at future round R+1 | old R denominator unchanged; R+1 may use new set |
| C08 | Valid signed/hash-chained pulses from all precommitted sources + deterministic combiner | accept sample if all other policy checks pass |

### Confidential adjudication / selective opening / reviewer revocation — D01..D08

| ID | Scenario | Required result |
|---|---|---|
| D01 | Evidence subset disclosed without prior complete population commitment | cannot claim complete adjudication |
| D02 | Selectively disclosed claim verifies cryptographically | accept authenticity of disclosed claim only |
| D03 | Hidden committed claim belongs to policy-required decision class but is not opened/proven | evidence insufficient |
| D04 | Reviewer quorum signs verdict but only one reviewer actually checked hidden required class | do not infer independent review of that class |
| D05 | Threshold review preserves plaintext secrecy while policy-required proofs cover all claim classes | accept if reviewer/evidence thresholds both satisfied |
| D06 | Reviewer R later revoked after being decisive in old verdict | preserve old verdict + apply degradation/re-audit policy; no history rewrite |
| D07 | Successor reviewer simply re-signs old verdict without evaluating committed population | not a re-audit |
| D08 | Fresh independent re-audit covers same population root with successor reviewer generation | accept successor verdict while retaining predecessor lineage |

### Transparency split view / PQ resumption lifecycle — E01..E08

| ID | Scenario | Required result |
|---|---|---|
| E01 | Two incompatible signed tree heads observed for same logical checkpoint | retain both; classify split-view/equivocation evidence |
| E02 | Adjudicator chooses canonical head then GC deletes losing signed head | reject evidence-retention policy |
| E03 | Five mirrors all consume one operator's feed | availability=5 copies, witness independence=1 domain unless other evidence exists |
| E04 | Independent witnesses retain conflicting heads plus trust-root lineage | later split-view proof remains verifiable after log retirement/key rotation |
| E05 | Resumption ticket was issued under policy now below current PQ/hybrid floor | do not resume below floor; full compliant handshake or fail closed |
| E06 | Ticket key is retired/unknown | ignore ticket/full handshake; do not weaken current suite requirements |
| E07 | Retry removes required PQ/hybrid offer after ticket rejection with no policy-authorized reason | downgrade detected |
| E08 | Historical signature/ticket uses algorithm now `legacy-use` only | historical verification may remain allowed; new consequential authorization denied |

## Implementation consequences for LAB-093+

When this architecture reaches executable work, do not introduce one monolithic "security policy" object. Keep generation boundaries explicit and independently testable:

- `ChallengeBudgetEpoch` / durable replay+spend ledger;
- `PromiseArchiveWitnessGeneration` / predecessor+mapping roots and witness policy;
- `BeaconDependencyEpoch` / membership, dependencies, combiner, timeout/emergency rules;
- `ConfidentialAdjudicationGeneration` / population root, disclosure policy, reviewer generation, verdict evidence;
- `CryptoPolicyEpoch` + ticket/session issuing epoch + transparency checkpoint lineage.

Every transition should be modelled as append-only successor state with anti-rollback checks. Runtime caches may accelerate reads but are not authority.

## Audit notes / non-claims

- No exact repository behavioral test was executed for this design slice in this run.
- No LAB-086 executable source closure was reconstructed or manually reserialized.
- RFC/NIST/W3C/TUF/drand mechanisms are donors; the lab-specific state machines above are design decisions/inferences, not claims that those standards mandate the exact lab schema.
- NIST IR 8213 and IR 8547 sources cited above are draft-status documents; they are used for concepts/transition vocabulary, not represented as final NIST requirements.
- W3C BBS is a Candidate Recommendation Draft as of 2026-04-07, not a final Recommendation.

## Exact next distinct research slice if executable source is still unavailable

Study and freeze:

**distributed budget lease expiration/clock authority + witness archival availability under witness retirement and archive-domain loss + beacon dependency-attestation authority compromise/revocation + confidential evidence population commitment redaction/deletion requests without audit-history corruption + PQ resumption across cross-cluster ticket-key replication, server identity rotation, and crypto-policy clock/freshness failure**.

If exact source execution becomes available first, stop fallback expansion and return immediately to LAB-086's retained exact gate.