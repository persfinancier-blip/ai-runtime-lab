# Current Lab State

Last updated: 2026-08-19

## Active objective

Execute LAB-021: prove sensitive-data labels survive transformations/fallbacks and that protected egress sinks cannot receive secret-derived data without destination/purpose-bound authorization.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-020.
- LAB-019: Issue #36 DONE; PR #37 merged as `678b104f85da55ceefc4eaebed50a2dee455c58c`.
- LAB-020: Issue #38 DONE; PR #39 remote-audited then manually integrated through supported GitHub Contents API because the normal merge endpoint was blocked before execution.
- LAB-020 integration commits: `6f3df493ae1927325b1e73d53d1b9e99c8490b31` through `18fe82363356f1ce2674651b1903079e7cedd818`.
- Next issue: #40 / LAB-021 sensitive-data taint propagation and egress sink gating — READY.
- Active branch: none yet for LAB-021.
- Active PR: none.

## Last completed step

LAB-020 researched current MCP, OpenAI, and OWASP prompt-injection/tool-security mechanisms and built a deterministic control/data authority kernel. A seeded unsafe design promoted tool-output fields into `send_secret/attacker.example`; the corrected kernel prevents external data from widening action authority, skipping escalation, replacing protected targets, or self-promoting claims into trusted evidence.

The first corrected draft exposed two audit defects before publication: trusted-control denials were not enforced and accepted evidence lacked artifact-version binding. Both were fixed and regression-tested. Corrected local suite: 12/12 passed; unsafe seed failed as intended; compileall passed. PR #39 was remote patch-audited. The normal merge operation was blocked before execution, so the exact audited five new paths were integrated through the supported Contents API and the PR was closed as manually integrated.

## Evidence produced

- `research/2026-08-19-versioned-kernel-migration.md`
- `experiments/versioned_kernel/` and LAB-019 PR #37 merge `678b104f85da55ceefc4eaebed50a2dee455c58c`.
- `research/2026-08-19-untrusted-tool-output-boundary.md`
- `experiments/untrusted_tool_output/`
- LAB-020 corrected suite: 12/12 passed.
- LAB-020 unsafe authority-promotion seed: failed as intended.
- Issue #40 / LAB-021 created as the next executable security/correctness gap.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- Preferred GitHub merge endpoint can be blocked before execution; audited small/file-scoped conflict-free changes may use the documented Contents API fallback.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.
- LAB-020 reduces prompt-injection blast radius; it does not solve model-level prompt injection or reasoning manipulation.

## Exact next action

Select Issue #40 / LAB-021. Research at least three current primary-source data-flow/egress/security-label mechanisms, create `lab/021-egress-taint`, implement a deterministic source→transform→sink policy prototype under `experiments/egress_taint/`, falsify one unsafe taint-loss design, run the required matrix, audit composition with evidence/fallback/escalation/LAB-020 authority boundaries, then integrate only after validation.

## Backlog

- #40 / LAB-021 — READY, highest-value executable task.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
