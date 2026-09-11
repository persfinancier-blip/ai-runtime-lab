# Recovery-set intersection, joint checkpoint rotation, unlearning supersession, resolver cutoffs, finality generations, and dynamic authority SCCs

Date: 2026-09-11
Status: DESIGN FROZEN / RED-FIRST; no executable PASS claimed
Primary follow-up: LAB-093 / #178. LAB-086 remains priority #1.

## Why this slice exists

LAB-086 exact-source execution was probed first in this run. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available, but no supported non-model connector-to-local-filesystem byte-exact materialization path is exposed. The retained LAB-086 gate therefore still prohibits manual/model reserialization of the executable closure.

The current PR remains open/draft/non-mergeable. A fresh compare in this run reports `lab/086-asymmetric-break-glass-history` diverged from current `main`, ahead 195 / behind 813. No historical merge-safety conclusion is carried forward.

This note executes the next distinct evidence task recorded in `state/CURRENT.md`. It freezes invariants and RED cases only; it does not substitute for exact repository execution.

## Primary donors

1. **The Update Framework (TUF) root continuity.** Sequential root updates require the successor metadata to satisfy both the predecessor root threshold and the successor root threshold, and clients reject rollback in root version. This is a donor for authenticated authority-generation transitions, but not a license to count a compromised predecessor as independent recovery authorization.
   - https://theupdateframework.github.io/specification/
   - https://theupdateframework.github.io/specification/v1.0.26/

2. **RFC 9162 Certificate Transparency.** Merkle consistency proofs establish append-only consistency between authenticated tree heads; global split-view detection requires comparing observations. This is the donor for witness-membership/checkpoint co-rotation and retention proofs.
   - https://www.rfc-editor.org/rfc/rfc9162.html

3. **Guo et al., Certified Data Removal from Machine Learning Models (ICML 2020).** Certified removal is defined relative to a precise guarantee/profile; evidence cannot be generalized beyond that theorem/assumption scope. This is the donor for supersession graphs of unlearning claims.
   - https://proceedings.mlr.press/v119/guo20c.html

4. **NIST SP 800-226.** Privacy budget is an upper bound on cumulative privacy loss across analyses of a dataset. Resolver evidence changes therefore cannot reduce already accrued accounting merely by moving the identity/evidence cutoff backward.
   - https://csrc.nist.gov/glossary/term/privacy_budget
   - https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-226.pdf

5. **NIST SP 800-88 Rev. 2.** Cryptographic erase requires assurance/validation and accounts for all copies of target keys, including externally managed key material. This is the donor for dynamic recursive authority-inventory proofs.
   - https://csrc.nist.gov/pubs/sp/800/88/r2/final

6. **Quorum-intersection literature (Paxos/Flexible Paxos family).** Consensus safety depends on the required quorum intersections for the phases/generations involved; counting signatures without proving the relevant intersection property is insufficient. This is used only as a structural donor for recovery/finality quorum-generation reasoning, not as a claim that LAB-093 implements Paxos.
   - https://arxiv.org/abs/1608.06696

## Frozen contract

`RECOVERY_INTERSECTION_CHECKPOINT_ROTATION_UNLEARNING_SUPERSESSION_RESOLVER_CUTOFF_FINALITY_GENERATION_AUTHORITY_SCC_V1_FROZEN`

### A. Recovery-root set intersection and partial-compromise admissibility

Represent each recovery generation as:

`R_g = (generation, canonical_domains, threshold_rule, validity_interval, predecessor_digest, compromise_evidence_cutoff)`.

A signature key is not itself an independent domain. Canonical domain identity includes operator/controller, HSM or KMS tenancy, escrow/recovery ancestor, restore credential lineage, and any other shared failure source already known to the verifier.

**Invariant A1 — admissibility is interval-scoped.**

A domain contributes to transition authorization only if it is admissible for the exact transition interval. Later compromise evidence that overlaps that interval invalidates its contribution to that historical quorum and reopens the decision; it does not roll back already learned monotonic uncertainty/security floors.

**Invariant A2 — required intersection is over admissible domains, not raw keys.**

For normal `R_g -> R_{g+1}` continuity, the transition must satisfy predecessor and successor authorization rules over canonical admissible domains. If policy relies on an intersection between generations, the verifier must be able to name at least one admissible domain in the required intersection after excluding compromised/correlated domains.

`raw_key_intersection != admissible_failure_domain_intersection`.

**Invariant A3 — partial predecessor compromise consumes safety margin.**

If some predecessor domains are compromised but the remaining admissible set still satisfies the declared predecessor threshold and the required predecessor/successor intersection property, continuity may remain admissible. If compromise removes the intersection or threshold, predecessor signatures become historical evidence only and emergency recovery requires an independent higher recovery authority.

**Invariant A4 — emergency generations cannot manufacture intersection.**

Cross-signing, key cloning, reassignment, or moving keys between labels does not restore lost failure-domain intersection. A new emergency generation must bind the compromised predecessor set and show an authorization path whose independence exists outside the compromised closure.

**Invariant A5 — incomparable valid emergency successors are explicit recovery fork.**

Two successors of the same last uncontested generation that each satisfy local threshold rules but have no authenticated ordering/coverage relation create `RECOVERY_FORK`. Timestamp, arrival order, lexical root id, or larger signer count cannot choose the canonical branch.

### B. Joint witness-membership and checkpoint-authority rotation

Membership history and checkpoint-signing authority are separate trust surfaces. Rotating both in one step is safe only when the transition authenticates the relationship between them.

**Invariant B1 — a joint transition has one canonical payload.**

The co-rotation payload commits to:
- predecessor membership epoch and checkpoint head;
- successor membership epoch and canonical witness/failure-domain set;
- predecessor checkpoint-authority generation;
- successor checkpoint-authority generation;
- thresholds and validity intervals for both roles;
- retention cutoff and exact predecessor history needed to verify the transition;
- consistency proof / predecessor hash linking old and new checkpoint views.

Membership and checkpoint-authority signatures over different payloads are not composable into one transition.

**Invariant B2 — at least one trusted side of each role transition must remain independently anchored.**

If predecessor membership and predecessor checkpoint authority are both compromised for the transition interval, their mutual co-signatures cannot bootstrap trust in their successors. A higher independent recovery root or externally anchored checkpoint is required.

**Invariant B3 — compacted history must retain the bridge needed by stale verifiers.**

Do not GC predecessor membership/checkpoint metadata until every supported verifier starting from the retained trust anchor can authenticate the successor transition. A current client being able to verify the head is insufficient evidence that an older supported verifier can reconstruct continuity.

**Invariant B4 — split membership and split checkpoint heads compound, not cancel.**

A consistent membership head paired with an inconsistent checkpoint-authority head, or vice versa, leaves the joint transition disputed. One valid role cannot mask equivocation in the other.

### C. Certified-unlearning theorem/profile supersession DAG

Model unlearning guarantees as a directed acyclic supersession graph, not a mutable `current_profile` pointer.

Each evidence node binds:

`(claim_id, theorem/profile version, implementation version, assumptions, model lineage, removed-set commitment, retained-set commitment, randomness/noise regime, result digest, evidence cutoff)`.

Edges are typed: `SUPERSEDES`, `REVOKES`, `NARROWS`, `REFINES`, or `TRANSFORMS_WITH_PROOF`.

**Invariant C1 — supersession does not retroactively strengthen evidence.**

A stronger profile released later does not upgrade certificates issued under an older weaker profile. Old evidence remains valid only for its original scope unless there is an explicit transformation proof whose theorem permits reuse.

**Invariant C2 — revocation is monotonic for authorization use.**

If profile P is revoked for a soundness defect, descendants that rely on P inherit the dispute unless their proof explicitly re-establishes the affected property independently. Renaming/re-signing the descendant does not sever the dependency.

**Invariant C3 — the supersession graph must be acyclic and content-addressed.**

A profile may not derive trust from itself through a chain of aliases or cross-certifications. Any cycle in theorem/profile dependency is `PROFILE_CYCLE` and invalid for authorization.

**Invariant C4 — composition budget is theorem-defined.**

For multiple component claims, the aggregate guarantee is no stronger than the composition rule explicitly proved by their profiles. Correlated optimizer state, shared caches/embeddings, common teacher/distillation lineage, or overlapping removed sets must be represented as dependencies. Unsupported composition degrades to `UNKNOWN`.

### D. Resolver evidence-cutoff rollback and conservative joins

Separate mutable resolver state from monotonic privacy-accounting evidence.

Each resolver assertion binds `(resolver_version, identity_graph_epoch, evidence_cutoff, source_set_digest, mapping_claim, confidence/proof class)`.

**Invariant D1 — evidence cutoff is monotonic per accepted lineage.**

A resolver update with an older evidence cutoff cannot supersede a newer accepted cutoff for the same lineage. It may be retained as historical evidence, but runtime rollback to it must not lower the canonical accounting floor or erase later possible-link claims.

**Invariant D2 — joins are cutoff-aware.**

When resolver branches disagree, compute the conservative join over all non-revoked evidence reachable at or before the decision cutoff. A later branch may add links, splits, or disjointness proofs, but cannot pretend evidence observed by another branch never existed.

**Invariant D3 — disjointness is scoped to a cutoff and proof class.**

A valid disjointness proof may separate *future* accounting after its authenticated cutoff if policy permits, but it does not refund cumulative historical privacy loss and cannot erase unknown-loss accumulated while branches were unresolved.

**Invariant D4 — source rollback is evidence poisoning, not ordinary version skew.**

If a resolver version is built from an older/incomplete source-set digest while claiming a newer epoch, mark the branch `SOURCE_ROLLBACK`; do not merge it as a normal lower-confidence claim.

### E. Provider-finality quorum-generation transitions

Represent finality authority generations independently from provider runtime generation:

`F_g = (authority_generation, canonical_domains, threshold_rule, validity_interval, covered_provider_epoch, predecessor_finality_digest)`.

**Invariant E1 — a new finality generation must account for predecessor unresolved state.**

Transition `F_g -> F_{g+1}` commits to all predecessor operations that are `UNKNOWN`, sequence-gapped, forked, or compensation-pending at the transition cutoff. Omission is not evidence of no effect.

**Invariant E2 — quorum transition safety depends on admissible domain intersection or independent reconciliation.**

If policy expects continuity via overlapping authority domains, that overlap must remain admissible after compromise/correlation filtering. If there is no admissible intersection, the successor may finalize predecessor operations only with independent provider-side reconciliation or a higher recovery/finality authority explicitly empowered to resolve the discontinuity.

**Invariant E3 — competing successor generations form a generation fork.**

Two locally valid successors of `F_g` with incompatible outstanding-operation sets or authority sets create `FINALITY_GENERATION_FORK`. Neither can finalize destructive effects from the disputed interval until fork resolution is itself authenticated.

**Invariant E4 — revocation and finality are orthogonal dimensions.**

Revoking the authority that signed a receipt affects trust in the receipt; it does not prove the external effect did or did not happen. Effect state falls back to `UNKNOWN` unless independent reconciliation proves it.

### F. Dynamic `CAN_RESTORE` SCC / fixed-point proofs during GC

Let graph `G_t = (V_t, E_t)` at evidence cutoff `t`, where edge `A -> B` means authority/domain A can restore or recreate B's effective capability.

**Invariant F1 — extinction proof uses a snapshot-complete graph.**

GC decision binds an authenticated graph/inventory cutoff and completeness proof. Running SCC analysis on a graph that can silently gain nodes/edges during the decision is unsound.

**Invariant F2 — unresolved SCCs are live.**

Collapse `G_t` into strongly connected components. An SCC containing any unsanitized node, unknown edge, disputed inventory source, or restoration path from another live SCC remains live. Mutual assertions inside the SCC cannot prove extinction.

**Invariant F3 — fixed-point extinction proceeds from externally grounded dead components.**

A component becomes extinct only when every node/credential is sanitized/revoked and every incoming restoration path originates in an already-extinct component or is independently proven unusable. Iterate until no state changes. Anything remaining live/unknown blocks GC for dependent ticket/security epochs.

**Invariant F4 — graph changes during GC invalidate the proof unless incorporated.**

If a new backup, escrow, cross-region restore path, wrapped key, or issuer-recovery edge is discovered after the bound cutoff but before destructive GC, abort/recompute. If discovered after GC, reopen the extinction assessment, quarantine affected resumption/recovery domains, and preserve monotonic security-epoch floors.

**Invariant F5 — inventory issuers are ordinary graph nodes.**

An issuer that attests graph completeness is not outside the graph. If predecessor authorities can restore that issuer or its signing capability, its completeness statement remains inside the same trust closure and cannot serve as the external break for its SCC.

## State machines / fail-closed outcomes

- Recovery generation: `TRUSTED -> PARTIAL_COMPROMISE -> ADMISSIBLE_WITH_REDUCED_MARGIN | RECOVERY_FORK | INDEPENDENT_RECOVERY_REQUIRED`.
- Joint checkpoint rotation: `ANCHORED -> CO_ROTATION_PENDING -> VERIFIED_BRIDGE -> RETENTION_SAFE`; any role equivocation -> `JOINT_EQUIVOCATION`.
- Unlearning profile: `ACTIVE -> SUPERSEDED | NARROWED | REVOKED`; aggregate evidence can be `COMPOSABLE`, `PARTIALLY_COMPOSABLE`, or `UNKNOWN`.
- Resolver: `CURRENT`, `STALE_CUTOFF`, `FORKED`, `SOURCE_ROLLBACK`, `CONSERVATIVE_JOINED`.
- Provider finality generation: `CURRENT`, `TRANSITION_PENDING`, `GENERATION_FORK`, `RECONCILED_SUCCESSOR`.
- Authority inventory: `SNAPSHOT_BOUND -> SCC_CLASSIFIED -> FIXED_POINT_REACHED -> EXTINCTION_PROVEN`; any graph mutation -> `RECOMPUTE_REQUIRED`.

## 40-case RED-first matrix

### Recovery-root intersection / partial compromise (1-7)
1. Predecessor and successor thresholds satisfied; required intersection contains an admissible independent domain -> accept normal continuity.
2. Same raw key appears in both generations but maps to compromised shared HSM/operator -> do not count as admissible intersection.
3. One predecessor domain compromised, remaining predecessor threshold and required intersection still hold -> accept with reduced safety-margin metadata.
4. Partial compromise drops predecessor below threshold -> predecessor cannot authorize successor; independent recovery required.
5. Predecessor threshold holds numerically but all overlap with successor is compromised -> reject continuity that relies on intersection.
6. Two emergency successors of same uncontested root each locally valid but incomparable -> `RECOVERY_FORK`.
7. Later compromise evidence overlaps a previously counted transition signer -> reopen transition admissibility; retain monotonic uncertainty/security floors.

### Joint membership + checkpoint authority rotation (8-14)
8. Membership successor and checkpoint-authority successor sign different payload digests -> reject co-rotation.
9. One canonical payload is signed by valid predecessor/successor role thresholds and carries predecessor checkpoint consistency proof -> accept bridge.
10. Both predecessor roles compromised for transition interval and only cross-sign each other's successors -> reject circular bootstrap.
11. Membership head consistent but checkpoint-authority head equivocated -> `JOINT_EQUIVOCATION`.
12. Checkpoint authority consistent but membership epoch split -> `JOINT_EQUIVOCATION`.
13. GC deletes the only intermediate bridge required by a supported stale verifier -> block retention GC.
14. New witness keys reuse same canonical failure domains during co-rotation -> count domains, not keys.

### Unlearning supersession DAG (15-21)
15. P2 explicitly supersedes P1 prospectively; P1 certificate remains only P1-strength -> do not upgrade historical claim.
16. P1 revoked for soundness defect; P2 depends on P1 result without independent re-proof -> P2 becomes disputed.
17. P2 contains valid transformation proof from P1 under theorem that remains sound -> accept only transformed scope.
18. P1->P2->P3->P1 alias/cross-cert cycle -> `PROFILE_CYCLE`, reject authorization use.
19. Two individually certified components share optimizer/teacher dependency outside theorem composition -> aggregate `UNKNOWN`.
20. Profile narrows supported model family; old certificate outside narrowed family -> no longer eligible for current authorization.
21. Re-sign identical result under new profile id without recomputation/transformation proof -> reject supersession shortcut.

### Resolver cutoff rollback / joins (22-27)
22. Resolver v3 cutoff 300 supersedes v2 cutoff 200; runtime rolls back to v2 -> canonical floor remains at least v3 evidence consequences.
23. Branch A cutoff 300 says possible-link; branch B cutoff 310 says no-match without disjointness proof -> conservative join retains possible-link.
24. Sound disjointness proof at cutoff 320 permits future separation but historical spend remains composed -> accept scoped separation only.
25. Resolver claims epoch 9 while source-set digest corresponds to older epoch 7 -> `SOURCE_ROLLBACK`.
26. Two branches use same cutoff but contradictory signed mapping claims -> `FORKED`; no preferred-arrival overwrite.
27. Namespace rotation emits fresh subject id after rollback -> map to existing accounting lineage; no fresh budget.

### Provider-finality quorum generations (28-34)
28. F2 transition covers every F1 outstanding operation and valid admissible quorum intersection exists -> accept successor continuity.
29. F2 omits one F1 `UNKNOWN` operation -> reject transition as incomplete.
30. Raw signer overlap exists but all overlap maps to one compromised signer service -> no admissible generation intersection.
31. No safe intersection, but independent provider-side reconciliation proves exact predecessor effect -> allow scoped reconciliation, not blanket continuity.
32. Two F2 successors carry incompatible outstanding-operation sets -> `FINALITY_GENERATION_FORK`.
33. Receipt signer later revoked for issuance interval -> receipt trust disputed; effect becomes `UNKNOWN`, not automatically `NOT_APPLIED`.
34. Successor quorum attempts to finalize across an unresolved predecessor sequence gap -> reject inferred finality.

### Dynamic authority SCC / fixed point (35-40)
35. Snapshot-bound graph has SCC `KMS<->escrow`; neither node independently sanitized -> SCC live, GC blocked.
36. One node in cycle has externally grounded sanitization evidence, all remaining restoration edges into it are dead -> recompute SCC/fixed point and permit progress only if closure is fully extinct.
37. Unknown dormant-region edge enters otherwise-dead SCC -> classify live/unknown; extinction not proven.
38. Inventory completeness issuer is restorable from predecessor SCC -> issuer statement cannot break that SCC.
39. New `CAN_RESTORE` edge discovered before destructive GC after fixed-point calculation -> abort and recompute from new authenticated graph cutoff.
40. Delayed edge discovered after GC -> reopen assessment, quarantine affected recovery/resumption domain, preserve monotonic security epoch; never claim prior proof was complete.

## Implementation guidance when exact execution becomes available

1. Add RED tests at existing authority/history abstractions before production refactors.
2. Persist canonical failure-domain identity separately from key identity; make compromise intervals first-class.
3. Encode recovery/finality generation transitions as content-addressed canonical payloads with complete predecessor outstanding/conflict sets.
4. Treat joint membership/checkpoint rotation as one authenticated bridge and retain enough intermediate evidence for supported stale verifiers.
5. Store unlearning profile/evidence dependencies as an acyclic content-addressed graph; reject cycles and unsupported composition.
6. Keep privacy-accounting floors monotonic and resolver-independent; bind resolver assertions to evidence cutoff and source-set digest.
7. Snapshot/version authority inventories before SCC/fixed-point evaluation; any graph mutation invalidates the proof until recomputed.
8. Never equate cryptographic signature validity with effect truth, guarantee soundness, failure-domain independence, or inventory completeness.

## Audit

- No GitHub Action/worker/background execution is used or assumed.
- No security-critical executable source was manually reconstructed.
- This slice strengthens existing monotonic/fail-closed rules and does not lower rollback, equivocation, privacy-loss, external-effect, or authority-extinction floors.
- It is distinct from the preceding fixed-point freeze by defining: admissible quorum intersection after partial compromise; a single bridge for simultaneous membership/checkpoint-authority rotation; a theorem/profile supersession DAG; resolver source/evidence cutoff rollback; explicit finality-authority generation transitions; and snapshot-bound SCC recomputation when restoration graphs change during GC.

Verdict: `RECOVERY_INTERSECTION_CHECKPOINT_ROTATION_UNLEARNING_SUPERSESSION_RESOLVER_CUTOFF_FINALITY_GENERATION_AUTHORITY_SCC_V1_FROZEN`.
