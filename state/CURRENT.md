# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-075 — remove the remaining trusted `sink_id -> runtime adapter/endpoint` mapping behind LAB-074 by binding each new broker reservation to an authenticated/versioned registry entry and enforcing safe rotation/reconciliation semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-074.
- Active: Issue #141 / LAB-075 — IN_PROGRESS.
- Active branch: `lab/075-sink-registry-binding-v2`.
- Active draft PR: #142; current HEAD after this run's supported-surface composition fixes is `b029ab29093275f0e3f1c12cbc87ee731f5df820`.
- PR remains draft until exact-source execution is clean; mergeability can transiently report false while GitHub recomputes after commits.

## Last completed step

A fresh supported-surface authority audit found two composition fail-opens beyond the previously fixed missing-`reconcile_by_key` case.

First, `CorrectedRegistryBoundJournal` still inherited the historical prototype's dict-capability compatibility path. That path fabricates safe retry/capability fields for structural test input, so on the audited `supported.py` surface an unauthenticated caller could otherwise reach a new reservation/execution path without a verified LAB-073 attestation. The audited class now overrides `_capability_fields` and requires claim+attestation for every non-terminal path; the inherited LAB-073 verifier remains authoritative. Terminal `CONFIRMED` remains receipt-only and returns before this gate.

Second, the supported worker itself could be manually paired with an unaudited prototype registry journal, reintroducing the legacy compatibility path by composition. `CorrectedRegistryBrokerWorker` now refuses any registry that is not the audited `CorrectedRegistryBoundJournal` surface (including its explicit test-only subclass).

## Evidence produced

- Re-read `AGENTS.md`, this state, `prompts/SELF_RESUME.md`, Issue #141, PR #142, current supported/audit/prototype paths and real-integration tests.
- Reconfirmed direct `git` and raw GitHub access are unavailable in this runtime: DNS resolution for `raw.githubusercontent.com` failed; GitHub connector remains functional.
- Finding 1: unauthenticated legacy dict capability could inherit fabricated `SAFE_RETRY_RECONCILE` authority on the supported surface.
- Fix commit `5aa1e7b03105067425e304927cd0816cdb7e6f9a`: audited `_capability_fields` fails closed for unauthenticated non-terminal paths.
- Regression/fixture commit `81e2bdbe67b97b4d1ca8bd996816aceff10f3628`: strict rejection with zero broker rows; legacy dict compatibility isolated to test-only fixtures.
- Finding 2: supported worker could be composed with unaudited prototype journal and bypass the new gate.
- Fix commit `b16c56979aea41879771dda677b0e19dd1f11193`: supported worker requires audited registry journal.
- Regression commit `b029ab29093275f0e3f1c12cbc87ee731f5df820`: worker/prototype-journal composition is rejected before request processing.
- PR #142 body updated to document the authenticated-capability supported-surface contract.
- No exact-source test success is claimed for the new HEAD. Prior 14/14 and 30/30 results predate these security fixes and are supporting history only.

## Known blockers / constraints

- No owner/product blocker.
- No known unresolved code defect after the latest static/remote audit, but validation is incomplete for the newly published HEAD.
- Direct GitHub clone/raw download is unavailable in this runtime due DNS; connector reconstruction is the supported fallback.
- Do not mark LAB-075 DONE until exact published-source execution and final remote patch audit are clean.
- LAB-075 must reuse LAB-022–025 transport/destination enforcement; adapter digest is a reference profile identity, not a claim that Python object identity is production code identity.

## Exact next action

Reconstruct the exact executable bytes of PR #142 HEAD `b029ab29093275f0e3f1c12cbc87ee731f5df820` through the GitHub connector and verify Git blob identities locally. Execute the LAB-075 supported/audit-fix + real integration tests, LAB-074/LAB-073/LAB-072 regressions, unsafe baseline, and compileall. The new regressions must prove (1) unauthenticated dict capability creates no broker row and (2) supported worker cannot be paired with the unaudited prototype journal. Then perform a fresh remote patch audit of all changed executable paths. If all gates are clean and PR HEAD is unchanged after validation, mark #142 ready, squash-merge it, close Issue #141 DONE, and select the next highest-value unblocked correctness gap.

## Backlog

- #141 / LAB-075 — authenticated sink-adapter and endpoint registry binding — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
