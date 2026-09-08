# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto13` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 is confirmed open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `WITNESS_PARTITION_CROSSLOG_OBLIGATION_BEACON_LIVENESS_SEMANTIC_ATTESTER_PROVENANCE_EFFECTIVE_TIME_V1_FROZEN` in `research/2026-09-08-witness-partition-crosslog-obligation-beacon-liveness-semantic-attester-provenance-effective-time-v1.md`, main commit `5b5152b2332a476acc98c2f8363861deb50384e1`; #178 comment `5591304017` records the result.

Key decisions:
- a partitioned witness/verifier must reconcile monotonically from its independently retained frontier; same-size/different-root is equivocation, larger-without-consistency-proof is UNKNOWN, and no newer checkpoint observed is never proof of latestness;
- mandatory cross-log anchoring is positively omission-provable only from a previously retained deadline-bearing promise plus authenticated post-deadline destination state and canonical non-inclusion evidence; timeout/404/empty query remain UNKNOWN;
- failed threshold-beacon completion proves availability failure, not member malice; attributable non-participation requires a prior participation obligation plus sufficiently complete independently authenticated observation evidence;
- semantic repair quorum counts independent reproductions under explicit provenance/control-domain policy, not signatures, processes, endpoints or copied outputs; deterministic divergence fails closed instead of majority-voting semantic truth;
- provenance-authority compromise/revocation carries an authenticated effective time/sequence boundary; provably pre-boundary evidence may remain historically usable under frozen policy, post-boundary evidence is rejected, and unknown-boundary evidence fails closed for consequential current use;
- late compromise/common-mode disclosure re-appraises current reliance without erasing historical evidence;
- frozen 64-case RED-first matrix across witness partition recovery, cross-log promise omission, beacon liveness attribution, semantic-attester independence, and provenance compromise effective-time.

Primary donors: RFC 9162 CT promise/MMD + consistency/auditing; transparency.dev witness retained-checkpoint semantics; drand threshold partials/catch-up; in-toto/SLSA independent functionary/reproduction boundaries; Sigstore transparency + TUF compromise-time/revocation boundary.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **witness-membership denominator continuity across partition + cross-log destination compromise/recovery + beacon observation-quorum completeness/collector equivocation + semantic-attester anti-copy challenge timing + compromise-boundary adjudication authority**. Define how membership changes during a partition preserve historical denominator and cannot silently discard a dissenting witness; how an anchor promise survives compromise or replacement of the destination log; what positive evidence is sufficient to call the liveness observation surface complete when collectors disagree or disappear; how commit/reveal ordering prevents semantic attesters from copying peers while still allowing deterministic reproducibility; and who can establish/correct an earlier compromise effective boundary without letting a compromised provenance authority self-exonerate or retroactively invalidate arbitrary history.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through witness partition recovery, cross-log anchor obligations, beacon liveness evidence, semantic-attester independence, and provenance compromise effective-time frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
