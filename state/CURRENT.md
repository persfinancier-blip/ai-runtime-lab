# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage; issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; head/base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based exactly on LAB-090 head. Current branch head `3f183bd539ff8547f5d8bd05b4be2d02b35bf995`; production provenance source blob `df99fa6bd9c0d9952008c4671f1f233ed1baaadd`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PR state. LAB-086 remains priority #1.

Fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository execution with `Could not resolve host: github.com`. The connector still exposes file reads and complete-body Contents writes but no observed byte-preserving fetched-bytes/local-file -> Contents replacement bridge. Manual/model reserialization of security-critical LAB-086 `strict_fence.py` remains prohibited, so no LAB-086 mutation was attempted.

Completed the next allowed LAB-092 concrete durable mutation audit and found a deterministic post-construction provenance deletion defect. After legitimate migration and construction, deleting the confirmed LAB-092 migration marker made `_classify()` return `DDL_INSTALLED_UNMARKED`, but inherited `execute()` still called inherited `reserve()` without re-checking provenance and could append/confirm a new durable intent. This requires no concurrency or whole-call linearizability assumption: marker deletion happens before the public mutation call.

Regression-first branch commit `60c71feb21a88ddac1530fd102913305f8de890f` added `test_activation_schema_postconstruction_marker_deletion.py`, exact blob `f2757e7de37f4d1402fb4b1da0e7c33513b4c432`. Fix commit/current PR #177 head `3f183bd539ff8547f5d8bd05b4be2d02b35bf995` adds `_require_complete_activation_schema_provenance()` and overrides `reserve()` so inherited `execute()` fails before reservation unless local provenance remains `COMPLETE`. Production blob is `df99fa6bd9c0d9952008c4671f1f233ed1baaadd`.

Exact behavioral RED/GREEN execution is not claimed because checkout/source execution remains unavailable. Durable evidence: `research/2026-09-01-lab092-postconstruction-marker-deletion-execute-gap.md`, main commit `74cfb98a466ab59e192c5142b05283be47101b86`; #176 comment `5493863932`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility and ordering evidence retained, plus post-construction marker-deletion execute guard. Exact PR #177 regression/full execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; direct source execution/checkout is not available in this run because local GitHub DNS resolution fails.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution is available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Live LAB-092 shared-anchor `reserve()`/`execute()` must now fail closed if post-construction provenance is no longer `COMPLETE`.
- Do not add an exactly-once migration-marker execute or whole-call linearizable runtime-freshness requirement unless a concrete correctness/security contract requires it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`; then execute PR #177 including the new post-construction marker-deletion regression on current head/source. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, audit inherited LAB-090 `rotate_provider()` under post-construction deletion of the confirmed LAB-092 marker. It does not call `reserve()`, so determine whether provider history / activation status can still mutate after provenance becomes `DDL_INSTALLED_UNMARKED`. If reachable, add a regression first and the smallest fail-closed provenance guard; otherwise record a negative audit. Do not generalize to new concurrency contracts without a concrete mutation-before-validation path.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; post-construction marker deletion can no longer pass through `reserve()`/`execute()`; exact regression gate and separate `rotate_provider()` tamper audit pending.
