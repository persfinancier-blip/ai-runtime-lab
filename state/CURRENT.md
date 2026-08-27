# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current reconstruction target for PR #165 remains HEAD `95fa5da3c457e3431cd596ec969d5939b0a1d925`; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD `1ba75bc93877f9202b8c1e551edc5f0749bdf076`; mergeable=true; draft.

## Last completed step

Resumed LAB-086 first. Exact PR-HEAD reconstruction is now anchored to Git tree `f8aac99765a4dfbd0aaffd12c01999f3fbbbe8ad`. The LAB-086 tests subtree `80372a45448f95673ca351b5d5dd065bc10893d6` was enumerated exactly: **29 normal test modules plus one unsafe legacy-promotion seed**, each with a branch-local blob SHA. This removes ambiguity about the current-head execution manifest. Direct transport was re-probed using the current DNS A record for github.com (`140.82.121.4`); explicit `--resolve` still cannot establish TCP/443, so connector blob reconstruction remains the safe execution path. No new LAB-086 PASS was claimed.

Because the remaining LAB-086 bulk reconstruction is still file-by-file, continued the approved LAB-091 fallback and found a real state-machine gap. The v3 intent guard required only that `predecessor_position` equal the current tail; an exact one-shot permit could therefore create PREPARED `predecessor=0, position=999`, after which the meta guard accepted `reserved_position 0 -> 999`. A focused SQLite counterexample reproduced the durable jump.

Fixed both boundaries independently on PR #173: intent insert now requires `position = predecessor + 1`, and meta update requires `new reserved_position = old + 1` in addition to the matching PREPARED row. Published commits: code `01c8fd697171fb2a2b330991cc159e0432a51ab7`, regression follow-up `5bf96d36d4b2ee40ba516ee7d7804cb5b614218d`, research note `1ba75bc93877f9202b8c1e551edc5f0749bdf076`.

Exact published-source execution byte-matched four files: permit `637784a5...`, row tokens `801eb0fb...`, patched v3 guard `aff3ef5f...`, regression `d1ad01e6...`. The exact v3 regression suite passed **8/8** and compileall passed. The unrelated artifact-tool spreadsheet warmup warning did not affect unittest/compileall return codes.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Current-head LAB-086 exact test manifest: 29 normal modules + 1 unsafe seed from the single PR-HEAD commit tree; no new full-stack PASS claimed yet.
- Current key LAB-086 blobs remain `migration_guard.py` `1a9209b...`, `strict_fence.py` `5da01e28...`, `suffix.py` `44847bde...`, `final_supported.py` `ceb7f48a...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 one-shot primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards + legacy persistence exact 12/12 PASS.
- LAB-091 v3 cross-table state-machine regression after contiguous-reservation fix exact **8/8 PASS + compileall**.
- LAB-091 v4 deterministic request-id/history-binding published-source regression exact 9/9 PASS + compileall.
- LAB-091 unsafe unrestricted raw-DML baseline failed as intended.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact current-head execution on one branch-local LAB-080→086 closure: all 29 normal LAB-086 modules, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Direct shell/raw GitHub transport cannot establish a connection even with current DNS/IP resolution. Connector exact blob reads remain healthy; no repository archive/export action is available.
- LAB-091 final candidate is `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`; it still needs execution against real LAB-080/LAB-082 across restart, actual concurrent workers, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
- LAB-091 triggers/UDFs are not a same-privilege SQL sandbox; LAB-087 remains the external single-writable-handle/process/filesystem boundary.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: continue branch-local byte-exact reconstruction from PR HEAD `95fa5da...` using exact blob SHAs, then execute all 29 current normal LAB-086 modules against the one LAB-080→086 source closure.
2. Execute unsafe legacy-promotion seed separately, full compileall, then a fresh security audit of migration/cardinality/cross-proof/fence/thaw/restart/concurrency paths. Only then mark #165 ready and reconcile/integrate.
3. If exact LAB-086 reconstruction remains tool-limited, continue LAB-091 real-stack execution with the newly fixed contiguous reservation invariant: restart, two actual workers sharing one request, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 composition.
4. Keep PR #165 and PR #173 draft until their complete real-stack gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact test manifest resolved, full current-head branch-local execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; contiguous reservation gap fixed with exact 8/8 + compileall; full real LAB-080/LAB-082 integration gate remains.
