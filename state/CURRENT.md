# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; atomic installation source fix is published at commit `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is a READY follow-up for migration-safe activation-schema installation provenance/post-install deletion detection. Provenance contract research is now recorded; do not fold it speculatively into LAB-090.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, issue #163 and active PRs #165/#175. LAB-086 remains first priority. In this run the GitHub connector successfully returned the complete exact predecessor blob `d4a6a40f...` and retained patch blob `61841b58...`, but still exposes no supported server-side patch-composition/write operation. Direct `git clone` was probed again and failed before repository execution with `Could not resolve host: github.com`. Because Contents replacement still requires supplying a complete replacement payload, LAB-086 was not mutated; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.

Used the allowed research fallback on LAB-092/#176. Inspected inherited LAB-080/LAB-081 shared-anchor/provider-history semantics and rejected a new singleton marker table, `PRAGMA user_version`/`application_id`, a `shared_anchor_meta` marker column, and generation-count inference as sole provenance authorities. They either live at the same mutable local DDL layer as the objects being protected or cannot distinguish legitimate pre-LAB-090 history.

Defined a stronger migration-safe contract: reuse one canonical deterministic `migration` intent in the existing authenticated shared-anchor history as installation provenance. Ordinary startup classifies confirmed-marker + missing/mismatched activation objects as fail-closed; marker absent + both objects absent is the only legacy candidate. First installation is explicitly two-phase across external/provider and SQLite domains: confirm the authenticated migration intent, then under `BEGIN IMMEDIATE` re-read/verify it and create+verify table/trigger atomically. Crash after marker confirmation but before DDL is a distinct migration-recovery state, not silent runtime repair.

Durable note: `research/2026-08-31-lab092-activation-schema-provenance-contract.md`, main commit `7f6b10e0fcbb42c1a72e301418ac37db963fe214`; #176 comment `5481896195`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening, trigger-definition verification, activation-table schema verification, and schema-installation writer-race regression are published. Atomic schema installation source fix is published at `d9a381dd...` / blob `8140d6e1...`; exact branch behavioral/full-suite execution remains pending.
- LAB-092 provenance/deletion-detection gap now has a concrete authenticated-migration-intent contract and required regression matrix; no speculative implementation was made.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, including complete predecessor and patch bytes, but no supported byte-preserving server-side composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable in this run because `github.com` DNS resolution failed; GitHub connector read/write operations are available.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute. Do not upgrade mechanism-level evidence into branch-level GREEN.
- Do not solve LAB-092 with an unauthenticated local marker or by simply requiring the activation table to pre-exist; both would violate the migration/deletion-detection contract.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then `test_activation_schema_tamper_restart.py`, `test_activation_trigger_tamper_restart.py`, activation restart/integration and downstream gates. Require GREEN before moving PR #175 out of draft.

If execution remains unavailable, advance LAB-092 contract without changing LAB-090: inspect the exact inherited migration/receipt APIs, define the smallest dedicated `migrate_activation_schema_v1(...)` API and RED regression payloads for (1) legitimate legacy first migration and (2) confirmed provenance marker + deleted activation table. Keep ordinary runtime startup fail-closed and keep migration recovery explicit.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — READY; authenticated migration-intent provenance contract defined; implementation/tests pending.