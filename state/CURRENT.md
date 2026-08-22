# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-075 — remove the remaining trusted `sink_id -> runtime adapter/endpoint` mapping behind LAB-074 by binding each new broker reservation to an authenticated/versioned registry entry and enforcing safe rotation/reconciliation semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-074.
- Active: Issue #141 / LAB-075 — IN_PROGRESS.
- Active branch: `lab/075-sink-registry-binding-v2`.
- Active draft PR: #142; current audited HEAD after this run's security fix/regression is `81e2bdbe67b97b4d1ca8bd996816aceff10f3628`.
- PR #142 is currently mergeable but intentionally remains draft until exact-source execution is clean.

## Last completed step

A fresh supported-surface authority audit found a new fail-open beyond the previously fixed missing-`reconcile_by_key` case. `CorrectedRegistryBoundJournal` still inherited the historical prototype's dict-capability compatibility path. That path fabricates safe retry/capability fields for structural test input, so on the audited `supported.py` surface an unauthenticated caller could otherwise reach a new reservation/execution path without a verified LAB-073 attestation.

The audited class now overrides `_capability_fields` and requires a capability object with claim+attestation for every non-terminal path; the inherited implementation then performs the actual LAB-073 verifier check. Terminal `CONFIRMED` remains receipt-only and returns before this gate, preserving the rule that already-committed evidence is readable after later authority changes. Historical prototype compatibility is retained only in a test-only subclass.

## Evidence produced

- Re-read `AGENTS.md`, this state, `prompts/SELF_RESUME.md`, Issue #141, PR #142, current supported/audit/prototype paths and real-integration tests.
- Reconfirmed direct `git`/raw GitHub access is unavailable in this runtime: DNS resolution for `raw.githubusercontent.com` failed; GitHub connector remains functional.
- Fresh audit finding: unauthenticated legacy dict capability could inherit fabricated `SAFE_RETRY_RECONCILE` authority on the supported surface.
- Fix commit: `5aa1e7b03105067425e304927cd0816cdb7e6f9a`; `CorrectedRegistryBoundJournal._capability_fields` now fails closed before any non-terminal execution/reconciliation authority is created.
- Regression/test-fixture commit: `81e2bdbe67b97b4d1ca8bd996816aceff10f3628`; adds strict supported-surface rejection with zero broker rows created while isolating legacy dict compatibility to test-only registry fixtures.
- Issue #141 comment records the finding, fix, and remaining gate.
- PR #142 re-fetched after the edits and is mergeable at HEAD `81e2bdbe67b97b4d1ca8bd996816aceff10f3628`.
- No exact-source test success is claimed for the new HEAD in this run. Prior 14/14 and 30/30 results predate this security fix and are supporting history only.

## Known blockers / constraints

- No owner/product blocker.
- No known unresolved code defect after the latest static/remote audit, but validation is incomplete for the new published HEAD.
- Direct GitHub clone/raw download is unavailable in this runtime due DNS; connector reconstruction is the supported fallback.
- Do not mark LAB-075 DONE until exact published-source execution and final remote patch audit are clean.
- LAB-075 must reuse LAB-022–025 transport/destination enforcement; adapter digest is a reference profile identity, not a claim that Python object identity is production code identity.

## Exact next action

Reconstruct the exact executable bytes of PR #142 HEAD `81e2bdbe67b97b4d1ca8bd996816aceff10f3628` through the GitHub connector and verify Git blob identities locally. Execute the LAB-075 supported/audit-fix + real integration tests, LAB-074/LAB-073/LAB-072 regressions, unsafe baseline, and compileall. The strict new regression must show an unauthenticated dict capability cannot create any broker row. Then perform a fresh remote patch audit of all changed executable paths. If all gates are clean and PR HEAD is unchanged after validation, mark #142 ready, squash-merge it, close Issue #141 DONE, and select the next highest-value unblocked correctness gap.

## Backlog

- #141 / LAB-075 — authenticated sink-adapter and endpoint registry binding — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
