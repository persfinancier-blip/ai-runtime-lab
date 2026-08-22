# LAB-084 — Provider rotation authority recovery

Break-glass recovery layer over LAB-083.

Normal LAB-083 authority rotation remains old-root threshold + new-root threshold. Break-glass recovery is authorized only by a separate recovery quorum bound to the exact predecessor authority and exact successor authority. Successful recovery advances authority version/generation, so the pre-recovery quorum cannot authorize new provider rotations.

`SupportedRecoveryThresholdProviderLedger` is the supported integration surface. It serializes normal authority rotation and recovery with unresolved LAB-080 PREPARED work under the same SQLite write-lock model. Restart verification accepts a mixed authority history only when every adjacent authority edge has exactly one valid proof type: a normal LAB-083 old+new quorum proof **or** a LAB-084 recovery-quorum proof. Historical provider threshold proofs remain bound to the exact authority generation that authorized them.

The lower-level `DurableRecoveryController` remains a reference primitive and is not a substitute for the supported surface.

Current recovery-authority generation is pinned to bootstrap. Recovery-authority lifecycle/rotation and asymmetric/HSM custody are separate follow-up work; if both normal authority and recovery quorum are lost or compromised, this experiment fails closed rather than recursively recovering itself.

Run focused tests:

```bash
python -m unittest experiments.provider_rotation_recovery.tests.test_protocol -v
python -m unittest experiments.provider_rotation_recovery.tests.test_supported_integration -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.provider_rotation_recovery.tests.unsafe_self_recovery_expected_failure -v
```
