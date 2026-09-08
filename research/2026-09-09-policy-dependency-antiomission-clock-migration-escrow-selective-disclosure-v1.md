# Policy dependency anti-omission, clock provenance, partial-loss migration, escrow compromise, and selective disclosure — v1

Date: 2026-09-09
Status: **FROZEN DESIGN CONTRACT**
Contract ID: `POLICY_DEPENDENCY_ANTIOMISSION_CLOCK_MIGRATION_ESCROW_SELECTIVE_DISCLOSURE_V1_FROZEN`
Parent: LAB-093 / #178

## Why this exists

The prior LAB-093 freezes made historical policy bytes a required evidence dependency, bound key rollover to exact effective boundaries, treated cross-log proofs as archival evidence packages, introduced threshold-decryption escrow for confidential semantic commit/reveal, and defined compromise-boundary adjudication finality.

Five remaining questions were still underspecified:

1. who is authorized to maintain the policy-dependency index, and how can a verifier positively prove that the index did not omit a live dependency before policy GC;
2. what authenticates the clock/effective-time boundary used for key rollover and compromise decisions;
3. when a cross-log migration package is only partially recoverable, what minimum recovered material is sufficient to preserve the historical claim;
4. what happens when a threshold-decryption escrow is itself compromised, partially unavailable, or aborts after some shares are released;
5. how adjudication can disclose enough evidence to justify a compromise boundary without leaking unrelated confidential evidence or turning redaction into unverifiable authority.

This note freezes those semantics before implementation.

## Primary donors and evidence

### RFC 9162 — positive promises, complete authenticated log state, and omission evidence
Certificate Transparency v2 treats an SCT as a signed promise that an accepted submission will be incorporated within the log's Maximum Merge Delay. Auditors can later compare that promise with authenticated post-deadline log state; a monitor can fetch all entries, reconstruct the tree, and verify the signed tree head. The useful pattern is that **absence is not inferred from a failed lookup**: it is evaluated against authenticated, sufficiently complete state and a prior signed obligation.

Source:
- https://www.rfc-editor.org/rfc/rfc9162.html

### RFC 3161 — authenticated time is an interval and ordering property, not an ambient wall clock
TSP timestamp tokens bind a message imprint to `genTime`, optional `accuracy`, ordering semantics, serial number, policy, and TSA identity. The accuracy field yields a lower/upper bound around `genTime`; absent explicit ordering, two timestamps cannot safely be ordered unless their time intervals are disjoint enough. This is the correct donor for effective-time provenance: **clock readings need authenticated source, uncertainty, policy, and ordering semantics**.

Source:
- https://www.rfc-editor.org/rfc/rfc3161.html

### RFC 4998 — partial archive loss and renewal dependencies
Evidence Record Syntax requires preservation of data/evidence needed to verify archive timestamps. Timestamp renewal can proceed without all original objects only when the old hash-tree binding remains secure; hash-tree renewal requires access to all relevant evidence data and archived objects. This yields the migration rule: a partially recovered archive is usable only if the exact historical claim remains derivable and independently authenticated from the recovered closure; missing material that is required to recompute a weakening binding is fatal to migration.

Source:
- https://www.rfc-editor.org/rfc/rfc4998/

### NIST Multi-Party Threshold Cryptography — distributed trust is a protocol, not reconstructed central custody
NIST's MPTC project treats threshold encryption/decryption as a distributed cryptographic operation in which trust is shared across parties and the private key need not be reconstructed at one location. As of 2026, NIST IR 8214C explicitly includes threshold public-key encryption/decryption among the scheme classes being collected. This is the donor for escrow: released shares, party compromise, threshold availability, and reconfiguration must be modeled independently.

Sources:
- https://csrc.nist.gov/Projects/threshold-cryptography
- https://www.nist.gov/publications/nist-first-call-multi-party-threshold-schemes

### RFC 9901 — selective disclosure must remain issuer-bound
RFC 9901 standardizes selective disclosure for JWT claims using issuer-bound commitments/digests and disclosures, allowing a holder to reveal selected values while retaining cryptographic linkage to the signed object. The donor principle here is narrower than SD-JWT itself: **redaction/selective disclosure is acceptable only when the disclosed subset remains cryptographically bound to the authenticated whole and omission semantics are explicit**.

Source:
- https://www.rfc-editor.org/rfc/rfc9901

## Frozen distinctions

The following equalities are forbidden:

```text
DEPENDENCY_INDEX_SIGNED == DEPENDENCY_INDEX_COMPLETE
INDEX_AUTHORITY == GC_AUTHORITY
NO_INDEX_MATCH == NO_LIVE_DEPENDENCY
LATEST_WALL_CLOCK == AUTHENTICATED_EFFECTIVE_TIME
TIMESTAMP_PRESENT == STRICT_ORDER_PROVEN
ONE_TSA == GLOBAL_TIME_TRUTH
K_FRAGMENTS_RECOVERED == HISTORICAL_CLAIM_RECOVERED
PROOF_VERIFIES == MIGRATION_CLOSURE_COMPLETE
ESCROW_THRESHOLD_AVAILABLE == ESCROW_SAFE
SOME_DECRYPTION_SHARES_RELEASED == RESULT_REVEALED
ESCROW_ABORT == RELEASED_SHARES_ERASED
REDACTED_EVIDENCE_SIGNED == REDACTION_COMPLETE
SELECTIVE_DISCLOSURE == NONDISCLOSED_CLAIMS_IRRELEVANT
HASH_OF_HIDDEN_EVIDENCE == SEMANTIC_SUFFICIENCY_PROVEN
```

## 1. Policy-dependency index authority and positive anti-omission proof

### 1.1 Index purpose

The dependency index is not merely a cache. It is the durable relation:

```text
policy_snapshot_digest -> retained evidence objects that still require those exact policy bytes
```

A GC decision that relies on this relation is consequential. Therefore index maintenance is an authority-bearing operation.

### 1.2 Separate roles

Define distinct roles:

- `EVIDENCE_ADMISSION_AUTHORITY`: admits/commits evidence objects and their policy dependency;
- `DEPENDENCY_INDEX_AUTHORITY`: maintains authenticated index generations;
- `DEPENDENCY_AUDITOR`: independently reconstructs/checks completeness;
- `POLICY_GC_AUTHORITY`: may authorize deletion only from independently proven complete state.

No single role may both create an evidence object, omit it from the index, and authorize GC based only on that same index.

### 1.3 Append-only dependency events

Every evidence admission, renewal, expiry, supersession, and deletion decision emits an immutable event:

```text
DependencyEvent {
  event_id,
  evidence_id,
  policy_snapshot_digest,
  event_type,
  predecessor_event_digest?,
  evidence_admission_frontier,
  effective_state_digest,
  authority_epoch,
  policy_snapshot_digest_for_event,
}
```

The dependency index is a derived authenticated view over these events, not the sole source of truth.

### 1.4 Index generation

```text
DependencyIndexGeneration {
  generation,
  predecessor_digest,
  source_event_frontier,
  canonical_index_root,
  active_dependency_count,
  policy_bucket_roots,
  authority_epoch,
  generated_at_time_evidence,
}
```

A later generation must bind the exact source event frontier it claims to cover.

### 1.5 Positive anti-omission requirement

`index lookup(policy) == empty` is insufficient for GC.

A GC candidate needs a **positive completeness proof** consisting of:

1. an authenticated evidence-admission/event frontier F;
2. authenticated evidence that the dependency index generation covers exactly F;
3. deterministic reconstruction or independently reproducible reconciliation of all dependency events through F;
4. a canonical query proving zero active dependencies on the target policy at F;
5. a closure rule showing no concurrently admitted evidence before the GC linearization point can be outside F;
6. a CAS/transaction binding the GC decision to the same F/index generation.

This is analogous to CT's signed-promise + authenticated post-deadline state pattern: absence is meaningful only relative to authenticated complete state.

### 1.6 Concurrent admission

If evidence admission can race GC, GC must either:

- serialize behind a common authoritative frontier/transaction; or
- compare-and-swap on the exact admission frontier and retry if it advanced.

A stale but correctly signed dependency index may never authorize deletion.

### 1.7 Index-authority compromise

Compromise of the dependency-index authority reopens reliance on affected index generations. It does not delete source dependency events.

A replacement index authority must reconstruct from retained authenticated source events and publish a new generation. It cannot declare the old source frontier "complete" merely by signing the old root again.

### 1.8 Typed states

```text
DEPENDENCY_COMPLETE_ZERO
DEPENDENCY_ACTIVE
DEPENDENCY_INDEX_STALE
DEPENDENCY_INDEX_UNREPRODUCIBLE
DEPENDENCY_SOURCE_FRONTIER_UNAVAILABLE
DEPENDENCY_AUTHORITY_COMPROMISED
DEPENDENCY_COMPLETENESS_UNKNOWN
```

Only `DEPENDENCY_COMPLETE_ZERO` may contribute to policy GC authorization.

## 2. Key-rollover effective-time clock provenance

### 2.1 Effective time is evidence

The effective boundary for key rollover, compromise, retirement, or algorithm policy is consequential historical evidence. It must not be derived solely from process-local wall clock.

Define:

```text
AuthenticatedTimeEvidence {
  source_identity,
  source_key_epoch,
  time_value,
  uncertainty_minus,
  uncertainty_plus,
  ordering_semantics,
  nonce_or_request_binding,
  evidence_digest,
  source_policy,
}
```

### 2.2 Interval semantics

A time observation represents an interval:

```text
[time_value - uncertainty_minus,
 time_value + uncertainty_plus]
```

This follows RFC 3161's `genTime + accuracy` model.

If two consequential boundaries' authenticated intervals overlap and there is no separately authenticated ordering relationship, their strict order is `UNKNOWN`.

### 2.3 No single ambient clock authority

A local OS clock may be recorded for diagnostics but is not sufficient alone for high-assurance effective-time claims.

A high-assurance profile SHOULD combine:

- at least one independently authenticated timestamp source;
- append-only publication/receipt establishing when the boundary statement was externally visible;
- monotonic local sequencing/frontier evidence so later local events cannot be backdated before an already accepted local predecessor.

### 2.4 Rollover boundary

Normal key rollover binds:

```text
predecessor_key_epoch
successor_key_epoch
effective_time_interval
time_evidence_set_digest
predecessor_frontier
successor_authorization
```

An event whose own authenticated interval overlaps the rollover interval is classified `BOUNDARY_TIME_AMBIGUOUS` unless another ordering proof resolves it.

It must not be assigned to the old/new epoch by rounding or local-clock preference.

### 2.5 Compromise-time conservatism

If compromise effective time is uncertain over interval `[a,b]`, consequential reliance treats evidence at or after `a` conservatively until adjudication narrows the interval.

Moving the boundary later remains rehabilitation and follows the stricter adjudication rule frozen previously.

### 2.6 Timestamp authority compromise

A TSA/time source whose key is compromised cannot establish trusted ordering after the compromise boundary. Pre-boundary tokens may remain historically valid if independently anchored and the applicable validation policy allows it.

Time-source compromise is therefore recursive evidence subject to the same effective-time/adjudication framework; it is not solved by trusting that source's own later statement.

### 2.7 Multiple time sources

Multiple sources improve resilience only if their control/key paths are independently governed. Two TSA endpoints behind one compromised signing root count as one time-authority domain.

Conflicting authenticated time intervals yield `TIME_SOURCE_CONFLICT`; do not choose median/majority unless the policy explicitly defines a threshold-time construction whose independence assumptions are satisfied.

## 3. Cross-log migration completeness under partial archive loss

### 3.1 Claim closure, not file count

Partial archive recovery is evaluated against the exact claim being verified or migrated.

Define a `ProofDependencyClosure` for each retained historical claim:

```text
claim_id
canonical_entry_bytes
source_checkpoint
source_log_identity/key epoch
source inclusion/consistency material
destination anchor entry
destination checkpoint
destination inclusion/consistency material
algorithm identifiers
policy snapshots
renewal/migration chain
verification metadata/trust anchors
```

A recovered archive is sufficient iff all **necessary** elements of this closure are available and authenticate to retained roots/anchors.

`RECOVERED_FILE_COUNT` has no security meaning by itself.

### 3.2 Three partial-loss classes

- `REDUNDANT_MATERIAL_LOST`: alternate copies/caches lost; claim closure still complete.
- `REGENERABLE_DERIVATIVE_LOST`: a proof can be deterministically regenerated from retained authenticated complete state (for example, an inclusion proof when the complete authenticated tree/prefix remains available).
- `NONREGENERABLE_BINDING_LOST`: required historical bytes, checkpoint signature, trust anchor, policy bytes, or pre-break renewal link are gone.

Only the first two may preserve current verifiability.

### 3.3 Regeneration is not invention

A lost proof component may be regenerated only from authenticated retained state that is independently sufficient to derive the same component.

Examples:

- lost Merkle inclusion path + complete authenticated tree leaves/checkpoint => regenerable;
- lost canonical submitted entry + only its old leaf hash remains => not sufficient if semantic re-verification needs the entry bytes;
- lost destination checkpoint signature + unsigned checkpoint fields => historical binding lost unless independently anchored elsewhere;
- lost old policy bytes + policy digest only => historical policy unavailable.

### 3.4 Migration before hash weakness

If the old hash algorithm is approaching deprecation and hash-tree renewal is required, all original/relevant claim-closure bytes needed for rehash must be recoverable **before** the old binding becomes unacceptable, following RFC 4998.

If partial archive loss makes that impossible, state becomes:

`MIGRATION_BLOCKED_INCOMPLETE_PREBREAK_CLOSURE`

After the old binding is already untrusted, reacquiring unauthenticated bytes from a live operator does not restore history.

### 3.5 Cross-domain recovery

Reconstruction from erasure shares is acceptable only after verifying:

1. recovered bytes match the committed archive object digests;
2. reconstruction manifest lineage is valid;
3. enough independently governed destructive domains remain for the required survivability profile;
4. the recovered `ProofDependencyClosure` is semantically complete.

Reconstructability and independence remain separate predicates.

### 3.6 Migration completeness certificate

A successful migration emits:

```text
MigrationCompletenessEvidence {
  old_claim_id,
  old_closure_digest,
  recovered_object_manifest_digest,
  missing_object_manifest_digest,
  regenerated_object_manifest_digest,
  verification_results,
  new_binding_digest,
  time_evidence_set_digest,
  authority_epoch,
}
```

The missing-object set is explicit, even when every missing object was classified redundant/regenerable. "Success" never means silently dropping unavailable inputs.

## 4. Threshold-decryption escrow compromise and abort semantics

### 4.1 Escrow purpose

Escrow exists only to recover an attester's already committed semantic result when ordinary reveal fails. It must not become an alternate early-answer oracle or an independent semantic vote.

### 4.2 Required binding

The escrow ciphertext binds exactly:

```text
challenge_digest
attester_identity_epoch
result_commitment
canonical encrypted result bytes
escrow_policy_epoch
escrow_key_epoch
reveal_deadline
```

Decryption output is accepted only if it opens the already published result commitment exactly.

### 4.3 Threshold state model

```text
ESCROW_SEALED
ESCROW_PARTIAL_RELEASE
ESCROW_THRESHOLD_REACHED
ESCROW_OPENED_VALID
ESCROW_OPENED_MISMATCH
ESCROW_ABORTED_SAFE
ESCROW_ABORTED_PARTIAL_EXPOSURE
ESCROW_COMPROMISE_SUSPECTED
ESCROW_COMPROMISE_CONFIRMED
```

### 4.4 Partial shares are durable exposure events

Once a valid decryption share is released, `abort` cannot erase that fact.

Every released share is attributable, append-only logged, bound to ciphertext/key epoch, and counted against the threshold.

If a protocol aborts after `r < t` shares were released:

- the result remains unopened under the frozen threshold assumption;
- the event is `ESCROW_ABORTED_PARTIAL_EXPOSURE`, not `ESCROW_ABORTED_SAFE`;
- subsequent compromise of additional parties may combine with retained old shares, so key-epoch retirement/forward-secrecy policy must account for those exposures.

### 4.5 No threshold lowering after commitment

The threshold/policy that governs a ciphertext is frozen at ciphertext commitment. Availability pressure cannot lower `t` after seeing non-reveal or after some shares were emitted.

Changing membership/threshold requires a new escrow key/policy epoch for future ciphertexts, not reinterpretation of old ones.

### 4.6 Escrow compromise before reveal deadline

If enough escrow parties/key material are compromised to decrypt before the permitted reveal boundary, confidentiality for affected ciphertexts is considered lost even if no public plaintext has yet appeared.

State:

`PRE_REVEAL_CONFIDENTIALITY_COMPROMISED`

The corresponding semantic quorum result may still be technically correct after normal reveal, but the anti-copy/confidential-independence assurance is downgraded and must be re-appraised.

### 4.7 Compromise after reveal

Post-reveal compromise does not retroactively make already public plaintext confidentially exposed. It can still affect authenticity of decryption-share provenance or future ciphertexts and therefore triggers key-epoch rotation and evidence re-appraisal.

### 4.8 Malicious share / equivocation

Threshold parties must produce verifiable/attributable decryption contributions under the selected scheme. Invalid shares do not count. Two incompatible valid-looking shares/statements for the same party/ciphertext/key epoch are `ESCROW_SHARE_EQUIVOCATION` and preserved as evidence.

NIST's threshold-cryptography program supports the architectural requirement that the private operation remain distributed rather than reconstructing a single escrow private key in one process.

### 4.9 Recovery after party loss

Share refresh/reconfiguration must not expose enough old+new material to collapse the threshold across epochs. Historical ciphertexts remain bound to their original key epoch unless a separately authenticated ciphertext re-encryption/resharing mechanism preserves the exact plaintext binding without revealing it.

No ad-hoc decrypt-and-reencrypt migration is allowed before the semantic reveal boundary.

## 5. Adjudication confidentiality and selective disclosure

### 5.1 Two goals must coexist

Adjudication evidence must be:

1. sufficient for independent verification of the published decision; and
2. minimally revealing when evidence contains secrets, personal data, proprietary implementation details, unrelated incidents, or protected operational data.

Confidentiality must not become an excuse for unverifiable authority.

### 5.2 Evidence package split

Every adjudication case defines:

```text
EvidencePackage {
  full_evidence_manifest_root,
  public_evidence_projection,
  selective_disclosures,
  nondisclosed_claim_commitments,
  decision-relevant predicate set,
  disclosure_policy_snapshot,
  adjudicator access log root,
}
```

The full manifest root is authenticated before adjudication. Later disclosure cannot add unseen evidence without producing a new/superseding evidence set.

### 5.3 Selective disclosure rule

A disclosed item must be cryptographically linked to the authenticated full evidence package. RFC 9901's issuer-bound disclosure principle is the donor: selective disclosure proves that revealed values are among committed/signed values; it does **not** automatically prove that hidden values are irrelevant.

Therefore every nondisclosed item is assigned one of:

- `IRRELEVANT_BY_PUBLIC_PREDICATE`: public policy proves this item cannot affect the decision predicate;
- `CONFIDENTIAL_BUT_REVIEWED`: authorized independent adjudicators reviewed it; public verifier sees commitment + role/quorum evidence but cannot fully reproduce semantics;
- `WITHHELD_MATERIAL`: required reviewer did not obtain it; decision cannot claim full evidentiary completeness.

### 5.4 No semantic sufficiency from hashes alone

A commitment/hash proves binding, not meaning. If the decision depends on a hidden fact, a public hash of the hidden evidence is insufficient to prove that fact.

High-assurance alternatives include:

- reveal the minimal necessary claim/value;
- publish a policy-approved zero-knowledge proof for a precisely defined predicate;
- obtain independent confidential review quorum whose limitations are explicitly reflected in the assurance class.

Do not invent a generic ZK claim where no audited circuit/specification exists.

### 5.5 Redaction completeness

Before public release, redact only through a deterministic/versioned disclosure policy over the already authenticated manifest.

The public projection binds:

- which evidence IDs exist;
- which are disclosed;
- which are hidden;
- reason code/policy for each hidden item;
- whether each hidden item is decision-relevant;
- adjudicator quorum that accessed/reviewed decision-relevant hidden items.

Thus redaction cannot make an evidence item disappear from the manifest.

### 5.6 Appeals and later disclosure

An appeal may disclose additional previously committed evidence without changing the original full-manifest root. If new evidence was genuinely unavailable during the first adjudication, it requires a new evidence-set generation and follows the previously frozen reopening rule.

A later confidentiality downgrade/public disclosure never rewrites the old decision object; it appends disclosure evidence and may allow stronger independent re-verification.

### 5.7 Confidential adjudicator compromise

If the threshold of adjudicators authorized to inspect confidential evidence is compromised, affected decisions become subject to re-appraisal even when the public evidence projection remains intact.

The compromise does not let the same adjudicators exonerate their prior hidden-evidence review. Recovery uses an independent authority/quorum.

## Combined assurance model

A policy GC or historical adjudication action may claim its strongest assurance class only if all relevant terms hold:

```text
AUTHENTICATED_SOURCE_EVENT_FRONTIER
&& DEPENDENCY_INDEX_REPRODUCIBLE_THROUGH_FRONTIER
&& POSITIVE_ZERO_DEPENDENCY_PROOF_IF_GC
&& AUTHENTICATED_EFFECTIVE_TIME_INTERVAL
&& REQUIRED_EVENT_ORDER_RESOLVED
&& HISTORICAL_PROOF_DEPENDENCY_CLOSURE_COMPLETE
&& CRYPTO_MIGRATION_PERFORMED_BEFORE_OLD_BINDING_FAILURE
&& ESCROW_THRESHOLD_POLICY_FROZEN
&& ESCROW_PRE_REVEAL_CONFIDENTIALITY_NOT_COMPROMISED
&& DISCLOSED_EVIDENCE_BOUND_TO_FULL_MANIFEST
&& HIDDEN_DECISION_RELEVANT_EVIDENCE_REVIEWED_UNDER_DECLARED_QUORUM
```

A failure yields a typed degraded/unknown state. Current policy, wall clock, majority intuition, or surviving live API responses never silently substitute missing historical evidence.

## RED-first executable matrix — 64 cases

### A. Dependency index / anti-omission — 1..16
1. complete source frontier + reproducible index + zero active dependency => GC eligibility PASS;
2. signed index says zero but source frontier advanced => `DEPENDENCY_INDEX_STALE`;
3. one admitted evidence event omitted from index => completeness FAIL;
4. evidence renewal removes dependency and index reflects exact event => dependency cleared;
5. renewal event indexed but predecessor admission missing from retained source events => source completeness UNKNOWN;
6. index authority and GC authority same identity with no independent audit => policy rejects;
7. index root valid but canonical query implementation/version unavailable => no zero-proof;
8. concurrent admission before GC CAS => CAS fails/retry;
9. admission after successfully linearized GC frontier => evaluated under successor policy, not retroactive dependency;
10. source event frontier signature invalid => fail closed;
11. source events available but one event body digest mismatch => fail closed;
12. index authority compromised after generation; independent reconstruction matches => may retain historical correctness under re-appraisal policy;
13. compromised index authority + source events unavailable => `DEPENDENCY_COMPLETENESS_UNKNOWN`;
14. empty lookup caused by malformed target policy key => reject, not zero proof;
15. retired policy author signs "no dependencies" => insufficient;
16. GC decision binds different index generation/frontier than proof => reject.

### B. Authenticated effective time — 17..28
17. RFC3161-style authenticated time interval wholly before rollover boundary => old epoch classification PASS;
18. interval wholly after boundary => new epoch classification PASS;
19. event interval overlaps boundary => `BOUNDARY_TIME_AMBIGUOUS`;
20. local wall clock only => insufficient for high-assurance boundary;
21. TSA token nonce/request binding mismatch => reject;
22. TSA signature valid but key compromised before token interval => reject/current reliance reopened;
23. two independent time sources with compatible intervals => stronger evidence;
24. two sources conflict materially => `TIME_SOURCE_CONFLICT`;
25. two endpoints share one compromised signing root => count as one authority domain;
26. explicit authenticated ordering resolves overlapping wall-time intervals => order PASS;
27. absent ordering + overlapping accuracy intervals => strict order UNKNOWN;
28. compromise interval [a,b], evidence at a+epsilon => conservatively distrusted until adjudication narrows.

### C. Partial archive loss / migration — 29..40
29. redundant replica lost, exact claim closure intact => PASS;
30. inclusion path lost, complete authenticated tree retained => regenerate and PASS;
31. canonical entry bytes lost, only leaf hash retained, semantics require entry => incomplete;
32. old policy bytes lost, digest retained => `HISTORICAL_POLICY_UNAVAILABLE`;
33. destination checkpoint signature lost, no independent anchor => binding incomplete;
34. one archive shard lost but k-of-n reconstructs exact bytes and independence threshold still holds => PASS;
35. k shares available but all under one destructive domain => reconstructable, independence degraded;
36. old hash nearing deprecation + complete closure available => pre-break migration allowed;
37. old hash nearing deprecation + required object missing => `MIGRATION_BLOCKED_INCOMPLETE_PREBREAK_CLOSURE`;
38. old hash already broken + bytes reacquired only from current operator => cannot rehabilitate history;
39. regenerated proof not bound to exact retained checkpoint => reject;
40. migration success record omits explicit missing-object manifest => reject completeness certificate.

### D. Threshold escrow compromise / abort — 41..52
41. normal non-reveal + threshold valid shares after allowed deadline + plaintext opens exact commitment => recovered semantic result PASS;
42. fewer than threshold shares + abort => no plaintext vote, record partial exposure if any share released;
43. zero shares released + abort => `ESCROW_ABORTED_SAFE`;
44. one or more shares released + abort => `ESCROW_ABORTED_PARTIAL_EXPOSURE`;
45. threshold lowered after ciphertext commitment => reject;
46. membership changed but old ciphertext reinterpreted under new threshold => reject;
47. enough parties compromised before reveal deadline => `PRE_REVEAL_CONFIDENTIALITY_COMPROMISED`;
48. compromise only after ordinary public reveal => confidentiality assurance for that already revealed plaintext not retroactively lost;
49. invalid decryption share => does not count;
50. party equivocates with incompatible contributions => preserve evidence, fail relevant opening unless scheme adjudicates uniquely;
51. decrypted plaintext does not open result commitment => `ESCROW_OPENED_MISMATCH`, no vote;
52. escrow produces valid plaintext for an attester that never committed => no semantic vote.

### E. Selective disclosure / adjudication — 53..64
53. disclosed claim verifies against authenticated full evidence manifest => PASS;
54. redaction removes evidence ID entirely from public manifest => reject;
55. hidden item marked irrelevant but public predicate shows it can affect outcome => reject assurance;
56. hidden decision-relevant item reviewed by required independent confidential quorum => declared confidential-review assurance only;
57. hidden decision-relevant item reviewed by insufficient quorum => incomplete adjudication;
58. hash of hidden evidence offered as proof of semantic claim => insufficient;
59. audited ZK predicate proof over committed hidden evidence verifies => may satisfy only that exact predicate;
60. later disclosure opens an originally committed hidden evidence item => strengthen reproducibility without rewriting decision;
61. appeal adds genuinely new uncommitted evidence => new evidence-set generation/reopening required;
62. disclosed bytes do not match selective-disclosure commitment => tamper/reject;
63. confidential adjudicator threshold compromised for case epoch => affected hidden-evidence review re-appraised;
64. compromised adjudicators alone sign their own exoneration => reject recovery/finality.

## Implementation ownership

This contract belongs conceptually under LAB-093/#178 until executable decomposition is selected.

Expected future implementation pieces:

1. append-only `DependencyEvent` ledger + authenticated dependency-index generations;
2. anti-omission auditor/reconstructor and GC CAS binding;
3. authenticated time-evidence abstraction with interval/order semantics;
4. explicit `ProofDependencyClosure` and migration-completeness verifier;
5. escrow ciphertext/share event log with frozen policy/key epochs;
6. adjudication evidence manifest + selective-disclosure projection verifier;
7. RED tests matching all 64 cases before production refactors.

Do not implement these as one monolith. Authority ownership and historical evidence lifecycles must remain independently testable.

## Frozen result

`POLICY_DEPENDENCY_ANTIOMISSION_CLOCK_MIGRATION_ESCROW_SELECTIVE_DISCLOSURE_V1_FROZEN`

The strongest invariants are:

```text
NO_INDEX_MATCH != NO_DEPENDENCY_PROVEN
SIGNED_INDEX != COMPLETE_INDEX
WALL_CLOCK != EFFECTIVE_TIME_EVIDENCE
TIMESTAMP != TOTAL_ORDER
PARTIAL_ARCHIVE_RECOVERY != CLAIM_CLOSURE_RECOVERY
RECONSTRUCTABLE != INDEPENDENT
ESCROW_ABORT != SHARE_ERASURE
ESCROW_THRESHOLD != MUTABLE_AVAILABILITY_KNOB
SELECTIVE_DISCLOSURE != HIDDEN_EVIDENCE_IRRELEVANCE
COMMITMENT_TO_HIDDEN_EVIDENCE != PROOF_OF_HIDDEN_SEMANTICS
```

Policy deletion requires positive anti-omission evidence against an authenticated complete source frontier. Effective time is a provenance-bearing interval/order claim. Cross-log migration succeeds only when the exact historical claim dependency closure survives. Threshold escrow failure/compromise is append-only evidence with no threshold laundering. Confidential adjudication may selectively disclose evidence only while preserving cryptographic linkage to a complete authenticated manifest and an explicit statement of what hidden evidence still limits public reproducibility.
