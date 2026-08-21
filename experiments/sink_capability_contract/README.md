# LAB-073 sink capability contract

Retry and UNKNOWN behavior is derived from observed/behaviorally verified sink capabilities, not adapter self-description.

Corrected suite:

```bash
python -m unittest experiments.sink_capability_contract.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.sink_capability_contract.tests.unsafe_generic_retry_expected_failure -v
```
