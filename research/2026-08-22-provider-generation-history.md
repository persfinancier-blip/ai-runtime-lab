# LAB-081 — Historical provider-generation continuity

## Problem

LAB-080 correctly fails closed after an anchor-provider generation rotates because LAB-036 verifies only the configured current `(provider_id, generation, key)`. That protects new-effect authority, but also makes retained receipts from an old generation unverifiable.

The missing abstraction is a split between **effect authority** and **historical verification authority**.

## Donor mechanism

The Update Framework root-update workflow provides the relevant continuity pattern: clients retain an authenticated chain of versioned trust roots; root `N+1` must be authorized by the trusted old root and the new root, and rollback to an older root is rejected. The transferable mechanism here is not software-update metadata itself, but explicit, persisted trust-generation continuity instead of accepting caller-supplied historical keys.

Primary source: https://theupdateframework.github.io/specification/latest/

## Reference protocol

For one logical provider:

1. bootstrap one pinned generation descriptor;
2. each successor is exactly generation `N+1` for the same provider ID;
3. transition identity commits exact old/new generation IDs;
4. both old and new key material authenticate the transition in the reference model;
5. the durable head identifies the sole generation allowed to authorize new effects;
6. old descriptors remain available only to verify signed receipts already bound to their exact generation;
7. every persisted historical receipt binds provider ID, generation, position and request ID.

Rotation is blocked while shared-anchor work is PREPARED so an effect cannot cross the authority boundary half-executed.

## First experiment result

The isolated corrected suite passed 12/12 tests and compileall passed. Covered cases include historical verification after rotation, old-generation effect rejection, same-generation substitution, provider substitution, PREPARED rotation blocking, restart rollback, missing/corrupt transition proofs, forged historical key material and receipt request/position rebinding.

An unsafe caller-supplied historical-key baseline demonstrates the core failure: a receipt and attacker-selected key can self-consistently verify without proving that the key was ever part of the authenticated provider lifecycle.

## Remaining integration gate

This first slice is not yet sufficient to close LAB-081. It must be wired into the exact merged LAB-080 ledger so the signed provider receipt is durably captured at confirmation and mixed old/new CONFIRMED history can be reverified after rotation without rewriting old receipt bindings. Exact-source LAB-081 + LAB-080 + LAB-036 regressions remain mandatory.

## Non-goals

No provider consensus, cross-provider failover, HSM key custody, certificate PKI, or compromise-recovery ceremony is claimed here.
