# Current Lab State

Last updated: 2026-08-20

## Active objective

Advance from LAB-046's correct multi-SCT local-policy aggregation to an authenticated trust-list lifecycle so LogID trust, operator diversity, distrust, and freshness are not caller-self-asserted.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-046.
- Completed Issue #88 / LAB-046; PR #89 remote patch-audited and squash-merged as `92d50dcc9ede4a1888ed46598de9a62b2adb9f5d`.
- Active next: Issue #90 / LAB-047 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-046 implemented `experiments/ctv2_multi_sct_policy/`: versioned policy/trust-generation binding, distinct trusted LogID counting, optional distinct operator-group threshold, explicit pending/inconclusive/violation outputs, duplicate suppression, unknown-log exclusion, and authenticated evidence/leaf binding. RFC 9162's protocol/local-policy boundary is documented rather than replaced with browser/vendor policy.

## Evidence produced

- `experiments/ctv2_multi_sct_policy/protocol.py`
- `experiments/ctv2_multi_sct_policy/tests/test_protocol.py`
- `experiments/ctv2_multi_sct_policy/tests/unsafe_duplicate_expected_failure.py`
- `experiments/ctv2_multi_sct_policy/README.md`
- `research/2026-08-20-ctv2-multi-sct-policy.md`
- Corrected deterministic suite: 13/13 passed.
- Unsafe duplicate/self-asserted baseline: expected failure because one LogID was counted twice.
- `python -m compileall -q experiments/ctv2_multi_sct_policy` passed.
- Exact branch protocol blob matched locally executed source: `782779ebe3428ae184408c6f0e2d1006fa369ad1`.
- Exact branch corrected tests blob matched locally executed source: `40778d47f9f8ba4529555a368e709bf40e9ba51c`.
- Primary provenance: RFC 9162 §§6.2–6.4, 8.1.6, 11.4.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-046 does not claim browser/vendor CT compliance; RFC 9162 leaves quantity/form of compliance evidence to local policy.
- LAB-046's HMAC is a deterministic stand-in for the already authenticated LAB-045 evidence boundary, not a replacement cryptographic authority.
- `trusted_logs` and `operator_id` are still caller-supplied reference inputs; this is the exact authority gap LAB-047 must close.

## Exact next action

Start Issue #90 / LAB-047. Research RFC 9162 §4.1/§6.2 plus current primary-source authenticated CT log-list/trust-distribution mechanisms. Build `experiments/ctv2_log_trust_lifecycle/` so an authenticated exact snapshot binds LogID -> verification profile -> operator group -> lifecycle state. Prove rollback/substitution/self-promotion/post-distrust counting fail closed, historical evidence remains attributable, and LAB-046-style evaluation binds to exact snapshot identity rather than trusting caller-supplied operator metadata.

## Backlog

- #90 / LAB-047 — authenticated CT log-list lifecycle and operator-identity binding — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally out of scope unless later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
