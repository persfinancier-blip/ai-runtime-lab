# Current Lab State

Last updated: 2026-09-03

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175, LAB-092 / #176 draft PR #177 (observed head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`), LAB-088 / #167 draft PR #172, and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain READY follow-ups.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open PR state, and #163. Re-probed direct repository transport with `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`; it again failed before repository execution with `Could not resolve host: github.com`.

Then inspected the current GitHub connector mutation surface specifically for a safe LAB-086 fallback. The connector exposes normal full-file Contents replacement with current-blob conflict protection, but no supported operation that machine-applies a unified diff/patch to an existing Git blob. PR/file patch operations are read-only. Because `update_file` requires complete replacement UTF-8 text, it cannot safely compose the complete security-critical predecessor with the retained hidden-rowid patch without model/manual reserialization. No LAB-086 branch mutation and no fresh behavioral PASS were claimed.

This capability result is now durable in `research/2026-09-03-lab086-current-connector-patch-capability-probe.md` and #163 comment `5530170080`.

## Evidence produced
- `research/2026-09-03-lab086-current-connector-patch-capability-probe.md` — main commit `c306505f700f91423275618274f44dbabb0c4524`; #163 comment `5530170080`.
- `research/2026-09-03-lab090-lab100-unified-provider-authority-redesign-contract.md` — main commit `4d303c94f4dcca95176e3e4653ade23b1c8cce0f`; #169 comment `5529408502`.
- `research/2026-09-03-lab092-minimal-safe-redesign-contract.md` — main commit `c215b3ab0ac5bb1c78dcd373077bac8174e3282f`; #176 comment `5528679972`.
- Retained LAB-092 evidence includes carrier-schema/trigger authentication, preseedable marker, explicit-migration/shared-tail, and constructor/restart/post-construction TOCTOU findings.
- Retained LAB-100 evidence includes provider subclass authority, inherited rotate bypass, caller-owned activation state, reconstructed provider position/request-result split, rejected-ticket orphan reservation, and reconstructed fence-counter reuse.
- Retained LAB-086 machine-handoff evidence includes `research/2026-09-03-lab086-container-download-handoff-probe.md` commit `3cc6187748211c8800a6a39d387aa5043f59b96d` and full-blob connector reprobe commit `159ad6ed9edab9ab870e8cb9fc244df53bed43b8`.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch bytes are connector-readable, but the current connector exposes no byte-preserving patch/apply transform: normal Contents `update_file` requires the complete replacement UTF-8 text. Direct filesystem network access again failed DNS in this run.
- Exact checkout/source execution remains unavailable; no fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-090/LAB-100 should be handled through the retained coherent provider-authority redesign contract rather than more unrelated lifecycle conditionals.
- LAB-092 should be handled through its retained domain-separated certificate + authority-schema/trigger + serialization-bound redesign rather than more independent `_classify()` checks.

## Exact next action
LAB-086 first: probe for a supported byte-preserving machine composition/materialization path for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. A normal Contents replacement is not sufficient unless exact candidate bytes already exist outside model text. If a safe machine path appears, conflict-check the predecessor, apply only the retained patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish through Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run the frozen 16-case LAB-090/LAB-100 RED matrix before production changes, then implement one coherent provider-authority boundary. After that run the retained LAB-092 regression matrix before production changes there.

If neither exact composition nor exact source execution becomes available, continue only with concrete distinct trust/capability/fail-closed evidence or consolidation that materially strengthens an existing issue; do not create duplicate narrow findings.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; unified LAB-090/LAB-100 authority redesign contract recorded.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending; consolidated redesign contract recorded.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups; LAB-100 composes into the unified PR #175 authority redesign contract.
