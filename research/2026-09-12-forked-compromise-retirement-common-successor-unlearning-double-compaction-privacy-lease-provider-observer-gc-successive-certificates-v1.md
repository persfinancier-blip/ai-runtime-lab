# Forked compromise timing, revoked common successors, double-compacted unlearning, privacy leases, observer disagreement, and successive compact GC certificates

Date: 2026-09-12
Status: `FORKED_COMPROMISE_RETIREMENT_COMMON_SUCCESSOR_UNLEARNING_DOUBLE_COMPACTION_PRIVACY_LEASE_PROVIDER_OBSERVER_GC_SUCCESSIVE_CERT_V1_FROZEN`
Scope: architecture/evidence contract only. Exact repository RED/GREEN remains pending until executable source materialization is available.

## Why this slice exists

The previous frozen slice covered partially overlapping emergency/root cut sets, mutually exclusive retirement revocations, remigration after lineage compaction, concurrent privacy spend across allocator generations, delayed external provider observations, and reconciliation of different compact GC snapshot boundaries.

This follow-up targets a harder class of continuity failures: evidence about *when* a compromise occurred can itself fork; a retirement fork may be reconciled by a common successor that is later revoked; multiple lineage stores can compact away detailed ancestry; privacy leases can cross a partition without trustworthy wall-clock expiry; independent external observers can disagree after idempotency/receipt retention expires; and consensus membership may survive only as two successive compact joint-consensus certificates with the detailed membership log gone.

The common rule is conservative continuity: a later compact object may replace detailed evidence only if it preserves the predecessor proof obligation. Self-consistency, generation number, timestamp, or terminal value is not sufficient proof of authority succession.

## Primary donors re-verified

1. The Update Framework specification v1.0.36 — root rotation requires trust in both the previously trusted root and the candidate successor; rollback/freeze attacks are explicitly part of the threat model. Mechanism reused: predecessor/successor authenticated continuity, not successor self-assertion.
   - https://theupdateframework.github.io/specification/
2. RFC 9162, Certificate Transparency v2 — Merkle consistency proofs prove that a later tree contains the exact earlier prefix. Mechanism reused: a later signed root/head is not, by itself, proof of history extension.
   - https://www.rfc-editor.org/rfc/rfc9162.html
3. NIST SP 800-226 / CSRC privacy-budget definition — privacy budget is an upper bound on cumulative privacy loss across analyses of a dataset. Mechanism reused: partition, lease, allocator rotation, rollback, or deletion cannot manufacture fresh budget.
   - https://csrc.nist.gov/glossary/term/privacy_budget
   - https://www.nist.gov/publications/guidelines-evaluating-differential-privacy-guarantees
4. AWS Well-Architected REL04-BP04 — retries of the same mutation use a stable idempotency token so repeated requests do not create additional effects. Mechanism reused: effect identity is independent of transport attempt; expiration of retained dedupe state does not prove that an old effect never occurred.
   - https://docs.aws.amazon.com/wellarchitected/2025-02-25/framework/rel_prevent_interaction_failure_idempotent.html
5. Ongaro/Ousterhout Raft paper — joint consensus prevents disjoint old/new majorities; snapshots retain `lastIncludedIndex`, `lastIncludedTerm`, and the latest cluster configuration so truncated log prefixes still have a positioning/configuration anchor. Mechanism reused: compact membership evidence must prove transition continuity, not merely contain a terminal membership set.
   - https://raft.github.io/raft.pdf

These are design donors, not claims that the lab implements TUF, CT, differential privacy accounting, AWS APIs, or Raft verbatim.

---

# Contract A — Forked compromise timing for partially overlapping emergency cut sets

## Problem

Suppose recovery/root authority rotates R0 -> R1 -> R2. Successive cut sets overlap partially. Later, authenticated evidence exists that failure domain `D` was compromised, but two branches disagree whether compromise happened before or after the R0->R1 transition. Treating the latest generation or latest timestamp as authoritative can validate the wrong succession chain.

## Frozen rule

1. Compromise is represented as authenticated interval/order evidence, not an unauthenticated wall-clock fact.
2. A succession edge is valid only if there exists a sufficient independent cut set whose members are proven uncompromised for the edge's authorization interval.
3. If two authenticated compromise histories are incomparable and one invalidates a required bridge while the other preserves it, the derived successor authority is `RECOVERY_SUCCESSION_AMBIGUOUS` until an authenticated common successor/order certificate covers both histories.
4. Counting signatures or unique key IDs is insufficient; independence is evaluated over explicit failure domains.
5. Later rotation cannot retroactively erase a fork in the proof of an earlier edge.
6. Compact recovery certificates must commit to predecessor authority root, successor root, cut-set/failure-domain policy, and the compromise/order evidence root used to validate the transition.

### Safety consequence

Fail closed on future emergency authority while retaining the maximum independently proven non-resurrection/revocation floors. Ambiguous succession does not resurrect predecessor mutation authority.

---

# Contract B — Retirement revocation ordering after a common successor is itself revoked

## Problem

Retirement bridges B1 and B2 fork. Common successor C authenticates an ordering/reconciliation that resolves them. Later C is revoked or compromised. A naive verifier may either discard C's old reconciliation (resurrecting the original fork) or continue trusting C for new authority despite revocation.

## Frozen rule

1. Distinguish `historical_statement_validity` from `current_signing_authority`.
2. Revoking C prospectively does not erase already-authenticated historical ordering statements unless the revocation explicitly has retroactive scope and itself has valid predecessor continuity.
3. C's historical reconciliation may therefore preserve the non-resurrection floor while C is barred from authorizing any later transition.
4. A successor D after C revocation must prove continuity from the latest still-valid historical state using authority that is currently acceptable under the revocation policy; it cannot rely on a fresh signature by revoked C.
5. If C's revocation is explicitly retroactive across the reconciliation interval, the retirement fork becomes unresolved again, but the verifier still preserves the maximum floor independently proven on each branch rather than lowering it.
6. Compact retirement certificates bind statement scope (`historical_order`, `future_authority`, or both) so revocation handling is not inferred from one generic validity bit.

### Safety consequence

A revoked common successor can lose prospective authority without causing old retired verifiers/generations to become live again.

---

# Contract C — Unlearning lineage after S3 -> S4 remigration when both detailed metadata sets are compacted

## Problem

A descendant migrates S1 -> S2 -> S3 -> S4. Earlier invalidation/unlearning ancestry becomes `dependency unknown`. Later S3 and then S4 compact their detailed metadata. A terminal S4 row that merely says `clean` cannot prove that the unknown ancestor was resolved.

## Frozen rule

1. Every migration carries a compact lineage proof root containing source lineage root, destination identity, invalidation vector/root, migration generation, and unresolved-dependency bit/vector.
2. Compaction may replace details only with a certificate that commits to those authority-relevant fields and to the predecessor compact root.
3. `dependency unknown` is monotonic until an explicit authenticated revalidation proves the complete affected closure; migration and compaction alone cannot clear it.
4. If both S3 and S4 detail are gone, S4 must still present a consistency chain from the retained ancestor compact root(s). Missing one required bridge yields `UNLEARNING_LINEAGE_UNRECOVERABLE` or `UNLEARNING_DEPENDENCY_UNKNOWN`, not `clean`.
5. Store retirement removes mutation authority but does not permit deleting the compact evidence required to prove descendants safe.
6. A fresh copy/re-export from S4 inherits unresolved lineage unless its revalidation proof covers the original invalidation closure.

### Safety consequence

Double compaction never upgrades unknown ancestry into trusted data merely because the intermediate stores no longer retain detail.

---

# Contract D — Privacy residual-budget lease/checkpoint reconciliation after partition heal without wall-clock trust

## Problem

Allocator generation A0 delegates residual-budget leases to A1/A2. They partition. Lease expiry is represented by local wall-clock time, both sides spend near the limit, and the partition heals after clocks have diverged or been rolled back. Treating `lease expired` as proof that unused/spent capacity returned can double allocate privacy budget.

## Frozen rule

1. Wall-clock expiry is advisory for liveness, never sufficient accounting evidence for reclaiming privacy budget.
2. A lease is identified by immutable allocation ID and parent checkpoint root and contains maximum delegated budget, consumed-event accumulator/root, and monotonic allocator generation/epoch.
3. Reclaim requires an authenticated closure/checkpoint proving the lease's final event set or a conservative upper bound on consumed loss.
4. During heal, reconcile by union of immutable release events plus any unresolved leased upper bounds. Unknown lease consumption is charged conservatively, not assumed zero.
5. Allocator-generation rollback cannot recreate a previously delegated residual balance.
6. Only a common successor checkpoint that commits to both partition heads may reduce reserved uncertainty, and then only by verifiable accounting over the same immutable event universe.

### Safety consequence

Clock rollback, expiry, restart, or allocator replacement cannot mint privacy budget. If reconciliation cannot prove remaining capacity, new disclosure fails closed.

---

# Contract E — Delayed provider observations with multiple disagreeing observers across retention expiry

## Problem

A provider mutation has stable effect identity E1. Dedupe/receipt retention later expires. Independent observers O1 and O2 report different world states; their observations arrive after different delays. A newer observation timestamp is not necessarily a stronger statement, and replaying E1 because the receipt expired can duplicate an irreversible effect.

## Frozen rule

1. Transport outcome, provider receipt, observer statement, and actual external effect are separate evidence classes.
2. Observer evidence is authenticated and binds observer identity/domain, effect identity, observed object/version where available, observation generation, and statement content.
3. Observations are ordered by authenticated object/version or other provider-specific monotonic evidence when available; local receive time/wall clock is not a universal tie-breaker.
4. Two valid incomparable observations create `EXTERNAL_EFFECT_EVIDENCE_FORK`; do not rewrite history or automatically replay the mutation.
5. Receipt/dedupe retention expiry means `proof unavailable`, not `effect absent`. Retrying a destructive mutation after expiry requires an independent no-effect proof or a newly authorized semantic operation with a distinct effect identity.
6. A later common observation can resolve the fork only if its evidence is causally/monotonically comparable to both prior observations. Majority of observers is insufficient unless observer-quorum semantics are explicitly part of the provider contract.

### Safety consequence

Delayed disagreement leads to quarantine/manual or provider-specific reconciliation, not duplicate mutation.

---

# Contract F — Two successive compact joint-consensus certificates with no detailed membership log

## Problem

Membership moves C0 -> joint(C0,C1) -> C1 -> joint(C1,C2) -> C2. Detailed membership log entries are truncated. Two compact certificates remain. A snapshot may advertise C2 and a high `lastIncludedIndex`, but this alone does not prove that both joint transitions committed safely.

## Frozen rule

1. Each compact membership certificate binds predecessor membership root, old config, new config, transition index/term, commit evidence/quorum policy, and successor certificate root.
2. The second certificate must explicitly commit to the first certificate/root (or to a consistency accumulator that proves inclusion), creating a compact succession chain.
3. Snapshot `lastIncludedIndex/Term` positions the compact state but does not replace membership-transition proof.
4. If detailed logs are gone and either compact certificate is missing, forked, or incomparable, destructive GC/membership mutation is withheld; terminal C2 membership alone is insufficient.
5. Survivors drawn only from C0 or only from C2 cannot independently manufacture the missing C0->C1 or C1->C2 joint proof.
6. Re-snapshotting may compact the two certificates into a new root only if the new certificate proves inclusion/continuity of both prior transition obligations.

### Safety consequence

Log truncation and repeated snapshotting preserve consensus-membership proof obligations instead of collapsing them to the newest configuration label.

---

# 48-case RED-first matrix

The matrix is intentionally executable in shape but is not claimed executed. For each case, the pre-fix expectation is the unsafe/ambiguous behavior to reproduce; GREEN requires the frozen rule above.

## A. Forked compromise timing / emergency cut sets

| ID | Scenario | Required GREEN outcome |
|---|---|---|
| A1 | compromise proven after R0->R1; independent bridge survives | accept edge |
| A2 | compromise proven before R0->R1 and removes required domain | reject edge |
| A3 | two authenticated incomparable compromise timings change edge validity | `RECOVERY_SUCCESSION_AMBIGUOUS` |
| A4 | many signer keys but one shared failure domain | do not satisfy independence threshold |
| A5 | later R2 certificate omits earlier compromise-evidence root | reject compact succession |
| A6 | common successor orders both timing histories and proves surviving cut set | accept from common successor forward |
| A7 | predecessor mutations attempted while succession ambiguous | reject; retain proven floors |
| A8 | wall-clock-only compromise timestamp offered as tie-breaker | ignore as authority evidence |

## B. Retirement common successor later revoked

| ID | Scenario | Required GREEN outcome |
|---|---|---|
| B1 | C resolves B1/B2, later prospectively revoked | retain historical ordering; block new C signatures |
| B2 | C revoked retroactively across reconciliation interval | reopen ordering ambiguity but preserve max proven floor |
| B3 | fresh transition signed only by revoked C | reject |
| B4 | D succeeds C using still-valid independent authority and historical C statement | accept if continuity proven |
| B5 | revocation certificate lacks scope | fail closed on future authority; do not lower floor |
| B6 | verifier treats revoked C as if its old statement never existed | regression: reject that rollback |
| B7 | verifier treats historical C statement as permission for new C transition | reject |
| B8 | compact bridge stores scope-separated historical/future authority bits | accept correct scoped behavior |

## C. S3->S4 double-compacted unlearning lineage

| ID | Scenario | Required GREEN outcome |
|---|---|---|
| C1 | clean lineage with complete compact bridge chain | accept |
| C2 | unknown dependency at S2 propagated through S3/S4 | remain unknown |
| C3 | S3 details compacted but valid compact root retained | preserve status |
| C4 | S3 and S4 details compacted with chained roots | preserve status |
| C5 | one compact bridge deleted | `UNLEARNING_LINEAGE_UNRECOVERABLE` |
| C6 | S4 terminal metadata rewrites unknown->clean without revalidation | reject |
| C7 | retired S3 attempts mutation after migration | reject mutation, retain evidence role |
| C8 | fresh export from S4 without full revalidation closure | inherit unresolved status |

## D. Privacy residual leases / partition heal

| ID | Scenario | Required GREEN outcome |
|---|---|---|
| D1 | A1/A2 lease spends reconcile below total budget | accept union accounting |
| D2 | local lease expiry with no closure proof | do not reclaim |
| D3 | wall clock rolled backward after spend | no budget resurrection |
| D4 | both partitions spend near limit; union exceeds parent budget | fail closed on further release; record overrun |
| D5 | allocator generation rollback presents old residual checkpoint | reject rollback |
| D6 | one lease consumption unknown | charge conservative upper bound |
| D7 | common successor checkpoint covers both heads and exact event union | allow residual recomputation |
| D8 | deletion of released result/event row proposed as refund | reject refund |

## E. Provider delayed observations / retention expiry

| ID | Scenario | Required GREEN outcome |
|---|---|---|
| E1 | receipt retained and observer agrees effect happened | record one effect |
| E2 | receipt expired, no-effect independently proven | safe new semantic operation may proceed under new effect ID |
| E3 | receipt expired, effect status unknown | prohibit blind replay |
| E4 | O1 says effect present, O2 says absent, incomparable evidence | `EXTERNAL_EFFECT_EVIDENCE_FORK` |
| E5 | later observation has newer wall-clock timestamp only | do not auto-dominate |
| E6 | later observation has provider monotonic version above both prior states | may resolve if semantics prove comparability |
| E7 | observer majority disagrees with stronger monotonic provider evidence | stronger contract evidence wins; no generic majority rule |
| E8 | compensation/new mutation reuses E1 after retention expiry | reject identity reuse |

## F. Successive compact joint-consensus certificates

| ID | Scenario | Required GREEN outcome |
|---|---|---|
| F1 | C0->C1 and C1->C2 compact certs both valid and chained | accept C2 continuity |
| F2 | terminal snapshot says C2 but first cert missing | reject destructive authority |
| F3 | second cert does not commit to first/root | reject chain |
| F4 | higher `lastIncludedIndex` but forked membership provenance | do not prefer by freshness alone |
| F5 | only C0 survivors attempt to recreate C1/C2 evidence | reject |
| F6 | only C2 survivors attempt to assert historical transitions | reject |
| F7 | re-snapshot compacts both certs into inclusion/continuity root | accept if proof verifies |
| F8 | one transition certificate has correct configs but wrong index/term predecessor binding | reject |

---

# Cross-contract audit findings

1. **Historical validity and current authority must be separate dimensions.** This is the core of the revoked-common-successor case and also applies to retired lineage stores and compact membership evidence.
2. **Compaction must preserve proof obligations, not just terminal values.** A root/head/configuration label is insufficient unless it is linked to predecessor evidence by a verifiable consistency/succession proof.
3. **Uncertainty is monotonic until resolved by evidence.** Unknown unlearning ancestry, unknown privacy lease consumption, ambiguous recovery succession, and unknown external provider effect all fail closed rather than being normalized by restart/expiry/compaction.
4. **Wall-clock time is not authority.** It may drive liveness/operational cleanup, but not compromise ordering, privacy refunds, or provider-effect dominance without an authenticated monotonic contract.
5. **Irreversible external facts survive internal rollback.** Privacy disclosures and provider effects remain part of accounting/history even when local records are deleted, compensation occurs, or a branch loses reconciliation.
6. **No new production code should be implemented from this document until exact executable source is available.** The next implementation step is tests first against the real supported surface.

# Implementation shape when exact execution becomes available

- Add canonical compact certificate dataclasses/encodings only at the layer that owns each authority boundary; do not invent one generic certificate type.
- Add persisted predecessor roots and scope bits before deleting any detailed evidence.
- Add verification helpers that distinguish `VALID`, `AMBIGUOUS/UNKNOWN`, and `INVALID/REVOKED` rather than collapsing all failures into booleans.
- Add the 48 tests first and demonstrate RED for the intended unsafe/ambiguous baseline before production refactors.
- For privacy/provider cases, make effect/release identities immutable and test replay after retention/partition explicitly.
- For GC membership, test at least two successive transitions and snapshot/log truncation; one transition is insufficient evidence for the targeted failure mode.

# Current execution limitation

This run re-probed exact repository materialization first. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`. The GitHub connector remains usable as control plane, but no supported byte-exact connector-to-local-executor materialization primitive is available in this run. Consequently this document is architecture/evidence only; no LAB-086 or new-contract behavioral PASS is claimed.
