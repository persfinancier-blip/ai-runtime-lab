# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain visible: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #165; resumed LAB-086 first.

Current-run capability/state:
- GitHub connector reads/writes are available;
- PR #165 is confirmed `open`, `draft`, `mergeable=false` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- retained prior evidence still says strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is complete LAB-080→086 real-ledger execution, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `RECOVERY_FRONTIER_RANDOMNESS_COPYDOMAIN_PQ_SUPPLY_CHAIN_V1_FROZEN` in `research/2026-09-09-recovery-frontier-randomness-copydomain-pq-supply-chain-v1.md`, main commit `20f61c98f522e4170cb4602fe6776533469af8db`; #178 comment `5598638007` records the result.

Key decisions:
- recovery-quorum membership/threshold changes create authenticated generations; a compromised incumbent cannot self-certify recovery; emergency-root authority must be authenticated before the incident, remain independently survivable, and obey a monotonic anti-rollback floor; historical quorum denominators do not shrink retroactively;
- receipt/log key migration must preserve an authenticated outstanding-promise frontier. K1 promises cannot disappear during K2/log rollover; positive omission requires a sufficiently late authenticated state/frontier and canonical non-inclusion/omission proof, not `404`/absence;
- challenge sampling now binds exact population, sampler/version, beacon/VRF epoch/input and commit ordering before usable randomness. `VERIFIABLE_RANDOM_OUTPUT != UNBIASED_SAMPLE`; VRF/beacon validity does not prevent population/input/round grinding, fallback rebinding or post-output algorithm changes;
- `CopyDomainUniverse` is a versioned authenticated topology claim with explicit domain×time coverage. Topology drift creates successor evidence; signed empty inventories prove absence only within authenticated scope; uncovered cells remain `NEGATIVE_SPACE_UNCOVERED`;
- PQ migration evidence now binds migration builder/parser/canonicalizer/crypto/verifier provenance, authenticated build/SBOM lineage, exact hybrid-combiner policy and complete algorithm-negotiation transcript. `VALID_PQ_SIGNATURE != TRUSTED_MIGRATION`; verifier independence is by implementation/failure domain and disagreement fails closed;
- frozen 40-case RED-first matrix across recovery authority, promise frontier, verifiable sampling, copy-domain topology and PQ supply-chain/negotiation.

Primary donors: RFC 9162; RFC 9381; drand distributed randomness beacon documentation; NIST SP 800-57 Part 1 Rev. 5 + Rev. 6 IPD; NIST IR 8547 IPD; NIST PQC project/FIPS 203/204/205.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **emergency-root custody-domain independence and dormant-key liveness proof + promise-frontier compaction/renewal without obligation loss + multi-beacon composition and last-revealer bias/abort semantics + copy-domain topology discovery reconciliation across mutually inconsistent authorities + PQ provenance-attestation key compromise/revocation and canonical negotiation transcript anti-equivocation**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers recovery-quorum/emergency-root generations, promise-frontier migration, commit-before-randomness verifiable sampling, versioned copy-domain topology, and PQ migration supply-chain/negotiation/verifier-diversity boundaries; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
