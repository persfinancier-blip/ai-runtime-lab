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

A durable `sink_capability_heads` watermark records the latest authenticated capability identity observed per sink. The existing LAB-072 request digest, credential generation, `INTENT / UNKNOWN / CONFIRMED` status, effect key and receipt remain authoritative request state.

## Transition rules

### New reservation / INTENT execution

A new reservation requires a currently authenticated LAB-073 capability and a policy of either `SAFE_RETRY_RECONCILE` or `SAFE_RETRY_IDEMPOTENT_ONLY`. Before request INSERT the capability head is rechecked inside the same SQL write transaction, closing the observe→reserve race. Before external execution, the worker also requires the configured sink adapter identity to match the durable sink ID and the exact capability generation, claim digest, probe generation and issuer. Retention is recomputed against the durable key-creation time; expiration can only reduce authority.

### UNKNOWN

With the exact same capability identity, `SAFE_RETRY_RECONCILE` may reconcile and, if the effect is absent and the current retention window still authorizes it, retry the same stable effect key. `SAFE_RETRY_IDEMPOTENT_ONLY` never performs an automatic second execution after UNKNOWN.

If capability generation has advanced after an UNKNOWN, new execution is forbidden. A trusted current capability for the same sink may only perform historical read-only reconciliation of the already durable effect key, and only if the current capability still authenticates reconciliation support. If no committed receipt exists, the operation remains unresolved rather than being replayed under the new capability.

### CONFIRMED

A confirmed durable receipt is returned before requiring current execution authority and without a new sink operation. Later capability rotation cannot erase the fact that this effect already committed. Request-content substitution remains rejected by LAB-072 request digest binding.

## Failure matrix

The exact integration tests cover:

1. same-generation authenticated claim mutation after reservation;
2. capability-generation rotation after reservation;
3. timeout-after-commit followed by capability rotation and exact reconciliation;
4. idempotent-only UNKNOWN with no second execution;
5. retention expiration while INTENT is pending;
6. forged probe attestation before reservation;
7. concurrent workers sharing one capability-bound effect;
8. restart reconstruction of exact capability identity from SQL;
9. confirmed-result replay after capability rotation;
10. configured sink identity substitution;
11. request-ID/content substitution;
12. corrupt durable capability digest;
13. signed capability-generation rollback;
14. same-generation capability-head substitution;
15. observe→INSERT capability-head race;
16. request capability ahead of durable sink head;
17. rotation to a capability that no longer authenticates reconciliation.

The unsafe seed keeps LAB-072 request state but omits capability binding entirely; it demonstrates that durable idempotency alone does not authorize an external retry route.

## Audit findings fixed before integration

1. Current capability was checked before returning an already `CONFIRMED` durable receipt. Ordering was corrected so historical durable fact remains readable without new execution authority.
2. Capability `sink_id` was not bound to the configured external adapter. The worker now has an explicit sink identity boundary before apply/reconcile.
3. Old but still correctly signed capability generations could be replayed. A durable monotonic `sink_capability_heads` watermark now rejects rollback and same-generation substitution across restart.
4. Capability head could rotate between observation and request INSERT. The exact head is rechecked under the final SQL write transaction.
5. Durable verification originally validated request and head tables independently. It now checks request-plan ↔ capability-head relationships.
6. Rotated UNKNOWN could still probe a sink whose current capability no longer authenticated reconciliation. That route now fails closed.

## Exact-source validation

Final published executable bytes were reconstructed through the GitHub connector and verified locally by Git object identity:

- PR `capability.py`: `0cfe0e2e555a234df96393abdf3e14b75ccff2f6`;
- PR integration tests: `d6f003b07484775e62e8da93b3574f8eb484ea7e`;
- PR unsafe seed: `4c5aef361082cfe8c6feaea97df5bc3cf31a3ee3`;
- main LAB-072 protocol/tests: `6817459fca8ac37c11cce71865937b8f65567d83` / `656284062a96b7915e3283b181c58bd7a8e9281d`;
- main LAB-073 protocol/tests: `fc05d27d5512ece585d7d6313e079ae6a234f737` / `55e42d5027fbbe1c7b66b11f08162765eba90a25`.

Observed exact-source execution: **49/49 tests passed** across LAB-074 integration + LAB-072 + LAB-073; `python -m compileall -q experiments` passed. The exact unsafe split-authority seed failed as intended with one external side effect where zero was expected.

## Boundaries / non-goals

- Sink retention duration is still provider/contract material and must be conservatively sourced; an unknown retention window must not be treated as infinite.
- Mapping a configured `sink_id` to a concrete production adapter/code/endpoint remains a trusted boundary not cryptographically solved by LAB-074.
- Reconciliation semantics are sink-specific. A rotated capability can authorize only read-only lookup of the exact historical effect identity; it cannot authorize a second execution.
- This does not claim universal exactly-once external effects. The safety primitive remains stable identity + durable intent + observed idempotency/reconciliation capability + fail-closed UNKNOWN handling.
- LAB-072 credential-generation authority and LAB-073 sink-capability generation are separate dimensions and are both required for new execution.
