# Current Lab State

Last updated: 2026-08-20

## Active objective

Advance from one authenticated CT v2 SCT promise audit to a versioned policy over multiple independently authenticated SCTs/logs. LAB-044 and LAB-045 are complete: the lab now proves exact leaf inclusion under an authenticated STH, authenticates the corresponding SCT against the exact leaf bytes, and applies RFC-accurate MMD audit semantics without inventing non-membership evidence.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-045.
- Completed Issue #84 / LAB-044; PR #85 squash-merged as `4003739d2017d77773819a20418d4750e6f9e260`.
- Completed Issue #86 / LAB-045; PR #87 remote patch-audited and squash-merged as `814e12c553d046ac63de99dde476ee3eba1e7b97`.
- Active next: Issue #88 / LAB-046 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-045 implemented `experiments/ctv2_sct_promise/`: strict RFC 9162 SCT v2 parsing, exact SCT→leaf signature/type/timestamp/extensions binding, LAB-043 authenticated STH integration, LAB-044 exact inclusion integration, and a four-state MMD audit model.

The audit corrected a material interpretation error in the initial task framing: inclusion first observed under a post-MMD STH is not proof of late insertion. RFC 9162 explicitly audits SCTs against STHs dated after `SCT timestamp + MMD`. Likewise, lack of an inclusion proof is not a cryptographic non-membership proof. `MMD_VIOLATION` is emitted only when a complete authenticated post-deadline tree snapshot reconstructs the STH root and proves the exact promised leaf absent.

## Evidence produced

- `experiments/ctv2_sct_promise/protocol.py`
- `experiments/ctv2_sct_promise/tests/test_protocol.py`
- `experiments/ctv2_sct_promise/tests/unsafe_inclusion_only_expected_failure.py`
- `experiments/ctv2_sct_promise/README.md`
- `research/2026-08-20-ctv2-sct-promise.md`
- Corrected deterministic suite after audit: 19/19 passed.
- Unsafe inclusion-only seed: expected failure because it accepted an included artifact that the presented SCT never promised.
- `python -m compileall -q experiments/ctv2_sct_promise` passed.
- Exact branch `protocol.py` Git blob matched locally executed source: `7dbaea77ef02cae463b9379f8e0dfa6c007c5c1e`.
- Exact branch corrected `test_protocol.py` Git blob matched locally executed source: `ddde946ef2b9e51579d31f6b0c230c5a90e84e8c`.
- Exact branch unsafe seed Git blob matched locally executed source: `f278e1abef16f60417244db3684018e24310b144`.
- Primary provenance: RFC 9162 §§4, 4.7, 4.8, 4.10, 8.1, 11.3.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-045 is a deterministic Ed25519/SHA-256 reference profile layered on existing LAB-043/044 profile assumptions; general signature/hash agility remains external.
- A post-deadline STH alone cannot prove non-membership. Compact CT Merkle proofs are membership proofs; monitor-style complete-tree evidence is required here to prove absence.
- Browser/vendor CT compliance rules are intentionally not hard-coded; RFC 9162 leaves quantity/form of compliance evidence to local client policy.

## Exact next action

Start Issue #88 / LAB-046. Research RFC 9162 §§6.2–6.4, 8.1.1, 8.1.6, and 11.4. Build `experiments/ctv2_multi_sct_policy/` with an explicit versioned policy and evidence-binding model over independently authenticated LAB-045 per-log audits. Count distinct trusted LogIDs (and optionally distinct operator groups), never double-count duplicate SCTs, preserve `NOT_YET_AUDITABLE` / `INCONCLUSIVE_AFTER_DEADLINE` / `MMD_VIOLATION` separately from fulfillment, fail closed on stale policy/trust generations, and retain an unsafe seed showing duplicate/self-asserted evidence can falsely satisfy a threshold.

## Backlog

- #88 / LAB-046 — multi-SCT evidence aggregation and versioned compliance-policy conformance — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally out of scope unless later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
