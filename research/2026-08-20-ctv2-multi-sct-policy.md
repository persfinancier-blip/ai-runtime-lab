# LAB-046 — Multi-SCT evidence aggregation

## Primary-source findings

RFC 9162 §6.2 recommends SCTs from multiple logs because client trust lists are independent and change over time; discovery/trust/distrust of logs is explicitly out of scope. §6.3 provides a list container for independently decodable TransItems. §6.4 requires an SCT in each handshake TransItemList and recommends inclusion proofs/STHs when available. §8.1.6 explicitly delegates the quantity and form of evidence required for compliance to local client policy. §11.4 states that multiple SCTs from different logs reduce the effectiveness of CA+log collusion.

Primary source: https://www.rfc-editor.org/rfc/rfc9162.html

## Policy boundary

RFC 9162 does not define a universal numeric SCT threshold, operator-diversity threshold, browser compliance rule, or trust-list lifecycle. LAB-046 therefore models those as versioned local policy inputs rather than protocol truth.

## Reference decision model

- Policy is bound to `policy_generation` and `trust_generation`; stale evaluation fails closed.
- Only authenticated evidence for the expected leaf and current trusted LogID can count.
- Thresholds count distinct LogIDs, never rows/SCT duplicates.
- Optional operator diversity counts distinct operator identities among fulfilled trusted logs.
- `NOT_YET_AUDITABLE`, `INCONCLUSIVE_AFTER_DEADLINE`, and `MMD_VIOLATION` remain distinct outputs.
- Any authenticated MMD violation is surfaced as `VIOLATION` even when other logs satisfy the numeric threshold; aggregation must not erase log-misbehavior evidence.
- Unknown logs are reported/ignored for threshold purposes rather than promoted to trust by their own claims.
- Conflicting authoritative evidence for the same LogID fails closed.

## Experiment

Unsafe baseline counts two self-asserted duplicate `FULFILLED` rows from one LogID and falsely satisfies a threshold of two. Corrected deterministic suite: 13/13 passed. Unsafe seed: expected failure. `python -m compileall -q experiments/ctv2_multi_sct_policy`: passed.

## Limits

This experiment does not claim browser/vendor CT compliance, live TLS capture, trust-list distribution, operator-identity governance, or cryptographic replacement of LAB-045. The HMAC evidence authenticator is a deterministic stand-in for consuming LAB-045's already authenticated evidence identity/binding; authority must flow from that lower layer, not from the aggregation object.
