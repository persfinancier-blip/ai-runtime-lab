# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-078 — prove an authenticated migration checkpoint that moves pre-LAB-077 single-signature sink-registry history onto the threshold-publication surface without silently promoting legacy authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-077.
- Active: Issue #147 / LAB-078 — IN_PROGRESS.
- Active branch: `lab/078-authenticated-registry-migration`.
- Draft PR: #148 `[LAB-078] Authenticated legacy registry migration checkpoint`.
- Current PR head after first published slice: `209e980fe6bd2a27e6cb13e14a51306d21f62b94`.

## Last completed step

Inspected the real merged LAB-076/LAB-077 schemas and publication boundaries. LAB-077 requires threshold proof for every new registry publication, while legacy LAB-076 rows have only historical single-signature authority bindings; therefore migration must not backfill synthetic threshold proofs.

Built and executed the first deterministic LAB-078 ceremony slice. The corrected checkpoint binds the exact legacy registry/history prefix, terminal authority identity/version/epoch, registry heads, capability heads, credential generation, exact CONFIRMED request identities, and cutoff sequence. `INTENT`/`UNKNOWN` block migration. The current threshold signs the checkpoint, and restart re-verifies the stored threshold proof against a content-addressed historical root snapshot.

Published the slice in branch `lab/078-authenticated-registry-migration` and opened draft PR #148. A remote patch audit confirmed the next integration gap: the reference prototype uses an isolated authority-head schema, whereas real LAB-076 stores root material in `registry_authorities` and its head contains only `(authority_id, version, epoch)`. The reference store must not become a second authority source.

## Evidence produced

- `experiments/sink_registry_migration_checkpoint/protocol.py`
- `experiments/sink_registry_migration_checkpoint/tests/test_protocol.py`
- `experiments/sink_registry_migration_checkpoint/tests/unsafe_auto_promotion_expected_failure.py`
- `experiments/sink_registry_migration_checkpoint/README.md`
- `research/2026-08-22-authenticated-registry-migration-checkpoint.md`
- Corrected local reference suite: **10/10 passed**.
- Unsafe auto-promotion seed: failed as expected because one legacy row became a fake threshold publication.
- Compileall: passed.
- Pre-publication audit found and fixed missing restart threshold-signature re-verification.
- Direct `git ls-remote`/clone remains unavailable in this runtime because `github.com` DNS resolution fails; GitHub connector remains the allowed exact-source fallback.
- TUF primary specification confirms the adopted continuity principle: stronger/new trusted metadata is explicitly threshold-authorized rather than inferred from old metadata presence.

## Known blockers / constraints

- No owner/product blocker.
- PR #148 is intentionally draft; real LAB-076/LAB-077 integration is not complete.
- Do not instantiate the isolated `MigrationStore` as a parallel authority source in production integration.
- Pending `INTENT`/`UNKNOWN` must be resolved before migration in the current safe policy; `CONFIRMED` remains receipt-only history.
- Legacy rows remain verification-only and must never receive synthetic LAB-077 threshold proofs.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.

## Exact next action

Add a real integration layer that operates on the existing LAB-076/LAB-077 SQLite database and reads the current/historical root through `DurableRegistryAuthority._load_root()` / `registry_authorities`, not through the isolated reference schema. In one `BEGIN IMMEDIATE`, re-read the exact LAB-076 authority head, registry heads, capability heads, credential generation and pending broker state; verify a current LAB-077 threshold proof over the canonical migration checkpoint; persist only the migration checkpoint/proof (no synthetic per-row threshold proofs). Then add an audited mixed-history journal/verifier that treats rows at/before the checkpoint as LAB-076 historical verification-only and rows after it as LAB-077 threshold-only. Prove: first threshold successor after migration, restart after suffix, root-rotation race, omitted/substituted legacy row, partial migration, pending-state refusal, and CONFIRMED receipt-only behavior. Finally reconstruct exact PR-head bytes through connector, run LAB-078 plus LAB-077/076/075 regressions and compileall, and perform a fresh remote patch audit before ready/merge.

## Backlog

- #147 / LAB-078 — authenticated migration checkpoint — IN_PROGRESS; draft PR #148.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
