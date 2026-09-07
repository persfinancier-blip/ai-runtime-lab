# Publication witness recovery quorum / lost-state disaster recovery / anti-cloning v1

Status: `PUBLICATION_WITNESS_RECOVERY_QUORUM_LOST_STATE_DISASTER_RECOVERY_ANTI_CLONING_V1_FROZEN`

Date: 2026-09-07

## Scope

This note extends the frozen publication-witness lifecycle contract with the failure mode that contract intentionally left open: a witness still owns, or can recover, its signing identity but loses the durable monotonic checkpoint state that makes the identity useful for anti-equivocation.

It answers five questions:

1. what evidence may authorize recovery after durable witness state is lost or suspected rolled back;
2. how to reconstruct a safe lower bound on the witness's last accepted publication frontier without trusting the current log alone;
3. how to prevent a restored clone and a stale/original instance from simultaneously cosigning under one witness identity;
4. how lease/fencing and key custody must compose so an expired or partitioned process cannot keep producing authority-valid cosignatures;
5. what happens when the purported terminal historical state is disputed, forked, incomplete, or available only from correlated sources.

This is a design/evidence freeze, not an implementation PASS.

## Core distinction

`SIGNING_KEY_POSSESSION != WITNESS_AUTHORITY != SINGLE_ACTIVE_WITNESS`.

A transparency witness is not merely a private key. It is a stateful monotonic authority whose safety depends on all three of:

- authentic witness signing authority;
- recovered durable checkpoint history that cannot move backwards or switch forks;
- a current singleton activation/fencing epoch that stale instances cannot use after recovery or failover.

Recovering only the key recreates a signer, not the previous witness.

## 1. Donor mechanisms and evidence

### C2SP transparency-log witness

C2SP `tlog-witness` v1.0.0 requires a witness to compare an incoming `old size` with the latest checkpoint it previously cosigned, reject mismatches, verify consistency, and persist the new checkpoint before returning a cosignature. The state check and persist operation must be atomic specifically to prevent rollback races.

The protocol also exposes an important narrow fact: a client that does not know the witness's latest size may send old size zero and receive a conflict containing the witness's stored size. That is a client-discovery convenience; it is **not** a disaster-recovery mechanism for a witness whose own state has been lost. A state-lost witness must not infer its old state from the current log and then resume signing.

Primary source: https://c2sp.org/tlog-witness@v1.0.0 (accessed 2026-09-07), especially add-checkpoint state/409 semantics and atomic-persist requirement.

### TUF root migration

TUF requires each successor root version N+1 to be signed by the threshold specified by trusted root N **and** by the threshold specified by N+1, and requires exact sequential version advancement. This is a useful donor for recovery-policy continuity: a recovery authority should not be able to replace the current witness-recovery policy solely by self-signing a new policy after a disaster.

Primary source: https://theupdateframework.github.io/specification/latest/ sections 5.3 and 6.1 (accessed 2026-09-07).

### etcd revisions / fencing

etcd documents that revision numbers can act as fencing tokens and that lease ownership alone does not safely protect an external resource unless the resource validates the fencing/version information. This is directly relevant to witnesses: an in-memory lease saying `instance A is leader` does not stop a paused A from later signing with the same private key unless the signing path itself enforces a monotonically newer activation epoch.

Primary source: https://etcd.io/docs/v3.5/learning/why/ and concurrency API documentation (accessed 2026-09-07).

### AWS KMS multi-Region key replicas

AWS KMS multi-Region keys deliberately use the same key ID and key material across multiple fully functional regional keys. This is useful as a negative donor: replicated key custody improves availability, but cryptographic identity alone cannot prove singleton execution. If a witness signing identity is intentionally cloned/replicated, another independent fencing layer is required to ensure only the currently activated replica can produce accepted witness authority.

Primary sources: https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html and https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html (accessed 2026-09-07).

## 2. Recovery state machine

Freeze witness runtime states:

- `ACTIVE(epoch, frontier)` — may cosign after all normal consistency checks;
- `QUIESCING(epoch, frontier)` — may finish already-authorized durable work but may not accept new cosign requests;
- `RECOVERY_REQUIRED_NO_COSIGN` — private key may exist, but monotonic state is missing, rolled back, corrupt, or disputed; no cosigning permitted;
- `RECOVERY_CANDIDATE(epoch_candidate, frontier_candidate)` — recovery evidence assembled but not yet independently authorized;
- `RECOVERY_ACTIVATED(epoch_new, frontier_recovered)` — new fencing epoch durably activated; old epochs are permanently stale;
- `FORK_DISPUTE_NO_COSIGN` — recovery evidence contains incompatible publication histories and policy cannot prove one canonical predecessor frontier;
- `RETIRED` — identity may only verify historical signatures.

Crash/restart from `ACTIVE` is allowed to return directly to `ACTIVE` only when the exact durable state seal and activation epoch are intact and current. Any uncertainty about rollback enters `RECOVERY_REQUIRED_NO_COSIGN`.

## 3. Recovery evidence universe

Define `WitnessRecoveryEvidenceV1` containing independently addressable evidence classes:

- last locally sealed witness state, if any;
- independently archived historical witness checkpoints/cosignatures;
- checkpoints retained by publication monitors/mirrors;
- peer-witness checkpoints/cosignatures from the same publication policy;
- transparency-log consistency proofs and retained log tiles/entries sufficient to recompute them;
- external monotonic generation witness/ledger, if configured;
- witness-policy history and exact policy generation active at candidate frontier;
- authenticated key-status/compromise evidence;
- archive completeness, durability, and verifier-durability proofs from earlier frozen contracts;
- source identity/failure-domain metadata for every evidence contributor;
- exact bytes/digests and observation times.

The current log endpoint alone is never sufficient evidence for witness recovery. Otherwise a forked or compromised log can erase witness memory by waiting for a witness disaster and presenting its preferred branch as the recovery state.

## 4. Recovered frontier semantics

Define `RecoveredWitnessFrontierV1`:

- witness identity and key generation;
- log origin and log-key generation;
- recovered tree size/root/checkpoint bytes;
- policy generation/digest;
- recovery evidence-set digest;
- quorum/independence proof;
- consistency closure proof from the strongest authenticated historical predecessor;
- ambiguity/fork status;
- candidate recovery epoch.

The recovered frontier is the **highest uniquely supported safe lower bound**, not simply the numerically largest tree size observed.

Selection rules:

1. discard unauthenticated or historically unauthorized evidence;
2. group checkpoints into consistency-compatible branches;
3. preserve every incompatible valid branch as contradiction evidence;
4. require the configured recovery quorum/independence policy to support one branch and one candidate frontier;
5. require consistency from a previously authenticated anchor or archived witness state to that candidate;
6. if two incompatible branches independently satisfy recovery authority, enter `FORK_DISPUTE_NO_COSIGN`;
7. never resolve a fork using longest-tree, newest-timestamp, current-log majority, or `last writer wins`.

A recovery process may choose a frontier **below** the maximum observed size if that is the highest point with sufficient independent proof. After activation it may catch up normally through verified consistency proofs.

## 5. Recovery quorum and independence

Define `WitnessRecoveryPolicyV1` separately from ordinary publication-witness quorum policy.

Minimum fields:

- policy generation and predecessor digest;
- allowed evidence-source classes;
- threshold requirements;
- failure-domain independence requirements;
- required archival/monitor/peer composition;
- maximum tolerated Byzantine/corrupt evidence sources;
- rules for absent sources;
- fork-dispute rules;
- activation authority threshold;
- required fencing authority and epoch source;
- key-custody requirements;
- policy rotation authorization.

A numeric `t-of-n` is not enough. Two evidence providers operated by one organization/account/KMS/admin domain can fail or equivocate together. Recovery acceptance must be claim-relative to the declared correlated-failure model.

Recommended high-assurance baseline:

- at least one independently retained historical archive/monitor source;
- at least one live source from a different administrative/failure domain;
- consistency closure from an authenticated pre-disaster anchor;
- no unresolved incompatible branch satisfying the same recovery threshold;
- activation authorized through a governance/fencing authority not controlled solely by the recovering process.

This baseline is a design policy, not a universal theorem.

## 6. Anti-cloning: recovery epoch as mandatory fencing token

The central rule is:

`COSIGNATURE_VALID = CRYPTO_VALID && CHECKPOINT_CONSISTENT && ACTIVATION_EPOCH_CURRENT`.

Define `WitnessActivationEpochV1` as a strictly monotonic fencing value bound to:

- witness authority namespace;
- witness key generation;
- recovery-policy generation;
- recovered predecessor frontier;
- exact active instance/custody identifier;
- activation lease generation, when leases are used;
- creation/authorization evidence;
- previous epoch digest.

Every authority-valid witness cosignature must bind the activation epoch, directly in the signed payload or through an inseparable signed envelope verified by clients/publication policy.

A stale process with epoch E remains cryptographically able to use copied key material, but its signatures cease to be authority-valid after epoch E+1 is activated.

### Why leases alone fail

Lease expiration is not a kill switch. A process can pause, lose its lease, then resume and use still-present key material. Therefore all consumers of witness authority must reject epochs lower than the current accepted fencing epoch. This follows the same safety principle as fencing tokens for distributed locks.

If the existing public witness protocol cannot encode/verify an activation epoch, safe anti-cloning requires one of:

- rotate to a new witness signing key for every disaster-recovery activation and retire the old key at the exact activation frontier; or
- wrap witness signatures in a separately verified epoch-bearing authority envelope; or
- place signing behind a non-exportable service that itself performs atomic current-epoch validation before every signature and cannot be bypassed by replicas.

Merely storing `current_epoch` in the recovering process is not fencing.

## 7. Key custody composition

### Exportable or replicated keys

When the same private key can exist in more than one process/HSM/region, singleton authority cannot be inferred from key possession. The anti-cloning epoch/fence is mandatory.

### Non-exportable single HSM key

A single non-exportable key reduces clone risk but does not eliminate stale authorization if multiple application instances can request signatures concurrently. The HSM/signing gateway must require the current epoch/lease token on each sign operation, or policy must rotate signing authority during recovery.

### Threshold signing

Threshold key shares do not automatically solve active-clone safety. Two overlapping quorums or duplicated shares may still sign concurrently. The threshold signer set must consume the same monotonic activation epoch and refuse stale epochs before participating.

### Lost key + lost state

If both signing key and monotonic state are lost, this is identity replacement, not ordinary state recovery. It requires witness-policy/key rotation continuity from independent governance according to the previously frozen policy-rotation contract. The new identity starts only at an explicitly recovered frontier and must not erase old witness history.

## 8. Recovery activation protocol

Freeze the following sequence:

1. `DECLARE_RECOVERY` — mark witness namespace `RECOVERY_REQUIRED_NO_COSIGN`; publication policy stops counting new signatures from ambiguous instances.
2. `FREEZE_OLD_EPOCH` — revoke/expire the old activation lease where possible and advance external fencing authority to a new pending epoch; do not yet sign.
3. `COLLECT_EVIDENCE` — gather exact recovery evidence from independent archives/peers/monitors/log proofs.
4. `CLASSIFY_BRANCHES` — verify signatures, policies, consistency, provenance, historical key status; preserve all valid incompatible branches.
5. `SELECT_SAFE_FRONTIER` — compute highest unique quorum-supported safe lower bound.
6. `AUTHORIZE_RECOVERY` — recovery/governance quorum signs `RecoveredWitnessFrontierV1` plus new activation epoch and policy/key bindings.
7. `INSTALL_STATE` — atomically persist recovered frontier + epoch + recovery proof before enabling signing.
8. `ACTIVATE_FENCE` — external fencing authority marks epoch current; any prior epoch becomes permanently stale.
9. `PROBE_SINGLETON` — deliberately attempt a stale-epoch sign request through every known old/replica path; all must fail authority validation.
10. `RESUME_COSIGN` — only after the stale-path negative proof and current-path positive proof succeed.

If crash occurs before step 8, restart remains no-cosign. If crash occurs after step 8 but before step 10, restart may reconstruct the already-activated epoch but must rerun singleton/stale-path validation before production cosigning.

## 9. Simultaneous-active witness semantics

Two processes under one witness identity may be simultaneously alive for availability, but only one **authority epoch** may be accepted at a time unless the signing backend itself serializes a shared state machine.

Allowed deployment classes:

- active/passive processes sharing one linearizable state+signing authority that atomically validates checkpoint and epoch;
- multiple stateless frontends behind one stateful witness signer;
- multiple independent replicas only if each request is fenced by a shared monotonic authority and stale epochs are rejected at the signature-validation boundary.

Forbidden deployment:

- copy witness DB + private key to two hosts and trust a TTL/heartbeat to prevent dual signing;
- use DNS/load-balancer leadership as authority;
- restore VM snapshot containing old key+state while original VM may still run;
- rely on wall-clock timestamps to choose which cosignature is newer;
- promote a replica solely because the primary is unreachable.

If two different active epochs produce independently policy-acceptable cosignatures over incompatible branches, record `WITNESS_ACTIVE_CLONE_EQUIVOCATION_PROVEN`; do not silently prefer the higher epoch until the contradiction is preserved and governance explicitly reconciles history.

## 10. Disputed terminal state

Recovery evidence may show:

- same size + same root: compatible duplicate evidence;
- different sizes + valid consistency: one branch, choose highest quorum-supported safe frontier;
- same size + different roots: fork proof;
- different sizes without a valid consistency relation: unresolved branch conflict;
- archived local state ahead of every live source: live sources may be stale; do not roll back;
- live source ahead of archive with valid consistency and sufficient independent support: may recover at supported newer frontier;
- current log alone ahead: insufficient for recovery authority.

No recovery path is allowed to convert `PUBLICATION_FORK_PROVEN` into ordinary healthy history by selecting one side and deleting the other. Recovery chooses whether signing can safely resume; it does not rewrite the historical truth set.

## 11. Recovery policy/key rotation

`WitnessRecoveryPolicyV1` itself must rotate with continuity. Normal generation P+1 requires:

- predecessor-policy threshold authorization;
- successor-policy threshold acceptance;
- exact sequential generation;
- preserved intermediate policies;
- authenticated activation frontier;
- anti-fork proof across the policy transition.

If predecessor recovery authority is itself lost/compromised beyond threshold, ordinary recovery is no longer justified. Only an explicitly defined higher/out-of-band root recovery procedure may replace it. That event must remain visibly distinct in history.

## 12. Fraud / contradiction proofs

Freeze at least these evidence classes:

1. `WITNESS_RECOVERY_FROM_CURRENT_LOG_ONLY_PROOF` — state rebuilt solely from mutable log endpoint.
2. `WITNESS_RECOVERY_ROLLBACK_PROOF` — recovered frontier is behind an independently authenticated prior frontier.
3. `WITNESS_RECOVERY_FORK_SELECTION_PROOF` — incompatible qualifying branch was suppressed during recovery.
4. `WITNESS_ACTIVE_CLONE_EQUIVOCATION_PROOF` — concurrent/stale replicas under one authority lineage sign incompatible histories.
5. `STALE_ACTIVATION_EPOCH_ACCEPTANCE_PROOF` — consumer accepts cosignature from epoch below current fence.
6. `LEASE_WITHOUT_FENCING_PROOF` — stale process signs after lease loss because signature path does not validate epoch.
7. `RECOVERY_POLICY_SELF_AUTHORIZATION_PROOF` — new recovery policy installs itself without predecessor/higher-root continuity.
8. `RECOVERY_EVIDENCE_DOMAIN_COLLAPSE_PROOF` — claimed independent quorum is actually one correlated custody/admin domain.
9. `RECOVERY_STATE_INSTALL_NONATOMIC_PROOF` — signing becomes possible before recovered state+epoch are durably installed.
10. `OLD_INSTANCE_REENABLE_PROOF` — an old VM/process snapshot can regain authority after a newer epoch exists.

## 13. Verdicts

- `RECOVERY_NOT_REQUIRED`
- `RECOVERY_REQUIRED_NO_COSIGN`
- `RECOVERY_EVIDENCE_INSUFFICIENT`
- `RECOVERY_FRONTIER_UNIQUELY_SUPPORTED`
- `RECOVERY_FRONTIER_ROLLBACK_DETECTED`
- `RECOVERY_FORK_DISPUTE_NO_COSIGN`
- `RECOVERY_AUTHORIZED_PENDING_FENCE`
- `RECOVERY_ACTIVATED_SINGLETON_PROVEN`
- `STALE_INSTANCE_FENCED`
- `WITNESS_ACTIVE_CLONE_EQUIVOCATION_PROVEN`
- `UNKNOWN_RECOVERY_AUTHORITY`

## 14. RED-first executable matrix

Implementation should begin with failing tests. Minimum matrix: 80 cases, grouped 10×8.

A. State-loss detection (8): intact restart; missing DB; corrupted state seal; older snapshot; same-size different root; epoch missing; policy mismatch; uncertain durable write outcome.

B. Evidence collection (8): independent archive; peer witness; monitor; mirror; current log only reject; correlated archive replicas; missing policy history; bad source provenance.

C. Frontier construction (8): same root duplicates; consistent larger checkpoint; archived state ahead of live; live ahead with independent proof; live ahead without proof; same-size fork; inconsistent-size fork; incomplete consistency chain.

D. Recovery quorum (8): threshold satisfied; insufficient threshold; independence collapse; one Byzantine source; two qualifying conflicting branches; absent required archive class; NOT_APPLICABLE evidence; recovery-policy version mismatch.

E. Activation epoch (8): first recovery increment; exact monotonic successor; skipped epoch; rollback epoch; duplicate epoch/same instance; duplicate epoch/different instance; stale epoch signature; current epoch signature.

F. Lease/fencing (8): lease current; lease expiry; paused old process resumes; partitioned old process; new owner activation; stale write/sign rejected; lease renewed after fencing loss; wall-clock skew irrelevant.

G. Key custody (8): one non-exportable key; copied software key; multi-region replicated key; threshold shares; duplicated threshold share; HSM available but epoch stale; key lost/state intact; key+state both lost.

H. Atomic activation/crash (8): crash before declare; after freeze; during evidence collection; after authorization before install; after install before fence; after fence before singleton probe; after probe before resume; recovery retry idempotence.

I. Simultaneous replicas (8): active/passive normal; old VM snapshot starts; two frontends one signer; two independent signers one fence; DNS split brain; LB split brain; old instance network partition heals; incompatible concurrent signatures preserved as fraud proof.

J. Governance/fraud (8): predecessor-authorized policy rotation; self-authorized recovery policy reject; compromised recovery key; suppressed fork branch; fabricated archive source; rollback frontier; old-instance re-enable; current-log-only reset.

## 15. Implementation consequences for LAB-093

When LAB-093 eventually reaches executable work, publication-witness recovery must not be implemented as a convenience method that writes a checkpoint into the witness DB and restarts the service. The capability boundary needs explicit separation between:

- recovery evidence reader/verifier;
- recovery adjudicator/governance authority;
- external monotonic activation/fencing authority;
- signing-key custody;
- live witness request path.

No single recovering process should be able to fabricate the frontier, install it, advance the fence, and issue the first accepted cosignature without an independently verifiable authority chain.

The likely smallest executable slice is therefore a pure recovery classifier plus fail-closed witness state machine and stale-epoch regression suite before any real key/HSM or distributed lease integration.

## 16. Frozen decision

Freeze `PUBLICATION_WITNESS_RECOVERY_QUORUM_LOST_STATE_DISASTER_RECOVERY_ANTI_CLONING_V1_FROZEN` with these invariants:

- state loss always disables cosigning until recovery closure;
- current log state alone can never reconstruct witness authority;
- recovery chooses the highest uniquely quorum-supported safe lower bound, not the largest observed tree;
- valid incompatible recovery branches remain explicit fork evidence and block signing when ambiguity reaches the authority threshold;
- key possession is not singleton authority;
- every post-recovery accepted cosignature must be fenced by a strictly monotonic activation generation, or recovery must rotate to a new key/authority generation that provides equivalent stale-instance rejection;
- leases coordinate liveness but do not replace fencing;
- old VM/process/key replicas must remain cryptographically or policy-invalid after a new recovery epoch activates;
- recovery policy rotation requires predecessor+successor continuity or an explicitly distinct higher-root emergency process;
- historical fork/equivocation evidence survives recovery and can never be laundered by choosing a new active branch.

## Next evidence task

If exact LAB-086 execution remains unavailable, the next distinct research target should be **witness activation-epoch distribution / verifier freshness / stale-policy cache invalidation semantics**: prove how every consumer learns a newer activation epoch quickly enough to reject an old clone; define offline-verifier semantics, bounded-staleness/freshness proofs, cache rollback resistance, and what happens when some relying parties have accepted epoch E+1 while partitioned parties still trust E.