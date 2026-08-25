# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD after this run: `86e0baec2183f8c46ce129b2310aa81d458882cc`.
- PR remains draft; full current-head real-ledger gate has not passed.

## Last completed step

Fresh transaction-scoped-thaw audit found a new least-privilege/correctness blocker. Current `remove_public_mutation_fence_locked()` drops `*_all_inherited_trigger_names()`, which includes UPDATE/DELETE immutability guards for already committed inherited history in addition to the INSERT-deny triggers that the final writer actually needs to remove. It also drops all public-recovery mutation triggers, including UPDATE/DELETE guards on existing public authority/transition history.

A focused SQLite semantic counterexample was actually executed for inherited root-transition history: current-source-equivalent thaw allowed an existing authenticated row to be UPDATEd; a minimal thaw that removed only the INSERT-deny left the UPDATE blocked and the row unchanged.

A red regression is committed at `experiments/asymmetric_break_glass_history/tests/test_transaction_scoped_thaw_minimality.py`. It now covers both inherited transition history and existing public-recovery authority/transition history. Research note `research/2026-08-25-lab086-minimal-transaction-thaw.md` records the exact minimal-fix shape.

## Evidence produced / reconfirmed

- Current exact `strict_fence.py` source shows `remove_public_mutation_fence_locked()` removes `*_all_inherited_trigger_names()`; `_all_inherited_trigger_names()` contains both creation-deny and UPDATE/DELETE history guards.
- Executed semantic counterexample: current broad thaw changed inherited transition marker `original -> tampered`; minimal creation-only thaw raised `sqlite3.IntegrityError` and preserved `original`.
- Red regression first commit `d34b9074cb06ae338e2e8b69aa665c71c7a81533`, strengthened commit `b190fcb8a3fb304b7c4bded2b7f8f8acca591b4d`.
- Research note commit/current branch HEAD `86e0baec2183f8c46ce129b2310aa81d458882cc`.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite previously passed 12/12; post-cutoff proof-row creation exact gate passed 12/12 before this new blocker.

## Known blockers / constraints

- New merge blocker: transaction-scoped thaw is broader than required and makes already authenticated inherited/public history mutable inside the privileged final-writer transaction.
- Required fix: split creation/head-mutation triggers from history-immutability triggers; remove only the former during thaw. Existing UPDATE/DELETE history guards must remain installed.
- After that fix, the remaining merge gate is exact current-head real-ledger `migration_guard + suffix + final_supported`, unsafe legacy-promotion seed, full compileall and a fresh final security audit.
- Direct shell GitHub transport remains unavailable; GitHub connector/Contents API is the supported fallback.
- LAB-087/#166 owns arbitrary same-privilege SQLite DDL/schema control.
- LAB-088/#167 owns threshold signer-noise robustness.
- LAB-090/#169 owns provider-generation handoff freshness/external-anchor race.
- LAB-091/#170 owns mutable shared-anchor/new provider-receipt ordinary-DML writer authorization.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the exact current branch `strict_fence.py` and apply the minimal thaw patch: for inherited history remove only `INHERITED_MUTATION_TRIGGERS.values()`; for public recovery split creation/head-mutation capability from UPDATE/DELETE history immutability and thaw only the exact operations required by supported rotation.
2. Verify the published Git blob and execute `test_transaction_scoped_thaw_minimality.py` together with the full current strict-fence regression set; fix every failure.
3. Resume the full exact current-head real-ledger LAB-086 migration/suffix/final-supported gate on the proven LAB-080→085 dependency closure.
4. Run unsafe legacy-promotion seed, full compileall and final security audit; only then mark PR #165 ready/integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new minimal-thaw blocker recorded with red regression/research note.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
