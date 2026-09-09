# LAB-093 follow-up — budget leases, witness retirement, beacon attestations, confidential deletion, PQ resumption

Date: 2026-09-09
Status: `BUDGET_LEASE_WITNESS_RETIREMENT_BEACON_ATTESTATION_CONFIDENTIAL_DELETION_PQ_RESUMPTION_V1_FROZEN`

## Why this exists

LAB-086 remains the primary executable task, but exact repository execution is unavailable in this runtime: direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com` (exit 128). No new LAB-086 behavioral or compile PASS is claimed here.

This document executes the distinct fallback recorded in `state/CURRENT.md`. It freezes security semantics that future RED/GREEN work must implement rather than inventing during production refactors.

## Primary donors checked

- etcd v3 API guarantees / leases: https://etcd.io/docs/v3.5/learning/api_guarantees/
- etcd Lease API: https://etcd.io/docs/v3.5/learning/api/
- etcd lease linearizability discussion: https://github.com/etcd-io/etcd/issues/13915
- RFC 9162 Certificate Transparency v2: https://www.rfc-editor.org/rfc/rfc9162
- Sigstore Rekor sharding: https://docs.sigstore.dev/logging/sharding/
- Sigstore Rekor monitoring/auditing: https://docs.sigstore.dev/logging/overview/
- Sigstore threat model / TUF-root freshness and revocation: https://docs.sigstore.dev/about/threat-model/
- NIST IR 8213 draft, interoperable randomness beacons: https://csrc.nist.gov/pubs/ir/8213/ipd
- NIST IR 8213 draft PDF security considerations: https://nvlpubs.nist.gov/nistpubs/ir/2019/NIST.IR.8213-draft.pdf
- SLSA v1.2 verifying artifacts: https://slsa.dev/spec/v1.2/verifying-artifacts
- SLSA v1.2 Verification Summary Attestation: https://slsa.dev/spec/v1.2/verification_summary
- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
- NIST SP 800-171 Rev. 3 audit information protection: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/800-171r3/NIST.SP.800-171r3.html
- W3C Data Integrity BBS Cryptosuites v1.0: https://www.w3.org/TR/vc-di-bbs/
- RFC 9846 TLS 1.3: https://www.rfc-editor.org/rfc/rfc9846
- RFC 9325 secure TLS recommendations: https://www.rfc-editor.org/rfc/rfc9325
- RFC 9813 operational TLS-PSK/resumption considerations: https://www.rfc-editor.org/rfc/rfc9813
- NIST PQC project: https://csrc.nist.gov/Projects/Post-Quantum-Cryptography
- NIST IR 8547 initial public draft: https://csrc.nist.gov/pubs/ir/8547/ipd

Draft-status note: NIST IR 8213 and the cited IR 8547 page are draft-status donors. Their mechanisms are used as design evidence, not asserted as final normative requirements.

---

## 1. Distributed challenge-budget leases: expiration and clock authority

### Finding

A distributed budget lease is not merely `amount + expires_at`. Expiration is an authority decision whose correctness depends on the clock and on partition semantics.

etcd explicitly documents that lease expiry is driven by wall-clock TTL, while consensus completion is a separate concept. Its maintainers also note that real-time leases cannot provide exactly the same guarantees as ordinary linearizable state and therefore centralize expiry decisions at the leader. This is the correct warning for a security budget: replicated storage consensus does not make local wall clocks authoritative.

### Frozen contract

A `BudgetLeaseGeneration` MUST authenticate at least:

- budget authority epoch;
- lease id and grantee/domain;
- total spend units;
- issue logical sequence;
- not-before and expiry semantics;
- the permitted time authority / bounded-time evidence class;
- partition mode (`FAIL_CLOSED`, `PREALLOCATED_SHARDS`, or another versioned mode);
- predecessor generation / anti-rollback floor.

The system MUST distinguish:

`LEASE_RECORD_REPLICATED != LEASE_EXPIRY_AUTHORITATIVE`

and

`LOCAL_CLOCK_AFTER_EXPIRY != GLOBAL_RIGHT_TO_RECLAIM_BUDGET`.

Rules:

1. A partition must not allow two sides to independently reclaim the same expired units merely because both local clocks passed `expires_at`.
2. If wall-clock expiry is used, the contract must name the authoritative clock domain or bounded-time evidence used to make reclaim consequential.
3. Clock rollback/freeze/forward-jump creates `TIME_AUTHORITY_DEGRADED`; it does not silently extend or reclaim budget.
4. Lease renewal creates a successor authorization event; it must not erase spend already consumed under the predecessor.
5. Authority rollover preserves all outstanding lease obligations and spent-unit conservation.
6. `FAIL_CLOSED` is the default when a lease expiry cannot be authenticated strongly enough to avoid double allocation.
7. A preallocated-shard design may continue during partition only when the maximum local spend was fixed before the partition and all shards sum to no more than the predecessor global budget.

### Design consequence

For an executable implementation, prefer consensus-ordered logical lease generations plus bounded/fenced expiry authorization. Do not make security-critical budget conservation depend only on `time.time()` at each replica.

---

## 2. Witness archival availability after retirement or archive-domain loss

### Finding

Transparency correctness and transparency survivability are different properties.

RFC 9162 gives append-only checkpoint/inclusion/consistency semantics. Sigstore Rekor explicitly supports freezing an old Merkle-tree shard and rotating to a new shard/key. A frozen shard can be historically valid even though it is no longer an active writer. Therefore retirement of a log/witness must not erase the material required to verify historical promises.

### Frozen contract

Each consequential historical witness claim MUST bind an immutable `WitnessArchiveGeneration` containing or committing to:

- log/shard identity;
- witnessed checkpoint/root/tree size;
- witness key/trust-root epoch;
- observation time/sequence;
- inclusion/consistency evidence required by policy;
- archive domain(s) and retrieval format/version;
- retirement state and successor lineage.

Required invariants:

`WITNESS_RETIRED != HISTORICAL_WITNESS_EVIDENCE_DISPOSABLE`

`LOG_FROZEN != LOG_UNVERIFIABLE`

`ONE_ARCHIVE_COPY != ARCHIVE_SURVIVABILITY`

Rules:

1. Retirement freezes authority for future observations but preserves predecessor verification material.
2. Historical verification must remain possible without contacting the retired online service.
3. Archive replication is counted by independent destructive/control domains, not copy count.
4. Losing one archive domain reduces survivability assurance but does not alter what the historical witness signed.
5. If policy-required historical proof material is no longer retrievable, status becomes `HISTORICAL_EVIDENCE_UNAVAILABLE`; it must not be converted to PASS from a digest-only summary unless that summary was the original accepted proof contract.
6. Split-view evidence retains both conflicting signed views even after adjudication.
7. Successor witness/log keys may attest archival continuity, but successor signatures do not recreate missing predecessor inclusion/consistency evidence.

### Design consequence

A future archive subsystem needs a manifest-level availability proof: exact historical objects, their hashes, decoding format, independent archive domains, and periodic retrieval challenges. Mere storage-provider durability claims are insufficient for cryptographic audit survivability.

---

## 3. Beacon dependency-attestation authority compromise and revocation

### Finding

A signed dependency attestation proves that an attesting key made a statement; it does not prove the dependency was independent, uncompromised, or honestly measured.

NIST IR 8213's security considerations explicitly discuss authenticated clocks/timestamps as mitigations against forward time skew and describes signed, hash-chained pulses with precommitment. SLSA similarly requires verifiers to configure roots of trust and explicitly warns that provenance trust assumes the trusted build platform/verifier itself is trustworthy.

### Frozen contract

A `BeaconDependencyAttestation` MUST be scoped to an exact beacon generation and commit to relevant failure domains, including as applicable:

- operator/legal control;
- hosting/cloud/region;
- implementation/build/SBOM identity;
- signing and DKG/threshold membership lineage;
- upstream entropy/time/network dependencies;
- attestor identity and attestor authority epoch;
- observation interval and freshness deadline.

The system MUST distinguish:

`VALID_ATTESTATION_SIGNATURE != TRUE_INDEPENDENCE`

`ATTESTOR_NOT_REVOKED_NOW != ATTESTOR_TRUSTED_AT_OBSERVATION_TIME`

Rules:

1. Dependency-attestation roots are versioned and revocable.
2. Compromise at time `t_c` degrades attestations whose trusted validity interval intersects the compromise uncertainty window.
3. A successor attestor re-signing old claims without independent remeasurement is `REENDORSEMENT`, not `REAUDIT`.
4. Independence calculations fail closed when required dependency dimensions are unknown or withheld.
5. Beacon sample generation must retain the dependency-attestation generation used to justify its independence denominator.
6. Post-reveal revocation cannot rewrite the randomness actually used; it changes assurance/degradation state for that decision and may trigger re-execution only where policy permits.
7. Attestation transparency can improve compromise detection but cannot by itself prove attestation truth.

---

## 4. Confidential evidence redaction/deletion without audit-history corruption

### Finding

Confidentiality/minimization and audit immutability are not the same requirement and neither should silently erase the other.

NIST SP 800-53/800-171 require protecting audit information from unauthorized modification/deletion and retaining records according to policy. W3C BBS demonstrates that authenticated selective disclosure can prove revealed claims without exposing the full source document. These mechanisms support a design where sensitive payload material can be withheld or cryptographically disposed while immutable audit history preserves non-sensitive commitments and lifecycle evidence.

### Frozen contract

A policy-authorized redaction/deletion creates a new immutable lifecycle event; it MUST NOT mutate an already authenticated historical record in place.

Separate objects:

1. `EvidencePayload` — confidential plaintext/ciphertext/material that may be retention-limited.
2. `EvidenceCommitment` — authenticated digest/commitment, schema/version, creation generation and authority lineage.
3. `DisclosureProof` — policy-scoped selective disclosure / derived proof when applicable.
4. `DispositionRecord` — why/when/by-whom material was redacted, crypto-erased, retention-expired, or legally held.

Required distinctions:

`PAYLOAD_DELETED != AUDIT_EVENT_DELETED`

`COMMITMENT_RETAINED != PLAINTEXT_RETAINED`

`VALID_SELECTIVE_PROOF != COMPLETE_EVIDENCE_POPULATION`

Rules:

1. Redaction/deletion never rewrites predecessor roots/checkpoints/verdicts.
2. If payload removal makes a prior verdict impossible to independently reproduce, the historical record must state that limitation (`PAYLOAD_UNAVAILABLE_FOR_REAUDIT`) rather than continue claiming reproducibility.
3. Retain only the minimum commitment/metadata needed by the audit contract; do not keep secret material merely to preserve a hash.
4. Crypto-erasure/disposition evidence identifies covered copy domains; it does not claim all copies are gone unless copy-domain completeness was separately proven.
5. Selective disclosure proves only revealed statements. Completeness must come from a precommitted evidence population/denominator or another explicit proof.
6. Legal/policy holds are versioned exceptions and do not silently change prior retention policy.
7. A deletion requester and audit adjudicator are separate authorities where policy requires separation of duties.

### Design consequence

Future implementation should make audit history append-only while making confidential payload storage independently lifecycle-managed. A tombstone/disposition event can preserve the authenticated commitment and reason without preserving the sensitive payload.

---

## 5. PQ/TLS resumption across cross-cluster ticket replication, server identity rotation, and crypto-policy clock/freshness failure

### Finding

A TLS resumption ticket is a predecessor-session credential, not a timeless authorization token.

RFC 9846 caps TLS 1.3 ticket use at seven days and recommends limiting the total lifetime of keying material derived across repeated resumptions. RFC 9325 recommends regular ticket-encryption-key rotation and destruction of old keys. RFC 9813 further emphasizes that authorization/policy information associated with an initial session must be reevaluated on resumption when relevant facts changed.

Cross-cluster ticket-key replication increases availability but also enlarges the key compromise domain. Server identity rotation and cryptographic-policy deprecation create fresh authorization questions that cannot be answered merely by decrypting an old ticket.

### Frozen contract

Every accepted resumption decision MUST bind:

- ticket issuance epoch / original handshake identity;
- issuing cluster/logical service identity;
- ticket-key generation and replication domain set;
- original crypto suite / hybrid-combiner policy;
- current server identity generation;
- current minimum crypto-policy epoch;
- authenticated freshness/time evidence used to evaluate ticket age and policy effective time;
- whether 0-RTT is permitted for the requested operation class.

Required distinctions:

`TICKET_DECRYPTS != RESUMPTION_AUTHORIZED`

`SAME_LOGICAL_SERVICE != SAME_TICKET_KEY_FAILURE_DOMAIN`

`VALID_OLD_SERVER_TICKET != CURRENT_SERVER_IDENTITY_AUTHORIZATION`

`LOCAL_CLOCK_SAYS_NOT_EXPIRED != POLICY_FRESHNESS_PROVEN`

Rules:

1. Cross-cluster ticket replication must be explicit in the credential's accepted failure-domain policy. Replication does not create independent trust roots.
2. If one replicated ticket-key domain is compromised, every ticket decryptable with that generation is evaluated against the compromise interval; clean peer clusters do not erase that exposure.
3. Server certificate/identity rotation may permit resumption only under an explicit logical-service continuity policy. A ticket cannot itself authorize the new server identity.
4. A stricter current PQ/hybrid crypto floor overrides a weaker predecessor ticket for new consequential use. Fall back to a fresh compliant full handshake or fail closed.
5. Crypto-policy `effective_from` is evaluated using authenticated/bounded freshness evidence. Clock rollback/freeze causing ambiguous policy epoch is fail-closed for consequential resumption.
6. 0-RTT is separately authorized because replay semantics differ from ordinary 1-RTT resumption.
7. Repeated resumption must not indefinitely extend predecessor authentication/keying-material lifetime.
8. Ticket-key rotation destroys retired private key material after the accepted validation window, while historical audit records retain only non-secret generation/provenance evidence.
9. Unknown/expired/deprecated tickets may trigger a fresh handshake; they must never trigger negotiation below the current crypto floor.

NIST's PQ migration work supplies the lifecycle direction: once a quantum-vulnerable mechanism moves below the accepted floor, legacy verification of historical evidence is not the same as authority for a fresh operation.

---

## Cross-cutting state model

For all five domains, use immutable generations and monotonic degradation rather than history rewriting.

Recommended common states:

- `VALID`
- `DEGRADED`
- `REAUTH_REQUIRED`
- `REAUDIT_REQUIRED`
- `EVIDENCE_UNAVAILABLE`
- `REVOKED_FOR_NEW_USE`
- `INVALIDATED`

A successor generation may restore eligibility for future operations, but it never changes the actual evidence, denominator, policy, time source, or trust roots under which a historical event occurred.

---

## RED-first regression matrix (40 cases)

### Budget lease / clock authority

1. Two partitioned nodes both pass local expiry and both reclaim the same budget -> reject one/global double allocation impossible.
2. Signed preallocated shards sum above predecessor global budget -> reject generation.
3. Clock rolls backward after spend -> no spend resurrection.
4. Clock jumps forward -> no unauthenticated early reclaim.
5. Lease authority key rotates with outstanding leases -> obligations carried exactly once.
6. Expired lease with unavailable authoritative-time evidence -> fail closed for reclaim.
7. Restart loses local rate-limit/lease spend cache but durable spend exists -> no budget reset.
8. Renewal changes expiry but also accidentally resets consumed units -> reject.

### Witness retirement / archival availability

9. Retire active log shard while all historical inclusion/consistency objects archived -> historical verify succeeds offline.
10. Retire shard but keep only root digest when policy requires inclusion path -> `HISTORICAL_EVIDENCE_UNAVAILABLE`.
11. Lose one of two archive copies in same cloud account -> independence remains one domain, assurance decreases.
12. Lose one of two genuinely independent archive domains -> surviving evidence still verifies, survivability status degrades.
13. Successor key signs statement that predecessor entry existed but predecessor proof is missing -> not equivalent to original proof.
14. Conflicting signed historical checkpoints survive adjudication -> both retained.
15. Archive decoder/schema metadata missing -> no unverifiable silent PASS.
16. Retrieval challenge finds corrupted historical bundle -> fail integrity and preserve corruption evidence.

### Beacon dependency-attestation compromise/revocation

17. Valid attestation signed by later-compromised key within uncertainty window -> generation degraded.
18. Successor attestor re-signs same old dependency JSON without remeasurement -> `REENDORSEMENT`, not re-audit.
19. Two beacons claim different operators but same cloud+DKG control -> count correlated domain according to policy.
20. Required dependency dimension withheld -> no independence quorum.
21. Attestor revoked after sample reveal -> historical sample unchanged, assurance state updated.
22. Dependency attestation references wrong beacon generation -> reject.
23. Authenticated clock attestation expired before pulse -> freshness failure.
24. Transparency inclusion proves attestation existed but underlying measurement false -> inclusion alone does not promote truth.

### Confidential evidence deletion/redaction

25. Delete confidential plaintext but retain authenticated commitment + disposition -> history remains verifiable at commitment level.
26. Delete payload required for exact re-audit -> mark `PAYLOAD_UNAVAILABLE_FOR_REAUDIT`.
27. Mutate old audit row to remove sensitive field instead of appending disposition -> reject integrity.
28. Valid BBS/selective proof over disclosed claim while hidden population completeness unproven -> no full-population verdict.
29. Crypto-erase one storage domain while backup domain remains -> no all-copy destruction claim.
30. Deletion request races with legal/policy hold -> deterministic authority ordering; no silent destructive race.
31. Retention expiry removes secret but also removes trust-root/key lineage needed to verify commitment -> reject disposition plan.
32. Requester can also alter disposition audit without separation required by policy -> reject authority graph.

### PQ/TLS resumption lifecycle

33. Ticket decrypts on cluster B via replicated key but B is outside allowed service/ticket domain -> reject resumption.
34. One cluster's replicated ticket key compromised -> tickets under that generation degraded across every holder cluster.
35. Server identity rotated to new certificate but logical-service continuity policy absent -> require full handshake.
36. Ticket issued under classical-only suite after current policy requires PQ/hybrid -> full compliant handshake or fail closed.
37. Local clock rollback makes ticket look younger than authenticated policy clock -> reject consequential resumption.
38. Ticket valid for 1-RTT but operation attempts consequential 0-RTT without replay-safe authorization -> reject early data.
39. Resumption chain continuously refreshes tickets beyond allowed total predecessor-authentication lifetime -> force full handshake.
40. Unknown/deprecated ticket causes fallback; client/server then negotiate weaker-than-current crypto floor -> reject downgrade.

---

## Implementation boundary

This is a design freeze, not executable proof. It does not supersede LAB-086, LAB-088, LAB-090, LAB-091 or LAB-092 execution gates.

When exact source execution becomes available, LAB-086 returns immediately to priority #1. For LAB-093+, implement these contracts regression-first and preserve exact generation/policy/trust-root lineage in durable evidence.

## Next distinct fallback if exact execution is still unavailable

Research and freeze:

- lease reallocation with delayed/duplicated expiry notifications and quorum leadership changes;
- historical witness proof-format migration/crypto deprecation without losing offline verifiability;
- beacon dependency graph transitive closure and hidden common-control discovery;
- confidential commitment key/pepper destruction and dictionary-attack/privacy leakage after payload deletion;
- PQ resumption ticket theft detection, replay caches across partitions, and hybrid policy negotiation under asymmetric client/server upgrade rollout.
