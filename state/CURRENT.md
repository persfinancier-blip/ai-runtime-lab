# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and active PRs. GitHub connector is healthy.

LAB-086 machine-transform probe remains blocked in this runtime. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository access with `Could not resolve host: github.com`. No supported byte-preserving predecessor+patch materialization path was observed, so `strict_fence.py` was not model-reserialized or mutated and no new LAB-086 behavioral PASS is claimed.

Completed the pre-recorded distinct fallback: froze `WORKER_EFFECT_COMPLETION_RESULT_DELIVERY_APPLICATION_IDEMPOTENCY_V1_FROZEN` in `research/2026-09-04-worker-effect-completion-result-delivery-application-idempotency-v1.md`, main commit `cb00039442711d0388dfe1dae7b91e61ad157532`; #178 comment `5544708024` records the result.

The LAB-093 bridge now distinguishes live-session `(session_id,worker_request_id)` idempotency from optional cross-session application idempotency. A cross-session key is canonical, principal/namespace scoped, and bound before effect preparation to one application-operation digest. New sessions can only observe/redeliver the exact immutable COMMITTED result after fresh authorization and full durable verification; they never inherit the old session, provider request, provenance transition or recovery ownership. BOUND keys block duplicate effects through PREPARED/UNKNOWN. Same key + different operation is an explicit conflict. V1 tombstones preserve non-reusability rather than turning expiry into a second effect opportunity. A 50-case RED-first matrix is frozen.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge from those bytes to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage schema, startup verifier/planner, external-evidence continuity, recovery-executor grammar and finite broker startup state machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, worker-session revocation/re-entry, request-envelope/effect-boundary, durable request/effect registry, and cross-session application-idempotency/result-delivery contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence-collector/recovery-executor/broker-state-machine/session-revocation/request-envelope/registry/application-idempotency contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the application-idempotency registry installation/provenance + retention-authority contract: authenticated first-install/migration, deletion detection, authority for COMMITTED->TOMBSTONED, retention-policy identity/version binding, crash-safe tombstone creation, and proof that cleanup cannot make a historical application key reusable or erase evidence needed for startup verification. Do not implement production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical descriptors + chain binding + atomic recovery/storage/verifier/evidence/executor/broker-startup contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 + parent-linked chain + atomic recovery/storage/verifier/evidence/executor/broker startup; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle + startup delegation gate + session revocation/re-entry + canonical request/effect boundary + durable request/effect registry + application-idempotency/result delivery frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance + canonical V1 + global chain + atomic recovery/storage/verifier/evidence/executor/broker startup + regression matrices frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 + global chain + atomic recovery/storage/verifier/evidence/executor/broker startup frozen.
