# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; atomic installation source fix is published at commit `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is a READY follow-up for migration-safe activation-schema installation provenance/post-install deletion detection. Do not fold it speculatively into LAB-090.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, issue #163 and all active PRs. LAB-086 remains first priority. In this run the GitHub connector again returned the complete exact predecessor blob `d4a6a40f...` and retained patch blob `61841b58...`. Direct `git clone` was probed again and failed before repository execution with `Could not resolve host: github.com`. No supported byte-preserving server-side patch-composition/write bridge is exposed, so LAB-086 was not mutated; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.

Advanced LAB-092/#176 using exact inherited APIs. `shared_anchor_intent_ledger.protocol` allows authenticated `migration` intents; `reserve()` binds deterministic request identity and persists PREPARED; `execute()` idempotently resumes the same intent, advances/reconciles the provider, and confirms it with authenticated receipt binding. LAB-090 `_init_activation_schema()` already installs and verifies the activation table+trigger under one `BEGIN IMMEDIATE`.

Corrected the previous LAB-092 ordering: marker-before-DDL cannot distinguish crash-before-install from later post-install deletion because both can yield `CONFIRMED marker + missing objects`. The stronger contract is DDL-first, completion-marker-second. Explicit `migrate_activation_schema_v1()` installs+verifies exact DDL atomically, then confirms one deterministic authenticated `migration` completion intent. Ordinary startup accepts only CONFIRMED completion marker + exact table + exact trigger. Before completion, only exact DDL plus absent/PREPARED marker is explicitly recoverable; partial/mismatched DDL fails closed. After completion, any missing/mismatched activation object is unambiguous tamper and must never be recreated by startup or migration.

Durable correction: `research/2026-08-31-lab092-ddl-before-provenance-marker-ordering.md`, main commit `21bd932173cf81819d5b775dba23fd7d8e8f59b8`; #176 comment `5482601499`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening, trigger-definition verification, activation-table schema verification, and schema-installation writer-race regression are published. Atomic schema installation source fix is published at `d9a381dd...` / blob `8140d6e1...`; exact branch behavioral/full-suite execution remains pending.
- LAB-092 now has corrected DDL-before-completion-provenance ordering, explicit recovery-state classification, and a six-case RED regression matrix; no speculative implementation was made.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, including complete predecessor and patch bytes, but no supported byte-preserving server-side composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable in this run because `github.com` DNS resolution failed; GitHub connector read/write operations are available.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute. Do not upgrade mechanism-level evidence into branch-level GREEN.
- Do not solve LAB-092 with an unauthenticated local marker, marker-before-DDL ordering, or by silently auto-repairing missing activation objects after a confirmed completion marker.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then `test_activation_schema_tamper_restart.py`, `test_activation_trigger_tamper_restart.py`, activation restart/integration and downstream gates. Require GREEN before moving PR #175 out of draft.

If execution remains unavailable, implement the smallest isolated LAB-092 slice: a startup state-classifier + explicit `migrate_activation_schema_v1()` using exact LAB-090 DDL constants and one deterministic post-DDL `migration` completion intent. Add RED regressions first for (1) legitimate legacy DB: ordinary startup migration-required, explicit migration succeeds, subsequent startup succeeds; and (2) completed migration followed by activation-table deletion: both startup and explicit migration fail closed and do not recreate the table. Keep LAB-090 unchanged until the LAB-092 regressions prove the contract.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — READY; corrected authenticated completion-provenance contract defined; implementation/tests pending.
