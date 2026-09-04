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

LAB-086 capability probe improved but did not cross the publication safety boundary: `fetch_blob` returned the complete exact predecessor blob `d4a6a40f...` and complete retained patch blob `61841b58...`. However, no supported operation in the current runtime can mechanically apply the patch to connector-returned bytes and feed the exact transformed payload to normal Contents publication. The Contents API still requires a complete replacement text. Copying/reconstructing the ~950-line security-critical source through model text would be prohibited manual/model reserialization. Therefore no LAB-086 branch mutation and no behavioral PASS are claimed.

Completed the pre-recorded distinct fallback: froze `WORKER_REQUEST_EFFECT_REGISTRY_STORAGE_V1_FROZEN` in `research/2026-09-04-worker-request-effect-registry-storage-v1.md`, main commit `6e559593ab612fffa214100583773d06e1c3e433`; #178 comment `5544096583` records the result.

The durable LAB-093 registry now freezes broker-private STRICT request/binding/result storage. Durability begins only at effect preparation; old worker sessions are never restart-resumable authority. One `(session_id,worker_request_id)` binds one canonical worker request digest; one durable request binds one canonical effect; ANCHORED effects bind one provenance transition and one existing LAB-080 intent rather than minting another provider request namespace. Durable PREPARED is immediately broker recovery-owned, UNKNOWN preserves the exact original LAB-080 request identity, and COMMITTED terminal results are immutable/presentation-only. Restart invalidates all sessions, verifies canonical joins and deletion/rebinding/orphans, and reconstructs only broker-owned recovery duty. A 50-case RED-first matrix is frozen.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch connector payloads are now directly observable in full, but no supported byte-preserving transform/materialization bridge from those payloads to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage schema, startup verifier/planner, external-evidence continuity, recovery-executor grammar and finite broker startup state machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, worker-session revocation/re-entry, request-envelope/effect-boundary, and durable request/effect registry contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence-collector/recovery-executor/broker-state-machine/session-revocation/request-envelope/registry contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the worker effect completion/result delivery + application-idempotency bridge contract: distinguish session-scoped worker request idempotency from optional cross-session application idempotency; define canonical application key binding, lookup/authorization after restart, committed-result replay without re-execution, conflict semantics, retention/tombstone rules, and how a new session may discover a prior COMMITTED result without reviving old session authority. Do not implement production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical descriptors + chain binding + atomic recovery/storage/verifier/evidence/executor/broker-startup contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 + parent-linked chain + atomic recovery/storage/verifier/evidence/executor/broker startup; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle + startup delegation gate + session revocation/re-entry + canonical request/effect boundary + durable request/effect registry frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance + canonical V1 + global chain + atomic recovery/storage/verifier/evidence/executor/broker startup + regression matrices frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 + global chain + atomic recovery/storage/verifier/evidence/executor/broker startup frozen.
