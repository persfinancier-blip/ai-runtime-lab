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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues, active draft PRs and repository branches. PR #165 remains open/draft and its own remaining gate still requires exact strict/thaw publication plus full LAB-080→086 real-ledger execution before ready/merge.

Re-probed direct source execution with:

`git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`

It failed before repository execution with `Could not resolve host: github.com` (exit 128). No security-critical source mutation was attempted and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `COMPATIBILITY_TRUST_FRONTIER_WITNESS_SPLIT_VIEW_GOSSIP_CHECKPOINT_CONSISTENCY_V1_FROZEN` in `research/2026-09-06-compatibility-trust-frontier-witness-split-view-gossip-checkpoint-consistency-v1.md`, main commit `67585ba2121ffe208a034961ccfb68177cfc64f4`; #178 comment `5557701639` records the result.

Key decisions:
- consequential compatibility admission requires a canonical signed trust-frontier checkpoint that is consistent with the verifier's retained checkpoint and satisfies current witness quorum/diversity policy; issuer signature alone is insufficient;
- frontier state is derived from an append-only canonical event history committed by Merkle event root plus direct predecessor checkpoint digest;
- witnesses are content-addressed capability generations, not merely keys; each verifies origin/signature/ancestry/consistency, atomically persists its latest accepted checkpoint, then cosigns;
- witness quorum is calculated only after scope/freshness/revocation/quarantine/common-mode diversity collapse;
- same-size/different-root or otherwise consistency-incompatible authenticated checkpoints are durable split-view evidence and fail closed regardless of observation channel;
- checkpoint gossip crosses independent service/witness/verifier/archive/offline channels; multiple endpoints under one common distribution/control domain do not create diversity;
- stale/withholding and fork are distinct states: stale state may catch up by consistency proof, while a fork cannot be resolved by latest/largest/majority-wins;
- partitions never implicitly weaken witness threshold; reconnect cross-compares checkpoints before consequential admission resumes;
- offline/archive restore cannot lower a newer retained/global frontier, and restored witness state must not cosign behind externally observed prior state;
- confirmed fork recovery requires separate explicit recovery authority, preserves both branches/fork evidence, binds the last common checkpoint, rotates compromised generations as needed, and revalidates affected compatibility edges;
- explicit 80-case RED-first matrix is frozen across checkpoint identity/canonicalization, consistency/ancestry, witness atomicity/diversity, gossip, withholding, partitions, revocation/compromise, offline restore and fork recovery.

Primary donors: RFC 9162 append-only consistency/split-view model; C2SP `tlog-witness`, checkpoint, cosignature and policy specifications; transparency-dev witness operational model. These are donor mechanisms only; no production witness network/verifier or behavioral compatibility PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier contracts rather than creating independent locally-valid authority islands.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception, plaintext-expanding evidence-policy upgrade, provider evidence-schema widening or fork recovery may be activated without the required explicit authority bound to that exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **trust-frontier monitor completeness / witness-liveness / omission-evidence contract**. Define required monitor identities/capabilities/diversity; publication/deadline commitments for frontier checkpoints; evidence that monitors actually observed required advances; benign delay vs selective omission/withholding; stale-but-non-equivocating witness degradation; archival-channel detection when reachable clients are uniformly withheld; monitoring coverage proofs that cannot be satisfied vacuously; and RED cases for silent monitor gaps, delayed publication, common-mode monitor outages, forged liveness telemetry, archive-only newer checkpoints, witness freshness collapse and recovery after omission.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; provider evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
