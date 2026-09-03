# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175, LAB-092 / #176 draft PR #177 (observed head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`), LAB-088 / #167 draft PR #172, and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain READY follow-ups.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, and current open issues/PRs. Fresh direct repository execution was re-probed with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; it again failed before repository access with `Could not resolve host: github.com`.

Re-probed the LAB-086 connector path and found one new exact-retrieval capability: `fetch_file` can return `strict_fence.py` as base64 for an exact source line range while preserving/reporting the live predecessor blob SHA `d4a6a40f...`; the retained hidden-rowid patch is also base64-readable on the LAB-086 branch. This removes the earlier assumption that connector source retrieval is only one presentation-truncated whole-file UTF-8 payload.

The missing step is still a supported connector-response -> filesystem/Python materialization bridge. Copying the security-critical file chunk-by-chunk through model output would violate the retained no-manual/no-model-reserialization contract, and Contents `update_file` still requires a complete replacement body rather than a predecessor+patch transform. Therefore `strict_fence.py` was not mutated and no behavioral PASS is claimed.

Durable evidence: `research/2026-09-04-lab086-base64-range-fetch-capability.md`, main commit `ea105eb63cdbc8db2054b0c4cf8b6dd8d3e1c522`, #163 comment `5532852452`.

## Evidence produced
- `research/2026-09-04-lab086-base64-range-fetch-capability.md` — main commit `ea105eb63cdbc8db2054b0c4cf8b6dd8d3e1c522`; #163 comment `5532852452`; exact line-range/base64 retrieval capability observed, but no machine handoff yet.
- `research/2026-09-04-lab091-fresh-reentrancy-write-surface-audit.md` — main commit `fa4c01c0334f9efc721127e24d6b76ab8a19d9f5`; #170 comment `5532300065`; fresh static reentrancy/write-surface audit PASS only.
- `research/2026-09-03-lab088-fresh-patch-authority-audit.md` — main commit `5bb50ffd122aa47ba83f54f494656906a1282ac3`; #167 comment `5531622222`; fresh authority audit PASS only.
- `research/2026-09-03-lab086-target-blob-object-database-probe.md` — main commit `bb3536ef482500073132abb1a3d05edb19d9972a`; #163 comment `5530915770`.
- `research/2026-09-03-lab086-current-connector-patch-capability-probe.md` — main commit `c306505f700f91423275618274f44dbabb0c4524`; #163 comment `5530170080`.
- `research/2026-09-03-lab090-lab100-unified-provider-authority-redesign-contract.md` — main commit `4d303c94f4dcca95176e3e4653ade23b1c8cce0f`; #169 comment `5529408502`.
- `research/2026-09-03-lab092-minimal-safe-redesign-contract.md` — main commit `c215b3ab0ac5bb1c78dcd373077bac8174e3282f`; #176 comment `5528679972`.
- Retained LAB-092 evidence includes carrier-schema/trigger authentication, preseedable marker, explicit-migration/shared-tail, and constructor/restart/post-construction TOCTOU findings.
- Retained LAB-100 evidence includes provider subclass authority, inherited rotate bypass, caller-owned activation state, reconstructed provider position/request-result split, rejected-ticket orphan reservation, and reconstructed fence-counter reuse.
- Retained LAB-086 machine-handoff evidence includes `research/2026-09-03-lab086-container-download-handoff-probe.md` commit `3cc6187748211c8800a6a39d387aa5043f59b96d` and full-blob connector reprobe commit `159ad6ed9edab9ab870e8cb9fc244df53bed43b8`.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor was freshly conflict-checked through the connector and is still blob `d4a6a40f...`.
- Exact predecessor and patch bytes are now known to be retrievable in bounded base64 chunks through the connector, but the current runtime exposes no supported direct connector-response-to-filesystem/Python materialization bridge.
- Normal Contents `update_file` requires the complete replacement UTF-8 text and does not perform predecessor+patch transformation.
- The required target blob `b78e7c98...` is not already present in the repository object database, so exact-object reuse is not a fallback.
- Exact checkout/source execution remains unavailable; direct git DNS resolution failed again in this run. No fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-088 fresh static authority audit is complete; only supported-integration + downstream LAB-084/085/086 execution compatibility gates remain.
- LAB-091 fresh static reentrancy/write-surface audit is complete; real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 restricted-worker composition and exact full regression/compile gates remain.
- LAB-090/LAB-100 should be handled through the retained coherent provider-authority redesign contract rather than more unrelated lifecycle conditionals.
- LAB-092 should be handled through its retained domain-separated certificate + authority-schema/trigger + serialization-bound redesign rather than more independent `_classify()` checks.

## Exact next action
LAB-086 first: probe specifically for a supported connector/file materialization operation that can consume a GitHub file/blob response (including exact base64 line-range chunks) as machine input into the filesystem/Python runtime without model reserialization.

If such a bridge appears, mechanically reconstruct predecessor bytes and first require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; mechanically apply only retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-088's existing LAB-083 `test_supported_integration.py` suite plus downstream LAB-084/LAB-085/LAB-086 compatibility gates on exact PR #172 head; then run LAB-091 final supported-class real LAB-080/LAB-082 integration + two-worker/crash + timeout-after-commit/UNKNOWN + LAB-087 restricted-worker composition. Both fresh static audits are already complete. Then run the frozen 16-case LAB-090/LAB-100 RED matrix before production changes, followed by the retained LAB-092 regression matrix before production changes there.

If neither exact composition nor exact source execution becomes available, continue only with concrete distinct trust/capability/fail-closed evidence or consolidation that materially strengthens an existing issue; do not create duplicate narrow findings.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending; bounded base64 source retrieval observed, machine handoff still missing.
- #167 / LAB-088 — IN_PROGRESS; fresh patch authority audit PASS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; unified LAB-090/LAB-100 authority redesign contract recorded.
- #170 / LAB-091 — IN_PROGRESS; fresh static reentrancy/write-surface audit PASS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending; consolidated redesign contract recorded.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups; LAB-100 composes into the unified PR #175 authority redesign contract.
