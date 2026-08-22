# Threshold-authorized sink registry publication (LAB-077)

LAB-076 protects authority rotation/recovery with threshold continuity, but its compatibility publication format still permits one active root key to sign one new registry entry. LAB-077 isolates the missing publication threshold.

A threshold publication uses one canonical `RegistryEntry.unsigned` payload bound to the exact authority content ID/version. Distinct active signers sign those same bytes. The entry's `signature` field stores the canonical threshold-proof digest; the full signer set is kept as historical proof and reverified on reload.

Run corrected prototype:

```bash
python -m unittest experiments.sink_registry_threshold_publication.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.sink_registry_threshold_publication.tests.unsafe_single_signer_expected_failure -v
```

Current slice is intentionally isolated. It proves signature-set semantics and historical proof integrity. Direct atomic integration with the LAB-076 supported journal is the next required gate; this README does not claim that the existing LAB-076 single-signature publication path has already been removed.
