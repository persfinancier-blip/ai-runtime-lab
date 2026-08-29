# LAB-091 real-stack process concurrency / crash regression — 2026-08-29

## Objective

Close the remaining evidence gap between the existing stubbed process-concurrency tests and the final supported LAB-091 surface.

The existing `test_process_concurrency_and_crash.py` replaces the LAB-080 intent module and the LAB-091 parent integration class with test stubs. It proves the narrow permit/CAS mechanism, but it does not prove `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` against the real LAB-080/LAB-082 dependency stack.

## Published regression

Branch: `lab/091-mutable-shared-anchor-writer`

Commit: `2e83e6b12e4e40f42df890f964f134c2d397ec7b`

File:
`experiments/mutable_shared_anchor_writer/tests/test_real_stack_process_concurrency_and_crash.py`

Published blob after re-fetch:
`938877479d4c4b997ea52e8b5857bf89e5c3e246`

The regression imports the real final class directly:

`SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`

and real LAB-080/LAB-082 cryptographic/runtime components:

- `AttestedCatchup`
- `AttestationVerifier`
- `ProviderIdentity`
- `SignedObservation`
- `GenerationSigner`
- real `Intent`

No LAB-091 parent class or LAB-080 intent module is replaced in `sys.modules`.

## Process-shareable provider fixture

A test-only `SharedSQLiteAnchorProvider` keeps external-anchor state in a second SQLite file, deliberately separate from the shared-anchor ledger DB. `BEGIN IMMEDIATE` serializes provider effects across OS processes; `provider_requests(request_id PRIMARY KEY, position)` makes the provider effect idempotent by request identity. Returned observations use the same canonical HMAC shape expected by the real `AttestationVerifier`.

A focused executable probe of this provider mechanism was run in the current runtime using two `fork` workers. Both workers raced on the same request ID and both converged on position 1; exit codes were 0, durable provider value remained 1, and the fixture recorded two increment invocations. Result: **PASS** for the provider idempotency/process-sharing mechanism.

This focused probe is not counted as a PASS for the full published regression.

## Full regression scenarios

### Two-process confirmation convergence

Two independently constructed final LAB-091 ledgers point at the same ledger DB and the same external provider-state DB, cross a process barrier, and execute the same exact intent. The expected invariant is:

- both workers return `CONFIRMED`;
- both observe one identical durable receipt binding;
- provider position advances exactly once to 1;
- restart returns the same confirmation;
- durable verification succeeds;
- exactly one asymmetric provider receipt remains in ledger history.

### Crash after receipt persistence, before intent confirmation

A subclass changes only `_commit_confirmation()` to terminate the process with exit code 17. All reservation, provider catch-up, reconciliation, signed-receipt persistence and guard logic before that point are the real final-class path.

Expected durable crash boundary:

- external provider is already at position 1;
- the intent remains `PREPARED` with no receipt binding;
- exactly one signed asymmetric provider receipt already exists for the request;
- a fresh final-ledger instance must converge that exact request to `CONFIRMED` without advancing the external anchor again;
- durable verification must then succeed.

## Execution limitation

The full unittest was **not executed** in this run. Connector reads/writes are healthy, but the executable environment still cannot resolve `github.com`, `api.github.com`, or `raw.githubusercontent.com`, and the connector does not mount a branch checkout into the executable filesystem. Therefore no full behavioural PASS is claimed.

The exact published regression must be executed unchanged when a supported branch-to-executable-filesystem path becomes available. Any failure should be treated as a real-stack defect and fixed without weakening the test.

## LAB-086 priority observation

LAB-086 remains first priority. Fresh branch source still reports `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`. The durable hidden-rowid delta is available as `research/2026-08-28-lab086-hidden-rowid-replace.patch`, but publishing the security-critical whole-file candidate still requires a byte-preserving bridge into the normal Contents API. No low-level Git ref/tree bypass was used.
