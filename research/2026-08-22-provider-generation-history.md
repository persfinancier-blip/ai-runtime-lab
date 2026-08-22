# LAB-081 — Historical provider-generation continuity

## Problem

LAB-080 correctly fails closed after an anchor-provider generation rotates because LAB-036 verifies only the configured current `(provider_id, generation, key)`. That protects new-effect authority, but also makes retained receipts from an old generation unverifiable.

The missing abstraction is a split between **effect authority** and **historical verification authority**.

## Donor mechanism

The Update Framework root-update workflow provides the relevant continuity pattern: clients retain an authenticated chain of versioned trust roots; root `N+1` must be authorized by the trusted old root and the new root, and rollback to an older root is rejected. The transferable mechanism here is explicit, persisted trust-generation continuity rather than accepting caller-supplied historical keys.

Primary source: https://theupdateframework.github.io/specification/latest/

## Integrated reference protocol

For one logical provider:

1. bootstrap one pinned generation descriptor;
2. each successor is exactly generation `N+1` for the same provider ID;
3. transition identity commits exact old/new generation IDs and is authenticated by both generations in the reference model;
4. the durable head identifies the sole generation allowed to authorize new effects;
5. old descriptors remain historical-verification material only through the supported execution surface;
6. every confirmed LAB-080 ledger row stores immutable signed receipt evidence bound to provider ID, generation, position and request ID;
7. the stable receipt identity excludes the fresh reconciliation challenge, so later authenticated checks do not rewrite historical evidence;
8. reservation and provider rotation serialize in the same LAB-080 SQLite database; provider rotation is blocked while any intent is `PREPARED`;
9. restart verification checks provider history, receipts, ledger rows and component watermarks in one consistent SQL read transaction;
10. direct standalone rotation on the integrated history object is blocked so callers cannot bypass the coordinator.

## Audit findings fixed before integration

- **PREPARED/rotation TOCTOU:** checking pending work outside the rotation transaction allowed a reservation to race the head update. Fixed by one `BEGIN IMMEDIATE` boundary shared with LAB-080.
- **Mixed SQL snapshots:** the first restart verifier read ledger rows and provider/receipt state through different connections. Fixed by transaction-internal provider/receipt verification helpers used from one read snapshot.
- **Challenge-dependent receipt overwrite:** LAB-036 reconciliation signs a fresh challenge. Treating each fresh observation as replacement evidence made a valid repeated verification look like substitution. Fixed by keeping the first exact signed observation immutable and separating stable receipt identity from freshness checks.
- **Direct rotation bypass:** exposing inherited standalone `provider_history.rotate()` let a caller supply `pending_prepared=0` and skip the shared transaction. The supported integrated history now permits authority mutation only through `rotate_provider()`.
- **Integrated persisted-binding omission:** restart recomputed a historical receipt binding but initially ignored the separately persisted `stable_binding` column. The integrated loader now requires stored and recomputed bindings to match exactly.
- **Standalone persisted-binding omission:** the low-level `DurableProviderHistory` had the same weakness and did not audit historical receipts on restart. Standalone restart/load now reverify every receipt signature and exact persisted binding.

## Security boundary

The reference implementation currently uses HMAC material to model authenticated generations because LAB-036 uses HMAC observations. Therefore “verification-only historical generation” is an execution-policy property of the supported surface, **not** a production key-custody claim: stored symmetric material is not cryptographically incapable of signing. A production design should keep historical verification material public-only (for example asymmetric signatures) and keep signing keys outside the durable verification store.

The local SQL commit is also not atomic with an external provider's own key-rotation ceremony. The integration fail-closes on provider-position mismatch and stale runtime generations, but distributed provider/DB rotation atomicity is a separate problem.

## Validation state

The final executable PR-head files and exact merged LAB-080/LAB-036 dependencies were reconstructed through the GitHub connector and verified against their Git blob identities before execution.

Observed final gate:

- 50/50 normal tests passed across LAB-081, LAB-080, and LAB-036;
- LAB-081 standalone persisted-binding corruption regression passed;
- `python -m compileall -q experiments` passed;
- LAB-080 unsafe monotonic-only baseline failed as expected because it trusted an unrelated higher position;
- LAB-036 unsafe unauthenticated-read baseline failed as expected because it trusted an unauthenticated claimed position;
- a fresh remote patch audit found no unresolved code-path defect after the persisted-binding fixes.

## Non-goals

No provider consensus, cross-provider failover, HSM custody, certificate PKI, or compromise-recovery ceremony is claimed here.
