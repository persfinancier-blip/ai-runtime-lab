# Untrusted Tool-Output Boundary Prototype

LAB-020 reference kernel for separating control-plane authority from untrusted external data.

## Rule

External content may contribute facts or evidence candidates, but it cannot authorize a new action, widen permissions, suppress escalation, replace a protected target, or promote its own claims into trusted evidence.

Authority requires all three:

1. an explicitly control-classified envelope;
2. a trusted source;
3. an explicitly declared `control` channel.

Even trusted control may narrow existing authority but does not silently widen the user's allowed action set.

## Run

```bash
python -m unittest discover -s experiments/untrusted_tool_output/tests -p 'test_*.py' -v
```

The unsafe regression seed is intentionally outside passing discovery:

```bash
python -m unittest experiments.untrusted_tool_output.tests.unsafe_seed_expected_failure
```

It is expected to fail because the unsafe agent lets tool-output fields overwrite the authorized action and target.

## Non-goals

This kernel does not claim to detect every prompt injection, sanitize arbitrary natural language, or make the model immune to adversarial content. It reduces blast radius by ensuring that model-visible external content cannot independently cross protected action/evidence/escalation boundaries.
