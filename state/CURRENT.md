# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `5ff56ec39673803acff49960a914951df16d6e46`.
- PR remains draft; full current-head real-ledger migration/suffix/final-supported regression gate has not passed.

## Last completed step

Performed a fresh final-writer/source audit of the current LAB-086 provider-generation rotation path. Confirmed a separate external-boundary TOCTOU inherited from LAB-082: `rotate_provider()` obtains an authenticated read of the candidate provider **before** `BEGIN IMMEDIATE`, then compares that earlier position with the durable `reserved_position` inside the SQL transaction. A deterministic executable interleaving reproduced: durable tail=10, candidate read=10, candidate externally advances to 11 before SQL commit, stale observation 10 still matches durable tail 10, and provider-generation rotation commits with the newly current provider already ahead of the ledger.

This is fail-closed availability/correctness, not authority escalation and not a bypass of LAB-086 SQL/DML fences. It is tracked separately as LAB-090 / Issue #169 unless the remaining real-stack LAB-086 gate demonstrates a direct acceptance failure. Issue #163 body was also corrected to the current HEAD/evidence and the already-closed LAB-089 premise was removed from the active finding set.

A source audit of `migration_guard.py`, `suffix.py`, `final_supported.py`, and the strengthened `strict_fence.py` found no new post-cutoff privilege-escalation path in this run. The supported consequential writer pattern remains: pre-verify lower+LAB-086 history under a writer-excluding interval, verify exact quorum/payload, transactionally thaw only the required current-write fences, mutate, reinstall/assert fences, verify affected history, commit.

## Evidence produced / reconfirmed

- LAB-090 / Issue #169 created with source ordering and executable minimal race schedule.
- Minimal race output: authenticated observation=10; external provider at commit=11; durable tail=10; rotation predicate accepts and durable generation advances; post-commit external position != durable tail.
- Issue #163 updated to current observed HEAD `5ff56ec...`, current lower-stack evidence, closed LAB-089 status, and LAB-090 follow-up boundary.
- Fresh branch/main compare: `ahead 124 / behind 65`; all 45 PR paths remain additions, so no path-level content collision with current `main` is observed.
- Existing exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite remains 12/12 PASS; unsafe legacy-auto-promotion seed failed as intended.
- Latest branch-focused strict-fence regressions remain green from prior runs; no new PASS is claimed for the six recently adapted verifier-corruption tests because the full exact dependency closure was not reconstructed in this run.

## Known blockers / constraints

- Remaining merge gate is full exact current-head real-ledger execution of `migration_guard + suffix + final_supported`, including the six adapted corruption tests, then unsafe seed, full compileall and final security audit.
- Direct shell GitHub transport remains unavailable in this run; connector reads/writes work and are the supported fallback. Full exact-suite reconstruction is therefore file-by-file unless transport availability changes.
- LAB-090/#169 is fail-closed provider-handoff freshness work. Do not silently claim SQLite serialization covers an external provider; keep it follow-up unless the remaining LAB-086 gate makes it an acceptance blocker.
- LAB-083/LAB-084 signer-noise robustness remains LAB-088/#167 and is fail-closed availability work.
- LAB-086 SQLite fences cover audited ordinary DML/stale supported paths, not arbitrary same-privilege SQLite schema/DDL authority; LAB-087/#166 owns that stronger boundary.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Re-fetch PR #165 HEAD; connector-reconstruct the exact LAB-080→085 dependency closure plus current LAB-086 implementation/tests, verifying executable/test files by Git blob identity.
2. Execute the complete current-head LAB-086 real-schema suite: migration v4/root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial state, full lower/public-history guards, public-rotation cross-binding, inherited/direct surfaces, strict fences, final verification snapshot, rotation races, and the six adapted corruption tests.
3. Run unsafe legacy-promotion seed and full `python -m compileall` over the reconstructed closure.
4. Perform a fresh full security audit of consequential/restart paths and branch/main divergence. Fix every blocker. Only after a clean current-head gate may PR #165 be marked ready and integrated.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; runtime fence blockers fixed; full current-head real-ledger execution remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
