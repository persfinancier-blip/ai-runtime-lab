# LAB-099 — precursor cutover marker versioning addendum

Date: 2026-09-12
Status: SOURCE-PROVED ADDENDUM; exact RED/GREEN pending
Related: PR #177 / LAB-092, LAB-099/#184

## Source fact

PR #177 currently defines the LAB-092 migration evidence as:

```text
intent_id = migration:provider-generation-activation-schema:v1
component = provider-generation-activation-schema
payload = { schema: provider-generation-activation, version: 1 }
```

That immutable historical statement authenticates the LAB-090 activation table/trigger schema V1 only. It contains no precursor relation identity, precursor protocol version, DDL digest/set commitment, or V2 transition-provenance semantics.

## Decision

`LAB099_PRECURSOR_CUTOVER_MARKER_VERSIONING_V1_FROZEN`

Do not reinterpret an already-CONFIRMED LAB-092 V1 migration marker as proof that the later `provider_activation_reservations` relation was installed or governed.

The precursor relation requires a **new authenticated cutover event** (a new deterministic intent/domain/version, or a separately versioned schema-set event) whose canonical payload explicitly commits to precursor governance. The old LAB-092 V1 marker remains historical evidence for exactly what it originally authenticated.

Minimum semantic content of the new event:

```text
logical database/history identity
precursor schema/protocol version
provider-transition provenance protocol version it enables
exact predecessor cutover/head identity
exact schema-set identity or canonical DDL commitment
```

Exact encoding/name remains implementation-gated until executable REDs return; the rule is that the new event cannot borrow authority from the old marker by changing its interpretation in code.

## Migration composition

For a database with valid LAB-092 V1 activation-schema provenance but no precursor cutover:

- if it has no LAB-090 activation history requiring retroactive ticket provenance and authenticated history proves migration eligibility, it may run the new explicit precursor cutover;
- if LAB-090 activation rows/history already exist without independently authenticated precursor/V2 evidence, classify `LEGACY_LAB090_UNATTESTED` and fail closed; confirming LAB-092 V1 does not make those ticket bytes authentic.

After the new precursor cutover is CONFIRMED, missing/mismatched precursor DDL is provenance loss/tamper and ordinary startup must not recreate it.

## Minimum RED additions

1. LAB-092 V1 CONFIRMED + precursor relation absent + no new precursor cutover -> ordinary governed startup must not treat V1 as precursor proof.
2. Mutating software to reinterpret the V1 payload as covering precursor DDL must not make the DB migration-complete.
3. New precursor cutover PREPARED + exact DDL -> recoverable only through explicit migration/reconciliation.
4. New precursor cutover CONFIRMED + relation deletion/mismatch -> fail closed without auto-repair.
5. LAB-092 V1 CONFIRMED + historical LAB-090 activation rows + no new authenticated precursor/V2 evidence -> `LEGACY_LAB090_UNATTESTED`, not auto-upgradeable.

## Verdict

Historical migration events are immutable authority statements. New security-relevant DDL/protocol semantics require a new authenticated versioned cutover event, not reinterpretation of the LAB-092 V1 marker.
