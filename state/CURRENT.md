# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — finish recovery-authority lifecycle by binding asymmetric/public-only custody to the authoritative LAB-084/LAB-083 recovery/root state without weakening restart or race semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Branch: `lab/085-recovery-authority-lifecycle`.
- Draft PR: #162.
- Current PR HEAD: `ef4adacdc340b7c524da9af4736c5b6ba37dea44`.
- Follow-up: Issue #163 / LAB-086 — asymmetric migration of historical LAB-084 break-glass proofs after LAB-085.

## Last completed step

Resumed PR #162 and addressed the remaining asymmetric-custody acceptance gap instead of treating symmetric lifecycle rotation as complete. Added `asymmetric_custody.py`, an Ed25519 public-only recovery-authority history: runtime `RecoverySigner` objects hold private signing capability, while durable SQLite state stores only public keys, accepted threshold signatures, transition identities, and the public authority head.

A focused audit found two defects before handoff: signer identity was initially truncated and extra malformed signatures could create a restart-only denial of service if persisted. Signer IDs now use full SHA-256 and rotation persists only valid unique accepted quorum signatures; malformed/unknown/revoked noise cannot inflate quorum or poison restart verification.

The branch README now records the KMS/HSM boundary using RFC 8032 plus current AWS/GCP asymmetric-signing documentation. It explicitly states that this public-only custody slice is not yet the authoritative supported recovery head and that LAB-084 break-glass history is still HMAC-based.

## Evidence produced

- PR #162 remains open, mergeable, and draft.
- Exact published asymmetric custody protocol blob: `920a2586e665aa5187a1a1e97e5fc6401cb49e29`.
- Exact published asymmetric custody test blob: `80f3ade5042ea2872b6395ca8fa4f1802d329d68`.
- Those exact two files matched locally executed bytes by `git hash-object`.
- Focused asymmetric custody suite: 7/7 passed.
- The suite covers public-only restart verification, old+new quorum, private-material non-persistence, authority substitution, transition tamper, and malformed-signature-noise robustness.
- Direct `git clone` from GitHub was probed in this run and failed before execution with DNS resolution failure; connector-backed repository operations remain available.
- Issue #163 created for the remaining later migration of historical break-glass proofs from HMAC verification to asymmetric/HSM-KMS-compatible public verification.

## Known blockers / constraints

- No owner/product blocker.
- PR #162 must remain draft: the asymmetric custody head is not yet atomically bound to the exact LAB-084/LAB-085 recovery head and current LAB-083 root.
- Existing LAB-084 break-glass proofs are HMAC-based and still require historical symmetric material. LAB-085 must not claim that those proofs are already public-only; Issue #163 tracks that migration.
- Full exact-source LAB-085 + LAB-084/083/082/080 regression gate has not yet been rerun for current PR HEAD.
- If both normal/root authorization and recovery-lifecycle authorization are unavailable/compromised, fail closed and require external bootstrap ceremony.

## Exact next action

On PR #162, add a supported asymmetric custody integration layer that binds `(symmetric recovery authority, public recovery authority)` by exact name/version/generation and advances the public custody head, LAB-085 lifecycle head, LAB-084 recovery head, and current-root-authorized transition inside one `BEGIN IMMEDIATE`. Add restart corruption tests for mismatched public/symmetric heads and a race test for recovery-custody rotation versus root/recovery transition. Then reconstruct the exact PR-head executable files plus merged LAB-084/083/082/080 dependencies through the GitHub connector, verify Git blob identities, run all LAB-085 tests (including asymmetric custody), LAB-084/083/082/080 regressions, unsafe seeds, and compileall. Perform a fresh full patch audit. Merge only if all acceptance gates are clean.

## Backlog

- #161 / LAB-085 — recovery-authority lifecycle + asymmetric custody — IN_PROGRESS.
- #163 / LAB-086 — asymmetric break-glass proof migration/public-only historical recovery — READY after LAB-085.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
