# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and PRs. GitHub connector is healthy, but no supported byte-preserving connector-response/predecessor+patch materialization transform is exposed for security-critical LAB-086 `strict_fence.py`. No LAB-086 branch mutation and no new behavioral PASS are claimed. #163 comment `5541864747` records the observation.

Completed the pre-recorded distinct fallback: froze `BROKER_STARTUP_RECOVERY_STATE_MACHINE_V1_FROZEN` in `research/2026-09-04-broker-startup-recovery-state-machine-v1.md`, main commit `81bc0eef31ac5b57eec03ab6e58b40aad8367b26`.

The broker is now a finite orchestration machine: construction -> side-effect-free verify -> observational external evidence -> pure plan -> at most one write-capable recovery execute -> mandatory full fresh reverify -> fresh final evidence/plan -> LAB-093 delegation. A recovery success never directly opens runtime. UNKNOWN, stale snapshot, concurrent progress, evidence outage and non-progress stop without an internal retry loop. Fatal trust discontinuity is never converted into repair. One executor invocation total per startup invocation is a hard liveness bound; repeated durable retries across invocations retain the same LAB-080 request id. Worker delegation requires a fresh aligned terminal snapshot, fresh NONE plan, no unresolved activation condition, and least-capability façade only. A 50-case RED-first matrix is frozen.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor/patch/target remain `d4a6a40f...` + `61841b58...` -> `b78e7c98...`; no supported connector-response-to-filesystem/Python machine transform has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Direct Git transport has repeatedly failed DNS before repository access in prior runs; no fresh exact repository behavioral PASS is claimed here.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage schema, startup verifier/planner, external-evidence continuity, recovery-executor grammar and finite broker startup state machine; no independent locally-valid provenance islands.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence-collector/recovery-executor/broker-state-machine contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the worker-session revocation/re-entry protocol after startup: exact authority/provenance/runtime conditions that invalidate a delegated LAB-093 session, in-flight request quiescing/draining, broker re-entry ordering, capability-generation binding, and proof that workers cannot retain stale SQLite/provider/activation handles across provider-generation, activation-authority or provenance-head changes. Do not implement production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical descriptors + chain binding + atomic recovery/storage/verifier/evidence/executor/broker-startup contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 + parent-linked chain + atomic recovery/storage/verifier/evidence/executor/broker startup; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle frozen; startup delegation gate now additionally frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance + canonical V1 + global chain + atomic recovery/storage/verifier/evidence/executor/broker startup + regression matrices frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 + global chain + atomic recovery/storage/verifier/evidence/executor/broker startup frozen.
