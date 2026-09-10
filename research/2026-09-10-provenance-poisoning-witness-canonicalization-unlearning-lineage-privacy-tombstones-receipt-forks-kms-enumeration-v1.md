# Provenance poisoning, witness canonicalization, unlearning lineage, privacy tombstones, receipt forks, and authority-domain enumeration

Date: 2026-09-10
Status: DESIGN FROZEN / RED-FIRST; **not executable proof**
Contract: `PROVENANCE_POISONING_WITNESS_CANONICALIZATION_UNLEARNING_PRIVACY_TOMBSTONE_RECEIPT_FORK_KMS_ENUMERATION_V1_FROZEN`

## Why this slice exists

LAB-086 remains priority #1. This run re-read `AGENTS.md`, `state/CURRENT.md`, and `prompts/SELF_RESUME.md`, inspected current open issues/PRs, and re-probed exact source materialization. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.

The GitHub connector can read/write repository state, but there is still no supported non-model connector-to-local-filesystem primitive that preserves pinned executable bytes for the retained LAB-086 gate. Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or branch/main conflict PASS is claimed here, and PR #165 remains draft.

This note executes the distinct fallback named in `state/CURRENT.md`. It extends the LAB-093-family authority/provenance model; it does not substitute for later executable RED/GREEN proof.

## Primary donors / facts

1. **SLSA v1.1 threat model** explicitly treats false provenance as a first-class threat: an attacker may get a trusted control plane to sign false provenance, so provenance correctness depends not merely on a signature but on who generated each field and whether the trusted builder/control plane itself is within the accepted trust boundary. https://slsa.dev/spec/v1.1/threats
2. **Sigstore threat model / Rekor security model** distinguishes cryptographic existence/transparency evidence from policy correctness and notes that compromise of identity providers, Fulcio, Rekor, monitors, or the TUF root changes what can be trusted. Long-term trust in a transparency log requires monitoring/auditing, not signature verification alone. https://docs.sigstore.dev/about/threat-model/ and https://docs.sigstore.dev/about/security/
3. **RFC 9162 (Certificate Transparency v2)** provides append-only inclusion/consistency machinery but global consistency still depends on comparing observations/views. A locally valid signed checkpoint is not proof that every party saw the same history. https://www.rfc-editor.org/rfc/rfc9162.html
4. **The Update Framework (TUF)** models root metadata as the authority that names trusted keys and signature thresholds. Authority reconstruction therefore needs canonical role/key/threshold metadata, not an unordered bag of individually valid signatures. https://theupdateframework.io/docs/metadata/
5. **Machine unlearning research** shows that approximate unlearning can fail to remove poisoning effects, and that even deletion/retraining-style mechanisms can create privacy leakage through retained outputs or cached intermediate computations. Useful donors: Pawelczyk et al., *Machine Unlearning Fails to Remove Data Poisoning Attacks* (2024), https://arxiv.org/abs/2406.17216 ; Chourasia & Shah, *Forget Unlearning* (2022), https://arxiv.org/abs/2210.08911 ; Cohen et al., *Protecting the Undeleted in Machine Unlearning* (2026), https://arxiv.org/abs/2602.16697
6. **NIST SP 800-226** defines privacy budget as an upper bound on cumulative privacy loss. Identity deletion/relink must therefore preserve accounting monotonicity rather than minting fresh budget through graph changes. https://csrc.nist.gov/pubs/sp/800/226/final
7. **HTTP Idempotency-Key draft** treats a key as a request-retry identity and explicitly requires that a key not be reused with a different payload. This is a useful donor for separating retry identity from proof of a unique external effect/history. https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-02
8. **NIST SP 800-88 Rev. 2** makes cryptographic erase dependent on sanitizing the relevant cryptographic keying material and explicitly discusses externally managed keys. A local KMS view is not enough to prove global predecessor-key extinction. https://csrc.nist.gov/pubs/sp/800/88/r2/final

## Frozen invariants

### A. Assessment-provenance poisoning and issuer compromise

`SIGNED_ASSESSMENT != TRUSTWORTHY_ASSESSMENT_PROVENANCE`

A compromise/recovery assessment is itself an authority-bearing artifact. It MUST carry authenticated provenance sufficient to distinguish:

- assessment subject and affected authority/failure-domain lineage;
- evidence inputs and immutable digests;
- evidence collector identity and collector epoch;
- assessment engine/policy version;
- issuer identity, issuer key epoch, and issuer trust domain;
- trusted ordering/evidence cutoff;
- predecessor assessment and supersession relation;
- independence claims for contributing evidence;
- whether any input was supplied by the subject being assessed.

A valid signature proves only that the issuer signed the assessment. It does not prove that the evidence inputs, independence labels, or policy result were generated by a trustworthy path. If the issuer or its provenance-generation path is later compromised, assessments intersecting the compromise interval become `ASSESSMENT_PROVENANCE_SUSPECT` until independently re-established.

`ASSESSMENT_REISSUED != EVIDENCE_RECOLLECTED`

Re-signing the same poisoned evidence under a successor key cannot clear suspicion. Recovery requires either independently preserved pre-compromise evidence or fresh evidence whose semantics legitimately apply to the historical question.

### B. Canonical witness authority across cross-signed overlapping intervals

`N_VALID_SIGNATURES != N_INDEPENDENT_WITNESSES`

Witness quorum verification MUST canonicalize voting identity before counting signatures. Canonical identity binds:

- stable witness/failure-domain identifier;
- membership epoch;
- role;
- key epoch(s);
- validity interval(s);
- cross-sign transition relation;
- threshold configuration;
- predecessor root/checkpoint;
- trusted event cutoff.

Two cross-signed keys controlled by one stable witness count as one vote. A key that is valid cryptographically but not authorized for the relevant membership/event interval contributes zero votes.

`CROSS_SIGNATURE_PRESENT != SUCCESSOR_AUTHORIZED`

A cross-signature is evidence of a transition only if the predecessor authority that signed it was itself canonical and sufficient under the predecessor threshold. Circular cross-signing among successor keys cannot bootstrap authority from zero.

If multiple canonical reconstructions are possible and produce different quorum decisions, the result is `WITNESS_AUTHORITY_AMBIGUOUS`, not whichever interpretation yields success.

### C. Holdout lineage after machine unlearning or component deletion

`COMPONENT_DELETED != HOLDOUT_INFLUENCE_PROVEN_ABSENT`

Removing a model component, adapter, sparse layer, shard, cache, embedding index, or training sample does not by itself prove removal of holdout-derived information from the reachable system.

For any unlearning/deletion operation, retain an authenticated lineage transition containing:

- predecessor artifact IDs/digests and exposure lineage;
- exact deletion/unlearning mechanism and version;
- components/data targeted for removal;
- retained components, caches, optimizer state, routing state, ensemble members, and derived features;
- whether outputs from the pre-unlearning model were used to train/select/validate the successor;
- verification method and guarantee class: `EXACT_BY_CONSTRUCTION | PROVABLE_BOUND | EMPIRICAL_ONLY | UNKNOWN`;
- successor exposure lineage.

Default rule:

`successor.exposure_lineage = predecessor.exposure_lineage`

unless a sound deletion proof establishes that a particular lineage component is unreachable and no retained artifact/controller can reconstruct or exploit it. Empirical membership-inference failure alone is insufficient proof of absence because attacks/metrics are incomplete and may miss poisoning or retained-data leakage.

For ensembles, deleting one exposed member does not remove the lineage from other members, learned routing/weights, distilled successors, or cached predictions derived from it.

### D. Privacy tombstone collision and false-relink isolation

`SAME_TOMBSTONE != SAME_SUBJECT`
`NO_DIRECT_IDENTIFIER != NO_ACCOUNTING_LINEAGE`

A privacy accounting tombstone must prevent spend reset without becoming a reconstructive identifier or a single collision-prone key that can merge unrelated subjects.

The accounting layer therefore separates:

- non-reconstructive stable accounting lineage token(s);
- collision/equivalence evidence;
- resolver/model version and graph epoch;
- predecessor spend/reservation/unknown-loss floors;
- confidence/proof class;
- disjointness evidence and expiry.

Collision handling is asymmetric:

- suspected false merge MUST NOT silently transfer one subject's full identifying history into another;
- suspected false split MUST NOT mint fresh privacy budget;
- unresolved collision/relink keeps conservative spend floors while isolating raw identifiers and unrelated payload data;
- `graph split -> merge -> split` never decreases cumulative privacy-loss floors already established.

A relink result is never authority to erase a predecessor tombstone. Proven disjointness may stop future joint composition only from the proof cutoff onward; it does not refund historical privacy loss.

### E. Provider receipt sequence forks, gap compaction, and recovery-key rollback

`VALID_RECEIPT != SINGLE_CANONICAL_EFFECT_HISTORY`

A provider may emit individually valid receipts that fork at the same predecessor/sequence. The runtime therefore canonicalizes each receipt over at least:

- provider identity and provider authority epoch;
- logical operation/idempotency key;
- semantic request digest;
- effect/result digest;
- provider sequence/epoch;
- predecessor receipt/effect reference;
- signing key epoch;
- receipt generation and compensation/reversal ancestry.

Rules:

- two valid children of one canonical predecessor with incompatible semantics produce `PROVIDER_SEQUENCE_FORK`;
- sequence-gap compaction may summarize contiguous known receipts but MUST preserve commitments to all unresolved gaps/forks;
- compacting `1,2,5` cannot convert missing `3,4` into proof that no effects occurred;
- receipt arrival order and signed wall-clock time do not override authenticated sequence/ancestry;
- an idempotency key reused with a different semantic payload is an explicit conflict, never deduplicated as the same request;
- restoring an old receipt-signing/recovery key cannot roll back the provider authority epoch;
- compensation/reversal is a successor effect and cannot delete the forked predecessor evidence.

Blind retry remains forbidden while any branch can contain the original intended effect.

### F. Complete authority-domain enumeration before ticket-security-epoch GC

`ALL_KNOWN_DOMAINS_ACKED != ALL_AUTHORITY_DOMAINS_ENUMERATED`

Before declaring predecessor ticket/resumption authority extinct, the runtime needs an authenticated authority-domain inventory, not merely acknowledgements from the current service registry.

Inventory categories include:

- active KMS/HSM partitions;
- standby/failover regions;
- backup and disaster-recovery generations;
- wrapped/imported/exported key stores;
- escrow and break-glass recovery services;
- offline administrative recovery material;
- replicas/caches able to serve predecessor PSKs/tickets;
- credentials or automation that can restore predecessor keys;
- replay-state authorities relevant to 0-RTT.

Each inventory snapshot binds membership provenance, discovery cutoff, enumerator/issuer identity, and evidence that excluded domains cannot still exercise predecessor authority.

`DISCOVERY_COMPLETE` is a claim requiring evidence, not the absence of another row in the database. Unknown or unreachable authority classes remain `UNKNOWN` and block destructive GC.

Late discovery of a predecessor authority after GC proof:

1. does **not** lower `ticket_security_epoch_floor`;
2. marks the prior enumeration proof `INCOMPLETE_DISCOVERED_LATE`;
3. re-quarantines affected resumption paths;
4. requires targeted destruction/fencing and a successor enumeration proof;
5. does not automatically invalidate fresh full-authenticated 1-RTT sessions that do not rely on the predecessor resumption authority.

## 40-case RED-first matrix

### Assessment provenance / issuer compromise (1-7)
1. valid signature over assessment whose evidence digest was substituted -> reject provenance;
2. subject under assessment supplies a supposedly independent evidence source -> independence conflict;
3. issuer compromised after event but before signing -> assessment suspect;
4. issuer compromised after signing with independently anchored pre-compromise evidence -> interval-aware result, not blanket rewrite;
5. re-sign poisoned predecessor evidence under successor key -> still suspect;
6. policy/assessment-engine version omitted from signed provenance -> fail closed;
7. incomparable assessment provenance roots -> `ASSESSMENT_PROVENANCE_CONFLICT`.

### Witness canonicalization (8-14)
8. two keys for one stable witness count once;
9. cross-signed overlapping keys without canonical transition cannot count twice;
10. successor cross-signature below predecessor threshold cannot bootstrap successor authority;
11. circular successor cross-signatures without predecessor authority -> reject;
12. key cryptographically valid but outside event membership interval -> zero vote;
13. same canonical reconstruction after historical key expiry -> preserved evidence;
14. two valid canonicalizations yielding different quorum outcomes -> fail closed.

### Unlearning / holdout lineage (15-21)
15. delete one exposed ensemble member while routing weights retain its influence -> lineage retained;
16. adapter deletion but merged base contains adapter effect -> lineage retained;
17. retrain affected shard exactly with disjoint retained data and no derived cache -> permit explicit lineage retirement proof;
18. approximate unlearning with only empirical MIA success -> no lineage retirement;
19. poisoned-data unlearning passes utility metric but poisoning effect persists -> no retirement;
20. successor distilled from pre-unlearning outputs -> predecessor lineage retained;
21. ANN/cache rebuild from successor embeddings still influenced by exposed predecessor -> lineage retained.

### Privacy tombstones / relink (22-27)
22. tombstone hash collision between unrelated subjects -> isolate collision, do not merge payload identity;
23. deletion followed by false split into fresh ID -> no fresh budget;
24. probabilistic relink to two predecessor tombstones -> conservative floor without raw-ID resurrection;
25. later proof one candidate is disjoint -> no historical spend refund;
26. graph merge then split -> floor monotonic;
27. resolver upgrade changes match result -> evidence version advances, prior spend remains.

### Provider receipt forks / compaction (28-34)
28. two valid receipts at same predecessor sequence with different effect digest -> `PROVIDER_SEQUENCE_FORK`;
29. same idempotency key + different request digest -> explicit conflict;
30. receipts 1,2,5 compacted while 3,4 missing -> gaps remain unresolved commitments;
31. delayed receipt 3 arrives after compaction -> reconcile into canonical chain or fork, never discard;
32. old signing key restored from backup signs new low-epoch receipt -> no authority rollback;
33. wall-clock earlier receipt cannot override higher authenticated sequence ancestry;
34. compensation of one fork branch does not erase sibling-fork evidence.

### Federated authority enumeration / ticket GC (35-40)
35. all currently registered regions ACK but escrow inventory omitted -> GC blocked;
36. backup catalog has unknown generation -> extinction proof blocked;
37. offline break-glass credential can restore predecessor key -> predecessor authority not extinct;
38. late-discovered KMS replica after retirement proof -> mark proof incomplete and quarantine affected resumption without lowering epoch floor;
39. predecessor PSK authority extinct but replay-state epoch lost -> 0-RTT still blocked independently;
40. successor inventory proves all predecessor authority absent/destroyed/fenced with validated evidence -> allow bounded GC while retaining compact extinction proof.

## Implementation direction when exact execution returns

Do not implement this six-domain slice as one patch. Convert each block into tests attached to the owning LAB issue and preserve the dependency ordering of LAB-086/088/090/091/092/093+.

Preferred implementation shapes:

- immutable provenance/evidence records with canonical digests and predecessor links;
- canonical stable identities separated from rotating keys;
- threshold/quorum evaluation at authenticated event cutoffs;
- monotonic uncertainty/privacy/security floors;
- explicit `UNKNOWN`, `AMBIGUOUS`, `FORKED`, and `SUSPECT` states rather than optimistic booleans;
- deletion/unlearning proof objects whose guarantee class is explicit;
- provider receipt DAG/sequence commitments that survive compaction;
- authority-domain inventory proofs that include discovery provenance and delayed-discovery handling.

For every future executable slice: reproduce the unsafe/ambiguous pre-fix behavior on exact pinned bytes first, add the minimal fail-closed implementation, run the owning real-schema tests plus dependent supported-surface tests, then audit for rollback, aliasing, replay, compaction, deletion, and recovery-path bypasses. This document is a design freeze only; it changes no draft PR readiness.
