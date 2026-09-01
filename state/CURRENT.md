# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage; issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; head/base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head. Current branch head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; production provenance source blob `396b67a46686f6df23584b1b366824c1b7ac1886`; post-construction tamper regression blob `8f177a88cc861d4790b859b739c80070e2c6c232`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues, and active PRs. LAB-086 remains priority #1.

Fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository execution with `Could not resolve host: github.com`. The connector still exposes normal reads and complete-body Contents writes but no observed byte-preserving fetched-bytes/local-file -> Contents replacement bridge. Manual/model reserialization of security-critical LAB-086 `strict_fence.py` remains prohibited, so no LAB-086 mutation was attempted.

Re-checked PR #177 mergeability before mutation. Fresh GitHub metadata reported `mergeable=true`, exact base `d9a381dd4607a928cd1315adef6431e239995bc1`, disproving the previous isolated `mergeable=false` observation as durable conflict evidence.

Continued the LAB-092 post-construction public-surface audit and found a fourth deterministic durable mutation path after confirmed migration provenance is deleted: `ledger.provider_history.store_receipt()`. `CoordinatorOnlyProviderHistory` blocks provider-generation `rotate()` but inherits `DurableProviderHistory.store_receipt()`, which verifies a cryptographically valid receipt and inserts it into `historical_provider_receipts` without requiring the request id to correspond to a shared-anchor ledger row. Therefore a live LAB-092 object whose migration marker was deleted could still mutate durable historical receipt state through the publicly exposed provider-history handle.

Regression-first commit `1f4175da0122633d66772202bda703bb6b0d9c65` adds `test_direct_provider_receipt_store_fails_closed_after_marker_deletion`; current regression blob `8f177a88cc861d4790b859b739c80070e2c6c232`.

Fix commit/current PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, production blob `396b67a46686f6df23584b1b366824c1b7ac1886`. Fully constructed LAB-092 objects now replace their public provider-history handle with `_ProvenanceBoundCoordinatorOnlyProviderHistory`, whose `store_receipt()` requires `_classify(path) == "COMPLETE"` before delegating to inherited receipt verification/insertion. The internal `_reservation_surface()` remains intentionally unbound because explicit migration/constructor confirmation may need to persist the migration marker receipt while marker status is PREPARED; that internal path is already preceded by full provider-history/runtime and activation-record integrity verification.

Public provider-history audit after the fix: `rotate()` is coordinator-blocked; `store_receipt()` is now provenance-bound on live LAB-092 objects; `current()`, `verify_durable()`, `require_current()`, `load_receipt()`, `verify_receipt()`, and `make_transition()` are non-mutating/proof-construction surfaces. Private underscore helpers are not promoted into the supported public contract.

Exact behavioral RED/GREEN execution is not claimed because checkout/source execution remains unavailable. Durable evidence: `research/2026-09-01-lab092-public-provider-history-receipt-provenance-gap.md`, latest main evidence commit `f649abae97ef24874541418e77aa1ef3b4406974`; #176 comment `5494621652`.

Fresh PR #177 metadata after the fix still reports `mergeable=true`; PR remains draft and no integration action was attempted.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility/order evidence retained; post-construction marker deletion is now guarded on shared-anchor reservation/execute, provider rotation, component watermark mutation, and public provider-history receipt insertion. Exact PR #177 regression/full execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; direct source execution/checkout is not available in this run because local GitHub DNS resolution fails.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Live LAB-092 `reserve()`/`execute()`, `rotate_provider()`, mutation-capable `verify_component()`, and public `provider_history.store_receipt()` must fail closed if post-construction provenance is no longer `COMPLETE`.
- Do not add an exactly-once migration-marker execute or whole-call linearizable runtime-freshness requirement unless a concrete correctness/security contract requires it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`; then execute PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, continue LAB-092 only by enumerating remaining externally reachable mutable handles/surfaces that can demonstrably write provider receipts, activation status, migration marker state, provider history, watermarks, or another durable authority surface after provenance becomes incomplete. In particular audit whether any public object reachable from `attested`, `provider_history`, or returned activation/provider objects can mutate LAB-owned durable state without passing through the four current provenance guards. Add regressions only for concrete mutation-before-validation paths; otherwise record negative audits.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; four post-construction provenance-deletion mutation surfaces guarded; exact regression/full gate pending; current PR metadata mergeable=true.
