# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Live LAB-086 `strict_fence.py` blob remains `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` (re-fetched this run).
- Exact unpublished hidden-rowid candidate remains `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues/PRs. LAB-086 predecessor was re-fetched and is still exact blob `d4a6a40f...`; no supported byte-preserving bridge for publishing exact candidate `b78e7c98...` appeared, so the security-critical file was not manually reserialized or pushed through a low-level bypass.

Attempted LAB-091 exact next action: execute published `experiments/mutable_shared_anchor_writer/tests/test_real_stack_timeout_unknown_convergence.py` blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e` at branch HEAD `5a72cbc3c1dda94d7ef3da19b776ab3afebc7c20`. Connector reads can retrieve exact source, but executable shell DNS probes to both `api.github.com` and `raw.githubusercontent.com` fail with temporary name-resolution errors and the connector does not mount a checkout into the executable FS. Therefore the full unittest was not executed and must not be counted as behavioral PASS.

Performed an executable focused semantic probe of the current LAB-036 timeout ordering from `anchor_attestation/protocol.py` blob `15d8b7cf8ff093490ccb75679030d3a0fe41e401`: provider effect commits once, first reconciliation is unavailable, retry observes the already reached target without re-increment, later reconciliation recovers the stored request result. Observed PASS with provider position=1 and increment_calls=1 throughout retry. Static audit found no contradiction between this mechanism and the published real-stack regression. Durable note: `research/2026-08-29-lab091-timeout-unknown-provider-mechanism-probe.md`, main commit `08d50ac869122c048ff9fd577ba9cbb903cc5f23`; Issue #170 comment `5460544240`; PR #173 comment `5460544623`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-086 hidden-rowid RED->GREEN evidence retained; exact predecessor `d4a6a40f...` -> candidate `b78e7c98...` was byte-rederived and focused mechanism-tested.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption hardening combined focused gate remains 17/17 PASS over identity/index/collation + NOT NULL + weakened-watermark-CHECK logic.
- LAB-091 published real-stack timeout/UNKNOWN regression remains blob `92133cdc...`; full execution still pending. Focused provider timeout mechanism PASS is retained separately and is not a substitute for the full gate.

## Known blockers / constraints

- LAB-086 remains first priority. Current live security delta is rowid-only hardening; do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- LAB-086 publication remains blocked by byte-preserving data-plane separation for the exact ~40 KB candidate. Do not use low-level blob/tree/ref manipulation, force updates, or manual lossy rewrites.
- PR #165 remains draft until exact candidate publication/hash verification, four focused regressions, complete strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft. The real-stack timeout/UNKNOWN test exists but has not yet been behaviorally executed. Existing process concurrency/crash tests still use stubs and do not prove the final supported class against exact real LAB-080/LAB-082 dependencies.
- Do not repeat the narrow LAB-091 combined adoption gate unless one of its pinned source blobs changes.
- CHECK/type-affinity equivalence is not globally claimed. Only demonstrated behavior gaps should add constraints/guards.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: re-check `strict_fence.py` remains `d4a6a40f...`. If a byte-preserving bridge to the normal Contents writer becomes available, publish only exact candidate `b78e7c98...`, require returned/re-fetched blob equality, then run four focused regressions + strict/thaw subgate + compileall + LAB-080->086 real-ledger gate.
2. If LAB-086 publication remains tool-limited, LAB-091: obtain a supported branch-to-executable-FS path and execute exact published timeout/UNKNOWN test blob `92133cdc...` against its real dependency closure. If it fails, fix the real-stack defect; do not weaken the test.
3. After timeout/UNKNOWN real-stack PASS, add and execute the analogous final-class two-worker confirmation/crash regression using real LAB-080/LAB-082 dependencies.
4. Retain/reconfirm LAB-087 restricted-worker composition and audit alternate write surfaces/reentrancy before PR #173 can leave draft.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact rowid candidate re-derived + focused mechanism PASS, publication/full gate pending.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; combined adoption gate 17/17 PASS; real-stack timeout/UNKNOWN regression published but execution pending; focused external timeout mechanism PASS; real-stack two-worker/crash gate pending.
