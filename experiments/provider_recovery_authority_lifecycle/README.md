# LAB-085 — recovery-authority lifecycle and asymmetric custody

The lifecycle rule is:

`old recovery quorum + new recovery quorum + current normal/root quorum`

must authorize one canonical recovery-authority transition. The supported LAB-085 integration obtains the current normal/root authority from LAB-083 inside the same SQLite transaction, serializes recovery-authority rotation with unresolved LAB-080 work, and advances the LAB-084 recovery head atomically.

## Asymmetric custody

`asymmetric_custody.py` provides an Ed25519 verification history. Runtime `RecoverySigner` objects hold private signing capability; SQLite stores only public Ed25519 keys, accepted threshold signatures, transition identities, and the public authority head. Historical public keys therefore remain useful for verification after rotation without themselves being signing capability.

`public_custody_supported.py` binds that public history to the compatibility LAB-085/LAB-084 recovery lifecycle. A supported rotation advances all of the following inside one `BEGIN IMMEDIATE` transaction:

1. the symmetric LAB-085 lifecycle head and its current-root-authorized transition;
2. the LAB-084 recovery head used by existing break-glass history;
3. the public Ed25519 custody head and its old+new public quorum proof; and
4. an exact `(symmetric authority ID, public authority ID, version, generation)` binding row.

The supported surface rejects a plain symmetric-only recovery-authority rotation once public custody is enabled. Restart verification checks one-to-one history cardinality, exact metadata continuity, predecessor continuity, equality of the co-authorizing root identity for each paired transition, and current-head binding.

`final_supported.py` is the final supported LAB-085 surface. It holds a write-excluding SQLite transaction across symmetric-history verification, public-history verification, and the final binding check so a concurrent writer cannot make those passes observe different authoritative snapshots.

## Security boundary

This models the custody split used by asymmetric KMS/HSM systems: private signing capability remains inside the signing boundary while public verification material can be distributed and retained.

Primary donors:

- RFC 8032 (Ed25519): https://www.rfc-editor.org/rfc/rfc8032
- AWS KMS Sign / GetPublicKey: https://docs.aws.amazon.com/kms/latest/APIReference/API_Sign.html and https://docs.aws.amazon.com/kms/latest/APIReference/API_GetPublicKey.html
- Google Cloud KMS asymmetric signatures: https://cloud.google.com/kms/docs/create-validate-signatures

Run the LAB-085 suites:

```bash
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_protocol -v
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_supported_integration -v
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_asymmetric_custody -v
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported -v
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_final_supported -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.unsafe_self_swap_expected_failure -v
```

## Explicit remaining boundary

The lifecycle/custody path is public-key-verifiable, but historical LAB-084 **break-glass proofs are still HMAC-based** and therefore still need historical symmetric verification material. They must not be described as public-only. Issue #163 / LAB-086 tracks the authenticated migration of that historical proof path to asymmetric/HSM-KMS-compatible verification.

If normal/root authorization and recovery-lifecycle authorization are both unavailable or compromised, fail closed and require an external bootstrap ceremony; there is no recursive self-recovery.
