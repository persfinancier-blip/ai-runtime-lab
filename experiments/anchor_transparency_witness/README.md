# Anchor Transparency Witness Reference

LAB-040 reference implementation.

The harness separates three guarantees:

1. **Local append-only consistency** — a checkpoint must extend the witness's last accepted checkpoint.
2. **Witness agreement** — clients may require signatures from distinct witness identities over the same checkpoint identity.
3. **Consensus/prevention** — intentionally not implemented. An isolated malicious operator can maintain separate forks until evidence crosses trust domains; this harness detects equivocation after observation/gossip, it does not prevent it.

The reference consistency proof carries appended leaves so the verifier can reconstruct the new Merkle root deterministically. Production RFC 9162 uses compact Merkle consistency proofs; the reference favors inspectability over proof compactness.

Run corrected suite:

```bash
python -m unittest discover -s experiments/anchor_transparency_witness/tests -p 'test_*.py' -v
```

Unsafe baseline (expected failure):

```bash
python -m unittest experiments.anchor_transparency_witness.tests.unsafe_self_presented_expected_failure -v
```
