# LAB-078 — authenticated registry migration checkpoint

## Decision

Do not backfill synthetic threshold proofs onto historical LAB-076 single-signature registry rows. Instead create one current-threshold-authorized checkpoint that commits the exact legacy prefix, terminal authority identity/version/epoch, registry heads, capability heads, credential generation, confirmed-request identities and migration cutoff sequence.

This follows the same continuity principle used by TUF: a stronger/new trust state must be authenticated by the currently trusted threshold rather than inferred from the mere presence of old metadata. TUF root migration likewise requires threshold authorization and explicit version continuity rather than silent promotion.

## Pending effects

The first safe reference policy blocks migration while any `INTENT` or `UNKNOWN` broker request exists. This is deliberately conservative: unresolved work must be reconciled under pre-migration authority before the stronger publication boundary becomes active. `CONFIRMED` rows are historical receipt-only facts and may cross the migration.

## Boundary

The checkpoint proves the local migration state it signs. Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic-anchor work. The current prototype proves the ceremony and unsafe baseline; direct integration with the real LAB-076/077 supported journal surface remains required before completion.
