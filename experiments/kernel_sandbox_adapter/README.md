# Kernel sandbox adapter reference

LAB-029 reference model for binding requested sandbox dimensions to **observed** OS/process enforcement capabilities.

Run corrected tests:

```bash
python -m unittest discover -s experiments/kernel_sandbox_adapter/tests -p 'test_*.py' -v
```

Run the retained unsafe seed separately; it is expected to fail:

```bash
python -m unittest experiments.kernel_sandbox_adapter.tests.unsafe_seed_expected_failure -v
```

The adapter fails closed for REQUIRED dimensions when no fresh observed backend exists. `POLICY_ONLY` is allowed only for AUDIT dimensions of explicitly non-security-critical tasks. `validate_launch()` rechecks plan bindings, capability report generation/digest, sandbox generation, and credential generation at the launch boundary.

`probe.py` is a Linux probe for this experiment. It does not claim that all reported primitives compose into a complete sandbox; each capability is dimension-specific.
