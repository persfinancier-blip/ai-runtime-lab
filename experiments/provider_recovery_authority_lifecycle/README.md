# LAB-085 — recovery-authority lifecycle reference slice

This first slice adapts the previously proven LAB-057 rule to the provider-rotation recovery domain:

`old recovery quorum + new recovery quorum + current normal/root quorum`

must authorize the same canonical recovery-authority transition.

The durable reference store preserves historical recovery authorities and the exact co-authorizing root material needed to reverify transitions after restart. An old recovery generation remains verification material but cannot authorize the next recovery-authority successor.

**Important boundary:** `DurableRecoveryAuthorityLifecycle.rotate(..., root=...)` is a reference primitive. It verifies the supplied root quorum but does not itself prove that the caller supplied the current LAB-083 root. The supported LAB-085 integration must obtain that root from LAB-084/LAB-083 inside the same SQL transaction and must serialize recovery-authority rotation with normal authority rotation, provider rotation, and break-glass recovery.

Run:

```bash
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.provider_recovery_authority_lifecycle.tests.unsafe_self_swap_expected_failure -v
```
