# LAB-084 — Provider rotation authority recovery

Reference break-glass recovery layer over LAB-083.

Normal LAB-083 authority rotation remains old-root threshold + new-root threshold. Break-glass recovery is authorized only by a separate recovery quorum bound to the exact predecessor authority and exact successor authority. Successful recovery advances authority version/generation, so old provider-rotation quorum proofs are stale.

This first slice is intentionally **not yet the final supported surface**: LAB-083's current durable verifier recognizes only normal authority rotations. The next integration step must make restart verification understand a mixed normal/recovery authority history and must serialize recovery with PREPARED LAB-080 work.

Run:

```bash
python -m unittest experiments.provider_rotation_recovery.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.provider_rotation_recovery.tests.unsafe_self_recovery_expected_failure -v
```
