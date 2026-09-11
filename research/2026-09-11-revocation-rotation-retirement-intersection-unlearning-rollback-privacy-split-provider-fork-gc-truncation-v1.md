# Transition-proof contracts across compacted authority changes — V1

Date: 2026-09-11
Status: `REVOCATION_ROTATION_RETIREMENT_INTERSECTION_UNLEARNING_ROLLBACK_PRIVACY_SPLIT_PROVIDER_FORK_GC_TRUNCATION_V1_FROZEN`
Scope: architecture/evidence contract only; RED/GREEN execution is still pending exact executable source.

## Why this slice exists

The previous freezes established monotonic recovery, retirement, unlearning, privacy, provider-effect and GC invariants under compaction, rotation and partial evidence loss. The remaining gap is narrower and more dangerous: **what authenticates a transition when the old and new authority sets may be disjoint, one side has been retired/compromised, and detailed history has already been compacted or truncated?**

This note freezes six contracts before implementation:

1. recovery revocation-policy succession after the revocation authority itself rotates or is compromised;
2. retirement-bridge quorum continuity when witness sets are disjoint across generations;
3. unlearning migration rollback after the source result store has been retired;
4. privacy Merkle split/merge when branches advance independently before reconciliation;
5. provider-effect reconciliation when receipts are individually valid but provider-generation lineage forks;
6. GC snapshot install/recovery when the membership proof spans a truncated Raft joint-consensus boundary.

No executable PASS is claimed here. The current runtime again could not clone GitHub directly (`Could not resolve host: github.com`), so LAB-086 remains ahead of this design work in priority.

---

## Primary donor mechanisms re-checked

### TUF root succession / rollback protection

TUF root updates are useful because a new trust root is not accepted merely because it is self-consistent. Root succession is authenticated across generations and version rollback is rejected. The reusable mechanism here is **predecessor-to-successor continuity plus monotonic generation**, not TUF's package-update domain itself.

Primary source: https://theupdateframework.io/specification/latest/

### RFC 9162 Merkle consistency

Certificate Transparency separates possession of a signed tree head from proof that two tree heads belong to one append-only history. Merkle consistency proofs authenticate that an earlier prefix remains embedded in a later tree. The reusable mechanism is **signed head != continuity proof**.

Primary source: https://www.rfc-editor.org/rfc/rfc9162.html

### NIST SP 800-226 privacy accounting

NIST's differential-privacy guidance treats privacy budgeting as cumulative across answered queries/releases. Deleting, moving or re-indexing released results does not erase already incurred privacy loss. The reusable mechanism is **one logical released-event lineage and cumulative loss accounting across representation changes**.

Primary source: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-226.pdf

### AWS idempotent mutation guidance

Idempotency tokens allow retries of one logical mutation without duplicating effects. A returned receipt can prove a particular request/effect, but idempotency does not by itself prove that the provider-generation lineage in which that receipt was produced is still the unique authoritative lineage. The reusable mechanism is **stable effect identity is necessary but not sufficient for lineage authority**.

Primary source: https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_prevent_interaction_failure_idempotent.html

### Raft joint consensus

Raft explicitly rejects direct old-config -> new-config switching because disjoint majorities can exist during transition. Joint consensus requires overlapping authorization across the transition before the new configuration acts alone. The reusable mechanism is **when authority sets can be disjoint, transition proof must cover both sides; cardinality in the successor set is not continuity**.

Primary source: https://raft.github.io/raft.pdf

---

# Contract A — revocation authority succession after rotation/compromise

## Problem

A compact recovery certificate may bind recovery generation `g`, signer/failure-domain cut-set, and revocation-policy generation `r`. Later, the revocation authority itself rotates from `R_old` to `R_new`, or `R_old` is discovered compromised.

Two unsafe shortcuts are possible:

- treat any certificate valid under the old revocation view as still sufficient for *new* recovery decisions;
- let `R_new` self-authorize succession without proving why it replaced `R_old` and which competing revocation heads were known at the boundary.

The first permits stale authority resurrection. The second lets a newly asserted revocation set rewrite trust history.

## Frozen contract

A revocation-policy transition record MUST bind:

- `revocation_generation_old` and `revocation_generation_new` with exact `+1` succession;
- immutable IDs/digests of `R_old` and `R_new` policies;
- the compact recovery-policy head/floor being governed at transition time;
- a commitment to every known competing revocation-policy head at the transition boundary;
- a transition reason class (`ROTATION`, `COMPROMISE_RECOVERY`, `EMERGENCY_ROOT_RECOVERY`);
- the authority path used to authorize the transition.

Normal rotation requires authenticated continuity from both old and new policy sets, analogous to joint consensus/TUF root succession.

Compromise recovery is different: a known-compromised `R_old` MUST NOT be treated as sufficient continuity authority merely because it can still sign. The successor must instead be authorized by an already-defined independent recovery/root authority whose failure domain is outside the compromised cut set. The record must explicitly mark which predecessor authority was considered compromised and why its signature is historical evidence rather than positive authorization.

A compact recovery certificate created under `r_old` remains historical evidence for decisions made while that policy was authoritative. It does **not** silently authorize new recovery after `r_new` becomes effective.

Same-generation competing revocation-policy heads are a fork. A later resolver must commit all known heads; choosing one by timestamp, lexicographic ID, signer count or local arrival order is forbidden.

## Failure states

- `REVOCATION_POLICY_ROLLBACK`
- `REVOCATION_POLICY_FORK`
- `REVOCATION_SUCCESSION_UNPROVEN`
- `REVOCATION_PREDECESSOR_COMPROMISED`
- `RECOVERY_CERTIFICATE_STALE_POLICY`

## Eight RED-first cases

A1. valid `r1` certificate, rotate to `r2`, then attempt fresh recovery using only `r1` -> reject stale policy.

A2. `R_old` and `R_new` are disjoint; successor self-signs only -> reject succession unproven.

A3. normal rotation carries valid old+new authorization -> accept `r2` as successor.

A4. `R_old` declared compromised but its signature is counted as sufficient predecessor continuity -> reject.

A5. independent emergency/root authority outside compromised cut set authorizes `r2`, explicitly recording compromised predecessor -> accept only if that authority was itself already anchored.

A6. two different `r2` heads exist with valid-looking thresholds -> classify fork; neither silently dominates.

A7. `r3` resolver commits only one known `r2` head -> reject incomplete fork resolution.

A8. rollback from authenticated `r3` to otherwise-valid `r2` certificate -> reject monotonic rollback.

---

# Contract B — retirement bridge continuity across disjoint witness sets

## Problem

Verifier retirement uses a monotonic non-resurrection floor. Across witness-policy generations, however, the witness sets can become completely disjoint. If generation `W2` can simply re-state the same or higher floor and self-sign it, then there is no proof that `W2` inherited the old retirement history rather than creating a fresh namespace.

Equal floor numbers are not provenance.

## Frozen contract

Every retirement bridge generation MUST bind:

- predecessor bridge ID/root;
- successor bridge ID/root;
- monotonic retirement floor;
- old witness-policy generation/set/threshold commitment;
- new witness-policy generation/set/threshold commitment;
- transition authorization proving continuity across the two policies;
- any known competing bridge heads.

When witness sets overlap, overlap is useful evidence but not the sole rule. When sets are disjoint, transition authorization MUST be joint: sufficient authorization under `W_old` **and** `W_new`, or a previously anchored higher recovery/root authority explicitly empowered to replace `W_old` after compromise/loss.

A higher numerical floor signed only by the successor set is not continuity proof.

Witness revocation changes who may authorize future bridge transitions; it never lowers the already authenticated non-resurrection floor and never resurrects an older verifier.

## Failure states

- `RETIREMENT_BRIDGE_SUCCESSION_UNPROVEN`
- `RETIREMENT_WITNESS_POLICY_FORK`
- `RETIREMENT_FLOOR_ROLLBACK`
- `RETIREMENT_PROVENANCE_AMBIGUOUS`

## Eight RED-first cases

B1. disjoint `W1`/`W2`, same floor, `W2` self-signs -> reject.

B2. disjoint `W1`/`W2`, higher floor, `W2` self-signs -> reject; higher value is not provenance.

B3. disjoint sets with valid old+new transition authorization -> accept successor bridge.

B4. old witness set unavailable due to a documented compromise and pre-anchored emergency authority authorizes replacement -> accept only through explicit emergency transition type.

B5. successor bridge presents lower floor but otherwise valid joint signatures -> reject rollback.

B6. equal floors with different predecessor roots -> do not deduplicate; classify provenance ambiguity/fork.

B7. revoke a `W1` witness after bridge commit, then attempt to resurrect verifier below floor -> reject; revocation does not undo historical retirement.

B8. compact away detailed `W1` signatures but retain authenticated bridge/root + joint-transition proof -> restart must preserve the same floor; absence of detailed signatures cannot reset namespace.

---

# Contract C — unlearning migration rollback after source-store retirement

## Problem

A result store `S1` is migrated to `S2`, carrying unlearning result IDs, theorem/profile generations, invalidation frontier and descendant-closure commitment. After migration succeeds, `S1` is retired or deleted.

Later rollback can happen in two ways:

- restore an older snapshot of `S2` from before migration completed;
- recreate/re-enable `S1` and treat it as authoritative because its local data is internally valid.

If the migration contract lives only inside `S1`, source retirement destroys the very evidence needed to reject rollback.

## Frozen contract

Migration completion MUST produce an external/independent succession checkpoint binding:

- logical unlearning lineage ID;
- source store generation/identity;
- source terminal checkpoint/root;
- destination store generation/identity;
- destination imported checkpoint/root;
- immutable result-ID set/range commitment;
- theorem/profile generation;
- invalidation frontier;
- descendant-closure root;
- migration generation and completion status;
- source retirement generation/floor.

Once the source retirement checkpoint is authoritative, `S1` can remain read-only evidence but cannot regain positive result authority without a new authenticated reverse-migration/recovery transition. Deleting and recreating `S2` from a pre-migration snapshot must fail against the independent migration/retirement head.

Unknown/missing descendant closure after rollback is never converted to a positive cache hit.

## Failure states

- `UNLEARNING_MIGRATION_ROLLBACK`
- `UNLEARNING_SOURCE_RETIRED`
- `UNLEARNING_DESTINATION_BEHIND_MIGRATION_HEAD`
- `UNLEARNING_CLOSURE_INCOMPLETE`
- `UNLEARNING_DEPENDENCY_UNKNOWN`

## Eight RED-first cases

C1. complete S1->S2 migration, retire S1, restart S2 from pre-import snapshot -> reject destination behind migration head.

C2. recreate S1 after retirement and query a formerly valid result -> reject source-retired authority.

C3. S2 contains result rows but lacks imported descendant-closure commitment -> no positive cache result.

C4. S2 has matching closure root but older theorem/profile generation -> require revalidation/reject stale result.

C5. S2 exact imported checkpoint matches external succession checkpoint -> allow normal authority according to current invalidation rules.

C6. reverse migration S2->S1 without an authenticated new migration generation -> reject resurrection.

C7. reverse migration with explicit successor generation committing current S2 terminal head and retirement state -> permit only as a new lineage transition, never as rollback.

C8. source detailed rows deleted after retirement but external migration checkpoint survives -> restart still rejects old-source authority and destination rollback.

---

# Contract D — privacy Merkle split/merge with independently advanced branches

## Problem

A privacy event ledger is split into branches/shards `P_A` and `P_B`. Both answer queries independently and incur privacy loss. Later they merge.

Dangerous shortcuts:

- treat each restored/split branch as owning a fresh full privacy budget;
- pick the tighter of two cumulative bounds at merge;
- add both branch totals without detecting duplicate events replayed into both branches;
- deduplicate merely because event labels match, even when payload/accounting semantics differ.

## Frozen contract

A split checkpoint MUST bind:

- one immutable parent privacy-lineage ID;
- parent event-set root/range/count and cumulative bound;
- branch IDs and parent checkpoint;
- explicit budget allocation/reservation contract if branches are allowed independent spending;
- accountant method/profile generation.

Every released event MUST have an immutable event ID bound to canonical query/release semantics and accountant inputs.

A merge checkpoint MUST authenticate both branch heads and compute over the set union of released events. Identical authenticated event IDs with identical canonical event commitments count once; the same event ID bound to different contents is a fork/error, not a deduplication opportunity.

The successor cumulative privacy bound must conservatively cover all unique released events from both branches under a supported composition rule. It must not choose `min(bound_A, bound_B)`, and deletion/compaction does not refund loss.

If the parent budget was explicitly partitioned, branch spending must stay within its authenticated allocation unless a new allocation transition is authorized. If no partition contract exists, split representation alone does not create independent full budgets.

## Failure states

- `PRIVACY_LINEAGE_FORK`
- `PRIVACY_EVENT_ID_COLLISION`
- `PRIVACY_SPLIT_ALLOCATION_MISSING`
- `PRIVACY_BRANCH_BUDGET_EXCEEDED`
- `PRIVACY_MERGE_UNDERACCOUNTED`
- `PRIVACY_EVENTSET_CONTINUITY_UNKNOWN`

## Eight RED-first cases

D1. split parent into A/B without allocation, each branch assumes full remaining budget -> reject independent spending authority.

D2. authenticated allocation gives A/B disjoint spending envelopes; both remain within envelope -> merge can proceed after union accounting.

D3. A and B independently release different events; merge chooses smaller cumulative bound -> reject under-accounting.

D4. same authenticated event ID/content is replayed into both branches -> count once at merge, preserve evidence of dual inclusion.

D5. same event ID but different canonical release/accounting commitment -> classify event-ID collision/fork; do not choose one.

D6. branch raw events compacted but branch Merkle head + consistency/range proof retained -> merge allowed only if union/disjointness can still be proven.

D7. branch root exists without proof to parent split checkpoint -> event-set continuity unknown; block new releases requiring merged budget authority.

D8. after merge, restore pre-merge branch A and attempt additional releases under old allocation -> reject stale branch lineage.

---

# Contract E — provider receipts valid while provider-generation lineage forks

## Problem

Effect receipts can be cryptographically valid and idempotency-correct while being attached to incompatible provider-generation histories. Example: generations `g2a` and `g2b` both descend from `g1` due to a control-plane fork; each provider produces a valid receipt for an effect ID. Receipt verification alone cannot decide which lineage owns authority.

## Frozen contract

Every provider effect receipt MUST bind:

- immutable logical effect ID/idempotency token;
- canonical operation parameters;
- provider generation ID;
- provider-generation parent/head commitment;
- effect sequence/fence position when applicable;
- terminal provider result/evidence generation;
- receipt signer/provider identity.

Reconciliation validates two different things:

1. **effect evidence** — is the receipt authentic for that provider generation and request?
2. **lineage authority** — is that provider generation on the unique authenticated generation lineage currently allowed to mutate/reconcile?

A valid receipt on a non-authoritative or forked generation is evidence that an external effect may have happened; it is not permission to replay, compensate, confirm or erase that effect automatically.

If conflicting provider-generation heads are unresolved, all effects whose interpretation depends on choosing a head become `PROVIDER_EFFECT_LINEAGE_FORK`. Compensation must itself use a separate immutable effect ID and cannot be issued merely to make local state match one preferred fork.

## Failure states

- `PROVIDER_GENERATION_FORK`
- `PROVIDER_EFFECT_LINEAGE_FORK`
- `PROVIDER_RECEIPT_STALE_GENERATION`
- `PROVIDER_EFFECT_UNKNOWN_AUTHORITY`
- `PROVIDER_COMPENSATION_UNSAFE_DURING_FORK`

## Eight RED-first cases

E1. valid receipt on unique current generation -> normal reconciliation allowed.

E2. valid receipt on stale but historically unique generation for an already-finalized historical effect -> retain as historical evidence; no new dispatch authority.

E3. valid receipts on `g2a` and `g2b` where both descend from g1 and neither fork resolved -> classify lineage fork.

E4. choose receipt from fork by newest timestamp -> forbidden.

E5. choose fork by higher provider generation number with no authenticated succession proof -> forbidden.

E6. issue compensation for effect on g2a while g2a/g2b authority fork unresolved -> block as unsafe.

E7. later resolver commits all known generation heads and selects successor via authenticated transition; reconcile prior receipts as historical effect evidence under resolved lineage without replaying them.

E8. idempotency retention expires during unresolved lineage fork -> expiry does not prove no effect and does not authorize blind redispatch.

---

# Contract F — GC snapshot recovery across truncated joint-consensus membership boundary

## Problem

Consensus history changes membership `C_old -> C_joint -> C_new`. Later a snapshot is installed and old log entries are truncated. GC/destructive maintenance depends on knowing which membership configuration had authority at the relevant commit/finality index.

A snapshot may contain `C_new` state without proving that `C_joint` and then `C_new` were actually committed. After truncation, the evidence required to distinguish "installed" from "committed" can disappear.

## Frozen contract

Any snapshot that truncates across a membership transition MUST retain a compact membership-finality proof package containing at least:

- last included consensus index/term;
- effective configuration at that index;
- old config commitment;
- joint config commitment and commit/finality evidence;
- new config commitment and commit/finality evidence, if transition completed;
- quorum/voter-set commitments needed to verify the relevant commit rules;
- predecessor snapshot/proof root when prior detailed log is no longer retained;
- snapshot generation and monotonic succession proof.

If the snapshot is taken while joint consensus is active, it must preserve the joint configuration as active authority; it cannot normalize prematurely to `C_new`.

If a recovery node receives a snapshot containing `C_new` but cannot verify the compact proof that `C_joint` and `C_new` reached the required commit/finality boundary, it may use the bytes as untrusted recovery material but MUST NOT grant destructive GC authority from that membership claim.

Truncation is permitted only after the compact proof package itself is durably authenticated and covered by the successor snapshot/root.

## Failure states

- `GC_MEMBERSHIP_FINALITY_UNKNOWN`
- `GC_JOINT_BOUNDARY_PROOF_MISSING`
- `GC_SNAPSHOT_MEMBERSHIP_ROLLBACK`
- `GC_SNAPSHOT_SUCCESSION_FORK`
- `GC_DESTRUCTIVE_AUTHORITY_BLOCKED`

## Eight RED-first cases

F1. snapshot says `C_new`, logs containing `C_joint`/commit proof truncated, no compact transition proof -> block destructive GC.

F2. snapshot taken during active `C_joint` but serialized as `C_new` only -> reject premature normalization.

F3. snapshot preserves active `C_joint` plus required old/new voter commitments -> recovery retains joint commit rule.

F4. final `C_new` committed, compact package proves old->joint->new transition before truncation -> snapshot may carry `C_new` authority.

F5. restore an older snapshot whose membership generation precedes authenticated successor snapshot -> reject rollback.

F6. two same-generation snapshots carry different membership proof roots -> classify snapshot succession fork.

F7. detailed consensus log deleted but authenticated compact membership-finality chain survives -> destructive GC may continue only within proven scope/floor.

F8. compact proof itself is lost after truncation -> classify finality unknown/proof unrecoverable; fail closed rather than infer authority from surviving state-machine data.

---

# Cross-contract invariants

The six contracts reduce to the same safety pattern:

1. **A successor's self-consistency is not succession proof.** New signatures, a higher counter, a newer timestamp, a tighter bound or a state snapshot do not prove continuity by themselves.
2. **Disjoint authority sets require explicit transition authorization.** Normal transitions need both sides (joint authorization) unless a previously anchored independent emergency authority is intentionally invoked.
3. **Compromise changes evidentiary role.** A compromised predecessor may remain historical evidence, but must not be counted as the independent authorization used to escape its own compromise.
4. **Compaction may replace detail with a commitment, not erase the invariant.** After detail is discarded, the compact artifact must still prove the monotonic floor/head/event-set/membership property required for future decisions.
5. **Forks remain forks until an authenticated resolver commits all known heads.** Never resolve by timestamp, local arrival, lexical ID, "largest value", signer count or whichever branch is easiest to execute.
6. **Destructive operations need stronger evidence than read-only recovery.** When continuity is unknown, it can be acceptable to retain material for investigation/read-only reconstruction while blocking mutation, confirmation, compensation, new privacy releases or destructive GC.

---

# Combined 48-case matrix

The RED-first executable matrix is the union of A1-A8, B1-B8, C1-C8, D1-D8, E1-E8 and F1-F8 above (48 cases total).

Implementation order when exact source becomes executable:

1. Encode the transition record/checkpoint types and canonical payloads first.
2. Add RED regressions for self-authorized/disjoint successor transitions before adding production acceptance paths.
3. Add monotonic/fork detection and explicit emergency-authority branches.
4. Add compaction/truncation regressions proving compact evidence preserves decisions after detail deletion.
5. Add restart/recovery tests from byte-exact persisted snapshots/stores.
6. Run downstream security gates and compileall; no design freeze is a substitute for those tests.

## Expected implementation discipline

- Canonical payloads must bind every authority-relevant field listed above; do not rely on mutable side tables as their own provenance.
- Transition verification must be deterministic and independent of local wall clock/order of arrival.
- Emergency recovery must be separately typed/audited; do not silently weaken normal joint authorization.
- Unknown evidence state must have explicit fail-closed enums/exceptions rather than being mapped to empty/fresh state.
- Durable stores may cache derived status, but cache values are hints unless they are themselves committed by the authenticated lineage.

## Non-claims

- This note does not claim the exact repository behavior currently violates every RED case; several are forward design contracts for frozen LAB-093..100 follow-up work.
- This note does not claim LAB-086, LAB-088, LAB-090, LAB-091 or LAB-092 executable gates passed in this runtime.
- This note does not authorize merging any current draft PR.

## Verdict

`REVOCATION_ROTATION_RETIREMENT_INTERSECTION_UNLEARNING_ROLLBACK_PRIVACY_SPLIT_PROVIDER_FORK_GC_TRUNCATION_V1_FROZEN`

The central rule is now explicit: **when authority crosses a boundary and the predecessor may later disappear, be revoked, be compromised, or become disjoint from the successor, continuity must be proved at the boundary and carried forward in compact authenticated form.** A surviving successor state is never enough evidence on its own.