# Witness survivability, Byzantine time aggregation, proof-closure migration, escrow refresh, and ZK setup migration v1

Date: 2026-09-09
Status: `WITNESS_TIME_PROOFCLOSURE_ESCROW_ZK_MIGRATION_V1_FROZEN`
Parent: LAB-093 / #178

## Why this slice exists

LAB-086 remains priority #1, but exact local source execution is currently unavailable because direct Git transport fails before repository execution with DNS resolution failure. This document is a distinct fallback evidence slice; it does **not** substitute for LAB-086 RED/GREEN execution.

The prior freeze established authenticated dependency-event frontiers, multi-source time evidence, immutable proof-closure manifests, threshold-share refresh/reconfiguration separation, and exact ZK predicate/verifier provenance. This slice closes the next recursion points:

1. what survives if dependency-log witnesses disappear;
2. how Byzantine time sources are aggregated without denominator laundering;
3. how a regenerated proof closure survives generator/parser migration;
4. how proactive escrow refresh behaves with rollback and offline members;
5. how setup-parameter compromise and proof-system migration affect historical ZK evidence.

## Primary donors

- RFC 9162, Certificate Transparency v2: append-only Merkle logs, signed tree heads/checkpoints, inclusion and consistency proofs, MMD promises, and signed evidence of log misbehavior. https://www.rfc-editor.org/rfc/rfc9162.html
- IETF Roughtime draft `draft-ietf-ntp-roughtime-19`: nonce-bound signed time responses and multi-server chaining that can expose inconsistent/malicious time assertions. https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/19/
- NIST Multi-Party Threshold Cryptography project / IR 8214C program: threshold operations keep shares distributed, tolerate bounded corruptions, and motivate proactive share renewal and robust threshold-service recovery. https://csrc.nist.gov/Projects/threshold-cryptography
- Ethereum KZG ceremony: structured reference string security depends on at least one honest contribution destroying its secret; ceremony transcript/contributions are independently verifiable. https://ceremony.ethereum.org/
- Ethereum Foundation Perpetual Powers of Tau description: public contribution files and transcript can be independently verified and reused as setup input for downstream circuits. https://blog.ethereum.org/2020/04/14/ef-supported-teams-research-and-development-update-2020-pt-1

## Frozen vocabulary

### `HistoricalCheckpointPackage`
Immutable object containing at least:

- log identity and log-key epoch;
- tree size and root hash;
- signed checkpoint/STH bytes;
- predecessor checkpoint reference;
- required consistency proof or enough retained tree material to regenerate it;
- witness-policy generation and historical witness denominator;
- witness observations/cosignatures actually obtained;
- archival locations and digest commitments.

### `TimeAggregationPolicy`
Versioned policy containing:

- eligible time-source population fixed before queries;
- historical denominator and required threshold;
- independence dimensions (operator/control domain, implementation family where relevant, key authority);
- nonce/chaining rules;
- source interval/radius interpretation;
- aggregation function;
- exclusion and rollover rules;
- ambiguity/fail-closed behavior.

### `ProofClosureGeneration`
Immutable generation binding:

- predecessor proof-closure digest;
- exact authenticated source frontier;
- canonical input bytes or reconstructable authenticated references;
- parser/schema version and executable provenance;
- generator implementation/toolchain/build provenance;
- algorithm/parameter version;
- generated proof artifacts;
- semantic-equivalence attestation policy;
- migration reason and effective boundary.

### `EscrowRefreshEpoch`
Immutable epoch containing:

- predecessor epoch;
- exact member set and threshold;
- refresh/reconfiguration protocol identifier;
- member key epochs;
- commitments/transcript needed to validate the refresh;
- completion quorum;
- activation boundary;
- explicit rollback disposition.

### `ZKParameterEpoch`
Immutable parameter lineage containing:

- proof-system identifier/version;
- circuit/predicate digest and public-input schema;
- setup model (`transparent`, `universal-updatable`, `circuit-specific`, etc.);
- SRS/parameter digest;
- ceremony/transcript provenance where applicable;
- verifier algorithm and implementation policy;
- activation/deprecation/compromise boundaries;
- predecessor/successor parameter epochs.

## Contract A — witness/checkpoint survivability under witness loss

### A1. Witness loss does not erase historical evidence

`CURRENT_WITNESS_UNAVAILABLE != HISTORICAL_CHECKPOINT_INVALID`.

A checkpoint that satisfied the historical witness policy remains historical evidence if its exact signed checkpoint, historical denominator, witness observations, and consistency ancestry remain independently verifiable.

### A2. Witness signatures alone are not enough for long-term survivability

A witness signature without the exact checkpoint bytes, log identity/key epoch, historical policy generation, and enough consistency material is an incomplete archival object.

Therefore a durable checkpoint package MUST retain or independently regenerate the append-only proof relation to its trusted predecessor.

### A3. Witness disappearance cannot shrink old denominator

If epoch `E7` required 3-of-5 witnesses, losing two witness organizations later does not turn the old requirement into 3-of-3 or 2-of-3. Historical evaluation uses the frozen `E7` denominator.

### A4. Recovery after total witness loss creates a new witness epoch

A replacement witness set may establish new current assurance, but it cannot retroactively cosign old checkpoints as if it were present then. It may attest to re-verification of archived evidence under a new epoch; that is a new evidence object.

### A5. Checkpoint archive completeness is positive, not inferred from lookup success

`CHECKPOINT_DIGEST_PRESENT != CHECKPOINT_PACKAGE_SURVIVABLE`.

Before GC of old witness/log material, the system requires a positive dependency census proving that all required checkpoint packages and their consistency ancestry are retained under the declared survivability profile.

## Contract B — Byzantine multi-time-source aggregation

### B1. Population before observation

Eligible time sources, denominator, threshold, query epoch, and aggregation function MUST be committed before any response is observed.

Adaptive removal of an inconvenient source after seeing its timestamp is denominator laundering and invalidates consequential time evidence.

### B2. Independent sources, not merely multiple signatures

`N_TIME_RESPONSES != N_INDEPENDENT_TIME_SOURCES`.

Responses sharing an operator/control plane or a common signing authority do not automatically satisfy an independence threshold. The policy records the independence dimensions actually required.

### B3. Intervals, not scalar timestamps

Each source contributes an authenticated interval (for example timestamp ± radius/accuracy) plus freshness/nonce evidence where the protocol supports it. Aggregation operates on intervals and ordering evidence, not naive arithmetic averaging of scalar timestamps.

### B4. Byzantine-safe acceptance is policy-specific and fail-closed

For a policy requiring `q` independent sources, acceptance requires at least `q` policy-eligible responses whose authenticated intervals/order constraints admit a policy-defined intersection or bounded consensus region.

If the surviving set can form two incompatible policy-valid regions, state is `TIME_QUORUM_EQUIVOCAL`, not "pick the median and continue" unless the frozen policy explicitly proves that the median rule tolerates the configured Byzantine bound.

### B5. Roughtime-style chaining is ordering evidence, not omniscient truth

Nonce-bound chaining can prove that one signed response was generated after material from another response existed. It strengthens anti-backdating/order claims. It does not by itself establish which server's wall-clock value is correct.

### B6. Time-source rollover preserves historical key epochs

A new key/source epoch does not reinterpret old responses. Historical evidence binds the key/source identity that signed it. Rollover continuity is a new authenticated statement with an explicit effective boundary.

## Contract C — reproducible generator/parser migration for proof closure

### C1. Generated proof is derived evidence; source frontier remains authority

A regenerated proof MUST remain linked to the exact authenticated source frontier and predecessor proof-closure generation. A new parser/generator cannot make previously unavailable source evidence appear complete.

### C2. Reproducibility proves build/output relation, not semantic correctness

Byte-identical output from independently controlled builds is useful evidence that declared inputs/toolchains reproduce an artifact. It does not prove that the parser interpreted source semantics correctly or that the generator implements the desired policy.

### C3. Parser migration requires dual interpretation audit

For a parser/schema migration affecting consequential historical evidence:

1. retain old parser/schema identity;
2. run old and candidate parsers over the exact same authenticated source corpus where executable history is available;
3. classify differences canonically;
4. require explicit semantic-equivalence adjudication for every decision-relevant divergence;
5. emit a new `ProofClosureGeneration`; never overwrite the old one.

### C4. Generator migration cannot self-attest equivalence

The new generator implementation cannot be sole authority asserting that its output is semantically equivalent to the predecessor. Equivalence requires the frozen independent attestation/reproduction policy.

### C5. Missing old executable/parser narrows assurance

If old source bytes remain but the old parser semantics cannot be reconstructed or independently specified, state is `SOURCE_RETAINED_PARSER_SEMANTICS_UNRECOVERABLE`. A new parser may produce a current interpretation but cannot silently claim historical semantic equivalence.

## Contract D — proactive escrow refresh, rollback, and offline members

### D1. Refresh and reconfiguration remain different operations

Share refresh keeps the same logical secret/access policy while replacing share material. Membership or threshold change is reconfiguration and requires its own authorization/evidence.

### D2. Activation is atomic at epoch level

A refresh epoch becomes active only after the scheme-defined completion threshold and validation transcript are satisfied. Partial distribution is not a valid mixed epoch unless the cryptographic scheme explicitly defines safe mixed-epoch semantics.

### D3. Offline member does not justify silent threshold reduction

If a member is offline during refresh, the system either completes under the already-authorized protocol/threshold or remains in the previous valid epoch. It must not lower the threshold after seeing who is available.

### D4. Rollback cannot resurrect revoked share capability

Once a new epoch is authoritatively activated and old shares are revoked/retired, application rollback to software/state from the old epoch must not re-enable old share acceptance. Runtime rollback and cryptographic epoch rollback are distinct decisions.

### D5. Refresh does not erase prior compromise

If enough shares from epoch `E` were compromised to meet its reconstruction/operation threshold, refreshing to `E+1` can restore future secrecy only under an explicitly justified proactive-security model. It does not make historical exposure of `E` disappear.

### D6. Offline-member recovery emits new evidence

A returning member must authenticate the active epoch before receiving/recovering a valid share. Recovery from a stale local epoch cannot be accepted as proof that the member still belongs to the active denominator.

## Contract E — ZK setup compromise and proof-system migration

### E1. Proof validity is parameter-epoch relative

`ZK_PROOF_VALID` means verification under a specific circuit/predicate, verifier policy, proof-system version, and `ZKParameterEpoch`. A proof has no context-free validity.

### E2. Trusted/updatable setup compromise reopens soundness reliance

For an SRS whose soundness depends on destruction of setup secrets, evidence that the required setup assumption failed marks affected proofs `PARAMETER_ASSUMPTION_COMPROMISED` for current consequential reliance.

Ethereum's KZG ceremony is a useful donor: the published security claim is that the SRS remains secure if at least one participant contributed honestly and destroyed their secret. The ceremony transcript supports independent verification of contributions, but no transcript can cryptographically prove that every secret was physically erased.

### E3. Ceremony transcript is evidence, not magic

A complete transcript can prove accepted contribution transformations under the ceremony protocol. It does not prove participant independence, endpoint cleanliness, or secret deletion unless the protocol has separate evidence for those properties.

### E4. Successor parameters do not rehabilitate predecessor proofs

Migrating to a new uncompromised SRS/proof system secures new proofs. It does not retroactively restore soundness of old proofs created under parameters whose assumption is known compromised.

Historical claims may be re-proved only if the underlying authenticated witness/source evidence survives and the new circuit/predicate is shown semantically equivalent for the claim being renewed.

### E5. Proof-system migration is new evidence lineage

A migration creates a successor `ZKParameterEpoch` and new proof objects linked to predecessor claim/source evidence. Old proofs remain immutable historical artifacts with their historical assurance classification.

### E6. Transparent proof systems remove setup-secret risk, not all migration risk

Moving to a transparent setup removes one class of toxic-waste/SRS compromise. It does not eliminate circuit bugs, verifier bugs, parser/canonicalization bugs, cryptographic-assumption changes, or implementation provenance requirements.

## Derived fail-closed states

- `HISTORICAL_CHECKPOINT_PACKAGE_INCOMPLETE`
- `WITNESS_DENOMINATOR_UNRECOVERABLE`
- `TIME_SOURCE_DENOMINATOR_LAUNDERED`
- `TIME_QUORUM_EQUIVOCAL`
- `TIME_SOURCE_INDEPENDENCE_UNPROVEN`
- `SOURCE_RETAINED_PARSER_SEMANTICS_UNRECOVERABLE`
- `PROOF_CLOSURE_MIGRATION_EQUIVALENCE_UNPROVEN`
- `ESCROW_REFRESH_INCOMPLETE`
- `ESCROW_STALE_EPOCH_MEMBER`
- `ESCROW_PRIOR_THRESHOLD_EXPOSURE`
- `PARAMETER_ASSUMPTION_COMPROMISED`
- `ZK_MIGRATION_SOURCE_WITNESS_UNAVAILABLE`
- `ZK_MIGRATION_EQUIVALENCE_UNPROVEN`

## RED-first matrix (40 cases)

### Witness/checkpoint survivability
1. Historical 3-of-5 checkpoint remains verifiable after two witness organizations disappear.
2. Same evidence is rejected if historical witness denominator metadata is missing.
3. Replacement 3-of-3 witness epoch must not retroactively satisfy old 3-of-5 requirement.
4. Signed checkpoint without consistency ancestry => incomplete package.
5. Same-size/different-root archived checkpoints => equivocation evidence.
6. Newer checkpoint with valid consistency proof => accepted continuation.
7. Newer checkpoint without consistency material => unknown, not accepted continuation.
8. GC attempted with only checkpoint digest retained => reject.

### Byzantine time aggregation
9. Population fixed before query, q consistent independent intervals => accept.
10. Remove outlier after observation to reach q => reject denominator laundering.
11. q signatures but two share one forbidden control domain => independence threshold not met.
12. Two incompatible q-sized valid regions => `TIME_QUORUM_EQUIVOCAL`.
13. Nonce replay from old response => freshness failure.
14. Roughtime chain proves ordering but intervals disagree => ordering accepted, wall-clock conclusion remains ambiguous.
15. Key rollover with predecessor authorization and boundary => new epoch only.
16. New key used to revalidate old unsigned response => reject.

### Proof-closure parser/generator migration
17. Exact old/new parser outputs identical on authenticated corpus => candidate equivalence evidence.
18. Decision-relevant parse difference without adjudication => migration blocked.
19. New generator produces same bytes from independent reproducible build => build relation proven only.
20. Same output but shared compromised pipeline => independence claim rejected.
21. Old parser executable missing, spec unambiguous and independently reimplemented => reduced but explicit assurance path.
22. Old parser semantics unavailable/ambiguous => no historical semantic-equivalence claim.
23. New generator signs its own equivalence only => insufficient.
24. Migration overwrites predecessor proof object => reject immutability violation.

### Escrow refresh/reconfiguration
25. All required refresh contributions validate, epoch activates atomically => accept.
26. Partial refresh then crash => remain/recover according to old valid epoch; no mixed acceptance.
27. Offline member causes ad-hoc threshold reduction => reject.
28. Authorized membership reconfiguration uses explicit new epoch => accept when scheme validates.
29. Software rollback presents old retired share => reject by active cryptographic epoch.
30. Returning member proves identity but not active epoch membership => no share recovery.
31. Prior epoch threshold compromise followed by refresh => historical exposure remains recorded.
32. Concurrent refresh attempts from same predecessor => require single authoritative successor/CAS; conflicting successors fail closed.

### ZK setup/proof-system migration
33. Proof verifies under exact uncompromised parameter epoch => normal historical validation.
34. Same proof presented without parameter epoch => reject contextual ambiguity.
35. Credible setup-secret compromise for its SRS => current reliance re-opened.
36. New SRS introduced => old proofs remain classified under old SRS, not rehabilitated.
37. Re-prove old claim from surviving authenticated witness under semantically equivalent new circuit => new evidence lineage.
38. Underlying witness/source unavailable => migration cannot recreate truth from old proof alone.
39. Ceremony transcript valid but participant independence unknown => contribution validity does not imply independence.
40. Transparent successor proof system => setup-secret risk removed for successor, other verifier/circuit/provenance gates remain.

## Decisions

1. Freeze `WITNESS_TIME_PROOFCLOSURE_ESCROW_ZK_MIGRATION_V1_FROZEN`.
2. Historical denominators and key/parameter epochs are immutable evaluation inputs; later availability or policy changes never rewrite them.
3. Complete archival evidence requires the objects needed to reproduce the claimed relation, not merely hashes/signatures referencing vanished material.
4. Multi-time-source assurance is a policy over precommitted independent populations and authenticated intervals/order evidence; it is not naive averaging.
5. Proof-closure migration creates a successor evidence generation and requires explicit parser/generator semantic-equivalence evidence.
6. Escrow refresh is epoch-atomic, cannot silently reduce thresholds around offline members, and cannot erase prior threshold exposure.
7. ZK setup/proof-system migration secures successor evidence only; compromised predecessor parameters are not rehabilitated without surviving underlying authenticated witness/source evidence and a new proof.

## Exact next distinct fallback if executable source remains unavailable

Freeze: **checkpoint-package archival denominator and anti-GC proof + Byzantine time-source membership recovery after authority compromise + proof-closure semantic-diff attestation and canonical corpus versioning + escrow refresh concurrency/epoch-fork adjudication + ZK ceremony transcript availability, contributor-independence evidence, and recursive proof renewal across parameter deprecation**.

If exact source execution becomes available first, immediately return to the LAB-086 full real-ledger gate recorded in `state/CURRENT.md`.
