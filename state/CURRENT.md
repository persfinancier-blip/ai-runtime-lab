# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage; issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; head/base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head. Current branch head `ba71515f99060216d7c4698d5566bbc7be207e54`; production provenance source blob `62a35b0fbbbb1c26d155df65d71e2009e01235aa`; post-construction tamper regression blob `4f1409672786ba23e1c258075f03f3c98dbcba9d`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PR state. LAB-086 remains priority #1.

Fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository execution with `Could not resolve host: github.com`. The connector still exposes reads and complete-body Contents writes but no observed byte-preserving fetched-bytes/local-file -> Contents bridge. Manual/model reserialization of security-critical LAB-086 `strict_fence.py` remains prohibited, so no LAB-086 mutation was attempted.

Completed a concrete LAB-092 post-construction provenance-deletion audit. Three deterministic durable mutation paths remained reachable after a legitimate migration object was constructed and the confirmed migration marker was then deleted, making local provenance `DDL_INSTALLED_UNMARKED`:

1. inherited `execute()` -> inherited `reserve()` could append/confirm a new durable shared-anchor intent;
2. inherited LAB-090 `rotate_provider()` could prepare/commit activation and mutate durable provider generation history without calling `reserve()`;
3. inherited `verify_component()` could advance an already-past-marker component watermark over a later confirmed suffix without revisiting the missing marker row.

All three require no concurrency assumption; tamper occurs before each public mutation call.

Regression-first commits: `60c71feb21a88ddac1530fd102913305f8de890f` (execute), `78f36768ac8d6b3489d4eb7cf3795f31bd7647ea` (rotation), `dd17e19c227e29b3262b031d0a1676a7a305fa8f` (watermark). Current regression blob `4f1409672786ba23e1c258075f03f3c98dbcba9d`.

Fix commits culminate at current PR #177 head `ba71515f99060216d7c4698d5566bbc7be207e54`, production blob `62a35b0fbbbb1c26d155df65d71e2009e01235aa`. `ProvenancedHistoricalSharedAnchorLedger` now requires `_classify(self.path) == "COMPLETE"` before `reserve()`, `rotate_provider()`, and `verify_component()`. Inherited `execute()` is covered through dynamic dispatch to the guarded `reserve()`. Explicit migration confirmation and constructor marker authentication still use the non-initializing inherited confirmation surface and are not blocked by these subclass guards.

Exact behavioral RED/GREEN execution is not claimed because checkout/source execution remains unavailable. Durable evidence: `research/2026-09-01-lab092-postconstruction-marker-deletion-execute-gap.md`, latest main commit `0c876959f57e4820b7833b6e7f1d94e9062e5008`; #176 comments `5493863932`, `5493891407`, `5493915859`.

Latest PR #177 metadata read after these changes reported `mergeable=false`; no integration action was attempted. This must be re-checked/reconciled before any future integration because earlier reads had reported mergeable=true.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility/order evidence retained; post-construction marker deletion is now guarded on shared-anchor reservation/execute, provider rotation, and component watermark mutation. Exact PR #177 regression/full execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; direct source execution/checkout is not available in this run because local GitHub DNS resolution fails.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Live LAB-092 `reserve()`/`execute()`, `rotate_provider()`, and mutation-capable `verify_component()` must fail closed if post-construction provenance is no longer `COMPLETE`.
- Do not add an exactly-once migration-marker execute or whole-call linearizable runtime-freshness requirement unless a concrete correctness/security contract requires it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`; then execute PR #177 including all three post-construction marker-deletion regressions on exact head `ba71515f...`. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, first re-check why PR #177 now reports `mergeable=false` against exact LAB-090 base without mutating either branch. Then enumerate remaining reachable LAB-092 public methods and audit only those that can demonstrably write provider receipts, activation status, migration marker state, provider history, watermarks, or another durable authority surface after provenance becomes incomplete. Add regressions only for concrete mutation-before-validation paths; otherwise record negative audits.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; three post-construction marker-deletion mutation surfaces guarded; exact regression/full gate and PR #177 mergeability/base reconciliation pending.
