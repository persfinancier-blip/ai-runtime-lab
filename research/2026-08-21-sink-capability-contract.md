# LAB-073 — Sink idempotency/reconciliation capability contract

## Primary-source mechanisms

AWS Well-Architected recommends stable idempotency tokens for mutating requests and requires duplicate requests with the same token to avoid repeated effects. AWS APIs such as EC2 additionally reject token reuse with changed request parameters. AWS Durable Execution guidance stresses that a replay must reuse the same idempotency key; generating a different key defeats deduplication. Google Cloud retry guidance distinguishes idempotent from non-idempotent targets instead of applying a universal retry policy.

## Decision

LAB-072 must not assume every sink inherits its strong `UNKNOWN -> reconcile -> no duplicate` semantics. A sink capability record is versioned by generation and accepted only after an observed behavioral probe. Self-description from an adapter/tool cannot upgrade retry authority.

Reference policies:
- `SAFE_RETRY_RECONCILE`: stable request-bound idempotency plus durable lookup/reconciliation.
- `SAFE_RETRY_IDEMPOTENT_ONLY`: stable request-bound idempotency inside a known-valid retention window, but no generic resolution of an already-UNKNOWN outcome.
- `NO_AUTOMATIC_RETRY`: non-idempotent, unbound, expired, unobserved, or failed-probe sink.
- `READ_ONLY`: no mutating effect.

Plan generation is part of the authority boundary. A later stronger capability observation cannot silently upgrade an already-issued plan; capability generation changes invalidate it.

## Boundary

This does not provide universal exactly-once delivery. External systems with no stable idempotency identity or no reconciliation path remain fundamentally ambiguous after timeout-after-commit; the correct generic behavior is fail closed rather than inventing a retry.
