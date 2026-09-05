# LAB-086 — public-custody history guard before consequential writes

## Finding

The LAB-086 final writer previously re-verified the lower LAB-080/LAB-082 committed history and the LAB-086 root/public-window semantics before each consequential mutation, but it did **not** re-run the LAB-085 `AsymmetricRecoveryCustody.verify_durable()` history verifier.

Those are different proof layers. LAB-086 `provider_asymmetric_recovery_public_root_proofs` prove that the current normal/root quorum co-authorized a public-recovery successor. LAB-085 `provider_recovery_public_transitions` separately contain the Ed25519 old-public/new-public quorum signatures that authorize the public-recovery transition itself.

A stored public-recovery transition could therefore have corrupted `old_signatures_json`/`new_signatures_json` while its LAB-086 root-coauthorization row remained structurally and cryptographically valid. A later normal-root/provider/public-recovery/asymmetric-recovery writer could pass the previous LAB-086 pre-check and commit a new successor. Only a later full restart verifier would detect the damaged LAB-085 public-custody history. That is a persistent fail-closed availability/correctness defect.

## Fix

The common final-writer pre-verification helper now performs both:

1. `SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable(ledger)`; and
2. `ledger.public_recovery_custody.verify_durable()`.

The caller already holds `BEGIN IMMEDIATE` on the authoritative database, so no concurrent writer can change either committed history while these read-only verifiers execute on their own connections.

All four consequential final-writer paths use this common helper before mutation. The final `verify_durable()` path uses the same composition.

## Regression

`test_public_custody_history_guard.py`:

1. creates and migrates a real LAB-086 ledger;
2. performs a valid post-cutoff public-recovery rotation;
3. corrupts only `provider_recovery_public_transitions.old_signatures_json`, leaving the LAB-086 root-coauthorization proof intact;
4. attempts a valid normal-root rotation; and
5. requires the operation to fail with root head, authority count, and normal-transition count unchanged.

The regression still needs to run inside the full connector-reconstructed LAB-080→086 dependency closure before PR #165 can leave draft.
