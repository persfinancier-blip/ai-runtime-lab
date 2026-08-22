# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-077 — remove the remaining single-signer sink-registry publication boundary by requiring a threshold of distinct currently authorized signers for every new mapping while preserving exact historical proof verification after authority rotation.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-076.
- LAB-076 Issue #143 — DONE.
- LAB-076 PR #144 squash-merged as `03a4fbc531740c79e197bc8fd56c6c38a01f698b` after exact-source validation and final audit.
- Active: Issue #145 / LAB-077 — IN_PROGRESS.
- Active branch: `lab/077-threshold-registry-publication`.
- Active draft PR: #146 `[LAB-077] Threshold-authorized sink-registry publication`.
- PR #146 head at creation: `200a24ccc0c38fbd2e2900f27fbcd0aa05e3819c`.

## Last completed step

LAB-076 was completed with additional audit fixes before merge: strict historical-only verification on the supported surface, preservation of legitimate first publication, and a SQLite `BEGIN IMMEDIATE` durable-verification guard against mixed snapshots during concurrent authority transitions. Exact published source was reconstructed via GitHub connector, matched by Git blob identity, and executed.

Observed LAB-076 final gate:
- LAB-076 protocol + real integration + integration audit + supported audit: 21/21 passed;
- exact LAB-075/074/073/072 backward regressions: 80/80 passed;
- total corrected gate: 101/101 passed;
- unsafe LAB-076 self-swap seed failed as expected;
- compileall passed;
- fresh remote patch audit found no unresolved blocker;
- PR #144 marked ready and normally squash-merged as `03a4fbc531740c79e197bc8fd56c6c38a01f698b`.

With no open issue remaining, the next direct correctness gap was selected: LAB-076 threshold-protects authority rotation/recovery, but a new registry entry is still accepted with one active root-key signature. LAB-077 therefore applies threshold semantics to publication itself.

The first isolated LAB-077 slice has been built and published. It defines one canonical registry-entry payload bound to exact authority ID/version, a canonical threshold proof, strict distinct/active signer checks, entry↔proof binding, historical proof storage/reverification, and an unsafe single-signer baseline.

## Evidence produced

LAB-076:
- Merge SHA: `03a4fbc531740c79e197bc8fd56c6c38a01f698b`.
- Issue #143 status: DONE.

LAB-077 first slice:
- Issue #145 / branch `lab/077-threshold-registry-publication` / draft PR #146.
- `experiments/sink_registry_threshold_publication/protocol.py`.
- `experiments/sink_registry_threshold_publication/tests/test_protocol.py`.
- `experiments/sink_registry_threshold_publication/tests/unsafe_single_signer_expected_failure.py`.
- `experiments/sink_registry_threshold_publication/README.md`.
- `research/2026-08-22-threshold-registry-publication.md`.
- Local corrected isolated suite: 11/11 passed.
- Unsafe one-signer expected-failure seed failed as expected under threshold=2.
- Compileall for the new experiment passed.
- Primary donor: TUF role/key-threshold semantics — publication metadata is trusted only after its configured role signature threshold is met; this is distinct from root-update continuity.

## Known blockers / constraints

- No owner/product blocker.
- LAB-077 PR #146 is intentionally draft/incomplete.
- The current LAB-077 slice proves threshold signature-set semantics only; it has **not yet removed** LAB-076's single-signature publication path from the supported journal.
- Historical roots must remain verification-only; an unpublished proof collected under an old root must not become publication authority after rotation.
- Threshold proof must be durably reverified after restart, never represented by a cached `threshold_met` boolean.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.
- Direct GitHub clone may be unavailable per-run; connector reconstruction remains an allowed exact-source fallback.

## Exact next action

Extend LAB-077 directly over the merged LAB-076 supported surface. Add durable storage for the exact threshold signature set/proof identity in the same broker SQLite database and build a threshold-aware supported registry journal/worker that accepts a threshold envelope rather than a single-signed entry. For a never-before-published mapping, one `BEGIN IMMEDIATE` transaction must re-read the exact current LAB-076 authority head, verify the threshold proof against that root, atomically persist the historical proof + registry historical binding + content-addressed registry row/head, and reject any authority rotation that won before commit. Existing historical mappings must be reverified against their stored historical root/proof without reviving old publication authority. Add regressions for rotation between proof collection and publication, activation of an unpublished old-root proof after rotation, threshold-proof corruption on restart, threshold changes across root versions, and confirmed receipt safety after rotation. Then run exact-source LAB-077 plus LAB-076/075/074 regressions, unsafe seed, compileall, and a fresh remote patch audit before making PR #146 ready.

## Backlog

- #145 / LAB-077 — threshold-authorized sink-registry publication — IN_PROGRESS; draft PR #146.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
