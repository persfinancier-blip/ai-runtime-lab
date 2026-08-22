# LAB-078 — authenticated registry migration checkpoint

## Decision

Do not backfill synthetic threshold proofs onto historical LAB-076 single-signature registry rows. Instead create one current-threshold-authorized checkpoint that commits the exact legacy prefix, terminal authority identity/version/epoch, registry heads, capability heads, credential generation, confirmed-request identities and migration cutoff sequence.

This follows the same continuity principle used by TUF: a stronger/new trust state must be authenticated by the currently trusted threshold rather than inferred from the mere presence of old metadata. TUF root migration likewise requires threshold authorization and explicit version continuity rather than silent promotion.

## Pending effects

The first safe policy blocks migration while any `INTENT` or `UNKNOWN` broker request exists. This is deliberately conservative: unresolved work must be reconciled under pre-migration authority before the stronger publication boundary becomes active. `CONFIRMED` rows are historical receipt-only facts and may cross the migration.

## Integrated authority boundary

The migration ceremony is integrated directly over the existing LAB-076/LAB-077 SQLite authority and registry tables. Historical roots are loaded through the durable LAB-076 lifecycle; no second migration-owned authority store exists. Legacy registry rows remain verification-only. After the checkpoint, every new registry mapping must be represented by LAB-077 threshold publication history, and mixed-history verification rejects synthetic promotion of a legacy row.

The supported migration surface accepts only the exact final audited LAB-077 journal type. Both a fresh migration and an exact idempotent retry re-run mixed-history verification before reporting success, so retry cannot rely on SQL row equality while skipping checkpoint signatures or historical-root authentication.

## Failure boundaries exercised

The experiment covers one-signer rejection, pending `INTENT`/`UNKNOWN`, root rotation between preview and commit, legacy-prefix substitution, synthetic threshold promotion, transaction abort during checkpoint insert, restart after the first threshold successor, and durable historical-authority corruption on idempotent retry. The unsafe baseline demonstrates that copying legacy rows into threshold-proof storage manufactures authority.

## Boundary

The checkpoint proves the local migration state it signs. It does not make whole-store rollback impossible; freshness/rollback remains delegated to LAB-034–037 external monotonic-anchor work. Full completion still requires exact-source execution of the current published HEAD plus merged LAB-077/076/075 regressions and one final post-execution patch audit.
