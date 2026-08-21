# LAB-074 — Transactional broker + authenticated sink-capability integration

## Question

Can LAB-072's durable request journal and LAB-073's authenticated retry contract become one authority boundary, so a persisted request cannot continue executing after its sink capability has changed while an already committed effect can still be reconciled without duplication?

## Integration decision

Do not create a second request state machine. LAB-074 migrates the existing LAB-072 `broker_requests` table in place and persists with each capability-bound reservation:

- sink identity;
- capability generation;
- exact authenticated claim digest;
- probe generation and issuer identity;
- original retry policy;
- idempotency-window creation time;
- the existing LAB-072 stable effect key.

The existing LAB-072 request digest, credential generation, `INTENT / UNKNOWN / CONFIRMED` status, effect key and receipt remain authoritative request state.

## Transition rules

### New reservation / INTENT execution

A new reservation requires a currently authenticated LAB-073 capability and a policy of either `SAFE_RETRY_RECONCILE` or `SAFE_RETRY_IDEMPOTENT_ONLY`. Before external execution, the worker requires the current capability to match the durable sink ID, capability generation, claim digest, probe generation and issuer. Retention is recomputed against the durable key-creation time; expiration can only reduce authority.

### UNKNOWN

With the exact same capability identity, `SAFE_RETRY_RECONCILE` may reconcile and, if the effect is absent and the current retention window still authorizes it, retry the same stable effect key. `SAFE_RETRY_IDEMPOTENT_ONLY` never performs an automatic second execution after UNKNOWN.

If capability generation has advanced after an UNKNOWN, new execution is forbidden. A trusted current capability for the same sink may only perform historical read-only reconciliation of the already durable effect key. If no committed receipt exists, the operation remains unresolved rather than being replayed under the new capability.

### CONFIRMED

A confirmed durable receipt is returned without a new sink operation. Later capability rotation cannot erase the fact that this effect already committed. Request-content substitution remains rejected by LAB-072 request digest binding.

## Failure matrix

The integration tests cover:

1. same-generation authenticated claim mutation after reservation;
2. capability-generation rotation after reservation;
3. timeout-after-commit followed by capability rotation and exact reconciliation;
4. idempotent-only UNKNOWN with no second execution;
5. retention expiration while INTENT is pending;
6. forged probe attestation before reservation;
7. concurrent workers sharing one capability-bound effect;
8. restart reconstruction of exact capability identity from SQL;
9. confirmed-result replay after capability rotation;
10. request-ID/content substitution;
11. corruption of durable capability digest.

The unsafe seed keeps LAB-072 request state but omits capability binding entirely; it demonstrates that durable idempotency alone does not authorize an external retry route.

## Audit finding fixed during implementation

The first integration draft authenticated the caller's current capability before reading an already `CONFIRMED` journal row. That accidentally allowed later capability rotation/revocation to suppress retrieval of a receipt that was already durable. The order was corrected: existing durable identity is read first; current capability authority is required only before new external work or UNKNOWN reconciliation.

## Boundaries / non-goals

- Sink retention duration is still provider/contract material and must be conservatively sourced; an unknown retention window must not be treated as infinite.
- Reconciliation semantics are sink-specific. A rotated capability can authorize only read-only lookup of the exact historical effect identity; it cannot authorize a second execution.
- This does not claim universal exactly-once external effects. The safety primitive remains stable identity + durable intent + observed idempotency/reconciliation capability + fail-closed UNKNOWN handling.
- LAB-072 credential-generation authority and LAB-073 sink-capability generation are separate dimensions and are both required for new execution.
