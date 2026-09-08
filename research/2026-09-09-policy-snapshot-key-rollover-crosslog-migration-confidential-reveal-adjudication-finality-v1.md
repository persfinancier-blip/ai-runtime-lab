# Historical policy snapshots, identity-key rollover, cross-log crypto migration, confidential reveal, and adjudication finality — v1

Date: 2026-09-09
Status: **FROZEN DESIGN CONTRACT**
Contract ID: `POLICY_SNAPSHOT_ROLLOVER_CROSSLOG_MIGRATION_CONFIDENTIAL_REVEAL_ADJUDICATION_FINALITY_V1_FROZEN`
Parent: LAB-093 / #178

## Why this exists

The preceding LAB-093 freezes established retained witness frontiers, epoch-bound denominators, cross-log anchor obligations, commit-before-reveal semantic attestation, and independent compromise-boundary adjudication. Five lifecycle questions remained materially open:

1. can historical verification survive policy metadata garbage collection;
2. can witness/collector identity keys roll without silently laundering continuity;
3. can cross-log proofs remain verifiable across hash/signature migrations;
4. can semantic challenges/results remain confidential until the reveal boundary without weakening anti-copy guarantees;
5. when is a compromise-boundary adjudication final, and what evidence is required to reopen it.

This note freezes those semantics before implementation.

## Primary donors and evidence

### TUF — retained trust-chain continuity
The Update Framework requires clients updating root trust to fetch intermediate root metadata sequentially and verify each successor under both predecessor and successor thresholds. Its specification also states that **all released root metadata versions must remain available** so outdated clients can retrace the chain of trust. Repository withholding can still cause a freeze attack; retention is therefore necessary for continuity, not sufficient for freshness.

Source: TUF specification, current v1.0.x workflow and key-management/migration sections:
- https://github.com/theupdateframework/specification/blob/master/tuf-spec.md
- https://theupdateframework.io/spec/

### RFC 9162 — immutable historical checkpoints and consistency
Certificate Transparency v2 defines signed tree heads, unique log identity, inclusion proofs, and append-only consistency proofs between tree heads. Historical proof verification depends on retaining the exact log parameters/key identity and the hashes/proofs needed to connect the relevant tree heads. A new log/key is not automatically the old log merely because an operator says so.

Source: RFC 9162:
- https://www.rfc-editor.org/rfc/rfc9162.html

### RFC 4998 — long-term evidence renewal
Evidence Record Syntax explicitly separates timestamp renewal from hash-tree renewal. If only timestamp/public-key validity is becoming weak, a new timestamp can cover the old timestamp. If the hash binding itself becomes weak, all relevant archived data/evidence must be accessed and hashed again under a new secure hash before the old binding loses trust. The evidence record also retains certificates, revocation information, trust anchors, policy details, and related validation material needed later.

Source: RFC 4998:
- https://www.rfc-editor.org/rfc/rfc4998/

### NIST SP 800-57 — key lifecycle and archived verification material
NIST key-management guidance treats cryptographic keys and associated metadata as lifecycle-managed security material and explicitly covers archive, backup, compromise, cryptoperiods, trust anchors, and key inventory/metadata protection. The 2025 Revision 6 draft additionally incorporates post-quantum algorithms and separates key-storage concerns more explicitly.

Sources:
- https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
- https://csrc.nist.gov/pubs/sp/800/57/pt1/r6/ipd

## Frozen distinctions

The following equalities are **forbidden**:

```text
POLICY_ID_KNOWN == POLICY_BYTES_AVAILABLE
CURRENT_POLICY == HISTORICAL_POLICY
KEY_ROLLED == IDENTITY_CONTINUITY_PROVEN
NEW_KEY_SIGNED_BY_OLD == ROLLOVER_NON_EQUIVOCATING
NEW_LOG_VERIFIES_NEW_HASH == OLD_CROSSLOG_PROOF_MIGRATED
REHASH_NOW == HISTORICAL_BINDING_RESTORED
COMMITMENT_EXISTS == PRE_REVEAL_CONFIDENTIALITY
ENCRYPTED_RESULT == INDEPENDENT_SEMANTIC_COMPUTATION
APPEAL_FILED == PRIOR_DECISION_VOID
NEWER_ADJUDICATION == LEGITIMATE_REOPENING
FINAL == FOREVER UNCHANGEABLE
```

## 1. Historical policy snapshot availability and GC safety

### 1.1 Policy snapshots are evidence dependencies
Every consequential historical statement must bind an immutable `policy_snapshot_digest` plus a versioned policy identity. Verification of that historical statement requires the exact policy bytes (or a formally sufficient canonical projection) that were in force for that decision.

A policy digest without recoverable bytes proves only that *some bytes* were committed, not what rules must be applied.

### 1.2 Three retention classes
Policy material is classified as:

- `ACTIVE_POLICY`: current rule set used for new decisions;
- `HISTORICAL_REQUIRED`: no longer current but still required to verify at least one retained evidence chain;
- `GC_ELIGIBLE`: no retained evidence chain can legally or technically depend on it, and an authenticated dependency census proves this.

`SUPERSEDED != GC_ELIGIBLE`.

### 1.3 GC admission rule
Garbage collection of a policy snapshot is allowed only if all are true:

1. an authenticated dependency index identifies every evidence object that binds the snapshot;
2. every such evidence object is itself expired under a policy that permits deletion **or** has been renewed into a self-sufficient successor evidence package that no longer depends on the old policy bytes;
3. the GC decision binds the exact policy digest and dependency-index frontier;
4. the GC decision is append-only/auditable and cannot rewrite historical evidence;
5. at least the required independent archival domains have durably retained any migration package necessary for later verification.

### 1.4 Fail-closed state
If historical evidence references a policy digest whose bytes cannot be recovered from an authenticated archive, verification returns:

`HISTORICAL_POLICY_UNAVAILABLE`

It must not silently apply the current policy or a semantically "similar" policy.

### 1.5 Policy self-description is not enough
A policy snapshot cannot unilaterally declare itself safe to delete. Retention/GC authority is a separate role from policy-authoring authority, and the dependency census is independently reproducible.

## 2. Witness / collector identity-key rollover without continuity laundering

### 2.1 Stable logical identity vs key epochs
A witness or collector has:

```text
logical_identity
identity_lineage_id
key_epoch
verification_key
valid_from
valid_until / retired_at
predecessor_epoch_digest
rollover_evidence_digest
```

Historical statements bind **both** logical identity and key epoch.

### 2.2 Rollover continuity
Normal rollover requires a `KeyEpochTransition` that is:

- authorized by the predecessor epoch under the predecessor policy;
- authorized by the successor epoch under the successor policy;
- bound to exact predecessor/successor key material and effective boundary;
- transparently published before relying on the successor for consequential decisions;
- non-equivocating at a single predecessor frontier.

This mirrors TUF's predecessor+successor root-threshold continuity.

### 2.3 Rollover does not rewrite historical quorum
A witness that signed checkpoint X with key epoch K1 remains K1 for that historical checkpoint. Later K2 signatures do not recast X as if K2 had signed it.

Likewise, removing K1 from the current key set does not remove K1's historical dissent, participation, or denominator membership.

### 2.4 Equivocating rollover
Two different validly authorized successors from the same predecessor epoch/frontier produce:

`IDENTITY_KEY_ROLLOVER_EQUIVOCATION`

Do not choose the higher timestamp or lexicographically larger key. Resolution requires the separately frozen recovery/adjudication path.

### 2.5 Compromised predecessor
If predecessor authority is known compromised before the claimed rollover boundary, its signature cannot by itself establish continuity. Recovery must use an independently trusted recovery/higher root or begin a new lineage.

## 3. Cross-log proof survivability under hash/key algorithm migration

### 3.1 Cross-log proof package
A durable cross-log anchor package must retain:

```text
source_log_id
source_log_key_epoch
source_log_parameters
source_checkpoint_bytes
source_checkpoint_signature
source_hash_algorithm
source_tree_proof material

destination_log_id
destination_log_key_epoch
destination_log_parameters
destination_checkpoint_bytes
destination_checkpoint_signature
destination_hash_algorithm
anchor_entry_bytes
inclusion_proof
consistency/frontier evidence

policy_snapshot_digest
migration_evidence_chain
```

A pointer to a live API is not preservation evidence.

### 3.2 Key rotation vs log identity
A signature-key rotation for the same logical log requires an authenticated key-epoch transition. A replacement log with a new `log_id` is a new log unless an independently frozen migration contract explicitly links the identities.

`SAME_OPERATOR != SAME_LOG_IDENTITY`.

### 3.3 Signature-algorithm migration
If the Merkle/hash binding remains secure but a signing algorithm/key is approaching expiry/deprecation, a successor evidence layer may timestamp/sign the old checkpoint/proof package before the old signature trust is lost. This is analogous to RFC 4998 timestamp renewal.

### 3.4 Hash migration
If a hash algorithm used in the source or destination tree/proof is approaching unacceptable status, **the complete evidence inputs required to recompute the binding must be available before migration**. A new secure hash must bind:

- the original canonical entry/checkpoint/proof bytes;
- the complete prior evidence chain;
- the old algorithm identifiers;
- the policy/validity state under which the migration occurred.

This is analogous to RFC 4998 Hash-Tree Renewal.

### 3.5 No post-break rehabilitation
If the only historical binding used hash H and H is already untrustworthy before any independent successor anchor was created, hashing the bytes presented today under H2 does not prove those are the bytes that existed historically.

State:

`HISTORICAL_BINDING_LOST_NO_PREBREAK_RENEWAL`

### 3.6 Dual-frontier migration
During a planned migration, current reliance may require both legacy and successor proof families for an overlap window:

`LEGACY_VALID && SUCCESSOR_VALID && CROSS_BOUNDARY_LINK_VALID`

Only after the frozen retirement boundary may new evidence omit the legacy family. Historical evidence keeps the legacy identifiers and renewal chain forever while it remains retained.

## 4. Challenge/result confidentiality before semantic-attester reveal

Commit-before-reveal blocks trivial answer copying only if participants cannot read another participant's semantic result before their own commitment is irrevocably fixed.

### 4.1 Required phases

```text
CHALLENGE_COMMITTED
CHALLENGE_DISTRIBUTED_CONFIDENTIALLY
RESULT_COMMITTED
COMMIT_PHASE_CLOSED
RESULT_REVEAL
QUORUM_EVALUATION
```

### 4.2 Challenge confidentiality
If the challenge itself would permit precomputation/collusion, the scheduler commits to a challenge digest first, then distributes the challenge to each attester over an authenticated confidential channel. Public reveal occurs only after the result-commit deadline.

Scheduler visibility is explicitly a trust dependency; confidentiality from peers does not imply confidentiality from the scheduler.

### 4.3 Result commitment
Before reveal, each attester publishes/retains a binding commitment over:

```text
challenge_digest
input_digest
verdict
canonical_output_digest
evidence_digest
provenance_digest
attester_identity_epoch
nonce
```

The commitment must be hiding enough that practical verdict/output inference is not possible from the commitment alone. A plain unsalted hash over a low-entropy Boolean verdict is forbidden.

### 4.4 Optional encrypted escrow
For stronger availability, an attester may also publish ciphertext of the committed result to an independently governed threshold-decryption escrow. Requirements:

- ciphertext is bound to the same commitment;
- no single peer attester can decrypt before commit close;
- emergency decryption is policy-gated, attributable, and transparent;
- escrow availability does not increase semantic quorum count.

### 4.5 Reveal failure
An attester that committed but does not reveal is `COMMITTED_NONREVEAL`. Its commitment is evidence of participation, but it contributes no semantic verdict unless the predeclared escrow recovery path successfully opens the exact committed value.

### 4.6 What this does not prove
Confidential commit/reveal reduces opportunistic copying. It does **not** prove independent computation when attesters share an implementation, operator, precomputed answer channel, or collude before commitment. Provenance/control-domain independence remains a separate predicate.

## 5. Appeal and finality for compromise-boundary adjudication

### 5.1 Decision object
Every boundary decision is immutable:

```text
AdjudicationDecision {
  case_id,
  decision_id,
  predecessor_decision_id?,
  affected_authority_lineage,
  claimed_compromise_interval,
  effective_from,
  evidence_set_digest,
  policy_snapshot_digest,
  adjudicator_set_epoch,
  quorum_evidence,
  decision_time,
  status
}
```

### 5.2 Status vocabulary

- `PROVISIONAL`: usable only for fail-closed containment; appeal window open;
- `FINAL_CURRENT_RECORD`: normal appeal window exhausted or resolved;
- `SUPERSEDED_ON_APPEAL`: replaced by a later valid decision;
- `REOPENED_NEW_EVIDENCE`: extraordinary review accepted under a stricter reopening rule;
- `VOID_AUTHORITY_COMPROMISE`: adjudicator threshold itself proven compromised for the relevant decision.

Historical decision objects are never deleted.

### 5.3 Appeal is not nullification
Filing an appeal does not make the prior decision disappear. Consequential reliance during appeal follows the frozen risk rule, normally choosing the more conservative boundary unless policy explicitly provides otherwise.

### 5.4 Asymmetric burden for moving the boundary
Moving `effective_from` **earlier** invalidates additional evidence and is conservative for trust but can have availability/business consequences. Moving it **later** rehabilitates evidence previously treated as compromised and therefore requires the stricter authorization class.

Frozen rule:

```text
LATER_BOUNDARY_REQUIRES >= original_quorum
                       + independent_new_evidence
                       + recovery/higher-root authorization
```

A same-threshold self-review is insufficient when it would re-legitimize consequential history.

### 5.5 Extraordinary reopening
A `FINAL_CURRENT_RECORD` can reopen only for one of:

1. cryptographically authenticated new evidence unavailable with due diligence during original adjudication;
2. proof that a material evidence item was forged/tampered;
3. proof that the adjudicator threshold was compromised or conflicted;
4. policy-defined correction of a deterministic canonicalization/verification defect.

Mere disagreement or a new interpretation is insufficient.

### 5.6 Finality semantics
`FINAL_CURRENT_RECORD` means final under the ordinary process and current evidence, **not metaphysically immutable**. Append-only extraordinary reopening preserves both operational finality and the ability to recover from later-proven compromise.

### 5.7 No self-exoneration
An authority whose compromise boundary is being adjudicated cannot contribute to the independent quorum that moves its own boundary later. Likewise, adjudicators accused of threshold compromise are excluded from the recovery quorum deciding that allegation.

## Combined assurance model

A historical consequential decision is currently reproducible only if:

```text
POLICY_BYTES_AVAILABLE
&& POLICY_DIGEST_MATCHES
&& IDENTITY_KEY_EPOCH_CHAIN_VALID
&& HISTORICAL_DENOMINATOR_PRESERVED
&& LOG_CHECKPOINT_AND_PROOF_PACKAGE_AVAILABLE
&& CRYPTO_RENEWAL_CHAIN_VALID_AT_EACH_BOUNDARY
&& SEMANTIC_COMMIT_REVEAL_RULES_SATISFIED
&& APPLICABLE_ADJUDICATION_RECORD_VALID
```

Any missing term yields a typed degraded/unknown state; no term is silently substituted by current configuration.

## RED-first executable matrix (64 cases)

### A. Historical policy snapshot / GC — 1..16
1. historical evidence + exact retained policy => PASS;
2. digest retained, bytes deleted => `HISTORICAL_POLICY_UNAVAILABLE`;
3. current policy substituted for missing historical policy => REJECT;
4. semantically similar policy with different bytes => REJECT;
5. superseded policy still referenced => not GC-eligible;
6. dependency index omits one retained evidence object => GC REJECT;
7. dependency index frontier stale during concurrent evidence append => GC REJECT/CAS retry;
8. renewed self-sufficient evidence removes last dependency => GC may become eligible;
9. renewal package missing old policy digest => REJECT;
10. policy author alone signs GC => insufficient authority;
11. GC authority deletes policy before archival receipt threshold => REJECT;
12. one archive domain later lost but threshold remains => historical verification still PASS;
13. all policy archives lost => typed unavailable, no current-policy fallback;
14. retained policy bytes hash mismatch => tamper/fail closed;
15. historical policy parser version unavailable => verification degraded, no parser substitution;
16. GC event retained but target policy already absent without valid GC evidence => tamper/unknown.

### B. Witness/collector key rollover — 17..28
17. valid predecessor+successor authorized rollover => PASS;
18. successor self-signature only => REJECT;
19. predecessor signature only, successor threshold missing => REJECT;
20. skipped intermediate key epoch => continuity REJECT;
21. two successors from same predecessor frontier => equivocation;
22. current K2 cannot rewrite old K1 signature identity => preserve K1;
23. retiring K1 cannot shrink historical witness denominator => preserve denominator;
24. compromised predecessor before rollover effective time => normal continuity invalid;
25. out-of-band recovery starts authorized successor lineage => PASS under recovery policy;
26. same operator/name with unrelated key and no transition => new identity/unknown;
27. rollover transition withheld from partitioned verifier => verifier remains on retained K1 frontier/fails freshness;
28. replay old valid rollover after newer accepted epoch => rollback REJECT.

### C. Cross-log key/hash migration — 29..42
29. old source+destination proof package fully retained => historical PASS;
30. destination API gone but proof bytes/checkpoints retained => PASS;
31. pointer retained but historical proof bytes unavailable => nonreproducible;
32. signing-key rotation with authenticated key-epoch link => PASS;
33. new operator key without link => new identity/reject continuity;
34. new log id claimed as old log => REJECT;
35. pre-expiry signature/timestamp renewal covers old package => PASS;
36. post-compromise-only re-sign with no prior anchor => cannot rehabilitate;
37. pre-break hash-tree renewal with complete old evidence => PASS;
38. hash migration missing canonical old entry bytes => REJECT;
39. hash migration missing old algorithm identifiers => REJECT;
40. overlap policy requires legacy+new; only new present => REJECT during overlap;
41. after retirement new evidence may use successor only, historical evidence keeps renewal chain => PASS;
42. algorithm later deprecated: current reliance re-appraised without deleting historical receipts.

### D. Confidential semantic commit/reveal — 43..54
43. peer cannot see verdict before own commitment => PASS baseline;
44. plain hash of Boolean verdict without nonce => REJECT as non-hiding;
45. commitment binds challenge/input/output/evidence/provenance => PASS;
46. reveal differs from commitment => REJECT/equivocation;
47. result revealed before commit close => round invalid or leaking participant excluded per frozen policy;
48. challenge publicly revealed before commit when secrecy required => round invalid;
49. scheduler sees challenge but peers do not => record scheduler as common trust dependency;
50. committed non-reveal => no semantic vote;
51. threshold escrow opens exact committed result after permitted deadline => recovered vote only under predeclared policy;
52. escrow decrypts mismatching plaintext => REJECT;
53. two attesters use same implementation/operator despite confidential reveal => count per independence policy, not signature count;
54. participant copies a result through pre-commit side channel => protocol cannot claim independence; provenance challenge must detect/limit separately.

### E. Adjudication appeal/finality — 55..64
55. provisional boundary applied fail-closed during appeal => PASS;
56. appeal filed => prior record remains immutable and operative per appeal policy;
57. ordinary quorum moves boundary earlier with authenticated new evidence => allowed if policy threshold met;
58. same quorum moves boundary later without stricter recovery evidence => REJECT;
59. later-boundary decision with independent new evidence + higher/recovery authorization => PASS;
60. final record reopened only because of disagreement => REJECT;
61. final record reopened for newly authenticated material evidence => PASS under extraordinary threshold;
62. adjudicator threshold later proven compromised => mark affected decision `VOID_AUTHORITY_COMPROMISE`, preserve bytes, invoke out-of-band recovery;
63. compromised subject authority votes to exonerate/move its boundary later => vote excluded;
64. contradictory final decisions at same predecessor/case frontier => adjudication equivocation; do not LWW.

## Implementation shape

Do not implement five isolated ad-hoc tables. The intended architecture is a common immutable evidence-envelope layer with typed payloads and explicit authority/epoch references:

- `PolicySnapshotEnvelopeV1`
- `PolicyDependencyIndexV1`
- `PolicyGcDecisionV1`
- `IdentityKeyEpochV1`
- `IdentityKeyTransitionV1`
- `CrossLogProofPackageV1`
- `CryptoRenewalRecordV1`
- `SemanticCommitmentV1`
- `SemanticRevealV1`
- `AdjudicationDecisionV1`

All consequential payloads use canonical encoding and content digests, and all mutable "current" views are derived indexes over append-only evidence rather than replacement history.

## Security audit

This contract deliberately does **not** claim:

- that retaining every historical policy proves that policy was good;
- that dual signatures alone prevent key-holder collusion;
- that cross-log anchoring makes either log semantically truthful;
- that crypto renewal after a primitive has already broken restores past authenticity;
- that commit/reveal proves independent reasoning;
- that adjudication can discover a compromise time with mathematical certainty.

It only freezes the evidence and authority semantics needed to avoid laundering those uncertainties into false certainty.

## Engineering handoff

LAB-086 remains priority #1. This design freeze must not be used as a substitute for its exact executable gate.

When exact source execution is unavailable, the next distinct LAB-093 evidence task should address **policy-dependency index authority/anti-omission proofs + key-rollover effective-time clock provenance + cross-log migration completeness under partial archive loss + threshold-decryption escrow compromise/abort semantics + adjudication evidence-disclosure confidentiality and selective disclosure**.
