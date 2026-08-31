# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; current branch head observed `98a1059e32d3927b661e873077acc070e2d22af7` (retained atomic-install candidate patch only; source fix not yet applied).
- LAB-092 / #176 is a READY follow-up for migration-safe activation-schema installation provenance/post-install deletion detection; do not fold it speculatively into LAB-090.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues/PR state, PR #175, the current LAB-090 activation coordinator implementation, the schema-installation race regression, and the retained atomic-install patch.

LAB-086 remains first priority. GitHub connector still exposes exact blob reads and complete UTF-8 Contents replacement but no supported byte-preserving server-side patch composition/write bridge for exact predecessor `d4a6a40f...` + retained patch `61841b58...` -> required target `b78e7c98...`. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`; LAB-086 was not mutated.

Direct `git ls-remote` was attempted again and failed before repository execution with `Could not resolve host: github.com`. Exact published-head behavioral/full-suite GREEN is therefore still not claimed.

LAB-090 atomic-install design remains valid: current `_init_activation_schema()` still uses two `executescript()` transaction boundaries, while the retained minimal patch changes this to one `BEGIN IMMEDIATE` transaction with single-statement `execute()` calls across table create/verify and trigger create/verify. Prior file-backed two-connection mechanism evidence remains PASS. The source fix itself is still not applied because no current high-level operation can patch only the exact method while demonstrably preserving every other byte of the file.

Fresh restart/schema durability audit found a separate provenance gap: exact-definition verification rejects same-name VIEW/trigger substitution, but complete absence of both activation objects is indistinguishable from legitimate first LAB-090 migration. `IF NOT EXISTS` must recreate objects for legacy migration, so post-install deletion cannot be detected without durable evidence that LAB-090 was installed previously. Do not add an ad-hoc marker inside PR #175. Opened #176 / LAB-092 with explicit migration-safe acceptance criteria. Durable note: `research/2026-08-31-lab090-schema-installation-provenance-gap.md`, main commit `28181cac474d637204259e02ae33a9c4883122cf`; #169 comment `5480560228`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published. Trigger-definition and activation-table schema fail-closed verification are published. Schema-installation writer-race regression is published. Atomic transaction mechanism for the intended fix is independently validated; exact branch source application + broader execution remain pending.
- LAB-092 provenance/deletion-detection gap is documented and tracked separately; no speculative implementation was made.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute. Do not claim the retained `.patch` file is an applied source fix.
- Do not solve LAB-092 by simply requiring the activation table to pre-exist: that would break legitimate pre-LAB-090 migration. Installation provenance needs an explicit durable/migration contract.

## Exact next action

LAB-086 first: probe again for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, apply the already-retained LAB-090 minimal source fix to exact current PR #175 `supported.py` only through a safe high-level operation that demonstrably preserves all other file bytes: replace the two `executescript()` boundaries in `_init_activation_schema()` with one explicit `BEGIN IMMEDIATE` and single-statement `execute()` calls, retaining exact table/trigger verification and rollback behavior. Re-fetch and diff-audit the result.

When exact source execution becomes available, run `test_activation_schema_installation_race.py` first, then `test_activation_schema_tamper_restart.py`, `test_activation_trigger_tamper_restart.py`, activation restart/integration and downstream gates. Require GREEN before moving PR #175 out of draft.

If neither safe source application nor execution is available, continue only narrow byte-verifiable LAB-090 provider/coordinator/restart audits. LAB-092 may be researched for a migration-safe provenance contract, but do not expand LAB-090 protocol scope speculatively.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation candidate diff retained and mechanism validated; exact source application + behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — READY; define activation-schema installation provenance and post-install deletion detection without breaking legacy migration.
