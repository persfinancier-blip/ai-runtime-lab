# LAB-095 locked custody payload tamper — fail-closed fix

Date: 2026-09-14
Issue: #180
PR: #187 (`lab-095-database-identity-red-intent`)

## Context

LAB-095 identity migration keeps a local custody tuple (`nonce_hex`, bootstrap generation id, payload digest, request id) and a separately persisted shared-anchor identity intent. The public read-only classifier already recomputes the payload digest from the nonce/bootstrap pair, but the under-transaction `_classify_locked()` path did not.

That asymmetry matters because `migrate_database_identity()` reauthenticates/executes the external intent and then opens a new `BEGIN IMMEDIATE` transaction for local finalization. A different SQLite writer can therefore modify custody between those phases. Before this fix, changing only the custody nonce/bootstrap while retaining the old payload digest and request id could still be classified as PREPARED by `_classify_locked()`.

## Reproduction

A narrow file-backed SQLite semantic probe reproduced the defect:

- valid PREPARED custody + matching PREPARED identity intent -> `PREPARED`;
- update only `nonce_hex`, leave `payload_digest` and intent unchanged -> old locked classifier still returned `PREPARED`;
- recomputing the canonical payload digest from the tampered nonce/bootstrap did not match the persisted digest.

This probe is semantic evidence for the exact condition. It is not a full exact-repository test run.

## Fix

PR #187 now makes `_classify_locked()`:

1. recompute `identity_payload_digest()` from persisted `nonce_hex` + `bootstrap_generation_id`;
2. return `CORRUPT` if canonical validation fails or the recomputed digest differs from the persisted payload digest;
3. catch `DatabaseIdentityError` from complete-state `confirmed_identity_digest()` validation and return `CORRUPT` instead of leaking malformed durable data as an uncontrolled validation exception.

Production commit: `0a767c10efead57094eb0281cbf9a25a4c6cd9cf`.
Production blob after fix: `9f61784c3c07df90dca650ea9867a3512d2d68a7`.

A branch regression was added first at commit `c1957dd6249bcd6ce154fd6520e3934eebcae6b0`:
`experiments/provider_generation_history/tests/red_intent_lab095_locked_custody_payload_tamper.py`.

The regression requires a retry over tampered PREPARED custody to fail with `identity custody is corrupt`, forbids replacement nonce generation, and verifies the existing payload/request and single intent remain unchanged.

## Validation actually performed

- direct LAB-086 clone probe was attempted first and again failed before repository execution with `Could not resolve host: github.com`, exit 128;
- pre-fix semantic SQLite probe reproduced `PREPARED` after nonce tamper;
- post-fix semantic SQLite probe produced `CORRUPT` for the same tamper while preserving `PREPARED` for the valid tuple;
- GitHub commit diff was inspected after the Contents API update and contains only the intended locked-classifier validation changes.

The committed full regression has not been executed against a byte-exact repository closure in this runtime. Do not claim full LAB-095 GREEN from this report.

## Security conclusion

The writer-locked classifier must validate the same canonical custody payload relation as the public classifier before permitting retry/finalization. Otherwise a post-reauth local custody mutation can cross the phase boundary and be consumed as coherent state.

## Next action

After the mandatory LAB-086 materialization probe, execute the committed LAB-095 recovery regressions (including this new tamper regression) on the smallest safely materialized byte-exact closure. Then execute DB-A -> DB-B and retained LAB-080/LAB-081/LAB-090/LAB-092 downstream gates before integration.
