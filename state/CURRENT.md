# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-068 — close the deferred LAB-027 crash gap for named credential-file fallback without deleting a file still owned by a live/recoverable process or trusting pathname-only identity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-067.
- LAB-067 Issue #125 DONE; PR #126 squash-merged as `a7b24440007b22ccc35ae358af0cdd287a84109f` after exact-source 64/64 regression evidence.
- Active Issue #127 / LAB-068 — IN_PROGRESS.
- Active branch: `lab/068-credential-scavenging`.
- Draft PR #128 — published first slice at HEAD `ffc0c2df862f81ccedb6f209a3f0eca7325a8353`; merge intentionally blocked by audit findings below.

## Last completed step

Started LAB-068 and built the named-credential cleanup reference path using existing lab primitives: non-secret durable lease/evidence, cleanup-generation fencing, LAB-032 PID+starttime+fresh-pidfd process-instance reconciliation, LAB-065 no-symlink directory-FD namespace binding, keyed HMAC secret identity, and idempotent UNKNOWN-after-unlink reconciliation.

The first local corrected slice passed 10/10 tests and the unsafe glob/path baseline failed as expected because it deleted a live child's credential file. Audit then found two deeper correctness defects:
1. `(st_dev, st_ino)` can be reused immediately after unlink/recreate in the observed filesystem. `st_ctime_ns` detected the replacement but is not stable across writing the secret, so it cannot be the durable pre-write object authority.
2. More importantly, the first published creation path writes+fsyncs secret bytes before inserting the durable lease. A crash in that window can leave plaintext filesystem debris with no authoritative lease. This is a merge blocker.

A corrected local design now persists `PREPARED` non-secret intent before any secret bytes exist, allocates an empty 0600 file, captures/persists LAB-066-style opaque `name_to_handle_at` object evidence as `ALLOCATED`, only then writes+fsyncs the secret, and finally advances to `CREATED`. Cleanup compares the opaque file-handle evidence plus directory identity; ctime is retained only as a diagnostic observation. A live old-generation child still blocks deletion after credential rotation. This corrected local design passes 11/11 against interface-compatible copies of the existing LAB-032/LAB-065/LAB-066 dependencies.

## Evidence produced

- Draft experiment: `experiments/credential_file_scavenging/protocol.py`.
- Failure matrix: `experiments/credential_file_scavenging/tests/test_protocol.py`.
- Unsafe seed: `experiments/credential_file_scavenging/tests/unsafe_glob_expected_failure.py`.
- Research note: `research/2026-08-21-credential-file-scavenging.md`.
- Draft PR #128 opened.
- First published/local slice: 10/10 corrected tests passed; unsafe glob seed failed as expected.
- Audit reproduction: byte-identical unlink/recreate reused `(dev,ino)` in the observed runtime.
- Locally corrected PREPARED->ALLOCATED->secret-write design with opaque handle evidence: 11/11 passed against interface-compatible dependency copies.
- Direct `git clone` was probed again and failed before checkout with `Could not resolve host: github.com`; therefore 11/11 is supporting development evidence, not exact published-source evidence.

## Known blockers / constraints

- PR #128 must remain draft. Its currently published code still has the audit-discovered secret-before-durable-lease creation-order defect and ctime-based object-identity design.
- The corrected PREPARED/ALLOCATED + opaque file-handle version exists locally but has not yet been published to PR #128.
- Direct shell GitHub DNS remains unavailable in this runtime. Connector reconstruction is the supported exact-source fallback.
- Opaque file-handle support is runtime/filesystem dependent; named fallback must fail closed if the required strong identity cannot be captured. Do not silently downgrade to pathname or `(dev,ino)` alone.
- Filesystem deletion is lifetime/storage reclamation, not forensic erasure.
- A live child remains authoritative for lifetime even after credential rotation; stale credential generation alone is not deletion authority.

## Exact next action

Resume draft PR #128. Publish the locally corrected creation ordering and LAB-066 `name_to_handle_at` file-object evidence to `protocol.py`, add the crash-after-secret-write-before-READY regression, and update the research note to remove any implication that ctime is authoritative. Re-fetch the PR and perform a fresh remote patch audit. If direct clone remains unavailable, reconstruct exact PR #128 executable bytes plus the repository's actual LAB-027/LAB-032/LAB-065/LAB-066 dependencies through the GitHub connector, verify local `git hash-object` values against GitHub blob SHAs, and run: LAB-068 corrected + unsafe suites, relevant LAB-027 credential regressions, LAB-032 supervisor-restart/process-lifetime regressions, LAB-065 namespace-binding regressions, LAB-066 reacquisition regressions, and compileall. Fix every failure and rerun. Only after exact-source execution and a clean audit may PR #128 be marked ready/integrated and Issue #127 closed.

## Backlog

- #127 / LAB-068 — crash-resilient credential-file scavenging and stale-secret cleanup — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
