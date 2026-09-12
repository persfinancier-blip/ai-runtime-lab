# LAB-099 first isolated RED-intent scaffold

Date: 2026-09-12
Status: RED-intent authored; NOT EXECUTED
Related: LAB-092/#176 PR #177, LAB-099/#184, draft PR #186

## Runtime observation

LAB-086 remained priority #1. A fresh direct materialization probe was attempted first:

```text
git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab
fatal: unable to access ...: Could not resolve host: github.com
exit 128
```

The failure occurred before repository code execution. The GitHub connector remained available, but this run exposed no supported byte-exact connector-to-local-executor materialization primitive. Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, conflict, RED, or GREEN PASS is claimed.

## Work performed

Following the exact fallback recorded in `state/CURRENT.md`, an isolated branch was created from exact LAB-092 PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`:

- branch: `lab-099-precursor-cutover-red-intent`
- draft PR: #186, base `lab-092-activation-schema-provenance`
- current test-scaffold head: `7695b28733b2c6bdf3f0dfb384a82d0bf095f7b1`
- compare against the pinned base: ahead 2, behind 0, one changed file only

Added:

`experiments/provider_generation_history/tests/red_intent_lab099_precursor_cutover.py`

The filename intentionally does not match normal `test_*.py` discovery. It is an explicit-run RED-intent contract, not a passing regression and not production behavior.

## First six frozen cases represented

1. LAB-092 V1 completion alone does not authorize LAB-099 precursor governance.
2. Physical precursor relation with no authenticated PREPARED evidence is `ORPHAN_UNAUTHENTICATED_SCHEMA` and fails closed.
3. Crash after atomic DDL + PREPARED is `PREPARED_INCOMPLETE`; recovery may continue only the exact PREPARED digest.
4. A PREPARED built on a stale/forked predecessor parent+epoch cannot be committed on the canonical lineage.
5. CONFIRMED must bind the exact PREPARED digest; a sibling digest is invalid.
6. Once CONFIRMED, deletion of the precursor relation is corruption and cannot downgrade startup to LAB-092/LAB-090 semantics.

## Audit correction during authoring

The first scaffold revision placed crash/corruption helper names such as `*_for_test_only` on the future production module. That would have polluted the security boundary with test mutation hooks.

Before opening the PR, the scaffold was corrected:

- future production surface is limited to the governed ledger/classifier/migration/recovery contract;
- corruption and crash-state injection is delegated to a future sibling **test-only fixture adapter** under the tests package;
- production code must not expose test-only mutation hooks.

This is why the PR contains two commits but only one final changed file.

## Execution status

The scaffold was not executed. The future LAB-099 production module and fixture adapter intentionally do not exist yet, and exact repository materialization is unavailable in this runtime. The draft therefore carries no claimed RED observation and no syntax/compile PASS.

Do not add production LAB-099 behavior merely to make this scaffold import. When exact execution becomes available, first implement the test fixture adapter from the already-frozen relation/provenance DDL contract, execute this module explicitly, record the intended RED reasons for all six cases, and only then begin production implementation.

## PR discipline

Keep #186 draft. It is a test-contract staging PR layered on draft PR #177 and must not be merged independently. It becomes actionable only after the underlying LAB-092/LAB-090 executable gates and exact LAB-099 RED execution are available.
