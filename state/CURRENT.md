# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Pinned executable/runtime/test snapshot for the remaining gate: `95fa5da3c457e3431cd596ec969d5939b0a1d925`.
- Current PR #165 branch HEAD: `5a1709fbe11f1a8e162280c393ba66d778c7f3b0`; the only change after the pinned executable snapshot is the non-executable exact-gate manifest `research/2026-08-27-lab086-exact-gate-manifest.md`.
- PR #165 remains draft; full exact LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD `e69ccbc47127319460dbcd3669083cbcba9baa40`, mergeable=true, draft.

## Last completed step

Resumed LAB-086 first from the pinned executable snapshot and enumerated the exact current LAB-086 test blobs through the connector. The newest lower-cardinality regression is `test_pre_cutoff_lower_evidence_cardinality.py` blob `d2ff264ebbce0611805b880949478df4e5cef6a1`. Inspection confirmed that even this focused real-ledger test imports `test_suffix.AsymmetricSuffixIntegrationTests`, so executing it correctly expands into the full LAB-080→086 import closure rather than a small standalone slice.

Re-probed safe bulk reconstruction paths. Tool-backed GitHub archive retrieval was unavailable, and direct raw GitHub transport remained unreachable even with `--noproxy` plus fixed `raw.githubusercontent.com` IPs. No non-exact/manual reconstruction was counted as evidence. Connector exact blob/file reads remain healthy and are still the accepted path defined by the gate manifest.

Because the exact LAB-086 closure remained tool-limited in this run, used the documented fallback on LAB-091 without changing LAB-086 priority. Reconstructed the exact published v4 restart dependencies and verified local Git hashes against GitHub: `operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be`, `state_machine_udfs.py` `8c1d6d0cd075285aed3a90ac337b60b60c1d608b`, and `history_binding_guards.py` `bd1f8fe16d3cdeaaa0f96bca1406e1edb02cfe0f`.

Added `test_v4_restart_persistence.py` to PR #173. The published test blob `e2ce0a277fc196cfe888fd2146242becf34aec7c` exactly matches the locally executed bytes. Exact restart-layer result: **3/3 PASS + compileall PASS**. It proves that v4 trigger definitions survive SQLite close/reopen, deterministic request-id and confirmation/receipt binding remain enforced after reopen, and a reopened connection that omits the required UDF fails closed instead of bypassing the persisted trigger. This is restart-layer evidence only, not the complete real LAB-080/LAB-082 integration gate.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current LAB-086 exact test inventory: 29 normal modules + one unsafe seed from the pinned executable tree; no new full-stack PASS claimed in this run.
- Key LAB-086 blobs remain `migration_guard.py` `1a9209b...`, `strict_fence.py` `5da01e28...`, `suffix.py` `44847bde...`, `final_supported.py` `ceb7f48a...`.
- Exact gate manifest exists durably on PR #165 and records lower implementation blob identities through LAB-085.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained exact evidence: one-shot primitive 6/6; full mutable-row guards + legacy persistence 12/12; v3 cross-table state-machine 8/8; v4 deterministic/history binding 9/9; latest v4 restart-persistence subgate **3/3 PASS + compileall**, exact published test blob `e2ce0a27...`.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact execution on one coherent branch-local LAB-080→086 closure: all 29 normal LAB-086 modules, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Direct shell/raw GitHub transport cannot establish a connection; connector exact blob reads remain healthy but there is no repository archive/export action. Reconstruction is therefore file-by-file unless a later runtime exposes a byte-safe bulk transport.
- Never count manually reformatted/transcribed files as exact evidence; hash mismatch means discard the run.
- LAB-091 final candidate still needs execution against real LAB-080/LAB-082 for the full restart path, two actual concurrent workers sharing one request, crash rollback, timeout/UNKNOWN reconciliation, and LAB-087 restricted-worker composition. The new 3/3 closes only the persisted v4-trigger restart sublayer.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: use `research/2026-08-27-lab086-exact-gate-manifest.md` and connector blob reads to reconstruct the pinned executable snapshot byte-for-byte; verify every file with `git hash-object` before import.
2. Execute all 29 normal LAB-086 real-schema modules, then the unsafe legacy-promotion seed separately, full compileall, and a fresh security audit of migration/cardinality/cross-proof/fence/thaw/restart/concurrency paths.
3. Re-check branch/main divergence only after the test/security gate is clean; then mark #165 ready and reconcile/integrate.
4. If exact LAB-086 reconstruction remains tool-limited in a run, continue LAB-091 real-stack execution. Next fallback target: two actual workers sharing one request and crash rollback on the final operation-scoped candidate, then timeout/UNKNOWN and LAB-087 composition.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact gate manifest durable, full branch-local execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; v4 restart persistence exact 3/3 added, real LAB-080/LAB-082 integration gate remains.
