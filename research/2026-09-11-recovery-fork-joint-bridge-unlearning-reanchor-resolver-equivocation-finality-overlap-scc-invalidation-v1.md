# Recovery fork, joint bridge revocation, unlearning re-anchoring, resolver equivocation, finality overlap, and SCC invalidation — V1

Date: 2026-09-11
Status: FROZEN DESIGN / RED-FIRST CONTRACT
Issue family: LAB-093 / #178 follow-up evidence slice

## Scope

This note freezes the next architecture/evidence slice while LAB-086 exact executable closure remains blocked by unavailable byte-exact source materialization into the local executor.

It covers six coupled failure modes that the previous frozen contracts leave intentionally open:

1. recovery-fork resolution when competing emergency successors retain different partially compromised domain intersections;
2. revocation/recovery of a joint witness-membership + checkpoint-authority bridge after stale-verifier retention has already begun;
3. compromise of a root-of-trust inside an unlearning supersession DAG and proof re-anchoring;
4. resolver evidence-cutoff attestations when the underlying source log itself equivocates;
5. provider-finality generation handoff when predecessor/successor quorum overlap is only partially admissible across time;
6. incremental invalidation of snapshot-bound `CAN_RESTORE` SCC/fixed-point proofs when inventory edges mutate during a GC epoch.

The result is a fail-closed contract. It is not executable proof and must not be treated as replacing RED/GREEN tests.

## Primary donors

- TUF root update continuity: each new root is verified by thresholds from both immediate predecessor and successor root metadata, with monotonic versioning and rollback detection. https://theupdateframework.github.io/specification/
- RFC 9162 Certificate Transparency: inclusion/consistency proofs establish authenticated append-only relationships between tree heads; consistency of views across parties requires comparison/gossip and conflicting signed views are evidence of misbehavior. https://www.rfc-editor.org/rfc/rfc9162.html
- Certified machine unlearning: formal guarantees are theorem/assumption scoped; a certificate is meaningful only relative to the guarantee under which it was established. Representative recent work: https://proceedings.mlr.press/v267/koloskova25a.html
- NIST SP 800-226: privacy budget is an upper bound on cumulative privacy loss across analyses of the same protected data. https://csrc.nist.gov/pubs/sp/800/226/final
- NIST SP 800-88 Rev. 2: cryptographic erase requires sanitization assurance/validation and coverage of relevant key copies, including externally managed keys. https://csrc.nist.gov/pubs/sp/800/88/r2/final

## Frozen invariants

### A. Recovery-fork resolution under partial compromise

A recovery successor is not selected by timestamp, arrival order, numeric generation alone, or raw key-count overlap.

For every candidate recovery generation `R_n`, define:

- `canonical_domains(R_n)` — stable failure-domain identities represented by its quorum;
- `compromised_at(d, interval)` — interval-scoped compromise classification;
- `correlated(d1,d2)` — shared custody/restore path that destroys independence;
- `admissible_domains(R_n,t)` — canonical domains remaining after compromise and correlation filtering at decision time `t`;
- `continuity(R_{n-1},R_n,t)` — authenticated predecessor->successor bridge plus required threshold/intersection over admissible domains.

Two same-rank successors `A` and `B` are a `RECOVERY_FORK` if both are individually well-formed yet neither has a valid authenticated domination/recovery bridge over the other. Different surviving partial intersections do not make one canonical by majority. Resolution requires a strictly higher recovery generation that:

1. commits both fork heads;
2. commits the last uncontested predecessor;
3. proves which predecessor domains remain admissible by interval;
4. is authorized by an independently sufficient recovery set after correlation filtering;
5. preserves the highest observed rollback/equivocation floor.

A later determination that one compromised-domain assertion was false may permit a new recovery evaluation but does not erase the historical fork or lower the monotonic safety floor.

### B. Joint membership/checkpoint bridge revocation after retention begins

A simultaneous membership and checkpoint-authority rotation is one canonical signed object:

`BRIDGE = H(prev_membership_head, prev_checkpoint_head, next_membership, next_checkpoint_authority, retention_floor, stale_verifier_set, evidence_cutoff)`.

Once predecessor compaction has begun, revoking the bridge authority cannot be treated as if the bridge never existed. The system must preserve enough retained evidence for supported stale verifiers to establish one of:

- valid bridge continuity;
- explicit bridge revocation plus a higher recovery bridge;
- explicit irrecoverable equivocation requiring quarantine.

A replacement bridge must commit the revoked bridge digest and the exact retention state already reached. It may not require predecessor evidence that has already been legitimately GC'd under the old bridge unless that evidence was required by the old retention contract. If required evidence was prematurely deleted, recovery fails closed rather than synthesizing it from successor state.

### C. Unlearning supersession root compromise and proof re-anchoring

Unlearning certificates form an acyclic DAG of theorem/profile dependencies and supersession edges. Each certificate binds at least:

- subject/model lineage digest;
- deletion request scope;
- theorem/profile ID and version;
- assumptions digest;
- issuer/root-of-trust generation;
- evidence cutoff;
- guarantee class (`EXACT`, `CERTIFIED_BOUND`, `EMPIRICAL`, `UNKNOWN`).

Compromise of a theorem/profile signing root at interval `I` taints every certificate whose trust path crosses that root in `I`, including descendants that merely supersede the certificate without independent re-proof.

Re-anchoring requires a new root generation to commit:

1. the compromised root and interval;
2. the affected certificate frontier;
3. the new theorem/profile assumptions;
4. either independent re-proof of each retained guarantee or explicit downgrade to the weakest still-supported guarantee.

Re-signing old proof material is not re-proof. Multiple correlated certified bounds are not composed as if independent unless the composition theorem explicitly covers the shared training state, optimizer state, caches, embeddings, distillation lineage, and randomness.

### D. Resolver evidence cutoffs under source-log equivocation

A privacy/identity resolver assertion must bind:

`(resolver_generation, source_log_id, source_tree_head, source_set_digest, evidence_cutoff, namespace_epoch, mapping_digest, accounting_floor)`.

If the source log presents two incompatible authenticated heads that cannot be joined by a valid consistency proof, all resolver assertions derived after their common uncontested ancestor enter `SOURCE_EQUIVOCATION`.

Convergence rules:

- never choose one head by arrival time;
- never lower `accounting_floor` while the fork is unresolved;
- preserve reservations/spend from both branches using a conservative join;
- future disjointness may resume only from a recovered canonical source generation that commits both conflicting heads and the last uncontested cutoff;
- namespace rotation, tombstone deletion, relink, or resolver replacement cannot reset cumulative budget.

### E. Provider-finality handoff with only partially admissible overlap

Finality authority generation `F_n` binds a canonical effect-history frontier including unresolved UNKNOWN operations, sequence gaps, forks, revocations, and compensation ancestry.

A transition `F_n -> F_{n+1}` is admissible only if the overlap of canonical failure domains is sufficient after time-scoped compromise/correlation filtering for the exact handoff interval. Raw overlap of signing keys is insufficient.

If overlap is sufficient only for a prefix of the transition interval, the successor may attest only effects whose authority path is contained in that admissible interval. Effects spanning the disputed interval remain `EFFECT_UNKNOWN` or `FINALITY_FORK` until independently reconciled.

Two competing successor finality generations are not resolved by timestamp or provider failover preference. A higher recovery/finality generation must commit both heads and every unresolved predecessor effect.

### F. Incremental SCC/fixed-point invalidation during authority GC

Authority extinction is evaluated over an authenticated snapshot `G_k = (V,E)` where `u -> v` means authority/domain `u` can restore or recreate `v`.

The proof algorithm:

1. canonicalize domain identities;
2. collapse SCCs;
3. mark any SCC containing an externally grounded live/unknown authority as live;
4. propagate liveness through restore edges to a fixed point;
5. permit GC only for target authorities proven outside the live closure;
6. bind the proof to graph snapshot digest, inventory issuer generation, evidence cutoff, and GC epoch.

Any edge addition, removal, confidence reclassification, issuer revocation, inventory expansion, or discovered dormant domain invalidates every extinction proof whose transitive dependency cone intersects the changed SCC condensation graph.

Incremental recomputation is allowed for performance, but only if it is semantically equivalent to full recomputation on the new authenticated snapshot. Unknown edges are live until resolved. Cyclic authorities cannot prove one another dead without an external grounded death proof.

## RED-first matrix (40 cases)

### Recovery fork — 1..7

1. Two same-generation emergency successors, disjoint admissible intersections -> `RECOVERY_FORK`.
2. Same keys under renamed domain IDs -> canonicalize; no fake extra independence.
3. One successor includes a domain compromised during signing interval -> remove domain, recompute threshold.
4. Both candidates individually threshold-valid but overlap insufficient after filtering -> no canonical winner.
5. Higher recovery generation commits only one fork head -> reject.
6. Higher recovery generation commits both heads + uncontested predecessor + sufficient independent quorum -> accept.
7. Later compromise-assessment reversal -> permit fresh evaluation; never erase recorded fork/floor.

### Joint bridge retention — 8..14

8. Membership rotates but checkpoint authority payload differs -> reject whole bridge.
9. Checkpoint authority rotates but membership payload differs -> reject whole bridge.
10. Valid bridge, retention begins, bridge key later revoked -> freeze destructive GC pending recovery.
11. Recovery bridge omits revoked bridge digest -> reject.
12. Recovery bridge ignores already-reached retention floor -> reject.
13. Required predecessor evidence was prematurely deleted -> fail closed; do not reconstruct from successor.
14. Supported stale verifier can verify retained continuity/revocation chain -> allow retention to continue.

### Unlearning re-anchor — 15..21

15. Compromised profile root signed certificate during affected interval -> certificate tainted.
16. Descendant supersession only re-signs same proof -> remains tainted.
17. Independent re-proof under uncompromised root -> may re-anchor.
18. Re-proof supports weaker guarantee only -> explicit downgrade, never retain stronger label.
19. Two correlated certified bounds composed as independent -> reject composition.
20. DAG cycle introduced through supersession/revocation metadata -> reject.
21. Unaffected branch with independent trust/evidence path -> remains valid.

### Resolver/source equivocation — 22..28

22. Two incompatible authenticated source heads -> `SOURCE_EQUIVOCATION`.
23. Resolver chooses latest timestamp head -> reject.
24. Resolver chooses lexicographically larger digest -> reject.
25. Accounting floors differ across heads -> conservative join, never min.
26. Namespace rotates while source fork unresolved -> no budget reset.
27. Recovery source generation commits both heads + uncontested ancestor -> allow convergence from new cutoff.
28. Old resolver assertion lacks source tree-head binding -> insufficient for destructive convergence decision.

### Provider finality overlap — 29..34

29. Successor finality generation overlaps predecessor only via compromised domain -> reject transition.
30. Overlap admissible for interval prefix only -> suffix effects remain UNKNOWN.
31. Successor omits predecessor UNKNOWN effect -> reject.
32. Competing successor generations each threshold-valid -> `FINALITY_GENERATION_FORK`.
33. Provider failover prefers one successor without authenticated recovery -> reject.
34. Higher generation commits both forks + unresolved effects + sufficient independent overlap -> accept.

### SCC/fixed-point invalidation — 35..40

35. New `CAN_RESTORE` edge enters a previously dead SCC -> invalidate affected GC proof.
36. Edge removal without authenticated inventory update -> ignore removal / remain live.
37. Unknown edge becomes proven absent -> recompute; may shrink live closure.
38. Inventory issuer revoked -> invalidate all dependent snapshot proofs.
39. New dormant KMS/escrow domain discovered after proof but before GC commit -> recompute; target remains live if reachable.
40. Incremental recomputation result differs from full fixed point on same snapshot -> fail closed and quarantine optimizer path.

## Implementation consequences

Do not implement these as six independent booleans. The common abstraction is an authenticated generation transition carrying:

- canonical subject/domain identities;
- predecessor heads;
- successor heads;
- evidence cutoff;
- interval-scoped compromise/revocation state;
- correlation/restore dependency digest;
- monotonic safety/accounting floor;
- unresolved fork/UNKNOWN frontier;
- proof profile/version.

Suggested future executable decomposition:

1. pure canonicalization + admissible-domain evaluator;
2. generic `GenerationBridge` verifier with fork states;
3. DAG/SCC proof engine with snapshot digest and invalidation cone;
4. domain adapters for recovery, checkpoint membership, unlearning, privacy resolver, provider finality, and KMS authority inventory;
5. property tests that mutation of any authority-relevant field changes the canonical digest and invalidates dependent proofs.

## Audit

- No executable PASS is claimed.
- This note does not change LAB-086 priority or draft status.
- The six contracts are monotonic/fail-closed: new evidence can restore forward progress but cannot silently reduce a previously observed rollback/equivocation/accounting/UNKNOWN floor.
- Donor mechanisms are used structurally, not copied as code.
- The next step remains exact executable LAB-086 materialization if a supported byte-preserving path appears; otherwise continue with the next distinct evidence slice rather than simulating execution.
