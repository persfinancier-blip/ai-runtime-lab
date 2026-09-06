# Current Lab State

Last updated: 2026-09-06

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and active draft PRs. The repository frontier remains consistent with the prior handoff: LAB-086 is still the blocking priority and downstream PRs remain draft.

Re-probed direct source execution with:

`git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-probe`

It failed before repository execution with `Could not resolve host: github.com` (exit 128). No security-critical source mutation was attempted and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `TRUST_FRONTIER_MONITOR_COMPLETENESS_WITNESS_LIVENESS_OMISSION_EVIDENCE_V1_FROZEN` in `research/2026-09-06-trust-frontier-monitor-completeness-witness-liveness-omission-evidence-v1.md`, main commit `4fee6eec192345761a03bb0ca0b13d2654b22091`; #178 comment `5557999550` records the result.

Key decisions:
- monitor identity is a content-addressed capability generation with operator/control/distribution/toolchain lineage; endpoint aliases are not independent monitors;
- completeness is an authenticated observation obligation over expected frontier advances, not a health boolean or old witness cosignature;
- monitoring coverage is evaluated only after stale/revoked/quarantined/scope-invalid monitors are removed and common-mode domains collapse; thresholds never auto-relax during outage/partition;
- publication and monitor-observation deadlines are explicit/versioned; an absent deadline is not unlimited staleness;
- classification distinguishes `DELAY_PENDING`, `STALE`, `OMISSION_SUSPECTED`, `OMISSION_PROVEN`, and `FORK`; stale is not automatically malicious but degrades consequential authority;
- authenticated newer mirror/archive evidence can expose uniform stale withholding across reachable online paths;
- liveness telemetry must bind monitor generation, observed checkpoint/frontier, policy generation and time source; dashboard/log heartbeat alone is diagnostic only;
- recovery preserves omission evidence and requires consistent catch-up; compromise/common-mode defects require new generation/re-admission;
- explicit 80-case RED-first matrix is frozen across identity/scope, non-vacuous coverage, liveness authenticity, diversity collapse, omission classification, deadlines/clocks, archive/offline evidence and restart/recovery.

Primary donors: RFC 9162 monitor/MMD/STH auditing semantics; C2SP `tlog-witness` monitor retrieval/stale-monitor partition model; C2SP `tlog-mirror` archival availability statement; Sigstore Rekor independent monitoring/event-stream model. Donor mechanisms only; no production monitor/witness network or behavioral compatibility PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring contracts rather than creating independent locally-valid authority islands.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception, plaintext-expanding evidence-policy upgrade, provider evidence-schema widening, fork recovery, or omission-recovery re-admission may be activated without required explicit authority bound to that exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze **monitor observation receipt / publication promise / omission challenge-response semantics**. Define canonical authenticated publication promises and monitor observation receipts; distinguish a verifiable missed deadline from non-provable absence; bind challenge requester/monitor/log/frontier/deadline into replay-resistant transcripts; define challenge windows and response evidence; prevent a monitor/log from selectively answering challengers with incomparable states; specify when archival/mirror evidence upgrades `STALE -> OMISSION_SUSPECTED`; define the additional signed/previously-held evidence required for `OMISSION_PROVEN`; retain challenge/timeout evidence across restart; and freeze RED cases for forged promises, replayed receipts, challenger partition, clock manipulation, selective challenge responses, absent-response false proofs and recovery after a resolved omission.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; provider evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitor-completeness contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
