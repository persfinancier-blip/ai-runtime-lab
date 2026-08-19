# Ephemeral Credential Delivery Prototype

LAB-027 reference harness for credential delivery across process boundaries.

## Contract

1. Raw credentials are forbidden in argv and ambient child environment.
2. Child environments are explicit allowlists/scrubbed copies, never blind inheritance.
3. File descriptors/handles are non-inheritable by default; explicit inheritance is allowlisted per child.
4. If a file fallback is unavoidable, it is mode `0600`, scoped to the operation, and unlinked on both success and failure paths.
5. Credential references bind stable ID, scope and generation; rotation/scope change invalidates stale references.
6. Retry/UNKNOWN correlation uses non-secret credential identity/fingerprint, never a durable raw-secret copy.
7. Evidence records credential ID/scope/generation plus keyed HMAC fingerprint only.

## Run

```bash
python -m unittest discover -s experiments/ephemeral_credentials/tests -p 'test_*.py' -v
python -m compileall -q experiments
```

Unsafe seeds are deliberately outside passing discovery:

```bash
python -m unittest experiments.ephemeral_credentials.tests.unsafe_seed_expected_failure -v
```

They are expected to fail because the raw credential appears in argv/environment.

## Important limitation

`unlink()` and best-effort overwrite do not prove physical media erasure. A production design should prefer OS credential stores, pipes/socketpairs, sealed/non-executable memory-backed FDs, or equivalent narrowly scoped handles over filesystem materialization. This prototype validates lifetime/namespace exposure, not forensic erasure.
