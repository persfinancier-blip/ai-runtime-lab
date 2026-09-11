# Registry-root compromise, retirement checkpoint loss, unlearning membership, privacy revocation, finality replica loss, and GC transition recovery — V1

Status: `REGISTRY_ROOT_LOSS_RETIREMENT_CHECKPOINT_UNLEARNING_MEMBERSHIP_PRIVACY_REVOCATION_FINALITY_REPLICA_GC_TRANSITION_V1_FROZEN`

Date: 2026-09-11

Context: LAB-086 remains the priority executable task. This run re-probed direct source materialization first; `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available, but there is still no supported non-model connector-to-executor primitive that can materialize the pinned security-critical closure byte-for-byte. Therefore this note is the next distinct evidence task recorded by the prior handoff; it does **not** claim RED/GREEN, compile, integration, or security-gate PASS.

## Scope

Freeze fail-closed recovery contracts for six failure modes left intentionally open by the previous architecture freeze:

1. issuer-domain registry recovery when the registry recovery root itself is compromised;
2. verifier-retirement tombstone continuity after partial checkpoint loss;
3. distributed unlearning worker-membership changes during an open proof snapshot;
4. privacy participant-attestation revocation after coordinator failover;
5. finality-checkpoint recovery after partial replica loss;
6. safe retirement of the old destructive-GC configuration after joint-consensus commit, including crash/restart at the `joint -> new` transition boundary.

The common rule is that **availability recovery must not silently manufacture authority**. A missing predecessor, compromised recovery root, failed replica, coordinator replacement, or membership change may force `UNKNOWN`/quarantine/re-proof, but it does not permit rollback, branch selection by arrival time, quorum reinterpretation, or deletion of unresolved evidence.

## Primary donors and facts

### TUF 1.0.36: threshold trust, rollback resistance, root succession

The current TUF specification is version 1.0.36, modified 2026-08-05. It explicitly treats rollback, mix-and-match, freeze, and key compromise as attacks, and relies on versioned root metadata plus threshold trust rather than accepting a replacement root merely because the replacement signs itself.

Source: https://theupdateframework.github.io/specification/latest/

Useful mechanism: trust-root changes are authenticated state transitions. If the authority that normally authorizes transition is itself compromised, recovery must rely on a separately established and independently rooted recovery path; it cannot infer safety from successor self-signature or freshness.

### RFC 9162: retained checkpoints require consistency, not mere inclusion

RFC 9162 separates inclusion from consistency. A later authenticated tree head proves append-only continuity from an earlier head only with a valid consistency proof; a signed later checkpoint alone is not enough. This is the donor for recovery after partial retirement/finality checkpoint loss.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

### NIST SP 800-226: privacy loss is cumulative

NIST SP 800-226 defines the privacy budget as an upper bound on cumulative privacy loss across analyses of a dataset. Coordinator failover, participant replacement, attestation revocation, or namespace movement therefore cannot reset accounting or refund already consumed loss.

Sources:
- https://csrc.nist.gov/pubs/sp/800/226/final
- https://csrc.nist.gov/glossary/term/privacy_budget

### Raft joint consensus: transition safety requires overlapping authority

Raft's joint-consensus membership-change design uses an intermediate configuration requiring majorities of both old and new memberships, followed by a final new-only configuration. The crucial recovery property is that a crash at the transition boundary must resume from durable replicated configuration state; a leader/coordinator cannot decide locally that the system is already in the new configuration.

Source: https://raft.github.io/

## Frozen contracts

### A. Issuer-registry recovery when the recovery root is compromised

`RECOVERY_ROOT_SIGNATURE != RECOVERY_AUTHORITY`.

The issuer-domain registry already has a versioned authenticated head and explicit equivocation state. This slice adds a recovery-root hierarchy and compromise semantics.

Each recovery authorization binds:

- registry generation being recovered;
- all conflicting registry heads being resolved;
- last undisputed predecessor head;
- recovery-policy generation;
- recovery-root identity set and canonical failure-domain mapping;
- compromise-evidence cutoff used to decide admissible roots;
- successor registry head;
- recovery event digest.

If the currently configured registry recovery root is compromised for the interval in which it authorized recovery, the resulting recovery event becomes `REGISTRY_RECOVERY_AUTHORITY_UNCERTAIN`. A successor recovery root cannot make that old event trustworthy by re-signing it.

Recovery is valid only through an independently established higher recovery-policy generation whose admissible failure domains remain above threshold after compromise filtering and which commits the uncertain event plus every registry fork head it supersedes. A recovery key that shares the same canonical operational/HSM/escrow failure domain as the compromised root does not count as independent.

A recovery-policy rollback is forbidden even if the rolled-back policy contains currently valid keys. Same-generation competing recovery policies are `RECOVERY_POLICY_EQUIVOCATION` and block registry advancement.

No rule chooses a branch because it is newer by wall clock, arrived first, has more signatures from correlated keys, or is the locally available branch.

### B. Retirement-tombstone continuity after partial checkpoint loss

Retirement history has three distinct categories of retained evidence:

1. monotonic retirement floor / verifier identity;
2. authenticated checkpoint head(s);
3. predecessor-to-successor consistency material.

Partial loss is not binary. Recovery classifies a verifier retirement as:

- `RETIREMENT_CONTINUITY_PROVEN` — retained authenticated material proves the accepted retirement floor and continuity from the last trusted predecessor;
- `RETIREMENT_FLOOR_PROVEN_CONTINUITY_UNKNOWN` — the system can prove the verifier was retired at/above a floor, but cannot prove which successor checkpoint extends the lost predecessor;
- `RETIREMENT_UNKNOWN` — even the monotonic floor cannot be established from retained authenticated evidence.

`RETIREMENT_FLOOR_PROVEN_CONTINUITY_UNKNOWN` is intentionally asymmetric: it may continue to forbid resurrection of the retired verifier, but it must block destructive compaction or claims that one surviving checkpoint branch is canonical.

A later checkpoint may repair continuity only if it includes an authenticated recovery bridge that commits all surviving incompatible heads, the last undisputed predecessor digest, and the lost-range boundary. Re-signing the surviving head is not recovery.

If a checkpoint replica is missing but at least one retained independent replica still has the exact predecessor checkpoint and consistency path, continuity may be reconstructed and then re-replicated. If all replicas lost the same predecessor material, replication count cannot substitute for missing proof.

### C. Distributed unlearning worker-membership changes during an open proof snapshot

The proof snapshot and the worker membership are separate authenticated objects. Each proof epoch binds:

`(proof_epoch, dag_generation, dag_root, theorem_profile, worker_membership_generation, worker_membership_digest)`.

A worker-membership change while a proof epoch is open does **not** mutate the epoch in place.

Rules:

- removed workers may finish computation but their result is accepted only if they were authorized by the membership bound to that epoch and their credential was not revoked for the evaluation interval;
- added workers cannot contribute to the old epoch merely by reading the same DAG snapshot;
- a coordinator that needs the new membership starts a successor proof epoch that references the predecessor epoch and the same DAG snapshot if still current, or a new DAG snapshot if dependencies changed;
- mixed old/new membership results are not aggregated into one quorum;
- worker identity independence is evaluated by canonical failure domain, not process count;
- membership equivocation for the same generation makes the proof epoch `UNLEARNING_MEMBERSHIP_FORK` and blocks certificate issuance;
- a worker crash/restart must reacquire both the exact proof snapshot and membership generation before resuming.

A membership transition may reuse already verified deterministic sub-results only when those sub-results are content-addressed, bind the same DAG/theorem profile, and do not themselves represent quorum/independence evidence. Quorum attestations are epoch-specific and are never promoted across membership generations.

### D. Privacy participant-attestation revocation after coordinator failover

A participant attestation is authority-bearing accounting evidence. Every attestation binds stable participant identity/failure domain, `analysis_id`, accounting generation, reservation/consume/release claim, coordinator epoch, participant-set digest, and validity interval.

If a participant attestation is later revoked or its signer is shown compromised for the relevant interval **after coordinator failover**, the successor cannot merely delete that participant from the set and recompute a lower cost.

The affected analysis moves to `PRIVACY_ACCOUNTING_UNCERTAIN` unless independent evidence establishes a conservative bound. Recovery rules:

- already consumed privacy loss remains charged at least at the previously accepted floor;
- unresolved reservations remain reserved unless proven unused through independent durable evidence;
- if revocation makes the exact participant contribution unknowable, accounting uses the conservative upper bound permitted by the policy, not zero;
- coordinator failover never changes the `analysis_id` or accounting lineage;
- a replacement participant is a new attestation in a successor generation, not a rewrite of the predecessor participant;
- same-generation contradictory participant revocation states create `PRIVACY_ATTESTATION_FORK` and block release;
- re-signing the old participant claim under the successor coordinator is not independent evidence.

A revocation discovered after a release was durably committed triggers a compensating accounting generation if the conservative floor must increase. It does not rewrite history or mint fresh budget.

### E. Finality-checkpoint recovery after partial replica loss

A finality checkpoint replica stores an authenticated checkpoint, not merely a cache of the resolved value. Recovery distinguishes replica loss from evidence loss.

Each retained checkpoint binds:

- checkpoint generation and predecessor digest;
- SCC membership and dependency-generation vector;
- source-evidence digests;
- authority generation;
- unresolved gaps/forks/unknowns;
- compaction watermark;
- replica-set generation.

If some replicas are lost, survivors may restore redundancy only after proving that their checkpoint head is canonical with respect to the last jointly accepted checkpoint. A surviving replica with a later signed head but no consistency path from the last accepted predecessor is insufficient.

If surviving replicas present different valid heads for the same predecessor/generation, state is `FINALITY_CHECKPOINT_FORK`; no branch is selected by replica majority, timestamp, or highest sequence number unless the protocol's authenticated quorum evidence explicitly proves that selection.

If all surviving replicas agree on a head but the source evidence required to invalidate/re-evaluate that head was compacted everywhere, the recovered checkpoint remains usable only for monotonic quarantine floors that were independently authenticated; it cannot authorize a new destructive/retry action whose safety depends on the missing evidence.

Replica replacement starts from the accepted checkpoint plus its retained consistency/invalidation evidence. A new empty replica does not count toward checkpoint quorum until catch-up is proven.

### F. Safe `joint -> new` destructive-GC transition across crash/restart

The destructive-GC protocol already binds an immutable inventory/`CAN_RESTORE` snapshot and uses joint consensus during membership change. This slice freezes the final transition and recovery rules.

Durable phases are:

1. `GC_PREPARE(epoch, snapshot, C_old)`;
2. `GC_JOINT(epoch, snapshot, C_old, C_new)`;
3. `GC_PROOF_COMMITTED(epoch, snapshot, proof_digest, C_old, C_new)`;
4. `GC_DESTRUCTIVE_COMMITTED(epoch, destructive_receipt_digest, C_old, C_new)`;
5. `GC_NEW_CONFIG_COMMITTED(epoch, C_new)`;
6. `GC_CLOSED(epoch)`.

The old configuration may be retired only after `GC_NEW_CONFIG_COMMITTED` is durably replicated under the joint rule. The fact that the destructive side effect already happened is **not** permission to skip the configuration-transition proof.

Crash/restart rules:

- crash after destructive side effect but before durable `GC_DESTRUCTIVE_COMMITTED` -> side effect is `DESTRUCTIVE_EFFECT_UNKNOWN`; reconcile independently before any retry;
- crash after `GC_DESTRUCTIVE_COMMITTED` but before `GC_NEW_CONFIG_COMMITTED` -> resume in joint configuration; both old and new quorums remain authoritative for the transition;
- crash after local application of `C_new` but before durable replicated new-config commit -> local `C_new` is not authoritative; recover joint state;
- old members may be retired only after the new-config commit is proven from durable replicated log/state;
- a new leader/coordinator elected by `C_new` alone while joint transition is still the highest durable configuration cannot finalize the epoch;
- competing durable `GC_NEW_CONFIG_COMMITTED` records with different `C_new` digests create `GC_CONFIG_FORK` and block closure;
- after `GC_NEW_CONFIG_COMMITTED`, stale `C_old` nodes may not resurrect an earlier epoch or vote on future epochs, but their retained evidence may still be required for audit/reconciliation retention.

A membership transition and destructive effect therefore have separate finality. One cannot be inferred from the other.

## RED-first matrix (42 cases)

### Registry recovery-root compromise (1-7)
1. Registry fork resolved by recovery root later proven compromised during signing interval -> recovery becomes authority-uncertain.
2. Successor recovery root simply re-signs uncertain recovery event -> still uncertain.
3. Higher recovery-policy generation omits one registry fork head being superseded -> reject recovery.
4. Recovery threshold is met only by multiple keys in one canonical failure domain -> reject as insufficient independence.
5. Same-generation recovery policies name different recovery-root sets -> `RECOVERY_POLICY_EQUIVOCATION`.
6. Recovery-policy rollback re-enables revoked recovery root -> reject rollback.
7. Independent higher recovery policy commits all conflicting heads + last undisputed predecessor and meets post-compromise threshold -> accept successor registry head.

### Retirement partial checkpoint loss (8-14)
8. Retirement floor survives but predecessor consistency path is lost -> floor remains enforced; compaction/canonical-branch claim blocked.
9. One independent replica retains predecessor checkpoint + valid consistency path -> reconstruct continuity and re-replicate.
10. All replicas retain only the same successor head with no predecessor proof -> replication count does not prove continuity.
11. Two surviving successor heads extend unknown/lost predecessor incompatibly -> `RETIREMENT_CONTINUITY_UNCERTAIN`.
12. Recovery bridge commits only one surviving incompatible head -> reject.
13. Lost material concerns a verifier already below a higher authenticated retirement floor -> verifier remains non-resurrectable despite continuity uncertainty.
14. Operator attempts to reset retirement generation because predecessor checkpoint file is missing -> reject rollback.

### Unlearning worker-membership transition (15-21)
15. Added worker contributes quorum signature to already-open old-membership proof epoch -> reject.
16. Removed worker result was produced inside old membership validity interval and binds exact epoch -> may remain usable subject to revocation checks.
17. Removed worker credential revoked for evaluation interval -> invalidate its epoch contribution.
18. Coordinator mixes two old-membership and two new-membership votes into a threshold neither membership independently satisfies -> reject mixed quorum.
19. Same-generation worker-membership digests disagree -> `UNLEARNING_MEMBERSHIP_FORK`.
20. Successor proof epoch reuses deterministic content-addressed sub-result with identical DAG/profile but recomputes membership quorum -> allowed.
21. Worker restart reacquires DAG snapshot but not bound membership generation -> reject resumed result.

### Privacy participant-attestation revocation (22-28)
22. Participant attestation revoked after failover; consumed loss already charged -> never refund consumed floor.
23. Revoked participant had unresolved reservation and no independent unused proof -> reservation remains conservatively held.
24. Successor coordinator drops revoked participant and lowers accounting total -> reject.
25. Replacement participant is inserted by rewriting predecessor participant-set digest -> reject; require successor generation.
26. Same-generation valid revocation and valid non-revocation views conflict -> `PRIVACY_ATTESTATION_FORK`; block release.
27. Revocation discovered after release commit requires higher conservative floor -> append compensating accounting generation.
28. Successor coordinator re-signs old participant claim without independent participant/source evidence -> insufficient recovery.

### Finality checkpoint replica loss (29-35)
29. Majority of surviving replicas share a head but no consistency proof to last accepted checkpoint -> majority alone insufficient.
30. One survivor has last accepted predecessor + valid consistency path to candidate head -> candidate may seed replica recovery if no conflicting accepted head exists.
31. Surviving replicas expose same-generation incompatible heads -> `FINALITY_CHECKPOINT_FORK`.
32. Replacement replica votes before exact checkpoint/evidence catch-up -> reject vote.
33. Resolved value survives but all source-evidence digests/invalidation lineage were lost -> cannot authorize new destructive/retry action from value alone.
34. Replica loss removes unresolved-gap evidence while retained checkpoint claims clean finality -> reject incomplete recovery.
35. Recovered replica set rolls checkpoint generation backward to match oldest survivor -> reject rollback.

### GC `joint -> new` transition (36-42)
36. Crash after destructive side effect but before durable destructive-commit record -> reconcile `DESTRUCTIVE_EFFECT_UNKNOWN`; do not blindly retry.
37. Crash after durable destructive commit but before new-config commit -> resume joint membership.
38. Node locally applied `C_new` before crash but durable highest configuration remains joint -> recover joint, not local new-only.
39. New-only quorum finalizes membership while durable joint transition remains open -> reject.
40. Old members are deleted immediately after destructive commit but before new-config commit -> forbidden; transition evidence still depends on them.
41. Two different `C_new` commits claim same joint predecessor/epoch -> `GC_CONFIG_FORK`; block close.
42. Durable new-config commit proven under joint rule -> retire old voting authority for future epochs while retaining required audit/reconciliation evidence.

## Audit

- No recovery path derives authority from wall-clock freshness, arrival order, local availability, self-signature, replica count, or coordinator identity.
- Compromise of a recovery root is treated as compromise of the authorization event, not merely as a key-rotation inconvenience.
- Partial checkpoint loss preserves monotonic safety floors even when canonical continuity cannot be proven.
- Membership changes create successor proof/accounting/consensus generations; they do not mutate open epochs in place.
- Privacy revocation is conservative: consumed loss never decreases and unresolved claims never become zero by disappearance.
- Replica recovery distinguishes replicated state from authenticated provenance; copying a value is not the same as restoring evidence.
- Destructive-effect finality and membership-transition finality are separate state machines.
- Split-view/equivocation remains explicit and blocks destructive/release/compaction operations until a higher authenticated recovery generation commits the conflict.

## Implementation direction

When exact source execution becomes available, add tests before production refactors. Prefer explicit immutable records for:

- recovery-policy head and recovery-event digest;
- retirement checkpoint-loss classification and recovery bridge;
- proof-epoch worker-membership binding;
- privacy participant revocation/compensation generation;
- finality replica-set generation and accepted-checkpoint proof;
- GC configuration phase and destructive-effect receipt.

Tests should assert both state result and non-mutation on rejection. Recovery tests must exercise restart from durable state, not only in-memory transitions. Every compaction/GC/release action should prove the predecessor generation and exact authority/membership snapshot it consumes.

No executable PASS is claimed by this research freeze.