# Replica authority recovery, receipt-key recovery, challenge provenance, destruction negative-space, and PQ supply-chain downgrade resistance — V1

Date: 2026-09-09
Status: `REPLICA_RECOVERY_RECEIPT_KEY_RECOVERY_CHALLENGE_PROVENANCE_DESTRUCTION_NEGATIVE_SPACE_PQ_SUPPLY_CHAIN_V1_FROZEN`
Scope: design/evidence freeze only. This does **not** substitute for executable RED/GREEN validation on LAB-086 or LAB-093..100.

## Why this exists

The preceding freeze established authority epochs and anti-replay for replica audits, witness/gossip survivability for receipt promises, confidential re-audit independence, destruction-inventory anti-omission, and PQ rollback protection. Five consequential gaps remained:

1. recovery of the replica-audit authority itself after compromise without accepting an attacker-chosen successor or rolling policy backward;
2. receipt-log signing-key rollover and witness compromise recovery while old accepted promises remain independently auditable;
3. challenge-generator provenance, anti-bias, and leakage accounting so a nominally secret/independent audit population cannot be adversarially selected;
4. source-authority compromise and negative-space coverage for destruction inventories, including copy domains that no single inventory source knows about;
5. supply-chain provenance for PQ migration attestations, verifier implementation compromise, and downgrade-resistant algorithm-negotiation transcripts.

## Primary donors

- RFC 9162, Certificate Transparency Version 2.0: signed tree heads, log identity, consistency proofs, SCT acceptance promises, MMD-bounded inclusion, auditing, and signed evidence of log misbehavior. https://www.rfc-editor.org/rfc/rfc9162.html
- NIST SP 800-57 Part 1 Rev. 5: cryptographic-key lifecycle, compromise, recovery, replacement, backup/archive handling, trust anchors, and separation of originator/recipient usage. https://doi.org/10.6028/NIST.SP.800-57pt1r5
- NIST SP 800-131A Rev. 2: explicit transition from weaker/retired cryptographic algorithms to stronger algorithms rather than silent verifier reinterpretation. https://doi.org/10.6028/NIST.SP.800-131Ar2
- NIST FIPS 203/204/205 and NIST PQC publications: ML-KEM, ML-DSA, and SLH-DSA are standardized PQ primitives; migration remains a lifecycle and system-integration problem, not merely primitive availability. https://csrc.nist.gov/projects/post-quantum-cryptography/publications
- NIST SP 800-227 final (September 2025): current KEM usage guidance and an additional reminder that secure migration depends on correct protocol/system composition around the primitive. https://csrc.nist.gov/pubs/sp/800/227/final
- NIST IR 8547 initial public draft: explicit transition planning for quantum-vulnerable standards and future disallow boundaries. https://csrc.nist.gov/pubs/ir/8547/ipd

## 1. Replica-audit authority recovery quorum and rollback protection

### Frozen boundary

`SUCCESSOR_AUTHORITY_KEY != RECOVERED_AUTHORITY`

After compromise, merely publishing a new authority key does not prove that the legitimate authority recovered. A compromised incumbent can sign an attacker-selected successor. Recovery therefore requires a path whose decisive authorization is not wholly controlled by the compromised epoch.

### ReplicaAuditRecoveryRecord

Every authority recovery MUST bind at least:

- compromised `authority_id` and `authority_key_epoch`;
- authenticated compromise-effective interval/boundary and its adjudication evidence;
- predecessor authority policy digest;
- successor authority identity/key epoch;
- successor policy digest;
- recovery quorum population, denominator, threshold, and membership epoch;
- exact recovery payload digest;
- independent recovery signatures/attestations;
- effective-from boundary;
- explicit statement of which predecessor audits are degraded, retained as historical-only, or require re-audit;
- anti-rollback floor: minimum accepted authority-policy generation and algorithm suite.

### Recovery quorum

Recovery quorum MUST be defined before compromise and before successor selection whenever possible. Members MUST be independent of the ordinary authority key/control plane to the degree required by policy.

If the normal authority is compromised, its signature MAY be retained as historical/cooperation evidence, but MUST NOT be sufficient to authorize its own clean successor.

Historical recovery quorum is evaluated against the recovery-policy denominator active for that recovery event. Later denominator shrink cannot retroactively validate an under-quorum recovery.

### Rollback protection

Every verifier MUST retain/authenticate a monotonic minimum recovery-policy generation. A successor record that proposes:

- an older authority policy;
- a weaker recovery threshold;
- a previously retired authority key;
- a weaker crypto suite after a disallow boundary;
- or an earlier effective boundary that would reactivate compromised evidence

is `AUTHORITY_RECOVERY_ROLLBACK_REJECTED` unless a separately defined higher-root/emergency process explicitly authorizes that downgrade and records the degraded assurance class.

### Compromise ambiguity

If compromise effective time cannot be ordered precisely enough, current consequential reliance on audits from the ambiguous interval fails closed. Recovery does not manufacture a precise historical boundary merely because a new authority exists.

`RECOVERY_COMPLETE != HISTORICAL_AMBIGUITY_RESOLVED`

## 2. Receipt-log key rollover and witness-compromise recovery

### Frozen boundary

`LOG_KEY_ROLLOVER != PROMISE_REBIND`

A receipt promise accepted under log identity/key epoch K1 remains a promise under K1's historical lineage. A K2 successor may maintain the log, but cannot make an old K1 receipt become a K2-origin receipt or erase the verification obligations attached to K1.

### LogKeyTransitionRecord

Normal rollover MUST authenticate:

- stable logical log identity (if continuity is intended);
- predecessor key epoch and successor key epoch;
- exact transition boundary;
- predecessor checkpoint/tree size/root;
- successor initial checkpoint/tree ancestry relation;
- outstanding promise set/frontier or a cryptographic commitment sufficient to prove their preservation;
- witness policy epoch and quorum approving/observing transition;
- algorithm-policy transition and anti-rollback floor.

If continuity cannot be proved, the successor is a new log identity and outstanding old-log promises require an explicit cross-log migration object rather than implicit rebinding.

### Old-promise survivability

For each pre-rollover acceptance promise, the system MUST retain enough authenticated evidence to determine one of:

- fulfilled under old lineage before transition;
- fulfilled under a valid continuity-preserving successor after transition;
- migrated through an authenticated cross-log supersession preserving the original obligation;
- violated/unfulfilled.

Deleting old verification keys/checkpoints before all such promises become independently decidable is not acceptable retirement.

### Witness compromise

Witness signatures establish observations under a witness-policy epoch; they are not eternal truth.

If a witness epoch is compromised later:

- checkpoints signed before a provable compromise boundary remain historical evidence under the frozen policy;
- checkpoints in the ambiguous/compromised interval lose current consequential eligibility as specified by policy;
- a clean successor witness epoch cannot rewrite old denominators or erase conflicting checkpoints already observed;
- previously gossiped incompatible signed views remain positive evidence even if one signer is later revoked.

### Witness recovery

Witness-set recovery requires an authenticated successor membership epoch. Same identifier with a new key is not sufficient unless continuity is explicitly authorized. Historical quorum remains tied to old membership; future checkpoints use the successor denominator.

`WITNESS_RECOVERED != OLD_EQUIVOCATION_ERASED`

## 3. Confidential challenge-generator provenance, anti-bias, and leakage accounting

### Frozen boundary

`SECRET_CHALLENGE != UNBIASED_CHALLENGE`

A challenge set can remain confidential yet be adversarially selected to avoid difficult cases. Confidentiality and sampling integrity are separate properties.

### ChallengeGenerationRecord

Each consequential challenge generation MUST bind:

- generator implementation/version and build/provenance digest;
- exact source population/corpus root and eligibility predicate;
- sampling/selection algorithm and policy;
- randomness-source identity/epoch and committed seed material or verifiable derivation;
- exclusions and their authenticated reasons;
- challenge-generation time/epoch;
- generated challenge commitments/root;
- access-control policy for plaintext challenges;
- all authorized disclosures and leakage events.

### Commit-before-selection influence

Where unpredictable sampling matters, the generator's eligible population and algorithm MUST be committed before final randomness becomes knowable to a party that can bias the population. Conversely, randomness SHOULD be unavailable to population curators until the eligible population commitment is fixed.

A challenge authority that can both choose the population after seeing randomness and control the randomness has no meaningful anti-bias guarantee even when output commitments are valid.

### Independence

Multiple challenge-generator signatures do not prove independence if they share one codebase, one curator, one randomness authority, or one control domain. Policy MUST state the independence dimensions being counted.

### Leakage accounting

Leakage is monotonic historical evidence. Every event that exposes challenge plaintext or enough metadata to materially reduce uncertainty MUST be recorded against the affected challenge generation:

- intended auditor/evaluator reveal;
- operator/debug access;
- threshold-escrow share exposure;
- logging/telemetry exposure;
- partial corpus identifiers that reveal selected cases;
- pre-deadline compromise of a sufficient custodian set.

A later clean run can create a new generation, but cannot mark the leaked predecessor as "never leaked".

`NO_PUBLIC_LEAK_OBSERVED != CHALLENGE_SECRECY_INTACT`

### Anti-overfitting boundary

If a challenge generation is reused beyond the policy-defined exposure/reuse budget, its assurance degrades even without a known compromise. Repeated evaluations can reveal enough information to tune specifically to the hidden set.

## 4. Destruction-inventory source-authority compromise and negative-space coverage

### Frozen boundary

`INVENTORY_SOURCE_AUTHENTIC != INVENTORY_COMPLETE`

A signed backup catalog or snapshot API proves what that source says. It does not prove that all copy-generating systems are represented, nor that the source was uncompromised for the whole relevant interval.

### InventorySourceEpoch

Every source feeding a destruction inventory MUST identify:

- source authority/system identity;
- key/attestation epoch;
- source type (backup controller, snapshot catalog, HSM export log, cloud replica inventory, archive registry, etc.);
- scope: which assets/accounts/regions/media/classes it can observe;
- completeness semantics and known exclusions;
- retention window;
- compromise/degradation state;
- immutable query/export evidence or authenticated frontier used by the inventory generation.

### Negative-space coverage

Complete destruction requires coverage of **where copies could have been created**, not only where copies were found.

Define a `CopyDomainUniverse` from independent configuration/control evidence such as:

- storage and backup policy definitions;
- infrastructure/account/region inventory;
- snapshot/replication configuration;
- disaster-recovery topology;
- HSM/secret-manager wrapping/export capability configuration;
- archive/tape/media lifecycle systems;
- software paths capable of local cache/export;
- third-party/provider managed retention classes;
- historical configuration changes covering the material lifetime.

A source can prove negative evidence only inside its authenticated scope. If a material could have existed in a domain not covered by any qualifying source, all-copy destruction remains unproven.

### Source compromise

If an inventory source is later proven compromised:

- evidence after the compromise boundary is untrusted for positive/negative claims unless independently corroborated;
- an ambiguous compromise interval degrades any completeness claim materially dependent on that source;
- successor clean exports do not reconstruct historical negative space that the compromised source might have hidden;
- independent overlapping sources can preserve a claim only if their authenticated scopes actually cover the missing domain/time interval.

### Discovery frontier

The final destruction claim MUST bind a coverage matrix:

`copy-domain class × time interval × inventory source(s) × completeness property × destruction evidence`

Any uncovered cell is explicit `NEGATIVE_SPACE_UNCOVERED`, not silently treated as empty.

## 5. PQ migration-attestation supply-chain provenance and negotiation downgrade resistance

### Frozen boundary

`VALID_PQ_SIGNATURE != TRUSTED_MIGRATION_IMPLEMENTATION`

Cryptographic validity says a key produced/verified a signature according to an algorithm. It does not prove the migration tool, parser, canonicalizer, verifier, dependency graph, or algorithm-selection logic faithfully represented the intended semantic object and policy.

### MigrationImplementationAttestation

Consequential PQ migration/renewal SHOULD bind:

- migration tool identity/version;
- source/build provenance and artifact digest;
- parser/canonicalizer version;
- cryptographic library/provider versions;
- dependency/SBOM or equivalent component manifest appropriate to assurance level;
- runtime/platform identity where relevant;
- verifier implementation identity/version;
- policy-engine version;
- independently produced verification result(s) where required;
- exact predecessor/successor semantic payload digests;
- algorithm negotiation transcript/policy inputs;
- effective migration/deprecation boundary.

A signature from a trusted key over a payload emitted by a compromised migration tool can still bind the wrong payload.

### Verifier compromise

If a verifier implementation is found to accept invalid proofs/signatures or parse/canonicalize incorrectly:

- affected verification generations are marked degraded by implementation/version and interval;
- re-verification with a clean implementation creates a new verification generation;
- prior decisions are not silently rewritten; consequential reliance follows policy for the degraded predecessor;
- multiple processes using the same vulnerable library count as one correlated verifier failure domain.

`REVERIFY_CLEAN != PREVIOUS_DECISION_NEVER_HAPPENED`

### Algorithm-negotiation transcript

When peers or components negotiate algorithm/hybrid choices, the consequential evidence MUST bind the offered sets and selected result, not only the final algorithm identifier.

At minimum bind:

- initiator supported/allowed algorithm set and policy generation;
- responder supported/allowed algorithm set and policy generation;
- required hybrid combiner semantics;
- selected algorithm(s)/parameters;
- transcript nonce/session identity;
- policy/deprecation effective boundary;
- authenticated negotiation result.

This prevents an attacker from stripping stronger/PQ options and leaving a valid-looking weak selection without evidence of the downgrade.

### Downgrade classification

- Strong/PQ option offered by both sides and policy requires it, but transcript selects weaker algorithm -> `NEGOTIATION_DOWNGRADE_REJECTED`.
- PQ option unavailable to one side and exact policy permits temporary classical fallback -> allowed only in the explicitly weaker assurance class and before the authenticated sunset boundary.
- Archived legacy negotiation used only to verify what historically happened -> historical verification may be allowed.
- Archived legacy transcript reused to authorize a new post-sunset action -> policy rollback reject.

### Current standards note

As of this freeze, NIST has final FIPS 203/204/205 for ML-KEM/ML-DSA/SLH-DSA and final SP 800-227 for KEM usage. NIST's PQC project also selected HQC for future standardization as a backup KEM based on a different mathematical family. The engineering conclusion is not "support every algorithm"; it is to make algorithm/policy transition, implementation provenance, and downgrade behavior explicit and auditable.

## 6. Frozen RED-first matrix

### A. Replica authority recovery / rollback (8)

1. compromised authority signs its own successor with no independent recovery quorum -> reject;
2. predeclared independent recovery quorum authorizes successor with exact compromise/policy lineage -> eligible;
3. recovery below historical denominator, then denominator later shrinks -> historical recovery remains invalid;
4. successor proposes older authority policy generation -> rollback reject;
5. successor proposes retired authority key -> rollback reject;
6. ambiguous compromise interval -> current reliance on affected audits fails closed;
7. clean successor audit restores future eligibility -> predecessor ambiguity remains historical;
8. higher-root emergency downgrade explicitly recorded -> only declared degraded assurance class, never silent normal recovery.

### B. Receipt key rollover / witness recovery (8)

9. K1->K2 transition with exact predecessor checkpoint, ancestry, outstanding-promise commitment and quorum -> continuity eligible;
10. K2 appears with no authenticated K1 transition -> treat as new log identity;
11. pre-K2 promise fulfilled under continuity-preserving K2 ancestry -> accept fulfillment while preserving K1 origin;
12. old verification material deleted with undecidable outstanding promises -> retirement incomplete;
13. witness compromised after provably earlier checkpoint -> preserve historical checkpoint under frozen policy;
14. checkpoint in ambiguous witness-compromise interval -> consequential reliance degraded/fail closed;
15. successor witness epoch tries to recount old checkpoint under smaller denominator -> reject;
16. old conflicting signed checkpoints survive witness retirement -> equivocation evidence retained.

### C. Challenge provenance / anti-bias / leakage (8)

17. population committed before randomness, generator provenance valid, unbiased policy followed -> eligible;
18. curator changes population after learning seed -> bias reject;
19. generator controls both population and hidden seed with no independent constraint -> independence claim reject;
20. valid challenge commitments but generator artifact provenance mismatches approved version -> reject;
21. pre-deadline debug/logging exposure reveals challenge plaintext -> leakage recorded/degrade;
22. no public leak observed but threshold custodians sufficient to reconstruct were compromised -> secrecy compromised;
23. repeated reuse exceeds exposure budget -> assurance degraded;
24. clean successor generation after leakage -> future eligible, leaked predecessor unchanged.

### D. Destruction negative space / source compromise (8)

25. all discovered copies destroyed but one copy-domain class has no qualifying inventory source -> no all-copy claim;
26. signed backup catalog is complete only for one account/region while material could exist elsewhere -> incomplete;
27. overlapping independent sources cover source-compromise interval and exact scope -> claim may survive if policy threshold met;
28. sole negative-evidence source compromised during relevant interval -> completeness degraded;
29. successor source export after recovery attempts to prove historical absence -> reject unless historical evidence exists;
30. coverage matrix contains uncovered time interval -> `NEGATIVE_SPACE_UNCOVERED`;
31. configuration history proves a domain/capability did not exist during material lifetime -> valid negative-space exclusion;
32. later discovered previously unknown domain -> prior completeness claim degraded, new destruction restores future state only.

### E. PQ supply chain / verifier / negotiation (8)

33. PQ signature valid but migration artifact digest/provenance mismatches approved tool -> reject trusted-migration claim;
34. two verifier processes share same vulnerable library -> one correlated failure domain;
35. clean independent verifier re-verifies old evidence after verifier compromise -> new verification generation only;
36. parser/canonicalizer version changes semantic payload despite signature validity -> migration reject;
37. both peers offered required PQ/hybrid choice but transcript selects classical-only -> downgrade reject;
38. one peer lacks PQ and policy explicitly permits temporary fallback before sunset -> accept weaker classified mode only;
39. same fallback after authenticated sunset boundary -> reject;
40. archived historical classical transcript reused as authorization for new post-sunset operation -> rollback/downgrade reject.

## 7. Implementation direction

These contracts belong in tests before production refactors. Do not implement five new authorities ad hoc inside LAB-093. Prefer immutable/versioned evidence records with explicit membership/policy epochs and degradation states.

The most important cross-cutting rule is:

`RECOVERY OR MIGRATION CREATES A SUCCESSOR GENERATION; IT DOES NOT REWRITE THE PREDECESSOR.`

That rule applies uniformly to replica audit authorities, receipt-log keys/witness sets, confidential challenge generations, destruction inventory generations, and PQ verifier/migration attestations.

## 8. Relationship to LAB-086

This freeze is a safe fallback because exact LAB-086 execution remains unavailable in the current runtime. It does not change LAB-086 acceptance criteria, does not authorize PR #165 to leave draft, and does not claim any new behavioral or compile PASS.

The next executable priority remains the exact LAB-086 real-ledger closure as recorded in `state/CURRENT.md`.