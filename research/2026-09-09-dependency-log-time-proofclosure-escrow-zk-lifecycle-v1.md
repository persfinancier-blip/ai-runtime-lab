# Dependency-log recovery, authenticated time, regenerated-proof closure, escrow refresh, and ZK verifier lifecycle v1

Date: 2026-09-09
Status: FROZEN DESIGN / RED-FIRST CONTRACT
Owner issue: LAB-093 / #178
Execution boundary: this does not substitute for the still-blocked exact LAB-086 executable gate.

## Contract name

`DEPENDENCY_LOG_TIME_PROOFCLOSURE_ESCROW_ZK_LIFECYCLE_V1_FROZEN`

## Why this slice exists

The previous policy-dependency design made the dependency index a derived authenticated view and required positive anti-omission evidence before policy GC. This follow-up closes five remaining authority gaps: event-log equivocation/recovery, survivable source frontiers, anti-backdating across time authorities and rollovers, versioned authority for regenerated proof closure, proactive threshold-escrow refresh/reconfiguration, and lifecycle/provenance for ZK predicates and verifiers used in selective-disclosure adjudication.

## Primary donors

- RFC 9162, Certificate Transparency v2: signed tree heads, append-only Merkle consistency proofs, monitor reconstruction, signed evidence of log misbehavior, and explicit log identity.
  - https://www.rfc-editor.org/rfc/rfc9162.html
- RFC 3161, Time-Stamp Protocol: `genTime`, bounded `accuracy`, nonce binding, and ordering semantics.
  - https://www.rfc-editor.org/rfc/rfc3161.html
- IETF Roughtime draft-ietf-ntp-roughtime-19: nonce-bound signed responses, uncertainty radius, multi-server inconsistency detection, and chained evidence that a later response was generated after an earlier response.
  - https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/19/
- NIST IR 8214C / Threshold Cryptography program: threshold cryptographic operations as distributed computation over secret-shared key material, with explicit implementation/specification/security-evaluation requirements.
  - https://www.nist.gov/publications/nist-first-call-multi-party-threshold-schemes
  - https://csrc.nist.gov/projects/threshold-cryptography

## Frozen boundaries

### 1. Dependency-event log authority and recovery

`INDEX_LOOKUP != EVENT_LOG_TRUTH` remains mandatory.

A policy dependency is admitted by an authenticated append-only `DependencyEventLog`, not by the current materialized index. Each checkpoint MUST bind at least:

- `log_id` and log-key epoch;
- tree/event size;
- root/commitment;
- checkpoint sequence/timestamp evidence;
- canonical event schema/version;
- current policy governing event validity;
- predecessor checkpoint identity or a consistency-proof path.

Two same-size checkpoints for one `log_id/key_epoch` with different roots are positive equivocation evidence. A larger checkpoint is not accepted merely because it is newer-looking: the verifier requires append-only consistency from an independently retained accepted frontier.

Recovery after log-key/operator compromise MUST NOT redefine old checkpoints as belonging to a new log. A successor log/key receives a new authenticated epoch/identity and an explicit predecessor-to-successor recovery statement authorized outside the compromised authority. Historical dependency decisions continue to reference the exact original checkpoint lineage.

### 2. Source-frontier survivability

`CHECKPOINT_DIGEST_RETAINED != FRONTIER_REPRODUCIBLE`.

A positive anti-omission proof used to authorize GC requires a survivable source frontier. At minimum the archive must retain enough authenticated material to reproduce the exact decision domain: canonical event bytes (or another complete authenticated representation), parser/schema version, checkpoint/root, consistency material needed from the previously accepted frontier, and policy bytes.

If only the root survives but the relevant complete event prefix cannot be reconstructed, historical inclusion claims may remain verifiable when their proofs survive, but a new exhaustive anti-omission claim cannot be regenerated. State becomes `FRONTIER_AUTHENTIC_BUT_NONEXHAUSTIVELY_REPRODUCIBLE`, not `NO_DEPENDENCIES_PROVEN`.

### 3. Multi-time-source anti-backdating and rollover

`SIGNED_TIMESTAMP != TRUE_TIME`.

Every consequential effective-time decision uses a `TimeEvidenceSet`, not ambient wall clock. Each observation binds authority identity/key epoch, request nonce/challenge when supported, signed reported time, uncertainty interval/radius, policy, and receipt order.

RFC 3161-style accuracy is interpreted as an interval, not a point. If intervals overlap and no stronger ordering evidence exists, the relation is `TIME_ORDER_AMBIGUOUS`.

For high-assurance anti-backdating, at least two independently governed time sources SHOULD be used. Roughtime-style chained nonce construction is a strong donor: a response from B that commits to material derived from A proves B's response was generated after A's signed response even if their wall-clock values disagree.

Clock-authority rollover is epoch-bound. A successor key cannot retroactively timestamp evidence under the predecessor epoch. Normal rollover requires authenticated predecessor/successor continuity plus an effective boundary supported by independent time/order evidence. Compromised-authority recovery requires an out-of-band/higher recovery root; the compromised clock cannot self-certify the safe boundary of its own compromise.

### 4. Proof-closure authority and regenerated evidence

`REGENERATED_PROOF == SAME CLAIM` is not assumed.

Every regenerated proof receives an immutable `ProofClosureManifest` binding:

- original claim/evidence identity;
- source checkpoint/frontier;
- exact retained inputs used;
- canonicalization/parser/schema versions;
- proof algorithm and parameters;
- generator implementation/provenance identity;
- output digest;
- policy version under which regeneration is valid;
- predecessor proof/evidence identity when this is a renewal.

A later generator/version may produce a semantically equivalent proof, but it is a new evidence object linked to the original closure. It MUST NOT overwrite the old proof or silently inherit its authority class.

The authority deciding that regeneration is equivalent is separate from the generator itself. If the required source closure is incomplete, the result is `REGENERATION_BLOCKED_INCOMPLETE_CLOSURE`, even if a tool can syntactically emit a proof.

### 5. Proactive threshold-escrow refresh and reconfiguration

`SHARE_REFRESH != THRESHOLD_RECONFIGURATION`.

Proactive refresh changes share material while preserving the same logical secret, threshold policy, membership semantics, and ciphertext/evidence contract. A refresh epoch MUST be linked to its predecessor and prove completion under the pre-existing authorized configuration before old shares become retireable.

Reconfiguration changes membership and/or threshold. It is a consequential authority transition and MUST be independently authorized before the new configuration participates. It cannot be used after a challenge/result commitment to lower the effective threshold needed to decrypt that already-committed ciphertext.

Partial refresh is fail-closed. If some participants install epoch N+1 shares while others remain at N, the escrow is `REFRESH_INCOMPLETE` until the protocol's exact completion condition is met. Old and new shares MUST NOT be freely mixable unless the underlying scheme explicitly proves cross-epoch compatibility.

Compromise semantics are monotonic: refreshing after an attacker already obtained threshold shares does not erase the fact that the protected plaintext may already be recoverable. The state remains `PREVIOUS_THRESHOLD_COMPROMISE_EXPOSURE` for the affected ciphertext/evidence epoch.

### 6. ZK predicate circuit provenance and verifier-policy lifecycle

`ZK_PROOF_VALID != CLAIM_POLICY_CORRECT`.

A valid proof only establishes the relation encoded by the exact circuit/statement/verifier policy. Therefore every adjudication-grade ZK predicate MUST bind:

- predicate/circuit semantic version and source digest;
- canonical statement/public-input schema;
- setup/parameter identity if the scheme requires one;
- prover implementation identity/provenance;
- verifier implementation identity/provenance;
- proof-system/algorithm version;
- verification policy and accepted parameter/key epochs;
- linkage to the complete authenticated hidden-evidence manifest.

Circuit changes are policy changes. A new circuit version does not retroactively reinterpret old proofs. If a bug is found in a circuit or verifier, current reliance is re-appraised by exact affected version/epoch; unaffected historical evidence is not silently deleted.

Where multiple verifiers are required for assurance, independence is measured by implementation/provenance domains rather than process count. Two wrappers around the same parser, crypto library, circuit compiler, or build pipeline are one failure domain for the shared component.

A verifier-policy rollover MUST explicitly state whether old proofs remain acceptable for historical verification, are deprecated for new decisions, or are disallowed because of a concrete soundness/parser/setup compromise.

## Required durable states

At minimum implementations need explicit states equivalent to:

- `DEPENDENCY_LOG_EQUIVOCATION`
- `DEPENDENCY_LOG_SUCCESSOR_UNTRUSTED`
- `FRONTIER_AUTHENTIC_BUT_NONEXHAUSTIVELY_REPRODUCIBLE`
- `TIME_ORDER_AMBIGUOUS`
- `CLOCK_AUTHORITY_COMPROMISE_BOUNDARY_UNKNOWN`
- `REGENERATION_BLOCKED_INCOMPLETE_CLOSURE`
- `REGENERATED_EVIDENCE_NEW_OBJECT`
- `REFRESH_INCOMPLETE`
- `RECONFIGURATION_NOT_AUTHORIZED_FOR_COMMITTED_CIPHERTEXT`
- `PREVIOUS_THRESHOLD_COMPROMISE_EXPOSURE`
- `ZK_CIRCUIT_VERSION_UNTRUSTED`
- `ZK_VERIFIER_POLICY_STALE`

## RED-first matrix

### Dependency log / frontier
1. Same-size, same-key-epoch checkpoints with different roots => equivocation.
2. Larger checkpoint without consistency from retained frontier => reject current reliance.
3. Successor key self-authorized only by compromised predecessor => reject.
4. New log identity presented as old log without recovery statement => reject.
5. Complete prefix + checkpoint + parser retained => exhaustive regeneration allowed.
6. Root retained but prefix unavailable => no new exhaustive anti-omission proof.
7. Materialized index empty while authenticated prefix contains dependency => GC rejected.
8. Concurrent dependency admission races GC proof => CAS/serialization required.

### Time provenance
9. Two non-overlapping RFC3161-style intervals => order may be established.
10. Overlapping intervals without ordering => `TIME_ORDER_AMBIGUOUS`.
11. Same TSA with valid explicit ordering semantics => order accepted within policy.
12. Roughtime-style nonce response proves response generated after challenge.
13. Chained A->B response conflicts with claimed earlier B creation => positive inconsistency evidence.
14. Successor time key backdates token into predecessor epoch => reject.
15. Compromised TSA self-declares a favorable compromise boundary => insufficient.
16. Missing nonce where request required nonce binding => reject freshness claim.

### Proof closure / regeneration
17. Same inputs+versions+algorithm regenerate matching proof/output => new linked evidence object, not overwrite.
18. Parser version differs without migration policy => equivalence not assumed.
19. Required policy bytes missing => regeneration blocked.
20. Required source frontier not reproducible => regeneration blocked.
21. Generator signs its own equivalence assertion as sole authority => insufficient.
22. Old proof retained after regeneration => historical chain remains append-only.
23. Algorithm renewal before old binding deprecation => allowed under versioned policy.
24. Regeneration after sole old binding already untrusted => no historical rehabilitation.

### Escrow refresh / reconfiguration
25. Full authorized proactive refresh preserves logical threshold policy => new epoch accepted.
26. Partial refresh => `REFRESH_INCOMPLETE`.
27. Old/new shares mixed without scheme proof => reject.
28. Membership changed but threshold same => still reconfiguration, needs authority.
29. Threshold lowered after ciphertext commitment => reject for that ciphertext.
30. New member added after commitment and counted toward decrypt quorum without precommitted policy => reject.
31. Threshold compromise before refresh => later refresh does not erase exposure state.
32. Retiring old shares before refresh completion => reject transition.

### ZK lifecycle
33. Valid proof under exact trusted circuit/verifier policy => predicate may be accepted at that assurance level.
34. Proof valid under wrong circuit version => reject intended claim.
35. Public-input schema/canonicalization mismatch => reject.
36. Setup/parameter epoch not authorized => reject.
37. Circuit bug discovered => re-appraise exact affected versions.
38. Two verifier processes share same vulnerable implementation lineage => not two independent verifiers.
39. Verifier policy deprecates old version for new decisions but permits historical verification => preserve historical evidence, reject new reliance.
40. Hidden evidence manifest digest does not match proof-linked commitment => reject adjudication linkage.

## Audit conclusions

- The design keeps authority monotonic: later indexing, key rollover, proof regeneration, share refresh, or verifier upgrades cannot silently rewrite what earlier evidence meant.
- Positive anti-omission remains a stronger operation than lookup failure and requires a reproducible authenticated frontier.
- Time becomes evidence with explicit uncertainty and provenance rather than a trusted ambient scalar.
- Threshold refresh improves forward security only prospectively; it cannot retroactively un-expose already compromised ciphertext epochs.
- ZK reduces disclosure but adds a new semantic authority surface: circuit + public-input schema + setup/parameters + verifier policy all require provenance and lifecycle controls.

## Implementation boundary

No production refactor should implement this design before exact RED tests exist at the same abstraction level. LAB-086 remains priority #1 and its retained exact executable gate must complete before any merge/readiness claim is changed.