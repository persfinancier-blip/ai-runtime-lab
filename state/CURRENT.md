# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass verification from durable symmetric/HMAC material to an explicit authenticated legacy cutoff plus Ed25519 public-only proof history, without auto-promoting legacy rows or weakening LAB-084/LAB-085 authority semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- LAB-085 Issue #161 — DONE.
- LAB-085 post-merge concurrency fix PR #164 squash-merged as `d2c9781f5a60dc9b8b94fc8dba651f804a73e509` from audited HEAD `dbc5e440378e4bb6e6ed29600362645c0c47b722`.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Active branch: `lab/086-asymmetric-break-glass-history`.
- Active draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current PR #165 HEAD after first slice: `61ae0b8424c655ac8e61b187c782d19906246301`.

## Last completed step

LAB-085 was closed after final remote patch audit confirmed PR #164 changed only the intended three verification/regression files. Exact current-delta tests had passed 11/11 with compileall; the unchanged lower layers retain prior exact 87/87 evidence. Because shell GitHub DNS remains unavailable and the connector cannot mount a repository archive, the narrow exact-delta result plus unchanged lower-stack evidence was accepted as the evidence-equivalent gate rather than fabricating a nonexistent full rerun. PR #164 then merged normally.

LAB-086 immediately started. A first deterministic reference implementation now establishes a threshold-signed boundary between legacy HMAC break-glass history and new Ed25519 threshold proof history. Legacy rows remain legacy rather than being copied into the stronger proof table. New proofs bind sequence, predecessor/successor root identities and exact recovery authority content/version/generation. Runtime private signing capability is not durable state; historical public keys remain usable only for verification after rotation.

The first corrected local suite passed 12/12, compileall passed, and the unsafe auto-promotion seed failed as expected because it incorrectly treated an existing legacy HMAC proof as new asymmetric authority. Five LAB-086 files were published and draft PR #165 was opened.

## Evidence produced

- LAB-085 PR #164 merge SHA: `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`.
- LAB-085 final Issue #161 records exact current-delta 11/11, prior unchanged lower-stack 87/87, compileall and final three-file patch audit.
- `experiments/asymmetric_break_glass_history/protocol.py`
- `experiments/asymmetric_break_glass_history/tests/test_protocol.py`
- `experiments/asymmetric_break_glass_history/tests/unsafe_legacy_promotion_expected_failure.py`
- `experiments/asymmetric_break_glass_history/README.md`
- `research/2026-08-23-asymmetric-break-glass-history.md`
- LAB-086 corrected reference suite: 12/12 passed.
- LAB-086 unsafe legacy auto-promotion seed: failed as expected.
- LAB-086 compileall: passed.
- Draft PR #165 opened from five new files; no merge is claimed.

## Known blockers / constraints

- PR #165 is deliberately draft: `PublicOnlyBreakGlassHistory` is a standalone reference SQLite authority and must not become a second production authority beside LAB-084/LAB-085.
- The authenticated cutoff currently accepts a supplied `legacy_digest`; the supported integration must derive/verify that digest from the real LAB-084 historical prefix inside the existing SQL authority boundary rather than trusting caller narration.
- New asymmetric break-glass proof insertion must be serialized with current LAB-085 recovery/custody heads and normal/root transitions in one write-excluding transaction.
- Mixed-history restart must verify the legacy HMAC prefix as legacy, then the signed cutoff, then only asymmetric proofs after the cutoff.
- No live HSM/KMS was exercised; Ed25519 signer objects are a reference interface for a future HSM/KMS adapter.
- Direct shell GitHub networking remains unavailable in this runtime; connector operations are healthy.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

Integrate LAB-086 with the real merged LAB-084/LAB-085 SQLite schema instead of the standalone reference store. Inspect `provider_recovery_authority_lifecycle` recovery-proof tables and supported final surface, then add one authenticated migration-cutoff row and asymmetric break-glass proof table behind the same `BEGIN IMMEDIATE` authority serialization boundary. Derive the legacy-prefix commitment from actual durable LAB-084 rows. Add mixed-history restart verification plus regressions for legacy auto-promotion, proof rebinding, missing historical public material, old-signer post-rotation use, recovery/rotation race, corrupted cutoff, and partial transaction. Run exact LAB-086 plus LAB-085/084 regressions, unsafe seed and compileall; remote-audit PR #165 before any merge.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; first semantics slice 12/12, real LAB-084/085 integration next.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
