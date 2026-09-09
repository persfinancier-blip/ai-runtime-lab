# Lease handoff fencing, proof-root migration, beacon privacy attestations, derived-cache revocation, and PQ single-use resumption v1

Date: 2026-09-09
Status: FROZEN DESIGN EVIDENCE; executable RED/GREEN remains pending exact source
Verdict: `LEASE_HANDOFF_PROOF_ROOT_BEACON_PRIVACY_CACHE_REVOCATION_PQ_SINGLE_USE_V1_FROZEN`

## Why this exists

LAB-086 remains the first executable priority. In this run the exact-source probe `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com` (exit 128). GitHub connector reads/writes remain available. Per `AGENTS.md`, no new LAB-086 behavioral/compile PASS is claimed; this note completes the next distinct evidence task already recorded in `state/CURRENT.md`.

## Primary donor evidence

1. HashiCorp Consul sessions/locks: `(Key, LockIndex, Session)` can be used as a sequencer; `LockIndex` increases on acquisition and can detect stale requests. Consul explicitly warns that locks are advisory unless the downstream operation validates the sequencer. Its `lock-delay` exists to give a potentially still-live former holder time to observe invalidation and stop unsafe work. https://developer.hashicorp.com/consul/docs/automate/session
2. etcd Lease API: lease expiry/revocation removes attached keys and lease TTL is cluster-owned state, not a client-local fencing proof. https://etcd.io/docs/v3.5/learning/api/
3. RFC 9162 Certificate Transparency v2: historical verification is rooted in signed tree heads plus inclusion/consistency proofs; a new trust/proof generation does not retroactively change the predecessor checkpoint. https://www.rfc-editor.org/rfc/rfc9162
4. Sigstore security/threat model and TUF trust-root practice: trust roots rotate, compromised material can be revoked with compromise time, stale root/key material must not silently remain authoritative, and threshold/offline roots improve compromise resilience. https://docs.sigstore.dev/about/security/ ; https://docs.sigstore.dev/about/threat-model/
5. SLSA provenance model: a builder identity represents the transitive closure of entities trusted to run the build and record provenance; different security modes should have different builder identities. This is a useful donor for dependency/common-control claims. https://slsa.dev/spec/v1.2/provenance
6. NIST randomness beacon work: signed/hash-chained pulses limit some operator power, but beacon users still depend on operator trust and on the correctness/completeness of declared dependencies. https://www.nist.gov/publications/new-randomness-beacon-format-standard-exercise-limiting-power-trusted-third-party
7. NIST SP 800-88 family: deletion/sanitization assurance is about all effective residual representations, not only the primary object. This supports treating indexes/caches/derived copies as separate deletion obligations. https://www.nist.gov/publications/guidelines-media-sanitization
8. RFC 9846 (current TLS 1.3): 0-RTT has no inherent replay protection; single-use tickets are the simplest anti-replay design; distributed deployments need consistent anti-replay state, and one authoritative zone per ticket is stronger than accepting the same ticket independently in every zone. https://www.rfc-editor.org/rfc/rfc9846

## 1. Lease handoff fencing, acknowledgement, and stale-owner write suppression

### Boundary

`LOCK_RELEASED != OLD_OWNER_UNABLE_TO_WRITE`.

A control-plane lease transition is not enough if the protected data plane accepts writes that do not carry and validate the current fencing generation.

### Required handoff state

Each consequential handoff should bind:

- `resource_id`;
- predecessor `lease_generation` / fencing token;
- predecessor owner identity;
- successor `lease_generation` / fencing token;
- handoff authority epoch;
- durable successor acquisition record;
- optional predecessor acknowledgement, if available;
- downstream minimum accepted generation;
- terminal disposition of predecessor authority.

The protected sink must reject any mutation carrying a generation lower than the highest generation it has durably accepted for that resource. This converts stale-owner suppression from an advisory lock property into a data-plane invariant.

### Acknowledgement rule

A clean acknowledgement from the predecessor is useful liveness evidence but is not required for safety if the sink enforces monotonic fencing. Conversely, predecessor acknowledgement without sink-side fencing is not sufficient: a paused/replayed/partitioned old process can later resume.

Frozen invariants:

`PREDECESSOR_ACK != STALE_WRITE_IMPOSSIBILITY`.

`SUCCESSOR_ACQUIRED != DATA_PLANE_FENCED`.

For a resource with accepted fence F, any write with `fence < F` fails closed before side effects.

### RED-first cases

1. owner g1 pauses, g2 acquires, g1 resumes and writes -> sink rejects g1;
2. g1 sends acknowledgement then a queued g1 request arrives -> reject;
3. lock-delay expires but sink has not advanced accepted fence -> no proof of safe successor effects;
4. successor acquires g2 but crashes before first sink write -> g1 still cannot regain authority by replay;
5. duplicate g2 acquisition event -> no extra authority generation;
6. downstream replica lag has only fence g1 while authority is g2 -> consequential write fails closed or routes through an authority that can prove g2;
7. resource handoff g2->g3 while delayed g1 request arrives -> reject all `< g3`;
8. control-plane rollback presents old g1 lock as current -> sink monotonic floor detects rollback.

## 2. Historical proof migration under trust-root compromise and dual-verifier transition

### Boundary

`NEW_ROOT_ACCEPTS != PREDECESSOR_HISTORY_REPAIRED`.

Compromise of a proof/log trust root changes assurance of affected historical generations. Rotating to a clean successor root can authorize future verification but cannot retroactively make previously suspect history trustworthy.

### Migration generation

A trust-root migration object should authenticate:

- predecessor root/version and validity interval;
- compromise/revocation status and effective compromise time when known;
- predecessor checkpoint population root;
- successor root/version;
- exact proof-format/hash/signature suites accepted by each verifier;
- migration bridge over predecessor population;
- verifier implementation/build identity;
- transition start/end policy;
- disagreement disposition.

### Dual-verifier window

During proof/hash/signature migration, two independent verifier implementations may run in parallel. Their purpose is cross-checking, not denominator inflation.

Frozen distinctions:

`TWO_PROCESSES != TWO_INDEPENDENT_VERIFIERS`.

`SUCCESSOR_ONLY_PASS + PREDECESSOR_FAIL != SAFE_MIGRATION`.

Within the declared overlap window, disagreement on the same canonical historical object is `VERIFIER_DIVERGENCE` and fails closed for consequential authorization until adjudicated. After predecessor algorithm retirement, archived history may remain historically verifiable under explicitly permitted legacy policy, but new authority uses the current floor.

### RED-first cases

9. predecessor root compromised before object timestamp -> historical assurance degrades;
10. successor root re-signs same predecessor root after compromise -> no repair;
11. verifier A accepts bridge, independent verifier B rejects -> fail closed;
12. two verifier processes share one library/build -> count one failure domain;
13. predecessor proof parser and successor parser canonicalize differently -> divergence;
14. root rollback serves an older still-signed metadata version -> reject monotonic rollback;
15. transition window expires while only predecessor verifier is healthy -> no silent extension;
16. clean successor migration preserves predecessor evidence plus explicit degraded status -> historical verification remains inspectable without rewriting assurance.

## 3. Privacy-preserving beacon dependency attestations without hiding common-control edges

### Boundary

`MINIMIZED_DISCLOSURE != MINIMIZED_DEPENDENCY_GRAPH`.

A beacon operator may need to avoid publishing sensitive infrastructure details, but privacy cannot be achieved by suppressing edges that materially determine whether supposedly independent beacons share one failure/control domain.

### Attestation shape

A dependency attestation may expose pseudonymous/stable domain commitments rather than raw vendor/account identifiers. It still needs to make equality/common-control relationships verifiable for threat-relevant classes such as:

- operator/governance control;
- cloud or hosting administrative root;
- KMS/HSM root;
- DKG/signing membership control;
- time source;
- upstream randomness/entropy source;
- build/signing pipeline;
- network/DNS control where consequential;
- emergency disable/fallback authority.

A privacy-preserving representation can commit to each scoped dependency identifier and disclose only equality/linkage proofs needed by the evaluator. But an omitted edge is not privacy; it is incomplete provenance.

Frozen distinctions:

`PSEUDONYMOUS_EDGE != UNKNOWN_EDGE`.

`ATTESTOR_SIGNATURE != GRAPH_COMPLETENESS`.

Dependency claims require version/freshness plus a completeness statement scoped to a published dependency schema. Unknown or undisclosed mandatory classes default to `INDEPENDENCE_NOT_PROVEN`.

### RED-first cases

17. two beacons hide raw cloud account IDs but prove same committed admin domain -> correlated;
18. attestation omits KMS class entirely -> independence not proven;
19. different pseudonyms are used for the same dependency to evade equality -> cross-attestor audit detects inconsistency;
20. dependency rotates mid-generation -> successor/delta required;
21. attestor proves only direct dependencies while shared upstream entropy is transitive -> incomplete;
22. disclosure policy changes and removes a mandatory threat class -> no silent assurance retention;
23. independent privacy auditor can verify equality without learning raw identifier -> acceptable;
24. attestation signer compromised -> affected generations degrade; clean re-attestation requires fresh measurement, not simple re-signing.

## 4. Commitment/key destruction must revoke derived indexes, caches, and materialized views

### Boundary

`PRIMARY_SECRET_DELETED != DERIVED_LOOKUP_AUTHORITY_REVOKED`.

Destroying payloads, encryption keys, peppers, or commitment keys does not automatically invalidate derivative artifacts that were computed while the secret was live.

### Derived-artifact inventory

Deletion policy must account for at least:

- deterministic search indexes;
- bloom/filter membership structures;
- caches and CDN/object caches;
- materialized views;
- analytics aggregates when they preserve sensitive membership;
- embeddings/features derived from sensitive values;
- deduplication fingerprints;
- queued jobs/retry payloads;
- replicas/backups/snapshots of any of the above;
- authorization caches that still bind the deleted identity/claim.

Each derived artifact needs an explicit post-deletion classification: `DESTROYED`, `INVALIDATED`, `REBUILT_WITHOUT_SUBJECT`, `RETAINED_NON_SENSITIVE`, or `UNACCOUNTED`.

Frozen invariants:

`KEY_ERASURE != INDEX_ERASURE`.

`CACHE_TTL_EXPIRED_EVENTUALLY != REVOCATION_COMPLETE_NOW`.

For consequential lookup/authorization, a deleted subject must not remain discoverable merely because a stale derived index or cache outlived the primary secret.

### RED-first cases

25. primary row/key deleted but deterministic secondary index still resolves subject -> fail deletion completeness;
26. cache returns pre-deletion authorization decision -> reject via deletion/revocation generation;
27. materialized view contains membership bit after payload deletion -> residual disclosure remains;
28. embedding/vector cache permits subject inference -> retained derived artifact must be classified;
29. old index survives in backup -> destruction universe incomplete;
30. index rebuilt without subject but stale replica remains queryable -> incomplete;
31. TTL cache eventually expires but consequential access is possible during TTL -> revocation not immediate;
32. audit-only aggregate is retained and proven non-identifying under policy -> may remain, but disposition is explicit rather than assumed.

## 5. PQ/TLS resumption: single-use ticket ownership through failover, draining, and mixed-version clusters

### Boundary

`TICKET_SINGLE_USE_POLICY != SINGLE_GLOBAL_CONSUMPTION`.

A ticket is single-use only if exactly one authoritative consumer can durably spend it for the relevant scope. Replicated copies with independent local consume state are multi-use credentials in practice.

### Ticket authority record

For consequential resumption, bind:

- ticket/PSK identity or canonical digest;
- issuance policy epoch and crypto suite/hybrid combiner;
- issuer/service identity;
- authoritative consumption zone/partition;
- consumption generation/state;
- current crypto-policy floor;
- server software/version eligibility;
- 0-RTT permission and application replay class;
- failover/drain state;
- terminal disposition.

### Failover and draining

A failover protocol must transfer ticket-spend authority, not merely ticket decryption keys. If old and new clusters can both consume the same ticket during a drain window, `single-use` is false.

Safe options include:

- one authoritative zone per ticket with deterministic routing;
- strongly consistent central consume state;
- pre-sharded ticket ownership where each ticket maps to exactly one active owner;
- fail closed for consequential 0-RTT while ownership is ambiguous.

A draining cluster may decrypt predecessor tickets for graceful 1-RTT fallback, but must not independently consume consequential 0-RTT if spend authority has moved.

### Mixed-version / PQ rollout rule

Older nodes that cannot enforce the current PQ/hybrid floor are not eligible authorities for new consequential resumption after the policy boundary, even if they can decrypt predecessor tickets. Retry to such a node cannot weaken the floor.

Frozen invariants:

`TICKET_DECRYPTION_KEY_REPLICATED != TICKET_SPEND_AUTHORITY_REPLICATED_SAFELY`.

`OLD_NODE_ACCEPTS != CURRENT_POLICY_AUTHORIZES`.

`FAILOVER != RESET_ANTI_REPLAY_STATE`.

### RED-first cases

33. ticket consumed in cluster A then replayed to failover cluster B -> B rejects 0-RTT or full-handshakes without replaying side effect;
34. A is draining while B becomes authoritative -> only one may consume the ticket;
35. ownership handoff acknowledgement lost -> ambiguous ticket fails consequential 0-RTT closed;
36. mixed-version old node accepts classical ticket after PQ floor activates -> reject current authorization;
37. new node receives old ticket and can decrypt it -> full fresh compliant handshake required if predecessor policy is below floor;
38. replay cache resets on node restart -> reject 0-RTT for overlapping freshness window;
39. ticket decryption key replicated to three zones but spend ownership is one zone -> other zones may decrypt for diagnosis/fallback but cannot spend consequential early-data authority;
40. client retries rejected 0-RTT as application request after 1-RTT -> application idempotency/replay key must prevent duplicated consequential effect.

## Cross-cutting frozen contract

1. Authority transitions require monotonic generations at the protected sink, not merely control-plane lock state.
2. Trust-root rotation preserves predecessor evidence and explicit degradation; it does not rewrite historical assurance.
3. Dual verification only adds assurance when verifier failure domains are independent and disagreement fails closed.
4. Privacy-preserving dependency attestations may hide raw identifiers but must preserve verifiable common-control relationships and mandatory-class completeness.
5. Deletion closes over derived indexes/caches/materializations, not only source payload/key objects.
6. Single-use resumption means one globally conserved spend authority, not one use per replica/cluster.
7. A stricter current PQ/hybrid policy floor dominates predecessor ticket decryptability and retry convenience.

## Implementation-facing RED matrix summary

Cases 1-8: stale-owner handoff and sink fencing.
Cases 9-16: trust-root compromise and dual-verifier migration.
Cases 17-24: privacy-preserving beacon dependency/common-control evidence.
Cases 25-32: derived index/cache revocation after secret/key destruction.
Cases 33-40: single-use resumption across failover/draining/mixed-version PQ rollout.

These are design-frozen RED cases only. No exact repository RED/GREEN execution is claimed in this run.

## Audit pass

- Correctness: separates observation/coordination state from data-plane authority and separates ticket decryptability from globally unique consumption.
- Security: explicitly covers stale writers, trust-root rollback/compromise, hidden common-control, residual derived artifacts, partitioned anti-replay, and downgrade through old nodes.
- Duplication: extends the preceding lease/proof/beacon/privacy/PQ research with new handoff, compromise-window, privacy-preserving graph, derived-cache, and single-consumer boundaries rather than restating prior generation/partition rules.
- Unsupported assumptions: no claim that Consul advisory locks automatically fence an arbitrary downstream sink; donor documentation explicitly says they do not. No claim that signed dependency attestations prove completeness. No claim that TLS single-use tickets solve application-layer retries by themselves.

## Exact next distinct evidence task if LAB-086 execution remains blocked

**sink-fence generation persistence across storage rollback/restore + dual-verifier canonicalization equivalence and parser differential attacks + beacon dependency-attestation schema evolution/mandatory-field downgrade + deletion tombstone/negative-cache propagation and reintroduction prevention + PQ resumption ticket-authority migration during regional disaster recovery and post-compromise ticket-key rotation**.

If an automated exact-source path becomes available first, immediately return to the LAB-086 executable gate recorded in `state/CURRENT.md`.
