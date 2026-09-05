# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live PR head rechecked this run: `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. GitHub connector is healthy. PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

LAB-086 capability probe improved one observation: the connector can return the exact predecessor blob `d4a6a40f...` and retained patch blob `61841b58...` in full. However, no supported operation in this runtime mechanically feeds those connector-returned bytes to a patch engine/materializer and emits a byte-verified replacement payload. Normal Contents writes still require complete replacement text. Manual/model reserialization of security-critical `strict_fence.py` remains prohibited, so no branch mutation or new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `EFFECTIVE_AUTHORITY_LEASE_ONE_SHOT_CRASH_REPLAY_V1_FROZEN` in `research/2026-09-05-effective-authority-lease-issuance-one-shot-consumption-crash-replay-v1.md`, main commit `ea1776c9f99cb1cfea515aa9b840b2ac41c889b3`; #178 comment `5552094267` records the result.

Key decisions: `EffectiveAuthorityLeaseV1` is one-shot attempt authority, exact-bound to operation/effect/attempt/application-key/payload/surface/provider/scope and all relevant authority generations; adapter verifies it immediately before consequential I/O; durable claim/consumption state prevents copied/replayed/stale leases across processes and restarts; `SEND_STARTED` is committed before provider I/O and conservatively marks the point after which local state cannot prove absence of an external effect; timeout/crash after that point enters UNKNOWN and cannot mint fresh effect authority; safe retry may reuse only the original pinned provider request/idempotency identity when provider capability semantics prove it safe; quarantine/revocation removes new authority but cannot erase an already-started external attempt. A 72-case RED-first matrix is frozen. No production code or behavioral PASS is claimed.

Primary donors recorded: RFC 9449 DPoP for request-bound proof and replay tracking; RFC 9396 for structured fine-grained authorization; July 2026 IETF Transaction Tokens draft for signed short-lived transaction context; RFC 7523 for `jti` replay-tracking pattern. LAB adds durable one-shot consumption, exact payload/effect binding, crash/UNKNOWN semantics and global provenance.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session/request/effect registry, application-idempotency/result delivery, authenticated retention/archive/DR/escrow/re-root/epoch/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, or manual consequential re-attempt may be activated without required explicit product/security/business authorization bound to the exact payload/effect.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze an **effective-authority retry authorization / in-flight attempt recovery contract**. Define a non-effect-minting retry authority that can authorize only the already pinned provider request identity after `SEND_STARTED`; exact predicates for same-token resend vs read-only oracle vs manual reconciliation; how retry authority survives broker restart without becoming a generic SEND lease; interaction with provider retention/expiry, `PENDING`, `COMMITTED`, `STRONG_NEGATIVE`, `UNKNOWN`, quarantine and capability drift; and crash races between retry claim, provider call and outcome commit. Prove that retry/recovery cannot create a second provider request identity or turn lease expiry/worker death into fresh effect authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/DR/escrow/human-reroot/post-reroot/client/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
