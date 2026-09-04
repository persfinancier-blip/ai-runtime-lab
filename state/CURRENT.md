# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175, LAB-092 / #176 draft PR #177, LAB-088 / #167 draft PR #172, and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain follow-ups; LAB-093 now has a selected boundary direction but no exact RED/GREEN implementation.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and draft PR #175. Fresh direct repository execution was re-probed with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; it again failed before repository access with `Could not resolve host: github.com`.

LAB-086 therefore remains blocked on the same exact machine-composition/source-execution capability; no `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed.

To avoid repeating that blocker, completed the next distinct LAB-093 architecture step. Mapped the proven delegated `ledger.attested` capability leak against merged LAB-087. LAB-087 already owns the real process/filesystem security boundary: broker owns the writable DB and worker gets a narrowed read-only handle; same-process Python introspection is explicitly outside its claim. Its current concrete façade is DB-only, so LAB-093 must extend/reuse the broker process with a **value-only ledger command/result protocol**, not rename `attested` or hand a lower-trust worker a live ledger object.

Selected first narrow delegated operations: `RESERVE | EXECUTE | ENTRY | VERIFY_DURABLE` as immutable/serializable messages/results. Broker-only/unreachable nodes: live ledger object, `AttestedCatchup`, provider/increment capability, LAB-090 activation state/methods, provider-history helper/locked methods, writable SQLite connection and DB path authority. Provider rotation remains a separate broker/admin capability, not generic reflective RPC. This direction also composes LAB-094/095/096 into one construction-bound authority graph rather than independent underscore fixes.

Durable evidence: `research/2026-09-04-lab093-supported-delegation-surface-and-broker-reuse.md`, main commit `80e9995ead46f064b467f30ba8f329c00a4899db`, #178 comment `5533852032`. Verdict: `LAB093_BROKER_BOUNDARY_REUSE_SELECTED` (architecture/source evidence only; exact RED/GREEN pending).

## Evidence produced
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
- LAB-093: do not implement `_attested` renaming as a security fix. A real least-capability claim requires the lower-trust consumer to receive only a value-only endpoint across the LAB-087 broker/process boundary, never the live ledger object.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-088 supported/downstream gates, then LAB-091 full supported-surface gates, then the frozen LAB-090/LAB-100 RED matrix and LAB-092 regression matrix.

If neither capability appears, continue only with distinct concrete evidence. For LAB-093 the next useful non-execution step is to freeze the exact value-only command/result schema and authorization boundary that can be implemented inside the LAB-087 broker, including a negative control proving that an in-process live-ledger façade cannot support the security claim. Do not implement production code before executable RED/GREEN is possible.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; unified LAB-090/LAB-100 authority redesign contract recorded; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; consolidated redesign contract recorded; exact regression/full gate pending.
- #178 / LAB-093 — READY; concrete delegation violation proven and LAB-087 broker-boundary reuse selected; exact protocol RED/GREEN pending.
- #179..#185 / LAB-094..LAB-100 — READY regression-first follow-ups.
