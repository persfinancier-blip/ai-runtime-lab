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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and active PRs. GitHub connector is healthy. A fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`, so no LAB-086 branch mutation and no new behavioral PASS are claimed. The retained exact lineage remains unchanged and manual/model reserialization of security-critical `strict_fence.py` remains prohibited.

Completed the pre-recorded distinct fallback: froze `WORKER_REQUEST_ENVELOPE_EFFECT_BOUNDARY_V1_FROZEN` in `research/2026-09-04-worker-request-envelope-effect-boundary-v1.md`, main commit `b46b174d2d8cc5a2526525eaff8e9fcf8f2fd53f`; #178 comment `5543370911` records the result.

Worker session validity now authorizes compute only, not a later effect. Every worker request has one canonical immutable value-only envelope/digest and one `(session_id, worker_request_id)` binding. Broker performs both pre-dispatch and fresh pre-effect checks against current session epoch, provider generation, LAB-100 authority digest, authenticated provenance head, aligned evidence and sole-writer state. Duplicate exact requests converge; same id with altered digest fails closed. LAB-080 provider request identity remains authoritative for external effects and is associated one-to-one with the worker request rather than replaced by it. Once an operation reaches PREPARED/UNKNOWN, ownership transfers irreversibly to broker-owned exact-request recovery; stale workers cannot retry or mint a new effect. Lost committed responses are presentation retries only. A 50-case RED-first matrix is frozen.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor/patch/target remain `d4a6a40f...` + `61841b58...` -> `b78e7c98...`; connector can fetch the retained patch blob, but no supported machine path from connector bytes + predecessor to exact transformed bytes has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Fresh direct Git transport in this run failed DNS before repository access: `Could not resolve host: github.com`; no exact repository behavioral PASS is claimed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage schema, startup verifier/planner, external-evidence continuity, recovery-executor grammar and finite broker startup state machine; no independent locally-valid provenance islands.
- LAB-093 must additionally implement the frozen least-capability façade, worker-session revocation/re-entry and worker request-envelope/effect-boundary protocols; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence-collector/recovery-executor/broker-state-machine/session-revocation/request-envelope contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the durable worker-request/effect registry storage + crash-consistency contract: exact tables/keys/state transitions for canonical worker request digest, one-to-one worker-request -> provenance/LAB-080 effect association, atomic PREPARED ownership transfer, terminal-result immutability, restart reconstruction without reviving old session authority, duplicate convergence, and deletion/rebinding detection. Do not implement production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical descriptors + chain binding + atomic recovery/storage/verifier/evidence/executor/broker-startup contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 + parent-linked chain + atomic recovery/storage/verifier/evidence/executor/broker startup; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle + startup delegation gate + worker-session revocation/re-entry + canonical request/effect boundary frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance + canonical V1 + global chain + atomic recovery/storage/verifier/evidence/executor/broker startup + regression matrices frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 + global chain + atomic recovery/storage/verifier/evidence/executor/broker startup frozen.
