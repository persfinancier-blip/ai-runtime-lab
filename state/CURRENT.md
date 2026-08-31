# Current Lab State

Last updated: 2026-08-31

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 `strict_fence.py` predecessor remains blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch`, blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; exact target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains the current allowed fallback while LAB-086 byte-preserving publication/execution is tool-limited. Draft PR #175; branch `lab-090-provider-activation-fencing`; current head `4d2d4f46e718e595ace9bbc963925e0415a5d869`.
- LAB-091 / #170 remains IN_PROGRESS fallback on draft PR #173.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 remained first priority. Direct `git ls-remote` again failed before repository-code execution with `Could not resolve host: github.com`; no safe connector-side predecessor+retained-patch composition primitive was available, so no LAB-086 mutation was attempted.

Resumed the permitted LAB-090 narrow audit on exact PR-head source. Found a provider-side linearizability defect: shared `ActivationState` had no synchronization even though `prepare_activation()` is claimed as the atomic external linearization point and the same state is intentionally shared across reconstructed provider objects. Concurrent prepares could both observe `pending=None`; additionally `increment()` could pass its fence check before a concurrent prepare installed the reservation and then advance the provider afterward.

Published minimal fix in commit `8d05c5ffeef1d770af3ec4bc700d556a8f905c23`: `ActivationState` now owns a shared `RLock`, and prepare/status/commit/release/abort plus the complete increment check+mutation path execute under it. Published implementation blob `fbc8cb4f581221c8b8755a43c436e4d6be74c7a7`.

Published focused regression `test_activation_concurrency.py` in commit `4d2d4f46e718e595ace9bbc963925e0415a5d869`, blob `80495b18cd17fa6b8c1af728ca5232ec1da9b486`. It checks single-winner concurrent prepares and prepare-vs-increment serializability.

Because direct git transport was unavailable, reconstructed the relevant slice from GitHub connector responses and independently verified Git blob hashes before execution: activation `fbc8cb4f...`, concurrency test `80495b18...`, existing primitive test `31d421a1...`, dependency `anchor_attestation/protocol.py` `15d8b7cf...`; all matched published blobs exactly. Executed primitive + concurrency suite: **10/10 PASS**. `compileall` for activation and both tests: **PASS**. This is exact-byte evidence for the provider primitive/concurrency slice only, not a whole-PR PASS.

Issue #169 updated in comment `5472203761`. Durable evidence: `research/2026-08-31-lab090-provider-activation-state-concurrency.md`, main commit `f25d343a534ad7c4c5e6629e4aaa86433b9342fd`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact published signer-noise/core evidence remains 22/22 PASS + compileall; supported/downstream execution pending.
- LAB-091 accumulated adoption hardening/focused reproduced evidence retained; whole-branch timeout/UNKNOWN and process concurrency/crash gates pending.
- LAB-090 provider primitive, premature-release, overlapping-rotation, historical-retry, historical-unresolved restart, orphan-activation restart and provider-state concurrency hardening are published. Latest provider primitive/concurrency exact-byte slice is 10/10 PASS + compileall; integration/restart/downstream exact execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only by conflict-checking exact predecessor `d4a6a40f...`, applying only retained patch `61841b58...` through a byte-preserving supported path, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Direct git/raw network transport remains unavailable due DNS in this run; treat this as a per-run observation. GitHub connector can read exact blob content and perform Contents writes, but no safe exact patch-composition bridge was observed.
- PR #175 remains draft. Only the provider primitive/concurrency slice has current exact-byte execution evidence; focused integration/restart/downstream execution remains pending.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge; if one exists, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require target blob `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate. Otherwise resume LAB-090 PR #175 and execute from independently hash-verified published bytes: `test_activation_orphan_restart.py`, `test_activation_historical_unresolved_restart.py`, historical-retry, overlapping-rotation, activation integration/premature-release, provider-generation integration, and downstream shared-anchor/provider-history suites. If the full dependency closure cannot be reconstructed safely, continue only a narrow source audit for another concrete restart/concurrency defect; do not expand the protocol speculatively.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending on draft PR #172.
- #169 / LAB-090 — IN_PROGRESS; provider-state concurrency fix published on draft PR #175; exact primitive/concurrency slice 10/10 PASS + compileall; integration/restart/downstream gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; draft PR #173; exact whole-branch/full behavioral gates pending.
