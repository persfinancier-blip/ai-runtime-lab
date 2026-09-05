# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live PR head remains `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs, #163 and live PR #165. LAB-086 remains first priority; PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b` and the authoritative hidden-rowid lineage remains unchanged.

Probed LAB-086 first in this runtime with a real `git clone --no-checkout`. Git transport again failed before repository access with `Could not resolve host: github.com` (exit 128). The connector remains readable/writable, but no supported machine bridge was observed that can consume exact connector-returned predecessor bytes plus the retained patch and mechanically emit the byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `TRANSPORT_OBSERVER_IMPLEMENTATION_ADMISSION_V1_FROZEN` in `research/2026-09-05-transport-observer-implementation-admission-contract-v1.md`, main commit `c4bc78136546934f3d6a72ce2a3a2b91aa3d7251`; #178 comment `5554207590` records the result.

Key implementation decision: durable `SINK_ENTERED` is appended and committed **before** entering the first forwarding-capable transport sink, then all DB locks/transactions are released before network I/O. This intentionally trades some availability for safety: after `SINK_ENTERED`, crash/timeout/reset/cancellation/missing callback is at least UNKNOWN absent an authenticated protocol-certified non-processing proof. `FAILED_BEFORE_IO` is legal only when failure is durably known to precede sink entry. This closes the crash-after-I/O-before-observation persistence gap without holding SQL transactions across network operations.

Concrete admission profiles are frozen for Python socket/plain TCP, Python SSL/TLS, HTTP/1 pools, HTTP/2/gRPC and proxy/service-mesh paths. Hidden retries, redirects, hedges, proxy retries, alternate upstream replay or middleware resend are admission failures unless exposed as separate authority-visible attempts. Multiplexed transports require exact stream attribution. Observer callbacks are evidence-only and may not send/retry/reconnect/redirect or synchronously reacquire provider/pool locks. Generic process-global socket monkeypatching is not sufficient proof when native/C-extension/kernel/proxy paths can bypass it.

A 64-case RED-first matrix is frozen covering pre-sink failures, partial write/sendall ambiguity, TLS, HTTP/1 pooling/retry/redirect, HTTP/2 `REFUSED_STREAM`/GOAWAY, gRPC cancellation/hedging, proxy forwarding, reentrancy/deadlock/evidence loss, restart/profile drift and provenance failure. No production observer or behavioral PASS is claimed.

Primary donors recorded: CPython `socket` and `ssl` documentation, urllib3 connection-pool retry/redirect semantics, RFC 9113 HTTP/2 stream non-processing proofs, and gRPC request-hedging behavior.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Direct git transport in this run failed before repository access with DNS resolution failure.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session/request/effect registry, application-idempotency/result delivery, authenticated retention/archive/DR/escrow/re-root/epoch/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease/retry-authority/replay-capsule/semantic-extractor/final-request-freeze/transport-egress-observation/transport-observer-admission contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, or manual consequential re-attempt may be activated without required explicit product/security/business authorization bound to the exact payload/effect.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze an **observer evidence durability / bounded queue / recovery-journal contract**. Specify how pre-call `SINK_ENTERED` and post-call observations persist under SQLite lock contention, process crash, disk-full, torn write, queue overflow and multi-process writers without holding a blocking SQL transaction around network I/O; define fail-closed admission/backpressure behavior, append/recovery ordering, bounded evidence loss semantics and a RED-first fault matrix. Keep production observer code read-only/offline until executable RED/GREEN exists.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/DR/escrow/human-reroot/post-reroot/client/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease/retry-authorization/replay-capsule/semantic-extractor/final-request-freeze/transport-egress-observation/transport-observer-admission contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
