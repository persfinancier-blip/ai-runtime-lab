# Lease reallocation, historical proof migration, beacon common-control, confidential key destruction, and PQ resumption partitions v1

Date: 2026-09-09
Status: FROZEN DESIGN EVIDENCE; executable RED/GREEN remains pending exact source
Verdict: `LEASE_PROOF_BEACON_PRIVACY_PQ_PARTITION_V1_FROZEN`

## Why this exists

LAB-086 remains the first executable priority, but the current runtime still cannot obtain exact repository source through direct git transport. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`. The GitHub connector remains usable for durable control-plane reads/writes. Per `AGENTS.md`, this run therefore performs the next already-recorded distinct evidence task without claiming executable proof.

This note freezes five cross-cutting failure contracts that are easy to get wrong when authority is distributed across clocks, logs, randomness sources, deletion keys, or TLS/PQ resumption caches.

## Primary donor evidence

1. etcd failure documentation: on leader failure, a new leader is elected after a timeout; writes cannot commit during election; uncommitted writes may be lost; committed writes are retained; the new leader extends lease timeouts so leases do not expire before their granted TTL because of leader loss. This is useful evidence that lease expiry and leadership transition are coupled operationally and that delayed expiry must not be interpreted as reusable authority without a conservation rule.
2. RFC 9162 Certificate Transparency v2: Merkle consistency proofs verify append-only ancestry between signed tree heads; proof objects are meaningful relative to versioned structures, hash/signature algorithms, log identity, and retained signed checkpoints. Historical verification therefore needs an explicit migration bridge when proof formats or cryptographic suites change.
3. NIST IR 8213 draft randomness-beacon reference: pulses are timestamped, signed and hash-chained, and can precommit to the next pulse so randomness from different beacons can be securely combined. This supports authentic pulse lineage but does not by itself prove that apparently separate beacons have independent operators, infrastructure, build roots, time sources, or upstream entropy.
4. NIST SP 800-63B (current 800-63-4 series) and OWASP Password Storage guidance: salts raise offline-guessing cost separation between records; an additional secret keyed step/pepper can make brute-force against stolen hashes impractical while the secret remains secret; compromise of a pepper materially changes assurance. This is a useful analogue for commitment/keyed-digest privacy after payload deletion.
5. NIST SP 800-88r2: cryptographic erase depends on sanitizing all relevant key material, including hierarchically related and previously unwrapped copies. Key destruction can render ciphertext infeasible to decrypt, but only if all effective recovery copies are actually gone.
6. RFC 8446 / RFC 9846 TLS 1.3: 0-RTT has replay hazards; inconsistent anti-replay state across clusters can allow multiple acceptance during replication windows; a safe design can make one storage zone authoritative for a given ticket; a fallback full handshake can still interact with application retries to duplicate operations. Current TLS 1.3 also caps ticket lifetime at seven days. RFC 9813 further requires resumption authorization/policy state to be reevaluated when relevant attributes changed.

## 1. Lease reallocation after delayed or duplicated expiry notifications

### Boundary

`EXPIRY_NOTIFICATION != AUTHORITY_TO_REALLOCATE`.

A notification is observation evidence. Reallocation authority requires an authenticated lease generation plus a globally conserved ownership transition.

### Required lease state

Each consequential lease allocation should bind at least:

- `resource_id`;
- `lease_generation`;
- `owner_id`;
- `grant_index` or equivalent consensus generation;
- `ttl_policy`;
- authoritative expiry basis;
- leadership/authority epoch;
- terminal disposition (`RELEASED`, `EXPIRED_CONFIRMED`, `REVOKED`, etc.).

A delayed expiry event for generation g after generation g+1 already exists is stale evidence, not a second release. A duplicated expiry event is idempotent only when bound to the same generation and terminal transition.

### Leadership-change rule

A leadership change may delay lease expiry, recompute remaining TTL, or extend expiry according to the replicated lease protocol. It must never produce two simultaneously spendable allocations from one predecessor lease.

Frozen invariant:

`SUM(active successor authority for one predecessor resource) <= 1`.

If the new leader cannot prove whether predecessor authority is still live, the state is `REALLOCATION_AMBIGUOUS` and consequential reuse fails closed unless a predeclared bounded partition-shard protocol proves conservation.

### RED-first cases

1. old leader emits expiry, loses leadership before commit, new leader retains lease -> stale event must not reallocate;
2. expiry event delivered twice -> exactly one successor;
3. delayed expiry for g arrives after explicit release and allocation g+1 -> no effect;
4. leader changes just before deadline -> no early reuse merely from local clock;
5. leader changes just after deadline but before durable expiry transition -> no duplicate owner;
6. partition minority locally believes lease expired -> cannot allocate if quorum authority absent;
7. preallocated bounded shards across partition -> total shard units remain globally bounded;
8. late old-leader notification after recovery -> historical evidence only.

## 2. Historical witness proof-format / crypto migration

### Boundary

`NEW_PROOF_FORMAT_VERIFIES != OLD_HISTORY_MIGRATED`.

A historical object proved under format/hash/signature suite V1 cannot simply be re-encoded into V2 and treated as if V2 originally witnessed it.

### Migration object

A successor proof generation should authenticate:

- predecessor log/proof identity;
- predecessor signed checkpoint/root;
- predecessor algorithm/format version;
- exact semantic object being carried forward;
- successor representation/root;
- migration implementation/provenance;
- successor verification suite;
- migration authority/quorum;
- effective policy epoch.

For append-only logs, the bridge must retain enough evidence to verify predecessor history offline and verify that the successor population is semantically complete. A new Merkle root alone does not prove that every predecessor leaf was conserved exactly once.

Frozen invariants:

`FORMAT_MIGRATION != HISTORY_REWRITE`.

`SUCCESSOR_ROOT != COMPLETE_PREDECESSOR_COVERAGE_PROOF`.

Old checkpoints remain immutable historical claims; migration creates a successor generation with an authenticated bridge.

### RED-first cases

9. V1 leaf omitted during V2 rebuild but V2 root signed -> reject full migration;
10. V1 leaf duplicated in V2 -> reject conservation;
11. order-sensitive history reordered under new tree semantics -> reject unless semantics explicitly permit it;
12. predecessor proof verifies but predecessor trust root is revoked for compromise -> mark assurance degradation, do not silently repair;
13. old signature algorithm deprecated after historical signing -> historical verification may remain, but new consequential authorization follows current policy;
14. migration tool compromised and re-signs malicious successor root -> signature alone insufficient;
15. proof verifier supports V2 but not archived V1 -> migration is not independently auditable;
16. log service retired -> offline bundle must retain predecessor checkpoint/proofs/trust-root lineage.

## 3. Beacon transitive dependency graph and hidden common control

### Boundary

`N_NAMED_BEACONS != N_INDEPENDENT_FAILURE_DOMAINS`.

Independence must be evaluated over a transitive dependency graph, not brand/operator labels.

### Dependency graph

Relevant nodes/edges can include:

- legal/operator control;
- cloud account / region / host provider;
- network transit / DNS;
- time source;
- entropy source or upstream beacon;
- DKG/signing participants;
- build pipeline / artifact signer;
- HSM/KMS root;
- monitoring/alert authority;
- emergency governance authority;
- common software implementation.

Two beacons that appear organizationally distinct but ultimately share one KMS account, one build signer, one upstream randomness source, or one emergency operator have a correlated compromise path.

### Assurance calculation

Each beacon generation should carry dependency attestations scoped in time and version. The evaluator computes transitive closure to identify common-control cut sets. Unknown dependency edges do not count as independent by default.

Frozen boundary:

`SIGNED_DEPENDENCY_CLAIM != VERIFIED_INDEPENDENCE`.

A signed attestation proves who asserted the graph; assurance still depends on attestor authority, freshness, completeness, and independent measurement.

### RED-first cases

17. two beacons share one cloud/KMS root -> count one correlated control domain for that threat;
18. distinct operators use same upstream beacon -> detect common entropy dependency;
19. distinct build pipelines use same artifact signing root -> detect software-supply correlation;
20. dependency attestation omits time source -> completeness insufficient;
21. dependency changes mid-generation -> successor/delta required;
22. common emergency operator can disable both sources after reveal -> correlated availability/control;
23. one source's fallback silently consumes another source -> graph edge must be explicit;
24. attestor later compromised -> affected historical generations degrade, not rewrite.

## 4. Confidential commitment-key / pepper destruction and residual dictionary leakage

### Boundary

`SECRET_KEY_DESTROYED != COMMITMENT_PRIVACY_PROVEN`.

Destroying a pepper/HMAC key or encryption key can remove one attack path, but any surviving public or low-entropy-verifiable commitment may still support guessing.

### Threat model

Suppose a deleted confidential payload had one or more retained artifacts:

- unsalted deterministic hash;
- salted hash with public salt;
- keyed digest/HMAC with secret pepper;
- encrypted ciphertext;
- structured metadata that narrows candidate values;
- selective-disclosure proof or commitment;
- indexes/counts/timestamps correlated with the payload.

After payload deletion, privacy depends on which artifacts survive and their entropy/guessability properties.

For low-entropy domains, a public deterministic hash or public-salt digest can still permit offline dictionary testing. Destroying a separate pepper blocks verification only if no effective copy of that pepper remains. NIST SP 800-88r2's cryptographic-erase boundary is relevant: all usable wrapped/unwrapped/hierarchical key copies must be accounted for.

Frozen distinctions:

`PAYLOAD_UNRECOVERABLE != ATTRIBUTE_UNGUESSABLE`.

`PEPPER_DESTROYED != ALL_EFFECTIVE_PEPPER_COPIES_DESTROYED`.

`COMMITMENT_RETAINED_FOR_AUDIT != ZERO_PRIVACY_LEAKAGE`.

### Required deletion disposition

A deletion record should state, separately:

- payload disposition;
- encryption-key disposition and copy-domain coverage;
- pepper/commitment-key disposition and copy-domain coverage;
- retained commitment/proof types;
- candidate-domain leakage assessment;
- whether exact re-audit remains possible;
- whether only existence/timestamp/structural audit remains possible.

### RED-first cases

25. payload deleted, unsalted hash retained for 6-digit value -> dictionary leakage remains;
26. public salt retained for low-entropy value -> offline guessing remains possible;
27. HMAC commitment retained and all pepper copies destroyed -> verification path removed, but metadata leakage still assessed separately;
28. one backup contains old pepper -> crypto-erasure claim fails;
29. wrapped pepper survives under recoverable KEK -> destruction incomplete;
30. plaintext payload gone but deterministic index leaks category membership -> privacy not fully restored;
31. deletion removes evidence needed for exact re-audit -> mark `PAYLOAD_UNAVAILABLE_FOR_REAUDIT`;
32. commitment migration creates a fresh unkeyed digest of old secret -> may reintroduce dictionary leakage.

## 5. PQ/TLS resumption under ticket theft, partitions, and asymmetric upgrades

### Boundary

`TICKET_DECRYPTS != CURRENT_SESSION_AUTHORIZED`.

A ticket is a credential derived from predecessor state. Resumption must re-evaluate current policy and current endpoint/session context where those can change authorization.

### Ticket theft and replay

TLS 1.3 explicitly treats 0-RTT as replayable unless deployment/application mechanisms prevent harmful reuse. Distributed clusters with inconsistent anti-replay state can accept multiple copies during replication windows. Therefore consequential operations must not rely on ticket possession plus local replay-cache miss as sufficient authority.

Recommended state machine:

- `FULL_HANDSHAKE_AUTHENTICATED(policy_epoch=P, suite=S)`;
- ticket issued with predecessor policy/session binding;
- resumption attempt validates ticket authenticity/age plus current service identity/policy floor;
- if current policy is stricter, perform fresh compliant handshake or fail closed;
- 0-RTT only for explicitly replay-safe application operations;
- anti-replay ownership for a ticket is either globally consistent or assigned to exactly one authoritative zone;
- partition ambiguity disables consequential 0-RTT rather than weakening replay guarantees.

### Asymmetric PQ rollout

Client/server versions may diverge:

- upgraded server + legacy client;
- legacy server + upgraded client;
- mixed cluster behind one identity;
- stale resumption ticket issued before PQ/hybrid minimum policy;
- retry from PQ-capable node to legacy node.

Frozen invariant:

`RETRY_OR_RESUMPTION != AUTHORITY_TO_DOWNGRADE_CURRENT_CRYPTO_FLOOR`.

If current server policy requires a PQ/hybrid suite and the client cannot comply, the correct result is a fresh policy-compliant negotiation or failure. A classical-only predecessor ticket cannot silently authorize a new consequential session below the current minimum.

### RED-first cases

33. stolen ticket reused on second node with independent replay cache -> consequential 0-RTT rejected/fails safe;
34. partition splits replay state -> ticket has one authoritative zone or 0-RTT disabled;
35. original cluster accepts 0-RTT, second cluster falls back to 1-RTT, client/app retries operation -> deduplication/idempotency must prevent duplicate side effect;
36. ticket issued under classical-only P1, server now requires hybrid P2 -> fresh P2 handshake required;
37. mixed cluster: upgraded node rejects old floor, legacy node would accept -> routing/retry cannot bypass P2;
38. upgraded client offers hybrid, retry path strips offer -> transcript/policy downgrade detection;
39. server identity/certificate authorization changed since ticket issuance -> reevaluate current authorization, do not rely on ticket decryption alone;
40. replay cache restarts and loses recording window -> reject 0-RTT for the unsafe overlap window, consistent with TLS guidance.

## Cross-cutting state model

Across all five areas, the recurring pattern is the same:

1. distinguish **observation** from **authority**;
2. version authority and policy into authenticated generations;
3. conserve predecessor obligations exactly once across migration/reallocation;
4. preserve historical evidence without retroactively rewriting old claims;
5. count independent failure/control domains, not labels or process counts;
6. treat unknown completeness/partition state as insufficient evidence for consequential reuse;
7. re-evaluate current policy for new consequential operations even when historical credentials remain cryptographically valid.

## Implementation guidance for future RED/GREEN work

When exact executable source becomes available, encode these as explicit state-machine tests rather than prose-only assertions. Prefer deterministic file-backed/cluster-model regressions that preserve tampered/ambiguous state for inspection after fail-closed behavior. For any migration, test omission, duplication, replay, stale generation, partition, authority rollover, compromise, and restart separately.

This design evidence does not substitute for LAB-086 executable acceptance and must not change PR #165 draft/merge status.

## Sources

- etcd v3.5 failure modes: https://etcd.io/docs/v3.5/op-guide/failures/
- RFC 9162 Certificate Transparency v2: https://www.rfc-editor.org/rfc/rfc9162.html
- NIST IR 8213 draft, randomness beacon reference: https://csrc.nist.gov/pubs/ir/8213/ipd
- NIST SP 800-63B current 800-63-4 series: https://pages.nist.gov/800-63-4/sp800-63b.html
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- NIST SP 800-88r2: https://csrc.nist.gov/pubs/sp/800/88/r2/final
- RFC 8446 TLS 1.3: https://www.rfc-editor.org/rfc/rfc8446.html
- RFC 9846 TLS 1.3: https://www.rfc-editor.org/rfc/rfc9846.html
- RFC 9813 TLS-PSK operational considerations: https://www.rfc-editor.org/rfc/rfc9813.html
