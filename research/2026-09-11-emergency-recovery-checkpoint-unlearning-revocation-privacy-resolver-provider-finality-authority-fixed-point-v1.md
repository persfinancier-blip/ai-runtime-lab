# Emergency recovery, compact checkpoints, revocable unlearning, resolver convergence, provider-finality quorums, and authority fixed points

Date: 2026-09-11
Status: DESIGN FROZEN / RED-FIRST; no executable PASS claimed
Primary follow-up: LAB-093 / #178. LAB-086 remains priority #1.

## Why this slice exists

LAB-086 exact-source execution was probed first in this run. Direct `git clone --no-checkout` failed before repository execution with `Could not resolve host: github.com`. The GitHub connector remains readable/writable, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed. The retained LAB-086 exact-byte gate therefore forbids manual/model reserialization of the executable closure.

This note completes the next distinct evidence task recorded in `state/CURRENT.md`. It freezes contracts and RED cases only; it is not executable proof and does not change any draft PR state.

## Primary donors

1. **The Update Framework (TUF) root continuity.** Root replacement requires sequential versions and each successor root must satisfy both the predecessor root threshold and the successor root threshold. This is a useful donor for emergency recovery authority continuity and rollback resistance, but it does not by itself solve a predecessor that is already known compromised over the relevant signing interval.
   - https://theupdateframework.github.io/specification/v1.0.26/

2. **RFC 9162 Certificate Transparency.** Merkle consistency proofs establish append-only consistency between authenticated tree heads; auditing the consistency of the view shown to all entities requires comparing observations. This is the donor for checkpoint anchoring of compacted membership history and for refusing split-view compaction.
   - https://www.rfc-editor.org/rfc/rfc9162.html

3. **Guo et al., Certified Data Removal from Machine Learning Models (ICML 2020).** Certified removal is guarantee-specific: the post-removal model must satisfy a stated indistinguishability relationship to a model that never observed the removed data. A certificate therefore inherits the assumptions/theorem/profile under which it was issued; a defect in that theorem/profile cannot be repaired by retaining the old certificate unchanged.
   - https://proceedings.mlr.press/v119/guo20c.html

4. **NIST SP 800-226 privacy budget.** Privacy budget is an upper bound on cumulative privacy loss across analyses of a dataset. Resolver-version rollback or identity-graph disagreement therefore cannot mint new budget merely by presenting a different mapping.
   - https://csrc.nist.gov/glossary/term/privacy_budget

5. **NIST SP 800-88 Rev. 2.** Cryptographic sanitization requires assurance/validation and explicitly addresses externally managed keys. This is the donor for recursive authority-inventory completeness: a local assertion of deletion is insufficient while a reachable recovery/escrow/backup authority may restore predecessor material.
   - https://csrc.nist.gov/pubs/sp/800/88/r2/final

## Frozen contract

`EMERGENCY_RECOVERY_CHECKPOINT_UNLEARNING_REVOCATION_PRIVACY_RESOLVER_PROVIDER_FINALITY_AUTHORITY_FIXED_POINT_V1_FROZEN`

### A. Emergency recovery authority with overlapping compromised predecessor roots

**Invariant A1 — successor continuity is necessary but not sufficient.**

A recovery generation `g+1` must bind:
- the last uncontested recovery generation/root;
- every known conflicting/equivocating branch at `g`;
- the compromise-evidence interval and evidence digest;
- the successor root identity, threshold, failure-domain set, and validity interval;
- an authorization relation that is independent of any predecessor authority known compromised over the issuance interval.

TUF-style `old-threshold + new-threshold` continuity is acceptable only when the old threshold remains admissible for the transition interval. If the predecessor threshold is already compromised for that interval, its signature may be retained as historical evidence but cannot be counted as the independent authorization needed to restore trust.

**Invariant A2 — overlapping emergency roots do not multiply independence.**

Two recovery roots that share a signing key, operator/controller, HSM tenant, escrow root, recovery credential, or `CAN_RESTORE` ancestor are correlated until proven otherwise. Threshold counting uses canonical failure-domain identity, not key count.

**Invariant A3 — recovery never lowers learned uncertainty floors.**

A later clean recovery can authorize future state but cannot erase the fact that an earlier generation had rollback/equivocation/compromise uncertainty. Historical decisions affected by that interval remain disputed unless separately revalidated.

### B. Authenticated checkpoint anchoring for compacted witness membership

**Invariant B1 — compact membership requires an anchored predecessor checkpoint.**

A compacted witness-membership checkpoint must commit at minimum to:
- monotonic membership epoch;
- canonical witness identities and failure-domain lineage;
- key-validity intervals;
- thresholds;
- tombstone/reassignment events;
- predecessor checkpoint hash/tree head;
- event cutoff covered by compaction.

**Invariant B2 — compaction needs consistency, not merely inclusion.**

A membership entry being included under a signed compact root does not prove that older authenticated membership history was not dropped or rewritten. Accept compaction only when there is an authenticated consistency/continuity proof from the last retained predecessor checkpoint to the new compact checkpoint.

**Invariant B3 — split view blocks GC.**

If two valid checkpoint heads for the same epoch/cutoff cannot be proven consistent, the system enters explicit membership equivocation. Neither branch is eligible to authorize GC of predecessor evidence.

### C. Revocation/recomputation of certified-unlearning claims after theorem/profile defect

**Invariant C1 — certificate validity is profile-scoped.**

An unlearning certificate binds `(algorithm, theorem/profile version, assumptions, model lineage, removed-set identity, retained-set commitment, randomness/noise regime, evaluation cutoff)`.

A defect or withdrawal in the theorem/profile invalidates affected certificates as authorization evidence even when their signatures remain valid.

**Invariant C2 — revocation is monotonic; replacement is recomputation.**

Revoking a defective profile cannot be undone by resigning the old result under a new key. A replacement claim requires recomputation or a new proof whose theorem explicitly proves safe transformation from the prior evidence.

**Invariant C3 — correlation survives certificate boundaries.**

Certified claims for components cannot be independently composed when residual state shares optimizer history, caches, embeddings, distillation lineage, adapters, ensemble teachers, or randomness in a way outside the theorem's composition assumptions. Unsupported composition degrades to `UNKNOWN`, not an invented aggregate certificate.

### D. Privacy-accounting convergence under resolver fork/rollback

**Invariant D1 — accounting has a monotonic canonical floor independent of resolver version.**

Maintain a privacy-accounting floor keyed by stable accounting lineage, not solely by one mutable resolver graph. Every resolver version may add aliases/links and may cause conservative aggregation, but no version may reduce cumulative spent/reserved/unknown-loss below the maximum already established for potentially related subjects.

**Invariant D2 — rollback cannot resurrect budget.**

If resolver `v3` merges identities A/B and later the runtime rolls back to `v2` where they were separate, both lineages retain at least the merged cumulative floor until a sound disjointness proof with an authenticated cutoff establishes how future accounting may separate. Historical loss is never refunded.

**Invariant D3 — fork convergence is conservative.**

When resolvers disagree, the converged state is the conservative join of all reachable claims: union possible-subject linkage; max/appropriate composition of spent and reservations; preservation of unknown-loss. Resolver disagreement is not proof of disjointness.

### E. Competing provider-finality authorities

**Invariant E1 — finality is authority-scoped and fork-detecting.**

A provider-finality statement binds provider identity, operation identity/digest, provider sequence or causality token, effect state, authority generation, and evidence cutoff. Two valid incompatible finality statements for the same operation/causal predecessor create `FINALITY_FORK`; timestamp or arrival order does not choose a winner.

**Invariant E2 — failover does not silently supersede predecessor finality.**

A successor/failover authority may finalize only if its transition evidence explicitly covers predecessor outstanding operations and forks, or if independent reconciliation proves the external effect. Otherwise predecessor `UNKNOWN` remains unresolved.

**Invariant E3 — quorum independence is canonical.**

Multiple finality signers that share a recovery root, signing service, operator, replicated database, or restore domain count according to canonical failure domains. Cross-signing and key rotation do not create independent votes.

### F. Fixed-point authority inventory with unknown/cyclic `CAN_RESTORE` edges

Model authority restoration as a directed graph. `A -> B` means authority/domain A can restore or recreate B's effective secret/credential/issuer capability.

**Invariant F1 — extinction is a fixed-point property.**

An authority is extinct only when every reachable restoration path is proven sanitized/revoked/unusable under current policy. Evaluation recursively expands known `CAN_RESTORE` edges until a fixed point is reached.

**Invariant F2 — unknown is live for GC purposes.**

An unknown/unenumerated edge or an inventory issuer whose completeness cannot be independently authenticated prevents extinction proof. `UNKNOWN` is conservatively treated as potentially restorable for ticket/security-epoch GC.

**Invariant F3 — cycles require an external break proof.**

A cycle such as `KMS -> escrow -> recovery credential -> KMS` cannot prove its own extinction by mutually signed assertions. At least one edge/node in every restoration cycle requires externally grounded sanitization/revocation evidence not derivable from the cycle itself.

**Invariant F4 — inventory issuers are part of the graph.**

The credential/authority that signs the inventory or completeness proof is itself a restoration-capable node if predecessor authorities can recreate it. Completeness proof is invalid while its issuer remains inside an unresolved restoration cycle.

## State machines / fail-closed outcomes

Use explicit states rather than booleans:

- Recovery: `TRUSTED -> DISPUTED -> RECOVERY_PENDING -> RECOVERED_FUTURE_ONLY`; historical affected interval remains separately marked.
- Membership checkpoint: `ANCHORED -> COMPACTABLE -> COMPACTED`; any inconsistent head yields `EQUIVOCATION` and blocks GC.
- Unlearning evidence: `VALID_PROFILE -> PROFILE_DISPUTED -> REVOKED -> RECOMPUTED_VALID`; signature validity does not bypass profile state.
- Privacy resolver: `AGREE`, `FORKED`, `ROLLBACK_DETECTED`, `CONSERVATIVE_JOIN`; budget floor monotonic in every state.
- Provider effect: `UNKNOWN`, `FINAL`, `FINALITY_FORK`, `RECONCILED_FINAL`; failover alone never maps fork/unknown to final.
- Authority inventory: `ENUMERATING`, `FIXED_POINT_REACHED`, `UNKNOWN_EDGE`, `CYCLIC_UNRESOLVED`, `EXTINCTION_PROVEN`.

## 40-case RED-first matrix

### Emergency recovery roots (1-7)
1. Clean predecessor + clean successor with predecessor+successor thresholds and no overlap -> accept continuity.
2. Predecessor known compromised before transition signing -> predecessor signatures cannot supply independent recovery authorization.
3. Emergency successor shares HSM/operator with compromised predecessor -> correlated; do not count as independent domain.
4. Two successor roots cross-sign each other with no uncontested ancestor/external authority -> reject circular trust creation.
5. Higher recovery generation omits one known equivocation branch -> reject incomplete recovery payload.
6. Higher recovery generation binds all conflicts but tries to clear historical disputed interval -> reject uncertainty-floor rollback.
7. Later compromise evidence overlaps previously accepted recovery issuance -> reopen affected recovery decision; do not silently revoke future monotonic generation floor.

### Compact witness checkpoints (8-14)
8. Compact root includes current membership but lacks predecessor checkpoint hash/consistency proof -> reject compaction.
9. Valid predecessor->successor consistency proof and monotonic epoch -> allow compaction subject to retention policy.
10. Same epoch/cutoff has two inconsistent signed compact roots -> `EQUIVOCATION`, block GC.
11. Compaction drops tombstone then old witness key reappears -> reject resurrection.
12. Key rotation under same canonical witness identity -> one witness vote, not two.
13. Reassignment of canonical identity without authenticated lineage -> reject checkpoint.
14. GC would delete the only evidence needed to prove a currently unresolved membership interval -> block GC.

### Certified unlearning (15-21)
15. Certificate under valid theorem/profile and satisfied assumptions -> eligible evidence.
16. Profile is withdrawn for a soundness defect -> all affected certificates become revoked/disputed regardless of signature validity.
17. Old certificate is merely resigned under new key/profile id without recomputation -> reject.
18. New proof theorem explicitly proves safe transformation from old artifact and assumptions hold -> accept replacement.
19. Two certified components share optimizer/cache lineage outside theorem composition rule -> aggregate result `UNKNOWN`.
20. Component deletion leaves distilled/ensemble descendant not covered by certificate -> descendant retains deletion lineage; reject full-removal claim.
21. Recomputed proof uses changed retained-set commitment without binding new set -> reject evidence substitution.

### Privacy resolver convergence (22-27)
22. Resolver v2 separates A/B; v3 merges them -> cumulative floor conservatively joins.
23. Runtime rolls back v3->v2 -> merged historical floor persists; no refunded budget.
24. Two concurrent resolver versions disagree on A/B linkage -> use conservative join, not preferred-version overwrite.
25. One resolver says `NO_MATCH` while another says `POSSIBLE_MATCH` -> retain possible linkage/unknown-loss.
26. Later sound disjointness proof with cutoff permits future separation -> historical cumulative loss remains, only future accounting may separate per proof scope.
27. Namespace/version rotation maps subject to fresh identifier -> cannot create fresh budget lineage.

### Provider finality authorities (28-34)
28. One valid finality receipt for exact operation digest/sequence under current independent authority -> eligible final evidence.
29. Two valid incompatible receipts for same operation/predecessor -> `FINALITY_FORK`; no timestamp tie-break.
30. Failover authority claims finality but transition omitted predecessor outstanding set -> reject silent supersession.
31. Failover transition binds outstanding set and independent reconciliation proves effect -> allow `RECONCILED_FINAL`.
32. Finality quorum uses three keys backed by one signer service/recovery root -> count canonical failure domain, not keys.
33. Old receipt signing key later compromised over issuance interval -> authority-validity disputed; destructive effect returns to `UNKNOWN` absent independent reconciliation.
34. Provider sequence gap exists before purported final receipt -> reject inferred no-effect for missing sequence.

### Authority fixed point (35-40)
35. All enumerated nodes sanitized but one `UNKNOWN CAN_RESTORE` edge remains -> extinction not proven.
36. KMS key deleted locally but escrow can restore wrapped predecessor -> extinction not proven.
37. KMS<->escrow recovery cycle mutually asserts deletion with no external break evidence -> reject circular proof.
38. Independent sanitization evidence breaks every restoration cycle and no unknown edges remain -> fixed-point extinction may be proven.
39. Inventory completeness signer can itself be restored by predecessor authority -> inventory proof remains cyclic/untrusted.
40. Delayed discovery adds dormant backup/recovery node after prior GC decision -> reopen extinction assessment, quarantine affected resumption/recovery domain, never lower already monotonic security epoch floor.

## Implementation guidance when exact execution becomes available

1. Add RED tests at the existing authority/history abstractions before production changes.
2. Represent canonical identities/failure domains and validity intervals explicitly; never infer independence from key IDs.
3. Persist monotonic floors separately from mutable resolver/profile/current-head views.
4. Use authenticated predecessor hashes/checkpoints for any compaction that discards detailed history.
5. Treat revocation/profile validity as a separate dimension from cryptographic signature validity.
6. Model external-effect finality as a state machine with explicit fork/unknown states.
7. Compute authority extinction over a graph until a fixed point; fail closed on cycles without external break evidence and on unknown edges.

## Audit

- No claim here depends on GitHub Actions/background workers.
- No branch code or security-critical executable payload was manually reconstructed.
- The contracts are monotonic/fail-closed and do not weaken previously frozen floors for rollback, equivocation, privacy loss, external-effect uncertainty, or key-authority extinction.
- The new slice is distinct from prior freezes: it focuses on compromised *recovery-of-recovery* authority, authenticated compaction checkpoints, revoking guarantee claims after theorem/profile defects, resolver-version convergence, competing finality authorities, and graph fixed-point completeness.

Verdict: `EMERGENCY_RECOVERY_CHECKPOINT_UNLEARNING_REVOCATION_PRIVACY_RESOLVER_PROVIDER_FINALITY_AUTHORITY_FIXED_POINT_V1_FROZEN`.
