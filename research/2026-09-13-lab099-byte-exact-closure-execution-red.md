# LAB-099 byte-exact closure execution and observed production RED

Date: 2026-09-13

## Scope

Resume the exact execution prerequisite recorded in `state/CURRENT.md` after the mandatory LAB-086 materialization probe.

No production LAB-099 implementation is introduced by this note.

## LAB-086 first-priority probe

A direct local clone was attempted first:

`git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git ...`

It failed before repository code execution with `Could not resolve host: github.com` and exit 128. Raw/archive download fallback was also unavailable through the current supported web/download path. No new LAB-086 behavioral, security, compile, or conflict PASS is claimed.

## New supported fallback that succeeded

The GitHub connector could return exact UTF-8 blob contents. Each frozen LAB-099 source blob was transferred into an isolated local filesystem tree and accepted only after local `git hash-object` exactly matched `LAB099_EXACT_ORCHESTRATION_IMPORT_CLOSURE_V1_FROZEN` from `research/2026-09-13-lab099-exact-orchestration-import-closure.md`.

Result: **18/18 manifest blobs matched exactly**. No mismatched or model-reserialized file was executed.

The exact frozen closure then passed:

- `python -m compileall` over the materialized closure: exit 0;
- import of `lab099_confirmed_orchestration_witness`;
- `validate_orchestration_contract_shape()`;
- fresh file-backed SQLite `execute_frozen_confirmed_orchestration()`.

The orchestration process exited 0 and returned exactly:

- request: `shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf`;
- receipt: `ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4`;
- confirmed position: `42`;
- confirmed head: `45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda`;
- final `HistoricalSharedAnchorLedger.verify_durable()` succeeded inside the orchestration.

A runtime-wide spreadsheet warmup hook printed an unrelated stderr traceback during Python startup, but the compileall and orchestration subprocesses both returned exit 0; it did not affect this isolated ledger execution.

## Observed RED

After the frozen execution prerequisite turned GREEN, the exact PR #186 non-discoverable contract `red_intent_lab099_precursor_cutover.py` was materialized from head `766434563a5ad82a88156687c84de9c9e17b14c6` and verified as Git blob `0a96b07196189add888df6e59ce5eb2f869138ef`.

Its inherited LAB-092 dependency `activation_schema_provenance.py` was also materialized byte-exact and verified as blob `396b67a46686f6df23584b1b366824c1b7ac1886`.

Explicit execution:

`python -m unittest -v experiments.provider_generation_history.tests.red_intent_lab099_precursor_cutover`

Result: **RED, exit 1, 6 tests run / 6 failures**. Every failure is the intended pre-fix surface failure:

`ModuleNotFoundError: No module named 'experiments.provider_generation_history.activation_reservation_provenance'`

The test converts that missing production module into the explicit assertion text `RED intent: LAB-099 precursor-cutover production module does not exist yet`.

This is now an actually observed executable RED, not a source-only contract.

## Decision / next engineering boundary

The previous prohibition on beginning LAB-099 production work due to unobserved execution is removed. The next slice may implement `activation_reservation_provenance`, but must first source-audit the frozen LAB-099 design and derive the smallest production authority model independently of `tests/lab099_*` modules. Test-only canonical vectors, deterministic witness keys, prefix payloads, and fixture mutation helpers must not become production authority.

Start with the smallest production surface required by the RED contract:

- `PrecursorCutoverMigrationRequired`;
- `PrecursorCutoverVerificationError`;
- `PrecursorGovernedHistoricalSharedAnchorLedger`;
- `classify_precursor_cutover_v1`;
- `migrate_precursor_cutover_v1`;
- `resume_precursor_cutover_v1`.

Re-run the exact RED after each minimal slice and let the next observed failure drive implementation. Keep PR #186 draft until the production implementation, six-case GREEN, downstream LAB-092/LAB-090 compatibility, compileall, security audit, and conflict audit are all observed.
