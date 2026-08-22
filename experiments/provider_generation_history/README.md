# LAB-081 — provider generation history

This experiment separates two authorities that LAB-080 deliberately conflated:

- **current effect authority** — only the active provider generation may create new anchor effects;
- **historical verification authority** — prior authenticated generations may verify receipts they originally produced, but cannot create new effects.

The durable history stores content-addressed generation descriptors and old+new authenticated transition proofs. Signed historical receipt evidence is stored separately and remains bound to provider ID, generation, position and request identity.

Run:

```bash
python -m unittest experiments.provider_generation_history.tests.test_protocol -v
```

This is a single-provider lifecycle reference model. It is not provider consensus, cross-provider failover, HSM custody or a general PKI.
