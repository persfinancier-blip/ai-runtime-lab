# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-079 — compose the authenticated LAB-078 migration checkpoint with the existing LAB-034–037 external monotonic-anchor boundary so whole-store rollback cannot erase/rewind a completed migration, and prove that the exact checkpoint—not merely the same numeric counter position—was externally anchored.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-078.
- Active: Issue #149 / LAB-079 — IN_PROGRESS.
- Active branch: `lab/079-migration-anchor-binding`.
- Active draft PR: #150 `[LAB-079] Bind migration checkpoint to authenticated monotonic anchor`.
- Current PR HEAD: `ef853897f94aa644de02913258b21d6b8d5212f1`.
- Current compare vs `main`: ahead 9 / behind 3; all seven LAB-079 paths are additions only.

## Last completed step

Reconstructed the current supported LAB-079 binding logic and its real LAB-036/LAB-078 dependency surfaces through the GitHub connector and performed a fresh PR patch audit. The request-specific fix remains intact: confirmation/restart require authenticated reconciliation of the exact `migration-anchor:<sequence>:<checkpoint_id>` request, and the persisted receipt binding is challenge-independent while every use still requires fresh signed provider evidence.

Probed direct shell GitHub access again; DNS resolution still fails, so connector reconstruction remains the supported exact-source route. Re-fetched PR #150 and compared branch to main. The branch has diverged because main advanced by three commits, but every LAB-079 changed path remains a new file with no path overlap; this is not a LAB-079 content conflict. A fresh patch audit found no additional fail-open in the supported request-binding layer.

## Evidence produced

- PR #150 HEAD remains `ef853897f94aa644de02913258b21d6b8d5212f1`.
- Current `supported.py` blob remains `8896a8b5d3dcf0a91e11f4063bcb27f6c38e3503`.
- `compare_commits(main, lab/079-migration-anchor-binding)`: `ahead_by=9`, `behind_by=3`; seven changed files, all `added`.
- Direct `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed with `Could not resolve host: github.com` in this invocation.
- Fresh remote PR patch audit completed; no new supported-layer fail-open identified.
- Issue #149 updated with the exact remaining integration matrix and safe post-test integration fallback.
- Prior evidence remains valid only for the previously executed slices: initial deterministic reference matrix 11/11, unsafe local-only rollback seed failed as expected, initial compileall passed, and focused exact-request binding execution passed after the stable-binding fix.

## Known blockers / constraints

- No owner/product blocker.
- PR #150 is not merge-ready yet because the current HEAD still lacks the full exact-source execution gate against the actual merged LAB-077/LAB-078 SQLite dependency stack.
- Direct shell GitHub DNS is unavailable; GitHub connector reconstruction is the supported fallback.
- A numeric monotonic position alone is not checkpoint identity. Consequential migration requires request-specific authenticated provider evidence.
- A local checkpoint without confirmed external binding is intentionally non-consequential.
- The external provider must durably reconcile stable request IDs; a provider that cannot do so cannot satisfy the stronger LAB-079 contract.
- Whole-store rollback detection remains distinct from consensus, backup durability, and anchor trust-root management.

## Exact next action

Complete the exact current-HEAD integration gate. Reconstruct through the GitHub connector the executable LAB-079 files plus the actual merged LAB-077/LAB-078 and LAB-036 dependency stack, verify every reconstructed executable file with `git hash-object`, and run the real SQLite composition. Required scenarios: migration -> exact-request anchor confirmation -> restart; unrelated pre-existing anchor position remains PENDING; pre-migration SQLite snapshot restore with provider ahead detects rollback or safely reconciles only the exact checkpoint-specific request; timeout-after-commit performs exact-request reconciliation without a second increment; tampered stable binding/provider-generation/unavailable anchor fail closed; first post-migration LAB-077 threshold successor still passes mixed-history + anchored restart verification. Then run LAB-079 + LAB-078 + LAB-077 + LAB-036 regressions and compileall, perform a fresh full PR patch audit, and only then integrate.

If normal draft/merge remains unavailable or branch divergence blocks the normal merge after that gate, re-check that all seven LAB-079 paths are still new/conflict-free and use the normal Contents API file-scoped fallback permitted by `AGENTS.md`; do not use ref/tree/force bypasses.

## Backlog

- #149 / LAB-079 — migration checkpoint monotonic-anchor binding and rollback conformance — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
