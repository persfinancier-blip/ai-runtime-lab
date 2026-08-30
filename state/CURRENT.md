# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains the current allowed fallback while LAB-086 byte-preserving publication/execution is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head `6c68ba69914d588efd6fe9c8f4529418b69e444c`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remained first priority. No supported byte-preserving connector-to-local or connector-side predecessor+patch composition path was available. Direct `git ls-remote` was probed again and failed before repository-code execution with `Could not resolve host: github.com`; no LAB-086 branch mutation was attempted.

Resumed the permitted LAB-090 narrow source audit on exact PR-head source. Found that `_verify_activation_records()` used an `INNER JOIN` from `provider_generation_activations` to `provider_generations`. Because `new_generation_id` has no FK, an orphan activation row could be omitted from durable verification; an orphan `SQL_COMMITTED` row would still be seen by the persisted writer-block trigger, allowing restart to succeed into permanent global writer blockage.

Published focused regression `test_activation_orphan_restart.py` in commit `35c530b7c8c316a8bd4e7d5331b9950e0c7d7db8`. Published minimal fail-closed fix in commit `6c68ba69914d588efd6fe9c8f4529418b69e444c`: activation verification now uses `LEFT JOIN` and raises `HistoricalVerificationError` when generation history is missing. GitHub commit diff shows only the intended join/check plus an EOF-newline presentation difference.

Executed a standalone SQLite mechanism check: the old INNER JOIN returned no row for the orphan, while LEFT JOIN returned it with NULL generation-key data. This is mechanism evidence only; exact PR-head unittest/compileall execution remains blocked by direct git DNS failure.

Issue #169 updated in comment `5471897376`. Durable evidence: `research/2026-08-31-lab090-orphan-activation-restart-verification.md`, main commit `12c7d2ce48c33d160f4ff0579ccb33bff70c105f`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 provider primitive, premature-release, overlapping-rotation, historical-retry, historical-unresolved restart, and orphan-activation restart hardening are published. Latest orphan verifier fix has an audited minimal GitHub diff but has not been executed from exact PR-head bytes.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained patch `61841b58...` through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/raw network transport remains unavailable due DNS in this run; treat this as a per-run observation. GitHub connector can read exact blob content and perform Contents writes, but no safe exact patch-composition bridge was observed.
- PR #175 remains draft. Exact-head focused/integration/downstream execution remains pending; do not convert mechanism checks into whole-branch PASS claims.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge; if one exists, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require target blob `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate. Otherwise resume LAB-090 PR #175: execute `test_activation_orphan_restart.py`, `test_activation_historical_unresolved_restart.py`, historical-retry, overlapping-rotation, activation primitive/integration/premature-release, provider-generation integration, and downstream shared-anchor/provider-history suites from exact published bytes. If exact execution is still blocked, perform only a narrow source audit for another concrete restart/concurrency defect; do not expand the protocol speculatively.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; orphan activation restart fail-closed verifier fix published on draft PR #175; exact executable gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
