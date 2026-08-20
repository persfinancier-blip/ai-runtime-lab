# LAB-060 — Authenticated History Checkpoints

This experiment layers authenticated prefix checkpoints over LAB-059's full bootstrap-to-head verifier.

A checkpoint is created only while a write-excluding transaction is held and after LAB-059 has fully verified the current prefix. It binds strict schema/protocol versions, bootstrap-derived history identity, verified sequence and root/recovery content IDs, a deterministic rolling prefix commitment, external monotonic-anchor identity, and a pinned checkpoint signer identity.

On restart, the latest locally monotonic checkpoint is authenticated and its O(1) authority IDs are reloaded by content ID. Only transitions after the checkpoint are re-verified using the same LAB-059 threshold rules.

Run:

```bash
python -m unittest experiments.transition_history_checkpoints.tests.test_protocol -v
python -m compileall -q experiments/transition_history_checkpoints
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.transition_history_checkpoints.tests.unsafe_cache_expected_failure -v
```

## Security boundary

The local `checkpoint_watermark` rejects an older checkpoint while the current database state is intact. If an attacker rolls back the entire database, including checkpoint rows and watermark, this layer cannot establish freshness by itself. LAB-034–037 external monotonic-anchor mechanisms remain authoritative for that problem.

The HMAC signer is a deterministic reference authenticity primitive, not a claim that a local symmetric key is the desired production trust architecture.

For periodic/forensic verification of archived prefix bytes, `audit_checkpoint_prefix()` recomputes the O(N) commitment explicitly. This work is not performed on the normal O(suffix) restart path.
