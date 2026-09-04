# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175, LAB-092 / #176 draft PR #177, LAB-088 / #167 draft PR #172, and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain follow-ups; LAB-093 now has both a frozen V1 façade schema and frozen endpoint/channel lifecycle contract, but no exact RED/GREEN implementation.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected the current open issues and PR frontier. Fresh direct repository execution was re-probed with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; it again failed before repository access with `Could not resolve host: github.com`.

LAB-086 therefore remains blocked on the exact machine-composition/source-execution capability; no `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed.

To avoid repeating that blocker, completed the next distinct LAB-093 architecture step: froze `LAB093_LEDGER_BROKER_V1` endpoint construction, channel authentication, descriptor-reuse, worker restart and broker restart authority semantics.

V1 uses one broker-created connected Unix-domain `SOCK_SEQPACKET` socketpair per worker process incarnation and intentionally has no ambient reconnect listener/bearer token. Authorization is attached to the live broker-side endpoint object, never selected by request fields, PID/UID alone, socket path or recyclable fd integer. `SO_PEERCRED` is fail-closed corroboration of the intentionally launched LAB-087 worker identity, not the source of authority.

Endpoint authorization is removed/revoked before socket close; a reused fd integer cannot inherit the old grant. Worker restart receives a fresh process/socketpair/authorization decision and reconstructs delegation only. Broker restart invalidates all old endpoints, reconstructs the canonical broker-owned authority graph, runs accepted durable verification + LAB-087 confinement checks, then creates fresh endpoints. No SQLite/provider/history/activation/keyring descriptor or `SCM_RIGHTS` capability crosses the worker protocol. Lost-response/retry semantics remain owned by LAB-080 canonical Intent/request idempotency, never transport `command_id`.

A 23-case lifecycle RED-first matrix is frozen covering peer mismatch, fd reuse, stale endpoint data, worker/broker restart, corrupt durable state, revocation, in-flight/lost-response/UNKNOWN handling, malformed frames, and the live-ledger in-process negative control.

Durable evidence: `research/2026-09-04-lab093-endpoint-channel-lifecycle-restart-authority.md`, main commit `f5c1bf8fd7fcab6441e628432f549fd438e47f9c`, #178 comment `5534733299`. Verdict: `LAB093_ENDPOINT_LIFECYCLE_V1_FROZEN` (architecture/source evidence only; exact RED/GREEN pending).

## Evidence produced
- `research/2026-09-04-lab093-endpoint-channel-lifecycle-restart-authority.md` — main commit `f5c1bf8fd7fcab6441e628432f549fd438e47f9c`; #178 comment `5534733299`; V1 socketpair/channel lifecycle, fd-reuse, restart authority and 23-case lifecycle matrix frozen.
- `research/2026-09-04-lab093-broker-facade-command-result-schema.md` — main commit `014ebbf6b881fc0cd58ce0a42e6fd9c5d3258de7`; #178 comment `5534292620`; V1 command/result schema, channel-bound authorization and 20-case façade RED-first matrix frozen.
- `research/2026-09-04-lab093-supported-delegation-surface-and-broker-reuse.md` — main commit `80e9995ead46f064b467f30ba8f329c00a4899db`; #178 comment `5533852032`; LAB-087 broker/process boundary selected for real delegated-ledger least-capability enforcement.
- `research/2026-09-04-lab093-delegated-ledger-capability-exposure.md` — main commit `994ada0ff1a5ec0c4b2a4dd8efa6f2e33dfca5b3`; #178 comment `5533390673`; concrete delegated least-capability violation proven.
- `research/2026-09-04-lab086-base64-range-fetch-capability.md` — main commit `ea105eb63cdbc8db2054b0c4cf8b6dd8d3e1c522`; #163 comment `5532852452`; exact line-range/base64 retrieval capability observed, but no machine handoff.
- `research/2026-09-04-lab091-fresh-reentrancy-write-surface-audit.md` — main commit `fa4c01c0334f9efc721127e24d6b76ab8a19d9f5`; #170 comment `5532300065`; fresh static reentrancy/write-surface audit PASS only.
- `research/2026-09-03-lab088-fresh-patch-authority-audit.md` — main commit `5bb50ffd122aa47ba83f54f494656906a1282ac3`; #167 comment `5531622222`; fresh authority audit PASS only.
- `research/2026-09-03-lab090-lab100-unified-provider-authority-redesign-contract.md` — main commit `4d303c94f4dcca95176e3e4653ade23b1c8cce0f`; #169 comment `5529408502`.
- `research/2026-09-03-lab092-minimal-safe-redesign-contract.md` — main commit `c215b3ab0ac5bb1c78dcd373077bac8174e3282f`; #176 comment `5528679972`.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor remains blob `d4a6a40f...`; predecessor and retained patch bytes are connector-retrievable, but no supported connector-response-to-filesystem/Python materialization bridge exists.
- Normal Contents `update_file` requires complete replacement UTF-8 and does not perform predecessor+patch transformation; required target blob `b78e7c98...` is not already present in the Git object database.
- Exact checkout/source execution remains unavailable; fresh direct Git clone again failed DNS before repository access. No fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-088: fresh static authority audit complete; supported-integration + downstream LAB-084/085/086 execution compatibility remain.
- LAB-091: fresh static reentrancy/write-surface audit complete; real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 restricted-worker composition and exact full regression/compile gates remain.
- LAB-090/LAB-100 should use the retained coherent provider-authority redesign contract; LAB-092 should use the retained domain-separated certificate + authority-schema/trigger + serialization-bound redesign.
- LAB-093: do not implement `_attested` renaming as a security fix. A real least-capability claim requires the lower-trust consumer to receive only the closed value-only V1 endpoint across LAB-087's process boundary. `verify_component`, provider rotation and activation operations are outside V1. Do not add a reconnect listener/bearer merely for convenience.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-088 supported/downstream gates, then LAB-091 full supported-surface gates, then the frozen LAB-090/LAB-100 RED matrix and LAB-092 regression matrix.

If neither capability appears, do not further elaborate LAB-093 transport without new source evidence: its V1 delegation and lifecycle contracts are sufficiently frozen for RED-first implementation. The next distinct evidence task is to reconcile LAB-094/#179, LAB-095/#180 and LAB-096/#181 into one construction-bound retained-authority graph contract from current source: bootstrap trust root, database identity/path and provider-history strategy must have one lifetime identity and one verified construction/restart boundary rather than three independent alias patches. Freeze the combined regression matrix, but do not write production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; unified LAB-090/LAB-100 authority redesign contract recorded; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; consolidated redesign contract recorded; exact regression/full gate pending.
- #178 / LAB-093 — READY; delegation violation proven, LAB-087 broker-boundary reuse selected, V1 façade schema + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..#185 / LAB-094..LAB-100 — READY regression-first follow-ups.
