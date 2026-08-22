# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-075 — remove the remaining trusted `sink_id -> runtime adapter/endpoint` mapping behind LAB-074 by binding each new broker reservation to an authenticated/versioned registry entry and enforcing safe rotation/reconciliation semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-074.
- Active: Issue #141 / LAB-075 — IN_PROGRESS.
- Active branch: `lab/075-sink-registry-binding-v2`.
- Active draft PR: #142 at HEAD `181feb0c963731202af64419ba6d7e8aa1b57cb8` at the start of this audit.

## Last completed step

A fresh remote audit of PR #142 found a new fail-open merge blocker in `CorrectedRegistryBrokerWorker.process()` for historical `UNKNOWN`: if a capability/claim is represented as a dict and omits `reconcile_by_key`, the current code evaluates `claim.get("reconcile_by_key", True)` and therefore grants reconciliation authority by omission. This contradicts the LAB-073/074 fail-closed capability contract. Issue #141 has been updated with the exact counterexample.

Direct `git clone` was re-probed in this run and still fails DNS resolution for github.com. The GitHub connector remains functional. PR #142 is intentionally still draft.

## Evidence produced

- `AGENTS.md`, this state, `prompts/SELF_RESUME.md`, Issue #141, and PR #142 were re-read before work.
- PR #142 remains open, draft, mergeable, nine changed files, HEAD `181feb0c963731202af64419ba6d7e8aa1b57cb8` when inspected.
- Fresh patch audit inspected the supported `audit_fixes.py` path and identified the exact fail-open expression.
- Counterexample: historical UNKNOWN + dict/legacy capability with no `reconcile_by_key` field is treated as authorized because the default is `True`.
- Issue #141 comment records the blocker and required regression.
- Direct shell clone probe failed with `Could not resolve host: github.com`; no test execution is claimed in this run.
- Prior evidence remains: interface-compatible matrix 14/14, audit-fix + inherited matrix 30/30, unsafe string-only baseline failed as expected. These are not exact-source evidence for the current/future corrected HEAD.

## Known blockers / constraints

- No owner/product blocker.
- PR #142 has a real code blocker: missing reconciliation authority is fail-open for dict-shaped capability claims.
- Direct GitHub clone is unavailable in this runtime due DNS.
- Do not mark LAB-075 DONE until the fail-open is fixed, a regression is added, and exact published-source execution is observed.
- LAB-075 must reuse LAB-022–025 transport/destination enforcement; adapter digest is a reference profile identity, not a claim that Python object identity is production code identity.

## Exact next action

On `lab/075-sink-registry-binding-v2`, change historical-UNKNOWN capability evaluation so reconciliation is authorized only when `reconcile_by_key is True`; missing/unknown fields must deny. Add a regression using a dict/legacy capability that omits `reconcile_by_key` and prove no reconciliation occurs. Then reconstruct the new exact PR #142 executable bytes through the GitHub connector, verify Git blob identities locally, run LAB-075 supported + real integration tests, LAB-074/LAB-073/LAB-072 regressions, unsafe baseline, and compileall. Perform a fresh remote patch audit. If all gates are clean and PR HEAD is unchanged after validation, mark #142 ready, squash-merge it, close Issue #141 DONE, and select the next highest-value unblocked correctness gap.

## Backlog

- #141 / LAB-075 — authenticated sink-adapter and endpoint registry binding — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
