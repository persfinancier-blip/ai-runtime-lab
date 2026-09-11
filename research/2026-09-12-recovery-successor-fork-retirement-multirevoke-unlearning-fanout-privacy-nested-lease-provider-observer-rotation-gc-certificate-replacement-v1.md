# Recovery successor fork + retirement multirevoke + unlearning fan-out + nested privacy lease + provider observer rotation + GC certificate replacement v1

Date: 2026-09-12
Status: DESIGN FROZEN / RED-FIRST CONTRACT ONLY
Parent follow-up: LAB-093 / #178
Execution note: this artifact does **not** substitute for executable RED/GREEN proof.

## Why this slice exists

LAB-086 remains the highest-priority executable gate, but this run again could not materialize its exact pinned source into the local executor: direct `git clone --no-checkout` failed before repository code ran with `Could not resolve host: github.com`. The connector can read and write repository bytes but does not expose a supported whole-closure byte-exact materialization primitive. Per the durable handoff, manual/model reserialization is prohibited for this security-critical gate.

The next distinct evidence task is therefore frozen here rather than inventing execution evidence.

## Contract name

`RECOVERY_SUCCESSOR_FORK_RETIREMENT_MULTIREVOKE_UNLEARNING_FANOUT_PRIVACY_NESTED_LEASE_PROVIDER_OBSERVER_ROTATION_GC_CERT_REPLACEMENT_V1_FROZEN`

## Primary donor mechanisms re-verified

1. **TUF 1.0.36** — root/key rotation is authenticated through previously trusted authority; threshold trust and revocation are explicit, and rollback/mix-and-match attacks are security failures rather than normal reconciliation outcomes. Relevant mechanisms: root succession, threshold signatures, revocation, rollback resistance, delegated trust. Source: https://theupdateframework.github.io/specification/latest/
2. **RFC 9162** — a signed tree head is not itself proof that two views are append-only compatible; consistency proofs authenticate continuity between heads. This is the model for compact authenticated-history bridges after detail is discarded. Source: https://www.rfc-editor.org/rfc/rfc9162.html
3. **NIST SP 800-226** — privacy budget is an upper bound on cumulative privacy loss across analyses; composition therefore survives allocator rotation, delegation, partition and result deletion. Source: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-226.ipd.pdf
4. **AWS idempotency guidance** — retries of the same mutation use a stable token and must not create a second effect; token retention is finite in concrete APIs, so expiry means deduplication evidence may no longer be available, not that an earlier external effect did not happen. Sources: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html and https://docs.aws.amazon.com/wellarchitected/2025-02-25/framework/rel_prevent_interaction_failure_idempotent.html
5. **Raft** — membership changes require an overlap/joint-consensus transition so two disjoint majorities cannot both decide; snapshots retain state needed to continue safely after log compaction. Source: https://raft.github.io/raft.pdf

These donors are analogical constraints, not copied implementations.

---

## A. Recovery common-successor whose own compromise evidence later forks

### Problem

Suppose recovery forks `R1a` and `R1b` are reconciled by common successor `R2`. Later evidence itself forks about whether `R2` was already compromised when it signed the reconciliation, producing histories `C2a` and `C2b`. A self-consistent descendant of `R2` must not be allowed to choose the compromise history that preserves its own authority.

### Frozen rules

- Compromise timing is authenticated ordering/interval evidence, never trusted wall-clock metadata.
- `R2` can reconcile `R1a/R1b` only if its succession evidence commits to both known competing heads and satisfies the required independent failure-domain cut-set.
- A later fork over `R2` compromise validity creates `RECOVERY_SUCCESSOR_AUTHORITY_AMBIGUOUS` unless a common successor after both compromise branches authenticates an ordering that resolves them.
- Historical statements signed before an authenticated compromise boundary may remain historically valid; prospective signing authority after the boundary is denied.
- A descendant may not use its own key lineage as the sole evidence that its ancestor was uncompromised.
- Compaction must retain a commitment to the competing compromise histories and the proof used to resolve them.

### RED-first matrix A (8)

A1. clean R1a/R1b -> R2 reconciliation with independent cut-set: accept.
A2. R2 reconciliation omits known R1b head: reject.
A3. later C2a/C2b disagree on whether R2 was compromised before reconciliation: ambiguous/fail closed.
A4. later common successor R3 commits to C2a+C2b and authenticated order proves compromise after R2 reconciliation: historical R2 reconciliation retained, R2 prospective authority revoked.
A5. same as A4 but order proves compromise before reconciliation: R2 reconciliation invalid; descendants require re-reconciliation from still-valid predecessor authority.
A6. R3 signed only by domains inherited from disputed R2 cut-set: reject independence.
A7. compact checkpoint drops one compromise branch commitment: reject checkpoint as insufficient authority evidence.
A8. same-generation alternative R3 heads claim opposite compromise resolutions: explicit recovery fork, never newest-wins.

---

## B. Multi-generation retirement historical-statement revocation and compaction

### Problem

Retirement bridges may successively revoke prospective authority while preserving some historical statements. After several generations and compaction, a later revocation may target an earlier historical statement itself. The system must distinguish prospective revocation from authenticated retroactive invalidation without lowering non-resurrection floors.

### Frozen rules

- Each retirement transition carries separate fields for `prospective_authority_floor` and `historical_statement_validity`.
- Prospective revocation never by itself erases already-authenticated historical evidence.
- Retroactive historical-statement revocation requires an authority chain that was already authorized to make that class of revocation and an authenticated ordering against competing revocations.
- Non-resurrection floors are monotonic even when historical statements are invalidated; invalidating proof cannot revive the retired verifier/key/store.
- Compaction must preserve enough bridge commitments to prove the maximum non-resurrection floor plus any unresolved historical-statement dispute.
- Mutually exclusive revocation branches need a common authenticated successor; generation number alone cannot choose one.

### RED-first matrix B (8)

B1. g1 retire -> g2 prospective revoke g1 -> g3 compact: g1 never regains prospective authority.
B2. g3 retroactively invalidates one g1 historical statement with valid revocation authority/order: statement rejected, retirement floor retained.
B3. retroactive revocation signed only by the already-retired g1 authority: reject.
B4. two same-generation revocations invalidate opposite historical statements: fork/fail closed.
B5. common successor covers both revocation heads and orders one after the other: reconcile according to authenticated order while retaining max floor.
B6. compaction retains floor but drops unresolved historical-statement fork commitment: reject compact bridge.
B7. deleting the statement targeted by revocation and replaying an older compact checkpoint: rollback reject.
B8. later verifier sees no detailed generations but valid compact bridge chain carrying max floor + dispute resolution: accept without resurrecting old authority.

---

## C. Unlearning lineage when S4 fans out into independently compacted S5/S6 descendants

### Problem

After S3->S4 migration, S4 may fan out into stores S5 and S6. Each branch can independently compact lineage and invalidation detail. If one branch later learns an invalidation that covers S4 ancestry, the other branch cannot treat its compact root as proof of unaffected lineage merely because local detail was discarded.

### Frozen rules

- Fan-out creates explicit branch identities rooted in the same authenticated S4 lineage checkpoint.
- Every compact descendant root carries an `unlearning_obligation_root` committing to unresolved invalidation/dependency obligations, not only surviving object hashes.
- An invalidation whose ancestry may intersect a compacted branch propagates as `DEPENDENCY_UNKNOWN` unless a full-closure proof establishes non-intersection.
- Reconciliation of S5/S6 takes the union of known invalidations and unresolved dependency obligations.
- Local compaction cannot downgrade `UNKNOWN -> CLEAR`.
- A re-migration S5->S7 carries S5's unresolved obligations transitively.

### RED-first matrix C (8)

C1. S4 fan-out to S5/S6 with identical clean obligation root: both valid.
C2. S5 learns invalidation definitely covering S4 ancestor; S6 lacks detail: S6 becomes unknown, not clear.
C3. S6 supplies authenticated full-closure proof of non-intersection: S6 may clear independently.
C4. S5 compact root omits its known invalidation obligation: reject root.
C5. S6 compact root created before invalidation and replayed after reconciliation: rollback/reconciliation reject.
C6. S5->S7 migration preserves unknown obligation: S7 remains unknown.
C7. S5/S6 independently compact different descendant subsets but same obligation union: merge allowed with canonical union proof.
C8. one branch fabricates absence by deleting local invalidation rows before compaction: compact checkpoint fails authenticated obligation-root continuity.

---

## D. Nested privacy-budget lease delegation across allocator generations and partition heal

### Problem

Allocator A0 may lease budget to A1, which subleases to A2. During a partition A0 rotates to A0', while A1/A2 continue spending. Wall-clock expiry, allocator generation changes, or deletion of results cannot make spent or conservatively reserved budget reappear.

### Frozen rules

- Delegation forms an authenticated lease tree; child ceilings are subsets of parent ceilings, never independent budgets.
- A lease records immutable scope, parent lease id, allocator generation, maximum delegated epsilon/delta (or mechanism-specific accounting state), and authenticated close/reclaim evidence.
- Rotation of an allocator generation does not duplicate unspent delegated capacity.
- Partition heal computes cumulative released-event union plus conservative bounds for unresolved open leases at every nesting level.
- Wall-clock expiry alone never reclaims capacity; reclaim requires authenticated closure proving unused remainder and no unresolved descendants.
- Deleting/invalidating a released result does not refund incurred privacy loss.
- Conflicting lease-close checkpoints create an accounting fork and force conservative maximum exposure until resolved.

### RED-first matrix D (8)

D1. A0 delegates 0.6 to A1; A1 delegates 0.4 to A2: total capacity remains bounded by A0 budget.
D2. A0 rotates while A1 lease open; A0' cannot reissue A1's full 0.6 as fresh capacity.
D3. partition: A2 spends near limit while A0' spends remaining root capacity; heal rejects/flags overrun based on union.
D4. A1 lease wall-clock expires with unresolved A2: no reclaim.
D5. authenticated A2 close + A1 close prove unused remainder: reclaim only proven unused amount.
D6. released A2 result later deleted: spend remains charged.
D7. two close checkpoints report incompatible residuals: accounting fork; use conservative worst case.
D8. compact privacy checkpoint drops parent-child lease relation but preserves only final residual scalar: reject as insufficient to prove non-duplication.

---

## E. Provider observer authority rotation/compromise with pre/post-rotation observations

### Problem

External-effect reconciliation may depend on authenticated observers in addition to transport outcomes and provider receipts. Observer authority itself can rotate or be compromised. A late observation must therefore be judged by authenticated authority interval and effect identity, not arrival time.

### Frozen rules

- Transport outcome, provider receipt, observer statement, and externally visible effect remain separate evidence classes.
- Observer statements commit to immutable `effect_id`, observation type/state, observer authority generation, and authenticated sequence/interval evidence.
- Rotation requires predecessor->successor continuity; old observer keys lose prospective authority after the authenticated boundary.
- A pre-rotation statement remains historically usable if its observation interval is proven before compromise/revocation.
- Post-revocation old-key statements are rejected even if they arrive later with syntactically valid signatures.
- Conflicting valid observer generations create an evidence fork until a common authority/order proof resolves them.
- Receipt/idempotency retention expiry never converts `UNKNOWN` into `NO_EFFECT`.

### RED-first matrix E (8)

E1. O1 observes effect before clean O1->O2 rotation: historical observation accepted.
E2. O1 statement signed after authenticated rotation boundary: reject prospective authority.
E3. O1 compromise later proven to predate its observation: observation invalid/unknown, not automatically no-effect.
E4. O2 independently observes same effect and binds same effect_id: reconcile without duplicate mutation.
E5. O1 says NO_EFFECT, O2 says EFFECT_PRESENT with incomparable authenticated intervals: evidence fork; no blind replay.
E6. common O3 authority orders both observations and external audit proves effect present: settle to effect-present while retaining conflicting history.
E7. provider receipt retention expired before observer conflict: proof unavailable; do not infer absence.
E8. attacker reuses observer statement with different effect parameters but same transport request: reject effect-id/parameter binding mismatch.

---

## F. GC compact membership-certificate revocation/replacement after multiple fully truncated joint-consensus transitions

### Problem

After C0->C1 and C1->C2 membership transitions, detailed Raft log entries may be fully truncated and only compact certificates/snapshots remain. A later discovery can revoke or replace one compact certificate. Recovery must not accept terminal membership C2 merely because it appears in the newest snapshot.

### Frozen rules

- Each compact membership certificate commits to predecessor configuration/certificate, joint transition proof, successor configuration, and included log/snapshot boundary (`lastIncludedIndex`, `lastIncludedTerm` or equivalent authenticated position).
- Successive transitions form a certificate chain; terminal membership alone is insufficient.
- Certificate revocation/replacement is itself an authenticated transition with predecessor continuity and monotonic sequence.
- Revoking C0->C1 proof invalidates descendants that cannot independently prove an equivalent safe bridge; it does not authorize fallback to C0 destructive authority.
- Competing replacement certificates at the same generation are an explicit membership-proof fork.
- Recovery across snapshots with different truncation boundaries requires proof that both descend from a compatible committed membership chain.

### RED-first matrix F (8)

F1. valid compact certs C0->C1 and C1->C2 after full log truncation: recover C2.
F2. newest snapshot names C2 but omits C0->C1 certificate commitment: reject.
F3. C0->C1 certificate later revoked with no replacement: C2 destructive authority unavailable/fail closed.
F4. authenticated replacement proves equivalent safe C0->C1' bridge and C1'->C2 continuity: recover through replacement chain.
F5. two same-generation replacements select incompatible C1 sets: membership-proof fork.
F6. snapshot with larger lastIncludedIndex but incompatible certificate chain: freshness does not win; reject.
F7. old snapshot reappears after certificate replacement: rollback reject even if locally self-consistent.
F8. compact successor certificate commits only terminal C2 quorum, not joint-transition obligation: reject as insufficient proof of safe membership succession.

---

## Cross-cutting invariants

1. **Successor self-consistency is not succession authority.** Every authority change needs authenticated predecessor/bridge evidence or an explicitly defined emergency root whose own succession is authenticated.
2. **Compaction preserves proof obligations, not just final state.** A root/hash/checkpoint is acceptable only if it commits to the evidence needed to establish the same safety property after detail is deleted.
3. **Unknown never silently becomes false.** Missing ancestry, expired receipts, deleted logs, or absent historical detail produce explicit unknown/ambiguous states unless a proof resolves them.
4. **Non-resurrection is monotonic.** Revoking historical evidence cannot restore retired mutation authority.
5. **Budgets and effects are conservation problems.** Privacy loss and irreversible external effects survive deletion, rotation and partition; reconciliation takes unions/conservative maxima rather than branch-local leftovers.
6. **Forks are first-class state.** Equal generation or later arrival never resolves incompatible authenticated histories by itself.

## Implementation guidance when exact execution is available

- Add tests before production refactors.
- Model authenticated positions explicitly instead of wall-clock comparisons.
- Keep effect identity, authority generation and evidence provenance immutable.
- Make compact checkpoint schemas carry predecessor commitments and unresolved-obligation roots.
- Ensure restart/recovery paths execute the same validation as live mutation paths.
- Add unsafe expected-failure seeds for self-authorizing successor, wall-clock lease reclaim, observer late-arrival winner, and terminal-membership-only recovery.
- Do not merge any design contract based on this artifact alone; exact RED/GREEN plus supported-surface regression gates remain mandatory.

## Result

Frozen 48-case RED-first matrix across six contracts. No repository executable PASS is claimed in this run. LAB-086 remains priority #1 and draft until the exact pinned closure can be materialized byte-for-byte and fully executed.