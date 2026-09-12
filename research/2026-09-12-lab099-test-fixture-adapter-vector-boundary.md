# LAB-099 test-only fixture adapter / independent-vector boundary

Date: 2026-09-12
Status: TEST HARNESS CONTRACT STAGED; executable RED/GREEN pending
Related: LAB-092/#176 PR #177, LAB-099/#184 PR #186

## Objective

Continue the first LAB-099 RED-intent slice without adding production behavior or allowing test corruption helpers to invent a second, unauthenticated precursor/cutover protocol.

## Runtime observation

The run re-probed LAB-086 first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository code execution with `Could not resolve host: github.com` (exit 128). GitHub connector reads/writes remained available. Therefore no new LAB-086 behavioral/unsafe-seed/compileall/security PASS and no LAB-099 RED/GREEN PASS is claimed.

## Source/design audit

The previous handoff requested a test-only `lab099_precursor_fixture_adapter` for PR #186 cases 2-6. Re-reading the frozen contracts exposed an important boundary:

1. `PROVIDER_ACTIVATION_RESERVATION_RELATION_DDL_CUTOVER_V1_FROZEN` freezes required precursor columns and uniqueness semantics, but explicitly leaves **exact SQL spelling implementation-gated until executable REDs are available**.
2. `PROVIDER_ACTIVATION_RESERVATION_PRECURSOR_CUTOVER_IDENTITY_ONE_WAY_UPGRADE_V1_FROZEN` requires PREPARED and CONFIRMED to be distinct canonical authenticated objects; a local phase bit or self-asserted row is not authority.
3. `AUTHENTICATED_PROVENANCE_CHAIN_LINK_V1_FROZEN` requires parent/head/epoch lineage and forbids reconstructing missing links from mutable current rows.
4. The precursor itself requires dual predecessor/successor authentication over exact `ytim.provider-activation-reservation.v1` canonical bytes.

Therefore a test helper that hard-codes guessed DDL, synthesizes arbitrary PREPARED/CONFIRMED rows, or manufactures digest/authenticator bytes would weaken the test: production could be made to pass a fixture-only protocol that was never frozen as authority.

## Decision

`LAB099_TEST_FIXTURE_INDEPENDENT_VECTOR_BOUNDARY_V1_FROZEN`

The test-only adapter may own **mechanical SQLite mutation only**. It must not own LAB-099 authority semantics.

It consumes a sibling independent fixture-vector module containing byte-exact frozen DDL/provenance/authenticator evidence. Until that vector bundle exists, every authority-bearing mutation helper fails closed rather than synthesizing values.

The adapter contract staged on PR #186 therefore requires the vector bundle to supply:

- exact precursor relation name and SQL definition;
- exact orphan-relation mutation plan;
- exact atomic DDL + authenticated PREPARED mutation plan plus 32-byte PREPARED event digest;
- exact uncommitted PREPARED fixture builder;
- exact independently authenticated provenance-parent advancement fixture;
- exact PREPARED commit/replay mutation plan;
- exact sibling PREPARED fixture;
- exact CONFIRMED event mutation plan.

The adapter itself:

- validates exact 32-byte digest typing;
- validates fixture plans as explicit SQL + tuple parameters;
- applies write plans only inside `BEGIN IMMEDIATE`;
- rolls back on error;
- keeps all corruption/crash injection under `tests/`;
- adds no `*_for_test_only` production methods;
- deliberately refuses to proceed when the independent vector module is missing or incomplete.

## Repository result

PR #186 received the new test-only file:

`experiments/provider_generation_history/tests/lab099_precursor_fixture_adapter.py`

Branch commit: `fc4456690b732b3e111379200bba58cf21af9ec8`.

Conflict/topology check after write against pinned PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`:

- status: ahead;
- ahead: 3 commits;
- behind: 0;
- changed files: exactly two test-only files (`red_intent_lab099_precursor_cutover.py` and the new adapter).

No production file changed.

## What remains before executable RED

The independent fixture-vector bundle does not exist yet. It must not be created by guessing exact SQL/authenticator/provenance bytes. The next smallest safe step is to freeze independent byte-level reference vectors for:

1. precursor relation DDL identity;
2. PREPARED canonical object and digest;
3. CONFIRMED canonical object and exact PREPARED binding;
4. provenance parent/head/epoch advancement used by stale/fork replay tests;
5. dual predecessor/successor authenticator reference values.

Those vectors should be independently checkable against the frozen canonical encoder contract and only then consumed by the adapter. Once exact repository materialization is available, explicitly execute the non-discovered RED-intent file and require the expected failures before production LAB-099 behavior is written.

## Verdict

The fixture adapter is now isolated and staged, but it does not fabricate security authority. This preserves the RED-first boundary while still advancing PR #186 through the supported GitHub Contents API under the current transport limitation.
