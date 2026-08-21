# LAB-071 brokered credential use

Linux reference prototype for operation-time revocation without handing raw credential bytes to the target.

The broker owns the secret and receives requests through an `AF_UNIX` datagram socket with `SO_PASSCRED`. Every message is authorized from kernel-provided `SCM_CREDENTIALS`, then bound to a live pidfd/starttime process instance, task, scope, credential generation, and exact request content.

A socket FD may still be transferred, but the authority is not defined by socket possession: when a grandchild sends through the transferred FD, the broker observes the grandchild PID and rejects it.

Run:

```bash
python -m unittest experiments.brokered_credential_use.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.brokered_credential_use.tests.unsafe_socket_possession_expected_failure -v
```

Boundary: brokered use can revoke *future mediated operations*. It cannot retract data/results already returned to an authorized target and is Linux-specific in this form.
