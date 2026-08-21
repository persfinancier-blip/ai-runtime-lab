# LAB-071 brokered credential use

Linux reference prototype for operation-time revocation without handing raw credential bytes to the target.

The broker owns the secret and receives requests through an `AF_UNIX` datagram socket with `SO_PASSCRED`. Every message is authorized from kernel-provided `SCM_CREDENTIALS`, then bound to a live pidfd/starttime process instance, task, scope, credential generation, and exact request content.

A socket FD may still be transferred, but the authority is not defined by socket possession: when a grandchild sends through the transferred FD, the broker observes the grandchild PID and rejects it.

The optional durable restart layer persists only non-secret permit/effect identity. It never serializes a pidfd. After broker restart, `reacquire_permit()` reopens a fresh pidfd from the persisted PID/starttime pair and fails closed if the process instance no longer matches. Exact already-committed request retries reconcile before current-generation checks, so `commit -> UNKNOWN -> credential rotation -> retry` returns the prior receipt without a second side effect; genuinely new old-generation work remains revoked.

Run:

```bash
python -m unittest experiments.brokered_credential_use.tests.test_protocol experiments.brokered_credential_use.tests.test_restart -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.brokered_credential_use.tests.unsafe_socket_possession_expected_failure -v
```

Boundary: brokered use can revoke *future mediated operations*. It cannot retract data/results already returned to an authorized target and is Linux-specific in this form. The reference JSON state file is a local durable-state mechanism, not a general tamper-proof secret-management database or replicated broker service.
