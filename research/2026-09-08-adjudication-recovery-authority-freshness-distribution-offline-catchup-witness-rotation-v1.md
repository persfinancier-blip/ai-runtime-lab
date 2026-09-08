# Adjudication/recovery authority freshness distribution, offline catch-up, witness/key rotation — V1 freeze

Date: 2026-09-08
Status: **ADJUDICATION_RECOVERY_AUTHORITY_FRESHNESS_DISTRIBUTION_OFFLINE_CATCHUP_WITNESS_ROTATION_V1_FROZEN**
Parent: LAB-093 / #178

## Scope

This freeze extends the prior adjudication-transparency/recovery-recursion contracts to the case where a relying party is offline across one or more of:

- adjudication-authority key rotation;
- recovery-root rotation;
- witness-set membership or witness-key rotation;
- quorum-policy changes;
- compromise/revocation publication;
- transparency-log checkpoint advancement;
- recovery/rebootstrap events.

The target property is not merely that each fetched object has a valid signature. The target is that an offline relying party can reconstruct an authenticated, non-truncated authority history from its last trusted frontier to a current usable frontier without accepting a selectively served healthy-looking branch.

## Core separation

Freeze the following non-equivalences:

`VALID_SIGNATURE != CURRENT_AUTHORITY`

`CURRENT_AUTHORITY != CURRENT_QUORUM_POLICY`

`CURRENT_QUORUM_POLICY != CURRENT_WITNESS_MEMBERSHIP`

`WITNESS_COSIGNATURE_QUORUM != SEMANTIC_ADJUDICATION_TRUTH`

`LATEST_CHECKPOINT_SEEN != COMPLETE_CATCHUP_HISTORY`

`APPEND_ONLY_CONSISTENCY != NO_OMITTED_AUTHORITY_GENERATIONS`

A relying party MUST NOT jump directly from a retained generation `gN` to a served `gN+k` solely because `gN+k` is well signed by keys named inside `gN+k`.

## Donor mechanisms and evidence

### TUF: sequential root reconstruction and rollback/freeze resistance

TUF clients update root trust one generation at a time. Version `N+1` must satisfy the threshold authorized by trusted root `N` and the threshold declared by `N+1`; clients must not replace trusted metadata with lower versions. All released root versions are retained so outdated clients can re-trace the chain of trust. Expiration/timestamp metadata limits indefinite freeze attacks.

Primary source:
- https://theupdateframework.github.io/specification/

Mechanisms reused here:
- sequential generation catch-up;
- predecessor + successor authorization for authority rotation;
- monotonic version/frontier persistence;
- explicit freshness/expiry;
- no direct jump to a self-authorizing newest authority document.

### RFC 9162: checkpoint consistency and monitor evidence

Certificate Transparency monitors verify append-only growth, fetch entries, validate consistency, and can retain signed evidence of log misbehavior. Consistency of views requires sharing/checking log responses; a signed checkpoint alone is not sufficient to prove all parties were shown the same history.

Primary source:
- https://www.rfc-editor.org/rfc/rfc9162.html

Mechanisms reused here:
- consistency proofs between retained and new checkpoints;
- signed checkpoint/frontier persistence;
- explicit failure when a served history cannot be reconciled with the retained checkpoint;
- evidence-preserving treatment of split-view conflicts.

### SCITT / RFC 9943: signed statements, receipts, multiple transparency services

SCITT distinguishes issuer-authenticated Signed Statements from Transparency Service receipts. The same Signed Statement may be registered in multiple Transparency Services, producing independent receipts. Relying parties decide which issuers and transparency services they trust; transparency provides auditability/accountability, not semantic truth.

Primary source:
- https://www.rfc-editor.org/rfc/rfc9943.html

Mechanisms reused here:
- authority statements and transparency receipts are separate evidence;
- cross-registration in independent logs is useful for survivability and equivocation detection;
- a receipt proves registration, not legitimacy of the authority transition.

### Transparency.dev witness model

A witness cosigns only checkpoints consistent with the checkpoint it previously accepted. A quorum of independently operated witnesses can reduce split-view risk. Witnesses intentionally do not judge log-leaf semantics.

Primary sources:
- https://blog.transparency.dev/can-i-get-a-witness-network
- https://transparency.dev/witnesses/

Mechanisms reused here:
- witness-local retained checkpoint frontier;
- consistency-before-cosign;
- quorum counted only after control-domain independence appraisal;
- witness cosignatures prove consistency/non-equivocation assurance, not semantic correctness.

## 1. Witness-set membership is an authority object

Define `WitnessSetAuthorityV1` separately from the witness set it governs.

Minimum fields:

- `authority_lineage_id`;
- `generation`;
- `predecessor_digest`;
- `valid_from` / `expires_at`;
- `witness_set_id`;
- ordered `WitnessMemberV1[]`;
- quorum policy reference/digest;
- independence-policy digest;
- allowed transparency-log lineages;
- signatures satisfying predecessor + successor thresholds for normal rotation;
- transparency receipts/checkpoint anchors.

`WitnessMemberV1` binds at least:

- stable logical witness id;
- verification key generation;
- operator/control-domain identity;
- custody domain;
- implementation/runtime lineage where policy requires it;
- validity interval;
- status: ACTIVE / RETIRING / REVOKED / COMPROMISED.

A witness signing key rotation MUST NOT implicitly remove the logical witness from quorum history or create a fresh independent witness identity.

Freeze:

`WITNESS_KEY_ROTATION != NEW_INDEPENDENT_WITNESS`.

## 2. Quorum-policy rotation is versioned and non-retroactive

Define `WitnessQuorumPolicyV1` with:

- policy lineage id;
- monotonic generation;
- predecessor digest;
- required `m-of-n` or rule expression;
- independence constraints;
- validity interval;
- emergency-policy reference if any;
- authorized signatures;
- transparency anchors.

A new quorum policy applies only to statements/checkpoints in its defined validity scope. It MUST NOT retroactively reinterpret an old 2-of-3 checkpoint as valid under a later 1-of-2 policy, or vice versa.

Historical appraisal records the policy generation actually used.

## 3. Offline relying-party retained frontier

Persist a `TrustedAdjudicationRecoveryFrontierV1` containing at minimum:

- highest trusted adjudication-authority generation + digest;
- highest trusted recovery-root generation + digest;
- highest trusted witness-set-authority generation + digest;
- highest trusted quorum-policy generation + digest;
- per-log trusted checkpoint size/root;
- per-witness highest accepted witness-key generation and last cosigned checkpoint digest where available;
- highest observed compromise/revocation generation;
- highest accepted adjudication/reclosure generation;
- secure-time/freshness evidence reference;
- unresolved contradiction set digest.

This frontier is monotonic persistent state. A lower served generation is rollback. Same generation with different authenticated digest is equivocation.

## 4. Required offline catch-up order

An offline relying party MUST NOT validate newest adjudication content before restoring the authorities that define how to validate it.

Required order:

1. Start from locally retained trusted frontier.
2. Reconstruct every missing recovery-root / authority-root generation sequentially.
3. Reconstruct witness-set-authority generations sequentially.
4. Reconstruct quorum-policy generations sequentially.
5. Reconstruct witness-key rotations/revocations referenced by those generations.
6. Reconcile transparency checkpoints from retained roots/sizes using consistency proofs.
7. Reconcile compromise/revocation/adjudication statements across the now-authenticated authority interval.
8. Verify required inclusion/receipts or cross-log anchors for high-impact statements.
9. Only then appraise the newest candidate current adjudication/recovery state.
10. Persist the new trusted frontier atomically with the acceptance decision.

If any required intermediate generation is unavailable or unverifiable, return:

`AUTHORITY_CATCHUP_INCOMPLETE_UNKNOWN`

and do not establish positive current reliance.

## 5. Selective truncation resistance

Attack: an offline verifier last trusted `g10`. During its absence, compromise was published at `g11`, recovery at `g12`, and a healthy new state at `g13`. A malicious mirror serves only `g13` and a matching recent checkpoint.

Rule: `g13` is not acceptable unless the verifier proves continuity from retained `g10` through every authority generation or through an equivalent authenticated prefix proof whose committed contents cover `g11..g13`.

A recent checkpoint consistent only with a newly served local root is insufficient. The proof must chain from the relying party's retained checkpoint/frontier.

Freeze:

`CURRENT_HEALTHY_LOOKING_VIEW + VALID_SIGNATURES != COMPLETE_POST_OFFLINE_HISTORY`.

## 6. Cross-log/checkpoint anchoring

For high-impact adjudication, compromise, recovery-root and witness-set changes, policy MAY require registration in `k` independent transparency logs and/or anchoring of checkpoint digests into another log lineage.

`CrossLogAnchorV1` binds:

- source log lineage/checkpoint digest;
- target log lineage;
- target inclusion proof/receipt;
- registration time/ordering evidence;
- policy generation.

Cross-log anchoring improves survivability and split-view detection but does not manufacture semantic truth. Two logs under one control domain are not automatically independent.

If required cross-log anchors disagree on the same generation/digest scope, state is conflict, not majority selection.

## 7. Witness-key rotation and stale checkpoint handling

A witness key is accepted only under an authenticated `WitnessMemberV1` key generation.

Normal rotation requires continuity authorized by the witness-set authority. A checkpoint cosigned by an expired/revoked witness key is historical evidence only unless policy explicitly permits its historical validity interval.

If an offline relying party receives a fresh log checkpoint carrying a quorum of signatures from witness keys that were revoked during the missed interval, it MUST reconstruct the missed witness-set/key generations before counting those signatures.

A stale-but-valid historical witness checkpoint may be used as a consistency anchor; it MUST NOT be treated as proof of current freshness.

## 8. Witness compromise after the fact

If a witness is later proven compromised for interval `[t0,t1]`, historical cosignatures in that interval remain immutable evidence that signatures existed but may cease to count toward current non-equivocation assurance.

Re-appraise affected checkpoints against the remaining independent witness set. If quorum drops below policy threshold:

`CURRENT_WITNESS_ASSURANCE_INSUFFICIENT_POST_COMPROMISE`.

Do not delete old receipts/cosignatures.

## 9. Freshness and freeze attacks

Every current-use authority/witness/quorum artifact has an explicit expiry or freshness bound. Secure-time requirements are inherited from the prior freshness contracts.

If a client cannot establish that the newest trusted authority metadata is unexpired/current enough, it may retain historical auditability but MUST NOT claim positive current reliance.

State:

`CURRENT_AUTHORITY_FRESHNESS_UNPROVEN`.

A mirror withholding newer authority generations cannot force trust in indefinitely stale metadata.

## 10. Crash consistency

Catch-up acceptance is transactional from the relying party's perspective.

Persist atomically:

- newly trusted authority generations;
- new witness/quorum state;
- new checkpoint frontiers;
- compromise/revocation frontier;
- unresolved contradictions;
- final current-reliance decision.

Crash between validation and frontier persistence MUST cause safe replay of catch-up, not acceptance from partially advanced metadata.

## 11. Conflict rules

The following are hard conflicts:

- same authority lineage + generation + different authenticated digest;
- same witness-set generation + different member set/digest;
- same quorum-policy generation + different rule/digest;
- same log size/generation + different authenticated checkpoint roots;
- same logical witness/key generation + different verification keys;
- same recovery generation + incompatible predecessor digests;
- required independent logs anchor incompatible histories.

Never resolve these using:

- last-write-wins;
- newest wall-clock timestamp;
- first response;
- fastest mirror/CDN;
- raw majority of endpoints without authenticated independence semantics.

Return a conflict state and remove positive current reliance until resolved by a higher authenticated recovery/adjudication process.

## 12. RED-first executable matrix (48 cases)

### A. Offline authority generation catch-up
1. g10 -> g11 valid sequential rotation.
2. g10 -> served g12 with g11 missing: reject/UNKNOWN.
3. g11 signed only by successor threshold: reject.
4. g11 signed only by predecessor threshold: reject.
5. lower authority generation rollback: reject.
6. same generation different digest: conflict.
7. expired newest authority: freshness unproven.
8. crash after validating g11 before persistence: safe replay.

### B. Witness-set membership/key lifecycle
9. valid witness key rotation under same logical witness.
10. rotated key counted as new independent witness: reject.
11. witness removed without authorized membership generation: reject.
12. witness revoked during offline interval then served as current: reject.
13. historical pre-revocation cosignature retained for audit.
14. same witness-key generation different keys: conflict.
15. two witnesses under one destructive/control domain fail independence threshold.
16. stale witness checkpoint accepted only as historical consistency anchor.

### C. Quorum-policy rotation
17. valid sequential quorum-policy rotation.
18. missing intermediate policy generation: UNKNOWN.
19. retroactive weaker policy applied to old checkpoint: reject.
20. retroactive stronger policy rewriting historical verdict: reject.
21. same policy generation different threshold: conflict.
22. policy expired before current checkpoint: current reliance fail.
23. policy rotation references unknown witness set: reject.
24. crash during policy/frontier update: safe replay.

### D. Transparency/checkpoint catch-up
25. retained checkpoint -> fresh checkpoint with valid consistency proof.
26. fresh checkpoint cannot prove consistency to retained root: conflict/fail.
27. same tree size different root: equivocation.
28. log serves only newest self-consistent local history not chained to retained root: reject.
29. required checkpoint unavailable: UNKNOWN, not healthy.
30. one independent log unavailable but policy threshold still met: bounded degraded acceptance if policy permits.
31. required cross-log anchor missing: fail current positive reliance.
32. two required logs anchor incompatible generation digests: conflict.

### E. Selective truncation / compromise-recovery interval
33. g10 retained; g11 compromise, g12 recovery, g13 healthy; only g13 served: reject.
34. complete g10->g13 chain served: appraise all intermediate events.
35. compromise statement omitted but independently cross-log anchored: omission detected.
36. recovery statement served before compromise statement: ordering conflict/UNKNOWN.
37. old compromised witness quorum selectively served: reject after key-history reconstruction.
38. healthy latest checkpoint with unresolved intervening contradiction: no positive reliance.
39. mirror withholds newer generation until old metadata expires: freeze detected.
40. two mirrors serve different same-generation roots: equivocation.

### F. Post-facto compromise / recovery recursion
41. witness compromise lowers usable quorum below threshold: current assurance invalidated.
42. compromised adjudicator key signed current statement in proven interval: reappraise.
43. recovery-root compromise with valid higher independent anchor: exceptional recovery path.
44. recovery-root threshold compromise without independent anchor: same-lineage recovery unproven.
45. late compromise notice preserves historical receipts.
46. false single-monitor compromise signal causes scoped quarantine only, not permanent global revoke.
47. recovery changes witness membership and quorum policy in same generation without deterministic dependency ordering: reject.
48. complete recovery package with separately authorized root, witness-set and quorum transitions: accept only after full catch-up and checkpoint reconciliation.

## 13. Required implementation invariants for LAB-093 exact RED/GREEN

When implementation becomes executable, tests should enforce at least:

- persistent trusted frontier cannot move backward;
- intermediate authority generations cannot be skipped;
- witness membership, witness keys and quorum policy are separate versioned authorities;
- witness signatures count only after membership validity + key validity + independence appraisal;
- checkpoint consistency must chain from the client's retained checkpoint, not merely from another freshly downloaded checkpoint;
- selectively truncated compromise/recovery history cannot yield positive current reliance;
- same-generation authenticated conflicts fail closed;
- historical receipts remain immutable after later compromise/revocation;
- catch-up persistence is crash-safe and replay-safe;
- witness consistency never substitutes for semantic adjudication/recovery authorization.

## Decision summary

Freeze **ADJUDICATION_RECOVERY_AUTHORITY_FRESHNESS_DISTRIBUTION_OFFLINE_CATCHUP_WITNESS_ROTATION_V1_FROZEN**.

The central safety rule is:

> An offline relying party may advance current trust only by reconstructing an authenticated authority/witness/quorum/checkpoint chain from its own retained trusted frontier. A newly served, internally consistent healthy-looking view is insufficient if intervening authority history can be selectively omitted.

This composes with prior compromise-adjudication recursion: if the catch-up process discovers that the authority required to validate an intermediate generation was itself compromised, normal same-lineage progression stops and the previously frozen independent exceptional recovery/rebootstrap rules apply.
