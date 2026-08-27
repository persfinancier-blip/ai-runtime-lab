# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Pinned executable/runtime/test snapshot for the remaining gate: `95fa5da3c457e3431cd596ec969d5939b0a1d925`.
- Current PR #165 branch HEAD: `5a1709fbe11f1a8e162280c393ba66d778c7f3b0`; the only change after the pinned executable snapshot is the non-executable exact-gate manifest `research/2026-08-27-lab086-exact-gate-manifest.md`.
- PR #165 remains draft and GitHub currently reports mergeable=true; full exact LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; its real-stack gate remains separate fallback work.

## Last completed step

Resumed LAB-086 first and converted the remaining reconstruction problem into a durable, branch-local gate manifest. Commit `5a1709fbe11f1a8e162280c393ba66d778c7f3b0` adds `research/2026-08-27-lab086-exact-gate-manifest.md`, pinning the exact LAB-080→086 implementation closure, key Git blob SHAs, LAB-086 test inventory and the rule that a reconstructed file counts only when local `git hash-object` matches the pinned blob.

Re-probed bulk transport. Direct shell/raw GitHub transport remains unavailable; an explicit HTTPS/API IP fallback also could not establish TCP/443. Manual source transcription was tested only as a diagnostic and immediately rejected after `git hash-object` mismatches. No non-exact workspace or test result was counted.

Performed a fresh cross-connection audit of the current exact `migration_guard.py` (`1a9209b...`). `verify_locked(q)` calls public-custody durable verification on a separate connection, but the outer LAB-086 path already holds `BEGIN IMMEDIATE` and the lower public-custody verifier uses ordinary `BEGIN`, not a second write transaction. Concurrent writers therefore remain excluded across the composed verification interval. No new mixed-writer snapshot or privilege-escalation blocker was established in this pass.

Updated PR #165 description and Issue #163 with the exact reconstruction discipline and current evidence. Fresh compare of current branch HEAD against current `main`: `ahead 155 / behind 112`, status diverged; all PR paths remain additions in the compare. Mergeability is not the acceptance gate.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current LAB-086 exact test inventory: 29 normal modules + one unsafe seed from the pinned executable tree; no new full-stack PASS claimed in this run.
- Key LAB-086 blobs remain `migration_guard.py` `1a9209b...`, `strict_fence.py` `5da01e28...`, `suffix.py` `44847bde...`, `final_supported.py` `ceb7f48a...`.
- Exact gate manifest now exists durably on PR #165 and records lower implementation blob identities through LAB-085.
- Fresh cross-connection audit: no second-write-lock/mixed-writer snapshot defect established.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 previously retained exact evidence remains valid, including one-shot primitive, v3/v4 guards and contiguous reservation fixes recorded in #170/PR #173.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact execution on one coherent branch-local LAB-080→086 closure: all 29 normal LAB-086 modules, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Direct shell/raw GitHub transport cannot establish a connection; connector exact blob reads remain healthy but there is no repository archive/export action. Reconstruction is therefore file-by-file unless a later runtime exposes a byte-safe bulk transport.
- Never count manually reformatted/transcribed files as exact evidence; hash mismatch means discard the run.
- LAB-091 final candidate still needs real LAB-080/LAB-082 restart/concurrency/crash/UNKNOWN/LAB-087 composition tests.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: use `research/2026-08-27-lab086-exact-gate-manifest.md` and connector blob reads to reconstruct the pinned executable snapshot byte-for-byte; verify every file with `git hash-object` before import.
2. Execute all 29 normal LAB-086 real-schema modules, then the unsafe legacy-promotion seed separately, full compileall, and a fresh security audit of migration/cardinality/cross-proof/fence/thaw/restart/concurrency paths.
3. Re-check branch/main divergence only after the test/security gate is clean; then mark #165 ready and reconcile/integrate.
4. If exact LAB-086 reconstruction remains tool-limited in a run, continue LAB-091 real-stack execution rather than weakening the LAB-086 evidence standard.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact gate manifest durable, full branch-local execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; real LAB-080/LAB-082 integration gate remains.
