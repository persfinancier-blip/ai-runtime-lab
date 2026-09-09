# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain visible: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/open PRs and PR #165; resumed LAB-086 first.

Current-run capability/state:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` was re-probed and failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes are available;
- PR #165 is confirmed `open`, `draft` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- retained prior evidence still says strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is complete LAB-080→086 real-ledger execution, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `EMERGENCY_ROOT_PROMISE_COMPACTION_MULTIBEACON_COPYDOMAIN_PQ_ATTESTATION_V1_FROZEN` in `research/2026-09-09-emergency-root-promise-compaction-multibeacon-copydomain-reconciliation-pq-attestation-v1.md`, main commit `eda0f3e9729ddb0d03bcee170c2041d5d82db39e`; #178 comment `5599485464` records the result.

Key decisions:
- emergency-root assurance now separates key count from independent custody/destructive-control domains. Emergency authority must pre-exist the incident, dormant keys require challenge-bound liveness with a frozen freshness policy, routine liveness must not reconstruct private material centrally, and correctly signed stale root metadata below the anti-rollback floor is rejected;
- promise-frontier compaction is an authenticated successor generation with an exact conservation invariant: every predecessor promise maps exactly once to `FULFILLED`, `OUTSTANDING_CARRIED`, or a policy-valid terminal disposition. Counts alone do not prove conservation, compaction cannot reset deadlines, and historical obligations must remain traceable across generations;
- multi-beacon composition fixes source population, source rounds, combiner, timeout, missing-source and fallback rules before reveal. Post-reveal subset selection/selective abort/fallback rebinding are explicit bias surfaces. Threshold-BLS availability failure is not interpreted as a choice among alternate valid random outputs;
- copy-domain topology reconciliation preserves conflicting authenticated source assertions. For destruction/negative-space claims, unresolved `PRESENT`/`POSSIBLE` dominates `ABSENT` fail-closed; absence only carries within the source's authenticated scope/interval; adjudication creates a successor generation rather than rewriting losing evidence;
- PQ provenance-attestation trust now binds signer/build-platform key epochs, compromise/revocation effective times, freshness/anti-rollback trust metadata, build-vs-reattest status, and complete two-sided algorithm-negotiation transcript. Logged/signed SBOM/provenance does not prove an uncompromised or semantically correct build; conflicting authenticated negotiation transcripts are positive equivocation evidence;
- frozen 40-case RED-first matrix across emergency-root liveness, promise compaction, multi-beacon selective-abort bias, copy-domain reconciliation, and PQ provenance/negotiation recovery.

Primary donors: NIST SP 800-57 Part 1 Rev. 5; RFC 9162; NIST IR 8213 / Randomness Beacon v2; drand protocol/security docs; SLSA provenance; Sigstore threat model; NIST IR 8547 and crypto-agility guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **emergency-root liveness challenge secrecy/denial-of-service and quorum-member replacement under partial loss + authenticated accumulator/proof design for promise compaction and archive survivability + multi-beacon independence/correlation evidence and commit/reveal timeout fairness + copy-domain conflict-adjudicator authority/appeal and topology-source completeness proofs + provenance transparency-log survivability, attestation transparency/TUF-style root rollover, and PQ negotiation replay/cross-session binding**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers emergency-root independent custody + dormant-key liveness, promise-frontier conservation compaction, precommitted multi-beacon composition/selective-abort handling, conflict-preserving copy-domain reconciliation, and PQ provenance-attestation compromise/revocation + negotiation anti-equivocation; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
