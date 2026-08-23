# LAB-085 — recovery-authority lifecycle and asymmetric custody

The lifecycle rule is:

`old recovery quorum + new recovery quorum + current normal/root quorum`

must authorize one canonical recovery-authority transition. The supported LAB-085 integration obtains the current normal/root authority from LAB-083 inside the same SQLite transaction, serializes recovery-authority rotation with unresolved LAB-080 work, and advances the LAB-084 recovery head atomically.

## Asymmetric custody slice

`asymmetric_custody.py` adds a deliberately separate Ed25519 verification history. Runtime `RecoverySigner` objects hold private signing capability; SQLite stores only public Ed25519 keys, threshold signatures, transition identities, and the public authority head. After rotation, historical public keys remain sufficient to reverify old lifecycle proofs but are not themselves capable of producing new signatures.

This models the security boundary used by asymmetric KMS/HSM systems: private signing capability remains inside the signing boundary while public verification material can be distributed and retained. AWS KMS documents that the private half of an asymmetric KMS key does not leave KMS unencrypted and that signatures may be verified with the public key outside KMS; Google Cloud KMS likewise separates asymmetric signing from public-key validation.

Primary donors:

- RFC 8032 (Ed25519): https://www.rfc-editor.org/rfc/rfc8032
- AWS KMS Sign / GetPublicKey: https://docs.aws.amazon.com/kms/latest/APIReference/API_Sign.html and https://docs.aws.amazon.com/kms/latest/APIReference/API_GetPublicKey.html
- Google Cloud KMS asymmetric signatures: https://cloud.google.com/kms/docs/create-validate-signatures

Run the custody slice:

```bash
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_asymmetric_custody -v
```

Run the existing lifecycle and supported integration:

```bash
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_protocol -v
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_supported_integration -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.unsafe_self_swap_expected_failure -v
```

## Explicit boundary / remaining acceptance gap

The asymmetric custody slice is **not yet the authoritative supported recovery head**. LAB-085 still has two things to prove before DONE:

1. bind the public-only recovery authority generation to the exact LAB-084/LAB-085 recovery head and rotate both in the same SQL transaction; and
2. distinguish lifecycle verification from historical LAB-084 break-glass proof verification. Existing LAB-084 recovery proofs are HMAC-based and therefore still need historical symmetric material. They must not be described as public-only until a later migration converts that proof path to asymmetric signatures (or an HSM/KMS verification record).

If normal/root authorization and recovery-lifecycle authorization are both unavailable or compromised, fail closed and require an external bootstrap ceremony; there is no recursive self-recovery.
