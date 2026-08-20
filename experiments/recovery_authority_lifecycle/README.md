# Recovery authority lifecycle

Planned recovery-quorum rotation requires old-recovery threshold + new-recovery threshold + current-root threshold over the same transition. Root break-glass recovery is bound to the exact current recovery authority identity/version/generation.

If both root and recovery quorums are unavailable or compromised, there is deliberately no recursive in-band recovery path: an external bootstrap/ceremony is required.

Corrected suite:

```bash
python -m unittest experiments.recovery_authority_lifecycle.tests.test_protocol -v
```

Unsafe self-authorized swap seed (expected failure):

```bash
python -m unittest experiments.recovery_authority_lifecycle.tests.unsafe_self_swap_expected_failure -v
```
