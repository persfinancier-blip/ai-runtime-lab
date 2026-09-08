# Source inventory authority key lifecycle, source identity rotation, frontier freshness, and ingestion-promise issuer independence — V1 FROZEN

Date: 2026-09-08
Status: `SOURCE_INVENTORY_AUTHORITY_KEY_LIFECYCLE_SOURCE_IDENTITY_ROTATION_FRONTIER_FRESHNESS_PROMISE_INDEPENDENCE_V1_FROZEN`
Parent: LAB-093 / #178

## Question

The preceding ingestion-completeness contract introduced an authenticated `EventSourceInventoryV1`, per-source event/frontier signatures, and `IngestionPromiseV1`. This follow-up closes four remaining authority gaps:

1. how source-inventory authority keys rotate/revoke without rewriting safe history;
2. how a logical source changes key/epoch without being treated as a new source and silently shrinking the completeness denominator;
3. how stale/replayed source frontiers are rejected after monitor catch-up or key rotation;
4. how inclusion promises remain evidentiary when the log producer itself is compromised.

## Primary boundary

The following are deliberately not equivalent:

`VALID_SIGNATURE != CURRENT_AUTHORITY != SAME_LOGICAL_SOURCE != FRESH_FRONTIER != INDEPENDENT_INGESTION_OBLIGATION`

A cryptographically valid object may be signed by a retired/compromised key, may identify a replacement key for the wrong logical source, may replay an old frontier, or may be an inclusion promise produced by the same compromised actor whose omission it is meant to prove.

## Donors and mechanisms

### TUF root rotation

TUF root metadata requires sequential trust continuity. A new root version is verified by a threshold of the previously trusted root and a threshold of the new root, while version monotonicity prevents rollback. This is a strong donor for source-inventory authority rotation: a successor inventory authority must not self-authorize or skip generations.

Source: The Update Framework specification, root update workflow: https://theupdateframework.github.io/specification/

### SPIFFE identity and bundle rotation

SPIFFE explicitly binds public verification material to a trust-domain identity; bundle contents rotate over time while the trust-domain identity remains stable. Federation guidance recommends publishing new keys before use so downstream validators can disseminate them. This is the relevant donor for separating a stable logical source identity from rotating source verification keys.

Sources:
- https://spiffe.io/docs/latest/spiffe-specs/spiffe_trust_domain_and_bundle/
- https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/

### NIST SP 800-57 key lifecycle

NIST distinguishes private signing-key cryptoperiod from the longer period during which corresponding public verification keys may need to remain available to validate historical signatures. This supports retaining historical source/inventory verification material after retirement while separately marking compromise intervals.

Source: NIST SP 800-57 Part 1 Rev.3: https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-57p1r3.pdf

### Certificate Transparency inclusion promises and monitors

RFC 9162 makes the log's signed timestamp an accountable promise to include an accepted object and relies on monitors/auditors to detect violations. The useful mechanism is not that the log is magically trusted, but that a retained signed promise can later be checked against an independently observed log history.

Source: RFC 9162: https://www.rfc-editor.org/rfc/rfc9162.html

### SCITT issuer vs transparency-service separation

RFC 9943 explicitly separates an Issuer-signed Statement from the Transparency Service receipt proving registration. Issuer and TS may both be compromised, and relying parties choose which issuers/TSs to trust. This is the donor for keeping source/event authority, ingestion-promise authority, and transparency registration authority as distinct roles.

Source: RFC 9943: https://www.rfc-editor.org/rfc/rfc9943.html

## Frozen contract

### 1. Stable logical source identity is not a key ID

Define:

`LogicalEventSourceIdV1`
- `source_id`
- immutable source namespace / role class
- source-owner/control-domain identity
- bootstrap lineage identifier
- allowed event classes
- sequence semantics: `CONTIGUOUS | SPARSE | EXTERNAL_ORDERED`

A signing key, certificate, workload instance, hostname, pod UID, process ID, or deployment generation is never the logical source identity by itself.

Invariant:

`SOURCE_KEY_ROTATION != SOURCE_RETIREMENT != NEW_LOGICAL_SOURCE`

Rotating keys for source `S` preserves `S` in the required-source denominator.

### 2. Source identity authority is generation-ordered

Define `SourceIdentityAuthorityV1`:

- `source_id`
- `authority_generation`
- active verification keys + threshold
- validity/issuance interval
- predecessor authority digest
- successor-transition digest when known
- status: `ACTIVE | RETIRED | COMPROMISED | UNKNOWN_HISTORICAL_TRUST`
- compromise interval when known
- allowed event/frontier classes

A normal `g -> g+1` transition requires authorization by the threshold defined in generation `g` and by the threshold defined in generation `g+1`, over the same canonical transition payload.

Skipped generation, self-authorized replacement, or same-generation/different-content transition is rejected.

### 3. Inventory authority is separate from source authority

Define `EventSourceInventoryAuthorityV1` separately from each `SourceIdentityAuthorityV1`.

The inventory authority decides membership of the required-source denominator. A source authority proves events/frontiers for one already-governed logical source. A source cannot sign itself out of the inventory.

Invariant:

`SOURCE_CONTROL != DENOMINATOR_CONTROL`

Source retirement from `EventSourceInventoryV1` requires inventory-authority authorization plus `SourceRetirementProofV1` showing a final authenticated frontier and zero unresolved ingestion obligations.

### 4. Inventory authority rotation cannot rewrite membership history

Inventory-authority rotation follows sequential predecessor+successor threshold authorization and monotonic generation.

Historical inventory snapshots remain verifiable under retained public verification material. Retirement of an inventory-authority private key does not retroactively invalidate correctly signed historical inventories.

If a key is later known compromised from time `Tc`, artifacts issued before a proven-safe boundary may remain valid; artifacts whose issuance falls in the affected interval become `UNKNOWN_OR_COMPROMISED_INVENTORY_AUTHORITY` according to policy. If compromise onset is unknown, dependent history cannot be silently upgraded to trusted.

### 5. Source key rotation must bind old and new keys to the same logical source

Define `SourceIdentityRotationV1`:

- logical `source_id`
- old authority generation/digest
- new authority generation/digest
- old threshold signatures
- new threshold signatures
- inventory generation/digest under which the source remains required
- last accepted old-epoch frontier
- first permitted new-epoch sequence semantics
- canonical transition nonce/digest

The new key material cannot merely claim `source_id=S`; continuity must be proven from the currently trusted source authority and cross-checked against the current required-source inventory.

This blocks denominator laundering by replacing `S-old` with attacker-created `S-new` and pretending the previous obligations disappeared.

### 6. Epoch changes never erase unresolved obligations

A new source epoch starts only after the previous epoch's terminal frontier is authenticated or explicitly marked unresolved.

All unresolved promises, gaps, partitions, or contradiction evidence from old epoch `e` are carried into the coverage ledger for epoch `e+1` until discharged.

Invariant:

`NEW_EPOCH != CLEAN_SLATE`

If old epoch termination cannot be proved, state is `SOURCE_EPOCH_TRANSITION_WITH_UNKNOWN_PREDECESSOR_FRONTIER` and semantic completeness cannot be proven.

### 7. Frontier freshness is local-state monotonic, not wall-clock-only

Define `SourceFrontierStatementV1` with:

- `source_id`
- source authority generation
- source epoch
- frontier sequence/order token
- predecessor frontier digest
- covered event-chain digest
- issuance nonce/epoch context where applicable
- signer set / signatures

Each verifier/monitor stores `TrustedSourceFrontierV1`:

- highest accepted source authority generation
- highest accepted epoch
- highest accepted frontier/order token for contiguous sources
- last frontier digest
- unresolved gap set

Rules:

- lower generation -> rollback reject;
- lower epoch -> rollback reject;
- same generation/epoch/frontier with different digest -> equivocation;
- for contiguous sources, lower sequence -> rollback reject;
- for sparse/external-ordered sources, freshness uses the source contract's order token/predecessor chain rather than fabricated integer contiguity;
- wall-clock timestamp alone never makes a frontier fresher.

### 8. Catch-up after monitor loss must recover authority continuity before frontier continuity

After monitor loss, restore in this order:

1. current inventory-authority generation and chain;
2. current source-inventory generation and membership;
3. source-identity authority chains for every required source;
4. retained trusted source frontiers;
5. promise obligations and unresolved gaps;
6. current source frontiers;
7. log/checkpoint coverage.

A monitor must not accept a fresh-looking frontier signed by a new source key before validating the rotation chain that binds that key to the already-required logical source.

### 9. Ingestion promises require role separation

`IngestionPromiseV1` is evidence against omission only if its issuing authority cannot be silently rewritten by the same single failure domain that controls the append-only log and its completeness claim.

Define `IngestionPromiseAuthorityV1` separately from `TransparencyLogAuthorityV1`.

High-assurance profile requires at least one of:

A. source-held submission receipt: the logical source signs the event/submission digest, and an independently keyed admission service countersigns the accepted obligation;

B. threshold admission authority: promise issuance requires signatures from independent control/key-custody domains, at least one outside the log producer's direct mutation domain;

C. externally witnessed promise: producer signs promise, which is durably registered with an independent transparency/witness service before being treated as a completeness obligation.

A promise signed only by the compromised log producer remains useful for accountability if retained externally, but it is not sufficient to prove absence of selectively suppressed promises.

### 10. Promise suppression and promise forgery are distinct failures

Possible states:

- `PROMISE_VALID_AND_PENDING`
- `PROMISE_FULFILLED`
- `PROMISE_DEADLINE_MISSED_OMISSION_PROVEN`
- `PROMISE_AUTHORITY_COMPROMISED`
- `PROMISE_REGISTRATION_MISSING`
- `PROMISE_SUPPRESSION_SUSPECTED_NOT_PROVEN`
- `PROMISE_EQUIVOCATION_PROVEN`

No promise observed is not equivalent to no submission accepted. Positive evidence may come from source-signed submission records, network/admission receipts, replicated queue state, or independent witnesses.

### 11. Promise-authority lifecycle is independently versioned

`IngestionPromiseAuthorityV1` has generation, threshold, issuance interval, predecessor digest, compromise/retirement status and freshness policy.

Rotation uses predecessor+successor authorization. Historical valid promises retain their verification material after private-key retirement. Compromise intervals affect only the evidence whose trust actually depends on the compromised authority state.

### 12. Producer and promise authority may share infrastructure only as an explicitly lower-assurance profile

Co-location is not forbidden, but its security claim must be weaker.

Profiles:

- `P0_SELF_PROMISE`: log producer is sole promise issuer. Detects violation of retained promises but cannot robustly detect selective non-issuance/suppression.
- `P1_SEPARATE_KEYS_SAME_CONTROL`: distinct keys/processes, same operator/control domain. Protects against some accidental faults, weak against operator compromise.
- `P2_INDEPENDENT_ADMISSION`: at least one promise/admission signer outside log mutation/control domain.
- `P3_MULTI_DOMAIN_WITNESSED`: threshold independent admission plus external transparency/witness registration.

Completeness verdicts must record which profile supported them.

## Failure / contradiction classes

Freeze the following proof classes:

1. `INVENTORY_AUTHORITY_ROLLBACK`
2. `INVENTORY_AUTHORITY_EQUIVOCATION`
3. `INVENTORY_AUTHORITY_COMPROMISE_INTERVAL`
4. `SOURCE_IDENTITY_SELF_AUTHORIZED_ROTATION`
5. `SOURCE_IDENTITY_ROTATION_CHAIN_GAP`
6. `SOURCE_DENOMINATOR_LAUNDERING`
7. `SOURCE_EPOCH_PREDECESSOR_UNKNOWN`
8. `SOURCE_FRONTIER_ROLLBACK`
9. `SOURCE_FRONTIER_EQUIVOCATION`
10. `SOURCE_FRONTIER_AUTHORITY_STALE`
11. `PROMISE_AUTHORITY_ROLLBACK`
12. `PROMISE_AUTHORITY_EQUIVOCATION`
13. `PROMISE_AUTHORITY_COMPROMISE_INTERVAL`
14. `PROMISE_LOG_SINGLE_DOMAIN_COLLAPSE`
15. `PROMISE_DEADLINE_OMISSION`
16. `PROMISE_SUPPRESSION_EVIDENCE_CONFLICT`

## RED-first matrix

At minimum the implementation gate must contain these 48 cases.

### Inventory authority lifecycle
1. valid `g -> g+1` predecessor+successor rotation accepted;
2. successor-only self-authorization rejected;
3. predecessor-only transition rejected;
4. skipped generation rejected;
5. lower generation replay rejected;
6. same generation/different payload equivocation detected;
7. retired key verifies safe historical inventory;
8. compromised-period inventory does not silently remain trusted.

### Source identity rotation
9. valid old+new rotation preserves same `source_id` denominator membership;
10. new key claiming same ID without continuity rejected;
11. replacement with new logical ID cannot satisfy old source obligations;
12. source cannot self-retire from inventory;
13. inventory-authorized retirement with unresolved promise rejected;
14. retirement with unresolved gap rejected;
15. clean final frontier + inventory retirement accepted;
16. retired source resurrection requires explicit new inventory transition, not heartbeat appearance.

### Epoch/frontier freshness
17. clean old-epoch terminal frontier -> new epoch accepted;
18. unknown old terminal frontier -> new epoch completeness remains UNKNOWN;
19. lower authority generation frontier rejected;
20. lower epoch frontier rejected;
21. lower contiguous sequence rejected;
22. same frontier token/different digest equivocation;
23. sparse source integer gap does not fabricate omission;
24. sparse source predecessor/order rollback still rejected;
25. wall-clock-newer but frontier-older statement rejected;
26. stale monitor cannot accept newest frontier before authority-chain catch-up;
27. restored snapshot with lower trusted frontier detected;
28. unresolved old-epoch obligation survives key rotation.

### Promise authority independence
29. retained independent promise + missed deadline proves omission;
30. self-promise-only profile records weaker assurance;
31. compromised producer cannot forge independent admission signature;
32. compromised producer suppressing its own promise cannot yield `COMPLETE_PROVEN` absent independent evidence;
33. same-control distinct keys classified P1, not P2;
34. independent admission signer classified P2;
35. multi-domain witnessed promise classified P3;
36. promise authority rotation requires predecessor+successor thresholds;
37. stale promise-authority generation rejected;
38. same-generation conflicting promise-authority metadata detected;
39. historical promise remains verifiable after planned private-key retirement;
40. promise inside known compromise interval downgraded/invalidated by policy.

### Catch-up / crash / contradictions
41. crash after source-rotation authorization but before inventory persistence cannot split logical identity;
42. crash after inventory update but before source frontier acceptance resumes idempotently;
43. monitor gap reconstructs inventory authority before source frontiers;
44. missing authority-chain generation blocks catch-up completion;
45. conflicting source and inventory rotation records produce conflict, not LWW;
46. promise says accepted while producer says never admitted -> contradiction retained;
47. source says submitted but no independent admission receipt -> suspicion/UNKNOWN, not fabricated omission proof;
48. late discovery of old-epoch promise reopens prior completeness verdict through monotonic invalidation generation.

## Implementation implications

No production refactor is authorized by this freeze alone. When exact execution becomes available, tests should be introduced before code and composed with the already frozen source-ingestion, checkpoint, continuous-assurance, convergence, recovery, and LAB-087 process-isolation contracts.

Likely minimal types:

- `LogicalEventSourceIdV1`
- `SourceIdentityAuthorityV1`
- `SourceIdentityRotationV1`
- `EventSourceInventoryAuthorityV1`
- `TrustedSourceFrontierV1`
- `IngestionPromiseAuthorityV1`
- `PromiseAssuranceProfileV1`

The key implementation invariant is that authority, membership, identity continuity, freshness, and evidence independence are separate checks and must not collapse into a single `signature_valid` boolean.

## Decision summary

Freeze:

`SOURCE_KEY_ROTATION != NEW_SOURCE`

`SOURCE_CONTROL != DENOMINATOR_CONTROL`

`NEW_EPOCH != CLEAN_SLATE`

`NEWER_TIMESTAMP != FRESHER_FRONTIER`

`LOG_SIGNATURE != INDEPENDENT_COMPLETENESS_PROMISE`

`VALID_SIGNATURE != CURRENT_AUTHORITY != SAME_LOGICAL_SOURCE != FRESH_FRONTIER != INDEPENDENT_INGESTION_OBLIGATION`

The next distinct unresolved layer is **source/promise authority transparency and compromise-notification propagation**: how relying monitors learn a key compromise or authority revocation quickly enough, how conflicting authority views are detected, and how a previously accepted completeness verdict is invalidated when the compromise notice arrives after the fact without rewriting historical receipts.