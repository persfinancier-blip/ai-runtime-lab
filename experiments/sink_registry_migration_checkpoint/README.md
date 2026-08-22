# LAB-078 — authenticated legacy migration checkpoint

The migration does **not** manufacture threshold proofs for LAB-076 legacy rows. It commits a threshold-authorized checkpoint over the exact legacy prefix and terminal authority/registry/capability/credential state. Legacy rows remain verification-only; post-checkpoint publication belongs exclusively to LAB-077.

Pending `INTENT`/`UNKNOWN` requests block migration in this reference slice so unresolved operations cannot silently inherit stronger post-migration authority. `CONFIRMED` rows remain receipt-only history.
