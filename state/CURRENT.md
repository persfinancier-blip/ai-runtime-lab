# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; GitHub currently reports mergeable=true; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD `56e0a64af7055ca89d8bd6bd662afdf5cc8ca95c`; mergeable=true; draft.

## Last completed step

Resumed LAB-086 first. Re-read AGENTS.md, CURRENT and SELF_RESUME, rechecked PR #165 and Issue #163, then re-audited current branch `migration_guard.py` (`1a9209b...`), `strict_fence.py` (`5da01e28...`), `suffix.py` (`44847bde...`) and `final_supported.py` (`ceb7f48a...`).

No new privilege-escalation/stale-supported-writer blocker was established. The current source still has the intended chain: pre-cutoff reverse-cardinality for lower root/provider/threshold evidence plus LAB-086-only proof tables; post-cutoff pre-verification; exact authorization; least-privilege transaction-scoped thaw; mutation; fence reinstall/assertion; post-verification; commit. Public-recovery rotation remains cross-bound to the same root authority and canonical intent payload.

Fresh PR metadata corrected a stale handoff observation: #165 is currently mergeable=true at the same HEAD. This does not satisfy the execution gate and PR #165 remains draft.

Probed an additional exact-source bulk path through the container downloader. It cannot fetch raw GitHub unless web first approves the URL, while web raw-GitHub fetch is disabled in this runtime. Direct shell GitHub DNS also remains unavailable. Connector reads remain healthy, so exact reconstruction is still possible file-by-file but expensive.

Used the recorded fallback for LAB-091 to audit the final candidate inheritance chain and v2/v3/v4 guards. No new one-shot-permit/alternate-surface bypass was established. Corrected stale PR/issue wording: v4 already has exact-published-source 9/9 PASS + compileall from the prior run; remaining work is real LAB-080/LAB-082 integration.

## Evidence retained

- LAB-086 lower-stack exact evidence: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Latest current-head LAB-086 source audit: no new blocker established; no new PASS claimed.
- PR #165 currently mergeable=true at HEAD `95fa5da3...`; draft remains mandatory until execution gate is clean.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards + legacy persistence exact 12/12 PASS.
- LAB-091 v3 cross-table state-machine published-source regression exact 6/6 PASS + compileall.
- LAB-091 v4 deterministic request-id/history-binding published-source regression exact 9/9 PASS + compileall.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is exact current-head execution on one LAB-080→086 closure: own/lower cardinality + migration + suffix + final-supported/security suites, unsafe seed, compileall and final audit. Do not reconcile/integrate before that gate is clean.
- Direct shell GitHub transport remains unavailable. Container download cannot bypass the restriction because raw GitHub cannot be web-approved here. Connector reconstruction works but the full closure remains file-by-file/expensive.
- LAB-091 final candidate is `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`; it still needs execution against real LAB-080/LAB-082 across restart, actual concurrent workers, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
- LAB-091 triggers/UDFs are not a same-privilege SQL sandbox; LAB-087 remains the external single-writable-handle/process/filesystem boundary.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: continue connector reconstruction of exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` plus the minimal real-schema test import closure on the proven LAB-080→085 stack; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw and restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If that closure remains tool-limited, execute `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` against real LAB-080/LAB-082 dependencies with two actual workers sharing one request, restart, crash rollback, timeout-after-commit/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
3. Keep PR #165 and PR #173 draft until their complete real-stack gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; v4 exact-published 9/9 + compileall proven; real LAB-080/LAB-082 integration gate remains.
