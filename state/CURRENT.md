# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and open PRs. GitHub connector is healthy.

Re-probed LAB-086 direct transport in this runtime: `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository access with `Could not resolve host: github.com` (exit 128). Connector surfaces repository bytes and normal Contents writes but still exposes no supported machine operation that consumes exact predecessor bytes + retained unified patch and emits transformed bytes. `strict_fence.py` was not model-reserialized/mutated; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `APPLICATION_IDEMPOTENCY_ARCHIVE_OBJECT_RETRIEVAL_V1_FROZEN` in `research/2026-09-05-application-idempotency-archive-object-identity-availability-authenticated-retrieval-v1.md`, main commit `e910581a1f404a0daf30681b3bab7748ca4795a3`; #178 comment `5547090853` records the result.

Key decisions: archive locators/paths/provider version IDs are retrieval hints, not authority; every sealed epoch has an immutable authenticated manifest identity binding logical history, canonical format/version, exact bytes digest/length, record count/range/root and parent checkpoint. Bytes from any replica are accepted only after re-authentication. A negative is complete only when active exact state plus every authority-required epoch is covered by authenticated exact lookup or a manifest-bound exact global index. Missing/unavailable/restoring/UNKNOWN epochs never become `MISS`. Multi-copy improves availability only. Byte-identical restore may move copies without changing authority; semantically equivalent re-encoding requires a separately authenticated migration/repack transition. Startup/delegation may not silently skip unavailable historical epochs. A 68-case RED-first matrix is frozen.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session revocation/re-entry, request/effect boundary, durable request/effect registry, application idempotency/result delivery, authenticated install/retention, bounded-growth/resource-exhaustion, consumed-key archival/checkpoint and authenticated archive retrieval contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence/recovery/broker/session/request/registry/application-idempotency/install-retention/capacity/archive/retrieval contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the **archive manifest/index mutation + replica lifecycle protocol**: canonical add/remove-locator operations, new exact-index generations, index/object replacement ordering, replica deletion eligibility, cold-tier migration, concurrent compaction versus manifest update, and crash recovery such that availability maintenance cannot mutate historical authority or create a coverage gap. Do not implement production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive-checkpoint/archive-retrieval contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
