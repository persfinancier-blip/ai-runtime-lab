# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 is the allowed fallback; draft PR #175; branch `lab-090-provider-activation-fencing`; latest branch commit observed/written this run `98a1059e32d3927b661e873077acc070e2d22af7` (retained candidate patch only; source fix not yet applied).
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues/PR state, PR #175 and the current LAB-090 activation coordinator implementation.

LAB-086 remains first priority. GitHub connector still exposes exact blob reads and complete UTF-8 Contents replacement but no supported byte-preserving server-side patch composition/write bridge for exact predecessor `d4a6a40f...` + retained patch `61841b58...` -> required target `b78e7c98...`. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`; LAB-086 was not mutated.

Direct git clone was attempted again and failed before repository execution with `Could not resolve host: github.com`. Exact published-head behavioral/full-suite GREEN is therefore still not claimed.

Continued LAB-090 schema-installation race work. Current `_init_activation_schema()` installs/verifies the activation table and blocking trigger in two separate `executescript()` transaction boundaries, leaving a restart writer window if the trigger is absent while unresolved activation evidence exists.

Independently executed a file-backed SQLite two-connection mechanism test for the proposed fix: one `BEGIN IMMEDIATE` held across table create/verify and trigger create/verify forced the concurrent writer to wait; after commit the writer failed with `provider activation unresolved`, and persisted shared-anchor intent count remained 0. Result: atomic install mechanism PASS.

Retained the exact minimal candidate diff on the LAB-090 branch at `research/patches/lab090-activation-schema-installation-transaction.patch`, commit `98a1059e32d3927b661e873077acc070e2d22af7`. This is evidence/design only; `supported.py` is not claimed fixed. Durable main note: `research/2026-08-31-lab090-activation-schema-installation-transaction-fix-design.md`, commit `57dc398b5228b8d0b32dcb76014126ee95cd6456`; issue #169 comment `5479760031`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall. Subsequent integration/restart/stale-runtime/verify-component/ticket-binding/numeric-type hardening is published. Trigger-definition and activation-table schema fail-closed verification are published. Schema-installation writer-race regression is published. Atomic transaction mechanism for the intended fix is independently validated; exact branch source application + broader execution remain pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact blob fetch is available, but no supported byte-preserving server-side patch composition/write bridge is currently exposed.
- Direct Git/raw repository execution transport remains unavailable; GitHub connector read/write operations are available.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute. Do not claim the retained `.patch` file is an applied source fix.

## Exact next action

LAB-086 first: probe again for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable, apply the already-retained LAB-090 minimal source fix to exact current PR #175 `supported.py` only through a safe high-level operation that preserves all other file bytes: replace the two `executescript()` boundaries in `_init_activation_schema()` with one explicit `BEGIN IMMEDIATE` and single-statement `execute()` calls, retaining exact table/trigger verification and rollback behavior. Re-fetch and diff-audit the result.

When exact source execution becomes available, run `test_activation_schema_installation_race.py` first, then `test_activation_schema_tamper_restart.py`, `test_activation_trigger_tamper_restart.py`, activation restart/integration and downstream gates. Require GREEN before moving PR #175 out of draft.

If neither safe source application nor execution is available, continue only narrow byte-verifiable LAB-090 provider/coordinator/restart audits; do not expand protocol scope speculatively.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation candidate diff retained and mechanism validated; exact source application + behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
