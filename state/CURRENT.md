# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Pinned executable/runtime/test snapshot for the remaining LAB-086 gate: `95fa5da3c457e3431cd596ec969d5939b0a1d925`.
- Current PR #165 branch HEAD: `5a1709fbe11f1a8e162280c393ba66d778c7f3b0`; post-snapshot change is the non-executable exact-gate manifest. PR remains draft; full exact LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD `7237951293a749697ae8b5c36854721781ff4cdb`; mergeable=true; draft.

## Last completed step

Resumed LAB-086 first. Re-read the pinned exact-gate manifest, fetched the exact recursive PR-snapshot tree and the complete LAB-086 test tree `80372a45448f95673ca351b5d5dd065bc10893d6`. The inventory contains 29 normal `test_*.py` modules plus the unsafe legacy-promotion seed. Exact connector blob reads are healthy; no repository archive/mount action is exposed and direct shell/raw GitHub transport remains unavailable, so no partial/manual reconstruction was counted as the full gate.

Used the documented fallback on LAB-091 and strengthened concurrency/crash evidence. Reconstructed and hash-verified exact published `operation_permit.py` (`637784a5cb61a024a1df3e0e983887b6d0a838be`) and `convergent_operation_scoped.py` (`84a84df633fbaaca7f424f4db5bd3fd20403263b`). Added `tests/test_process_concurrency_and_crash.py`, published blob `776ab61e70b062233939a9b0e53045042989a063`, commit `7237951293a749697ae8b5c36854721781ff4cdb`; published bytes match the locally executed test bytes.

The new file-backed Linux process regression executed **2/2 PASS**. Case 1 launches two independent OS processes simultaneously against the same PREPARED row; both converge on the same durable CONFIRMED winner and receipt binding. Case 2 gives a worker a correct one-shot permit, performs PREPARED→CONFIRMED inside `BEGIN IMMEDIATE`, then calls `os._exit(17)` before COMMIT; after process death SQLite recovery leaves the durable row PREPARED with NULL receipt binding. This is focused parent-stub evidence and does not replace the real LAB-080/LAB-082 supported-surface gate.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current LAB-086 exact test inventory: 29 normal modules + one unsafe seed from pinned executable tree; no new full-stack PASS claimed in this run.
- Key LAB-086 blobs remain `migration_guard.py` `1a9209b...`, `strict_fence.py` `5da01e28...`, `suffix.py` `44847bde...`, `final_supported.py` `ceb7f48a...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained exact evidence: one-shot primitive 6/6; full mutable-row guards + legacy persistence 12/12; v3 state-machine 8/8; v4 deterministic/history binding 9/9; v4 restart persistence 3/3; single-pending invariant 2/2; latest process concurrency/crash regression **2/2 PASS** on exact published test/source blobs.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact execution on one coherent branch-local LAB-080→086 closure: all 29 normal LAB-086 modules, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Connector can return exact tree/blob contents but does not expose repository archive/mount; direct shell/raw GitHub transport cannot connect. Reconstruction therefore remains file-by-file unless a later runtime exposes byte-safe bulk transport.
- Never count manually reformatted/transcribed files as exact evidence; hash mismatch means discard the run.
- LAB-091 final candidate still needs execution against real LAB-080/LAB-082 for two actual concurrent workers sharing one request end-to-end, provider timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition. Process-level confirmation convergence and crash rollback are now focused-proven.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: continue byte-exact reconstruction from pinned snapshot `95fa5da3...` using `research/2026-08-27-lab086-exact-gate-manifest.md`, exact tree/blob SHAs and `git hash-object` verification before import.
2. Execute all 29 normal LAB-086 real-schema modules, then unsafe legacy-promotion seed separately, full compileall and fresh security audit; only then reconcile/merge PR #165.
3. If exact LAB-086 reconstruction remains tool-limited, continue LAB-091 real-stack execution on `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`: first two actual supported workers on one request and crash rollback, then timeout/UNKNOWN and LAB-087 restricted-worker composition.
4. Keep PR #165 and PR #173 draft until complete real-stack gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact gate manifest/tree inventory durable, full branch-local execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; process-level convergence/crash 2/2 exact-published focused evidence added; real LAB-080/LAB-082 integration gate remains.
