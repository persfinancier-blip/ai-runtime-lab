# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD after this run: `63c305806a93ee4e1335594d781e789e31e13b44`.
- PR remains draft; current-head real-ledger gate has not passed.

## Last completed step

Fresh transaction-scoped-thaw audit found a new least-privilege/correctness merge blocker. `remove_public_mutation_fence_locked()` currently removes more SQL capabilities than any supported consequential writer needs: it drops inherited UPDATE/DELETE history guards, existing public-recovery history guards, and singleton-head INSERT/DELETE guards in addition to the exact creation/head-UPDATE operations required for rotation/recovery.

A focused SQLite semantic counterexample was actually executed for inherited history: current-source-equivalent broad thaw changed an existing authenticated transition from `original` to `tampered`; a creation-only thaw kept UPDATE blocked and preserved the row.

Source audit of the real lower primitives established the exact required operations:
- root rotation: INSERT root authority + INSERT root transition + UPDATE root head;
- provider rotation: INSERT provider generation + INSERT threshold proof + INSERT provider transition + UPDATE provider head;
- public-recovery rotation: INSERT public authority + INSERT public transition + UPDATE public head;
- asymmetric break-glass: INSERT root authority + UPDATE root head + INSERT asymmetric recovery proof.

No supported operation needs UPDATE/DELETE of committed history or INSERT/REPLACE/DELETE of an initialized singleton head.

The red regression `tests/test_transaction_scoped_thaw_minimality.py` now covers inherited history, existing public-recovery history, and public/root/provider singleton-head INSERT OR REPLACE + DELETE during thaw. Research note `research/2026-08-25-lab086-minimal-transaction-thaw.md` records the exact capability matrix.

## Evidence produced / reconfirmed

- Exact current `strict_fence.py` blob remains `02128fb866d7b4a3382622356f33e7b1739ff167`; source shows broad removal through `PUBLIC_MUTATION_TRIGGER_NAMES`, `_all_inherited_trigger_names()`, `ROOT_HEAD_MUTATION_TRIGGER_NAMES`, and `CURRENT_AUTHORITY_WRITER_TRIGGER_NAMES`.
- Executed focused semantic counterexample: broad thaw allowed UPDATE of committed inherited transition; creation-only thaw raised `sqlite3.IntegrityError` and preserved the row.
- Lower writer source audit confirmed head operations are UPDATE-only (`provider_rotation_authority_head`, `asymmetric_provider_head`, `provider_recovery_public_head`).
- Regression commits: initial `d34b9074cb06ae338e2e8b69aa665c71c7a81533`, history expansion `b190fcb8a3fb304b7c4bded2b7f8f8acca591b4d`, head-operation expansion `10d7ef311e22540ed957939ff5bd1af467a50e5e`.
- Research-note/current branch HEAD `63c305806a93ee4e1335594d781e789e31e13b44`.
- Cumulative lower-stack exact evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite previously passed 12/12; post-cutoff proof-row creation gate passed 12/12 before this newly found blocker.

## Known blockers / constraints

- New merge blocker: transaction-scoped thaw grants broader DML authority than supported writers require.
- Required implementation must distinguish full trigger cleanup/reinstall from runtime thaw. `install_public_mutation_fence_locked()` currently relies on broad removal to recreate triggers, so simply narrowing the existing removal loop would break repeated installation. Use a separate full-cleanup helper for reinstall and a minimal thaw helper for consequential writers.
- Minimal thaw should remove only: public authority INSERT, public transition INSERT, public-head UPDATE; inherited creation triggers; root-head UPDATE; root-authority INSERT; provider-generation INSERT; provider-head UPDATE; post-cutoff evidence creation triggers; obsolete upgrade triggers as needed. Keep all committed-history UPDATE/DELETE guards and singleton-head INSERT/DELETE guards installed.
- After this fix, remaining merge gate is exact current-head real-ledger `migration_guard + suffix + final_supported`, unsafe legacy-promotion seed, full compileall and final security audit.
- Direct shell GitHub transport remains unavailable; GitHub connector/Contents API is the supported fallback.
- LAB-087/#166 owns arbitrary same-privilege SQLite DDL/schema control; LAB-088/#167 signer-noise; LAB-090/#169 provider handoff freshness; LAB-091/#170 mutable shared-anchor/new-receipt DML authorization.

## Exact next action

1. Reconstruct exact current `strict_fence.py` and split broad reinstall cleanup from minimal transaction-scoped thaw. Keep install/reinstall behavior idempotent while narrowing final-writer capability to the exact operation matrix above.
2. Verify published blob identity and execute `test_transaction_scoped_thaw_minimality.py` plus the full current strict-fence regression set; fix every failure.
3. Resume exact current-head real-ledger LAB-086 migration/suffix/final-supported gate on the proven LAB-080→085 closure.
4. Run unsafe legacy-promotion seed, full compileall and final security audit; only then mark PR #165 ready/integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; minimal-thaw blocker recorded with strengthened red regression and exact capability audit.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
