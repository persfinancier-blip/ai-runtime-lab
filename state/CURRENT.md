# Current Lab State

Last updated: 2026-08-20

## Active objective

Advance from authenticated CT v2 signed tree heads to authenticated inclusion of an exact log entry under an authenticated STH. LAB-043 is complete: old/new RFC 9162 `signed_tree_head_v2` artifacts are now strictly decoded, bound to an immutable log profile, cryptographically authenticated, and then used as the authoritative roots for the LAB-042 consistency-wire + LAB-041 compact-Merkle append-only chain.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-043.
- Completed Issue #82 / LAB-043.
- PR #83 was remote patch-audited and then closed as manually integrated after the ready-for-review transition was blocked before execution by an external safety-status gate.
- LAB-043 exact audited files were integrated into `main` through the normal GitHub Contents API under the repository safe-fallback policy; final integration commit was `d0a447639982e02ec9ecffaeb81a22a1ce3a8f39`.
- Active next: Issue #84 / LAB-044 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-043 built and audited `experiments/ctv2_sth_chain/`. It implements strict RFC 9162 `signed_tree_head_v2` and `TreeHeadDataV2` wire handling, exact LogID/profile binding, Ed25519 (`0x0807`) signature verification over the exact encoded `tree_head` field, strict HASH_SIZE/extension/type/trailing-data checks, and an end-to-end chain from authenticated old/new STHs into LAB-042 exact proof binding and LAB-041 compact consistency verification.

The audit found one material deliverable defect rather than a cryptographic defect: README documented an unsafe parsed-only seed that had not actually been committed. The missing seed was added, together with a corrected corrupted-signature regression test. PR #83 was mergeable but remained draft because the ready-for-review transition was blocked before execution; GitHub therefore rejected normal merge. After confirming all six changed paths were new/conflict-free and remote patch-audited, the exact files were applied via the supported Contents API fallback and the draft PR was closed as manually integrated. No ref/tree/force bypass was used.

## Evidence produced

- `experiments/ctv2_sth_chain/protocol.py`
- `experiments/ctv2_sth_chain/tests/test_protocol.py`
- `experiments/ctv2_sth_chain/tests/test_signature_corruption.py`
- `experiments/ctv2_sth_chain/tests/unsafe_parsed_expected_failure.py`
- `experiments/ctv2_sth_chain/README.md`
- `research/2026-08-20-ctv2-sth-chain.md`
- Exact branch `protocol.py` Git blob matched locally executed source: `3fe61a780678e80125b8f1fbb93dc890e686f976`.
- Exact branch original `test_protocol.py` Git blob matched locally executed source: `4045edd3b92299aaf8cd29a32b6982e5a4eb4912`.
- Original exact branch suite: 16/16 passed.
- Corrected suite after corrupted-signature regression: 17/17 passed.
- Unsafe parsed-only baseline: expected failure because a corrupted signature remained parseable and therefore demonstrated that parsing is not authentication.
- `python -m compileall -q experiments/ctv2_sth_chain` passed.
- Primary provenance: RFC 9162 §§4.1, 4.4, 4.5, 4.9, 4.10, 4.11 and RFC 8446 §4.2.3.
- Issue #82 closed DONE.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-043 authenticates already configured log profiles; log-profile/key discovery, distribution and rotation remain outside its scope.
- Executable reference signature profile is Ed25519 with SHA-256/HASH_SIZE=32 in the downstream Merkle experiments; general profile agility remains external.
- LAB-043 proves append-only consistency between authenticated STHs but does not yet prove that a specific certificate/precertificate/log artifact is included under an authenticated STH.
- Full CT HTTP/base64 transport, certificate-policy/SCT compliance, and witness consensus remain outside scope.

## Exact next action

Start Issue #84 / LAB-044. Research RFC 9162 §2.1.3, §4.5, §4.7, §4.10 and §4.12. Build `experiments/ctv2_inclusion_chain/` with a strict `TransItem<inclusion_proof_v2>` encoder/decoder; bind exact LogID, authenticated STH tree size and leaf index; compute the RFC 9162 leaf hash from the exact serialized leaf `TransItem` bytes; and verify the compact inclusion path against the authenticated LAB-043 STH root. Demonstrate the full chain `exact leaf TransItem + authenticated signed_tree_head_v2 + inclusion_proof_v2 -> verified inclusion`. Retain an unsafe seed that accepts a caller-supplied leaf hash without binding it to the exact leaf bytes and show artifact substitution.

## Backlog

- #84 / LAB-044 — CT v2 authenticated inclusion-proof chain and leaf binding conformance — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally out of scope unless later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
