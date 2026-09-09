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

Completed the recorded distinct fallback and froze `EMERGENCY_ROOT_LIVENESS_ACCUMULATOR_MULTIBEACON_ADJUDICATION_PQ_REPLAY_V1_FROZEN` in `research/2026-09-09-emergency-root-liveness-accumulator-multibeacon-adjudication-pq-replay-v1.md`, main commit `04cb36026bcd105616604b784bf53d3d7f4f344a`; #178 comment `5600267952` records the result.

Key decisions:
- dormant emergency-root assurance now separates custody secrecy, current liveness and current recovery authority. Liveness challenges bind nonce/purpose/root+membership generation/policy/deadline/verifier; timeout means liveness is unproven, not that the key is lost, and partial-loss member replacement creates a new authenticated membership generation rather than silently reducing threshold;
- promise-frontier compaction now requires stable promise identity, immutable compaction generations and global exact conservation/anti-omission evidence. Sampled membership proofs or equal counts are insufficient; archive survivability must retain enough predecessor/population, canonicalization, mapping and checkpoint evidence to reverify the compaction after service retirement;
- multi-beacon assurance now distinguishes source count from independence evidence. Source population/rounds/combiner/timeouts/missing-source/fallback/retry rules are frozen before reveal; selective abort, post-reveal retry and fallback rebinding are explicit bias surfaces. Threshold-BLS uniqueness is not availability/fairness proof;
- copy-domain conflict adjudication is itself a versioned authority surface. Unresolved `PRESENT`/`POSSIBLE` dominates `ABSENT` for destruction completeness; appeals/reversals create successor generations, required topology-source classes/population must be completeness-accounted, and adjudicator compromise degrades affected decisions without erasing history;
- provenance/PQ evidence must survive transparency-log sharding/key rotation/retirement through archived entry/checkpoint/inclusion/trust-root lineage. TUF-style root metadata is monotonic and rejects signed rollback. PQ/hybrid negotiation evidence binds both offer sets, selected suite/combiner policy, retry/fallback path and fresh session context; archived transcripts cannot authorize another session;
- frozen 40-case RED-first matrix across emergency-root challenge replay/DoS/replacement, promise accumulator conservation/archive, multi-beacon independence/selective-abort/timeout fairness, copy-domain adjudication/appeal/completeness and provenance/PQ replay/downgrade.

Primary donors: NIST SP 800-57 Part 1 Rev. 5 / Rev. 6 IPD; RFC 9162 / CT lineage; NIST IR 8213 and public randomness-beacon work; drand threshold-BLS; TUF root/version rollback rules; Sigstore/Rekor sharding/trust-root model; TLS 1.3 transcript binding and RFC 9954 hybrid key exchange.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **emergency-root challenge-channel anti-amplification/rate-limit evidence and quorum-recovery authorization under simultaneous member compromise + promise-accumulator deletion/garbage-collection safety with historical non-membership proofs + multi-beacon source enrollment/removal governance and correlated outage recovery without outcome-conditioned denominator changes + copy-domain adjudicator quorum/independence and evidence-confidentiality boundaries + provenance transparency mirror/witness independence, trust-root expiry/offline recovery, and PQ negotiation state-machine downgrade across retries/resumption/0-RTT**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers challenge-bound dormant emergency-root liveness and partial-loss membership replacement, archive-reproducible promise conservation accumulators, precommitted multi-beacon independence/timeout/selective-abort semantics, versioned copy-domain conflict adjudication/completeness, and transparency/TUF/PQ negotiation replay/downgrade resistance; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
