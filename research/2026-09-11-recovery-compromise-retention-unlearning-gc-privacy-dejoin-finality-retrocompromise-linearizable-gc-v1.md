# Recovery compromise, retention expiry, unlearning-proof GC, privacy de-join, finality retro-compromise, and linearizable authority-GC — v1

Date: 2026-09-11
Status: FROZEN DESIGN / RED-FIRST
Contract name: `RECOVERY_COMPROMISE_RETENTION_UNLEARNING_GC_PRIVACY_DEJOIN_FINALITY_RETROCOMPROMISE_LINEARIZABLE_GC_V1_FROZEN`

## Scope

This slice extends the LAB-093 architecture after the previous recovery-fork/joint-bridge/unlearning-reanchor/resolver-equivocation/finality-overlap/SCC-invalidation freeze. It does **not** replace LAB-086 executable gates and does not claim production correctness. It freezes fail-closed invariants and a RED-first matrix for six remaining evidence problems:

1. convergence when the higher recovery authority that resolved a fork is itself later partially compromised;
2. safe retirement/expiry of stale-verifier obligations after joint membership/checkpoint retention;
3. garbage collection of revoked/superseded unlearning proofs without losing re-anchor provenance;
4. decomposing conservative privacy joins after source-log recovery without refunding cumulative spend;
5. retroactive compromise of a provider-finality generation after successor activation;
6. linearizable graph-snapshot/epoch rules that prevent `CAN_RESTORE` inventory mutation from racing destructive GC.

## Primary donors

- TUF root-update model: a new root is accepted only through sequential predecessor/successor threshold continuity; rollback is rejected. This is a useful donor for recovery-generation continuity, but threshold-root compromise still requires an out-of-band recovery assumption rather than circular self-authorization.
- RFC 9162 Certificate Transparency: Merkle consistency proofs establish append-only continuity between authenticated tree heads; a signed/inclusion-valid view alone does not establish cross-view consistency.
- Certified machine-unlearning literature: guarantees are theorem/profile/assumption scoped. A certificate is not a generic timeless fact independent of the proof system and assumptions that produced it.
- NIST SP 800-226: privacy budget is an upper bound on cumulative privacy loss. Resolver/source-log recovery may refine attribution but cannot refund already-consumed privacy loss merely because identity mapping changes.
- NIST SP 800-88 Rev. 2: cryptographic erase is an assurance/validation problem over relevant key material, including externally managed keys. This supports explicit authority-inventory closure before destructive GC.

## Frozen invariants

### A. Recovery authority later partially compromised

1. A recovery generation that resolved a prior fork is not retroactively treated as never having existed merely because one of its authority domains is later compromised.
2. Trust in that generation is interval-scoped: compromise evidence is evaluated against the signing/authorization interval and canonical failure-domain lineage.
3. If the surviving admissible domains no longer meet the generation's threshold or required intersection, the generation becomes `RECOVERY_AUTHORITY_UNCERTAIN`; it cannot authorize new recovery or GC.
4. Already-established rollback/equivocation floors are monotonic. A later compromise cannot make an older fork head canonical again.
5. Recovery from `RECOVERY_AUTHORITY_UNCERTAIN` requires a strictly higher generation that commits: both original fork heads, the contested recovery generation, the last uncontested predecessor, the compromise evidence/cutoff, and a newly sufficient independent quorum.
6. Raw key count is never a substitute for canonical failure-domain independence. Cross-signed/recovered/reassigned keys from one domain count once.
7. If no independent quorum remains, fail closed and require owner/out-of-band authority; do not synthesize continuity from compromised roots.

### B. Retirement of stale-verifier obligations after retention

8. A joint membership/checkpoint bridge creates a stale-verifier obligation set: which predecessor checkpoints/keys/proofs must remain available, for which verifier population/profile, until what authenticated expiry condition.
9. Wall-clock expiry alone is insufficient if expiry time is not bound to an authenticated monotonic epoch or trusted time source.
10. Retention may end only after an authenticated retirement record commits the bridge, retention floor, verifier-profile/version bound, and evidence that no supported verifier still requires predecessor material.
11. Revocation after retention start does not erase the obligation; replacement authority must either preserve the predecessor evidence or produce a bridge that old supported verifiers can authenticate.
12. Unsupported/explicitly retired verifier profiles may lose compatibility only through a recorded policy/version retirement event, not silent GC.
13. If predecessor evidence was deleted before authenticated retirement, continuity is irrecoverable for affected stale verifiers and the system must report a permanent verification gap.
14. Retention retirement must itself be append-only/checkpointed so rollback cannot resurrect an expired obligation or hide premature deletion.

### C. GC of revoked/superseded unlearning proofs

15. Revoked/superseded unlearning certificates are evidence in a provenance DAG even when they are no longer current authorization.
16. A current certificate must retain a cryptographic/provenance link to the theorem/profile root, superseded certificate(s), revocation reason, and re-proof/re-anchor event that established the current guarantee.
17. GC may remove bulky proof payloads only after preserving a compact authenticated tombstone/commitment sufficient to reconstruct the supersession/revocation path and detect substitution/rollback.
18. GC must not collapse `EXACT`, `CERTIFIED_BOUND`, `EMPIRICAL`, and `UNKNOWN` into one status; downgrade history is part of the retained provenance.
19. Revocation because of a theorem/profile soundness defect propagates to dependent descendants unless each descendant has an independent proof under a non-defective root.
20. Re-signing or format migration is not re-proof and cannot justify deleting the defective ancestor provenance.
21. If a retained compact commitment cannot prove which assumptions and deleted-data lineage the current certificate inherited, GC fails closed.

### D. Privacy de-join after source-log recovery

22. Resolver/source-log equivocation may force a conservative join of candidate identity/accounting histories. That join is an uncertainty response, not a new privacy event.
23. After a recovered source generation commits both conflicting heads and resolves mapping, attribution may be decomposed into proven components, but cumulative spend already incurred is never refunded.
24. A de-join may release only reservations/unknown-loss margins that are proven not to have been consumed and whose release is authorized by evidence newer than the fork cutoff.
25. Consumed privacy loss remains attached to the appropriate canonical dataset/subject lineage; if attribution remains ambiguous, charge the conservative upper bound.
26. Namespace rotation, tombstone collision repair, split/merge repair, or resolver replacement cannot create a fresh budget.
27. De-join evidence binds source heads, fork ancestor, recovery generation, cutoff, source-set digest, accounting floor, and released reservation identifiers.
28. Replaying pre-recovery resolver evidence cannot lower the post-recovery accounting floor.

### E. Provider-finality generation retro-compromise

29. Successor activation does not make predecessor finality attestations immutable facts if predecessor signing authority is later shown compromised during the relevant interval.
30. Retroactive authority compromise changes confidence in receipts/finality evidence, not the external side effect itself. A destructive effect becomes `EFFECT_UNKNOWN` unless independently reconciled.
31. Successor finality generation may attest predecessor effects only when its transition contract explicitly includes predecessor unresolved/forked ranges and it has independent evidence to reconcile them.
32. A successor signature over a predecessor receipt is not independent evidence if both authorities share the compromised failure domain/root.
33. Finality floors remain monotonic: compromise cannot authorize blind retry, erase compensation ancestry, or infer `NO_EFFECT` from a sequence gap.
34. Two independently admissible but conflicting reconciliations are `FINALITY_FORK`; timestamp/arrival/newer-generation ordering does not choose the winner.
35. Resolution requires a higher finality generation that commits the conflicting attestations, affected sequence/effect range, compromise cutoff, and independently sufficient reconciliation evidence.

### F. Linearizable `CAN_RESTORE` graph snapshot vs destructive GC

36. Every destructive authority-GC decision binds an immutable authenticated graph snapshot identifier and GC epoch. The proof is valid only for that snapshot/epoch.
37. Inventory mutation that could add/reclassify `CAN_RESTORE` reachability must serialize with GC epoch admission. It cannot race after proof evaluation but before destruction.
38. Safe rule: `BEGIN_GC(epoch,snapshot) -> freeze/admit inventory mutations -> compute SCC/fixed point -> validate unknown edges absent -> destructive step -> durable COMMIT_GC -> release mutation barrier`. Crash before `COMMIT_GC` leaves the epoch unresolved and requires reconciliation, not assumption of success.
39. A mutation queued during GC is applied only in a strictly higher graph epoch; if it reveals predecessor-restoration authority relevant to the just-completed destruction, the system records a sanitization-assurance incident and blocks dependent claims rather than pretending the prior proof covered it.
40. Unknown/unreadable inventory domains, cyclic issuer dependencies, or inability to prove the snapshot covered every enumerated authority domain keep the relevant SCC live and block destructive GC.

## RED-first test matrix

The 40 invariants above map one-to-one to initial RED tests. Minimum test harness requirements:

- explicit generation/epoch IDs and canonical failure-domain identities;
- interval-scoped compromise records;
- authenticated predecessor/successor checkpoint heads and consistency/bridge records;
- unlearning supersession DAG with theorem/profile roots and compact tombstones;
- privacy accounting ledger with consumed spend, reservations, unknown-loss margins, resolver fork/recovery heads and immutable accounting floor;
- provider-finality receipts with effect IDs, sequence ranges, generation transition records and independent reconciliation evidence;
- authenticated `CAN_RESTORE` graph snapshots, SCC computation, graph epochs and a deterministic GC/mutation scheduler capable of forcing race interleavings.

### Required negative seeds

At minimum preserve explicit expected failures for:

- selecting a recovery fork winner after the resolving recovery quorum falls below admissible threshold;
- deleting stale-verifier predecessor evidence on unauthenticated wall-clock expiry;
- GC of a revoked unlearning ancestor without a compact provenance commitment;
- refunding consumed privacy spend after resolver de-join;
- blindly retrying an effect after retroactive compromise of predecessor finality authority;
- adding a `CAN_RESTORE` edge between proof evaluation and destructive GC without forcing a new graph epoch.

## Security decisions

- **Monotonic uncertainty/floor principle:** later evidence may increase uncertainty or require a higher recovery generation, but it cannot lower a previously established rollback/equivocation/privacy/finality/security floor without explicit new evidence satisfying the higher-generation contract.
- **Evidence vs capability:** historical receipts, proofs, checkpoints and compact tombstones are evidence only. They never regain mutation/signing capability merely because they remain verifiable.
- **No circular self-repair:** a compromised authority cannot prove itself uncompromised, and an authority-inventory issuer cannot establish extinction if its own restoration chain remains in the live SCC being judged.
- **GC is a protocol, not deletion:** destructive cleanup requires authenticated snapshot binding, serialization against authority discovery/mutation, crash reconciliation, and durable completion evidence.

## Implementation order when exact execution becomes available

1. Keep LAB-086 priority first and execute its pinned exact real-schema gate.
2. For LAB-093+, implement the six negative seeds above before production changes.
3. Add data structures for generation/epoch/cutoff/snapshot binding without changing mutation authority.
4. Execute the full 40-case RED matrix and record exact failures.
5. Implement the smallest coherent state-machine changes domain by domain.
6. Re-run full matrix plus inherited LAB-080..092 supported surfaces and restricted-worker composition.
7. Perform a separate security audit for alternate write surfaces, rollback/replay, correlated-authority counting, crash windows, and GC/inventory races.

## Current-run execution observation

The preferred LAB-086 exact-source path was probed first. Direct `git clone --no-checkout` failed before repository code execution with `Could not resolve host: github.com`. GitHub connector reads/writes remained available. No LAB-086 executable PASS is claimed by this document.