# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current `get_pr_info` reports `mergeable=false`; do not change draft/merge status without the exact retained gate.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open PRs and exact PR #165 state/head.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto13` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `PUBLICATION_WITNESS_RECOVERY_QUORUM_LOST_STATE_DISASTER_RECOVERY_ANTI_CLONING_V1_FROZEN` in `research/2026-09-07-publication-witness-recovery-quorum-lost-state-disaster-recovery-anti-cloning-v1.md`, commit `7245755a888cec05bd6fd7cc3f1536d7f1673d76`; #178 comment `5573355056` records the result.

Key decisions:
- `SIGNING_KEY_POSSESSION != WITNESS_AUTHORITY != SINGLE_ACTIVE_WITNESS`;
- missing, rolled-back, corrupt or disputed witness checkpoint state forces `RECOVERY_REQUIRED_NO_COSIGN`; never restart from size zero;
- the current log endpoint alone is insufficient recovery evidence;
- recovery selects the highest uniquely quorum-supported safe lower bound, not the largest observed tree size;
- independently qualifying incompatible branches remain fork evidence and block signing as `RECOVERY_FORK_DISPUTE_NO_COSIGN`;
- accepted post-recovery cosignatures require a strictly monotonic activation epoch/fencing token, or an equivalent new signing-authority generation, so stale/restored clones cannot regain authority;
- leases coordinate liveness but do not replace stale-instance fencing;
- replicated/exportable/HSM key possession does not prove singleton execution; the signing/verification boundary must validate current activation authority;
- recovery activation is staged: no-cosign -> freeze old epoch -> collect independent evidence -> classify branches -> select safe frontier -> authorize -> atomically install -> activate fence -> prove stale paths fail -> resume;
- recovery-policy rotation requires predecessor+successor continuity or an explicitly separate higher-root emergency procedure;
- historical fork/equivocation evidence survives recovery;
- introduced `WitnessRecoveryEvidenceV1`, `RecoveredWitnessFrontierV1`, `WitnessRecoveryPolicyV1`, `WitnessActivationEpochV1`, 10 fraud/contradiction proof classes and an 80-case RED-first matrix.

Primary donors: C2SP `tlog-witness` v1.0.0 atomic checkpoint-state semantics; TUF predecessor+successor threshold migration; etcd revision/fencing semantics; AWS KMS multi-Region replicated key material as a negative donor for key-replication != singleton authority.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness/recovery contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **witness activation-epoch distribution / verifier freshness / stale-policy cache invalidation semantics**. Define how every relying verifier learns activation epoch E+1 quickly and authentically enough to reject signatures from a stale clone at E; how activation epochs are published and anti-rollback protected; what bounded-staleness/freshness evidence exists for online and offline verifiers; how cache expiry differs from authority revocation; and how to handle partitions where some relying parties have accepted E+1 while others still trust E without converting temporary propagation lag into an undetectable split-authority condition.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; witness recovery/lost-state/anti-cloning contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
