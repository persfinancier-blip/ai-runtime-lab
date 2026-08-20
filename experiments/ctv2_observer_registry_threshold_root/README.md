# LAB-056 observer-registry threshold root

Reference implementation of threshold-authenticated root authority for the LAB-055 observer registry.

Normal root rotation requires both predecessor-root and successor-root threshold authorization. Break-glass recovery is a separate quorum and advances `authority_epoch`. Registry snapshots bind exact `root_id`, `root_version`, and `authority_epoch`; new snapshots may only be signed by the current root. Historical evidence keeps exact historical root+registry identities.

Run:

```bash
python -m unittest experiments.ctv2_observer_registry_threshold_root.tests.test_protocol -v
python -m compileall -q experiments/ctv2_observer_registry_threshold_root
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.ctv2_observer_registry_threshold_root.tests.unsafe_single_signer_expected_failure -v
```

This is a reference authority/state protocol, not HSM/PKI implementation, consensus, gossip transport, or secret-key custody system.
