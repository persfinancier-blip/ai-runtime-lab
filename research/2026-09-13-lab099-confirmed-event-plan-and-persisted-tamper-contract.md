# LAB-099 — exact CONFIRMED event plan + persisted tamper contract

Date: 2026-09-13

## Scope

This slice remains test-owned only. No production `activation_reservation_provenance` code was added and no repository RED/GREEN execution is claimed.

LAB-086 was probed first as required. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128), so the exact LAB-086 full execution gate remains unavailable in this run.

## CONFIRMED fixture decision

`lab099_precursor_fixture_vectors.confirmed_event_plan()` now consumes `lab099_confirmed_ledger_reference.py` as the sole receipt/head/epoch bridge.

The plan is intentionally **not** a generic CONFIRMED generator:

- the supplied PREPARED digest must equal the frozen `77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e`;
- the bridge self-check must pass;
- the durable shared-anchor row must match every frozen authority-relevant field (intent/component/type/payload/provider generation/predecessor/position/request) while still `PREPARED` with no receipt;
- a matching cutover materialization row for the same PREPARED digest and anchor intent must exist;
- only then may the mutation set `status='CONFIRMED'` plus the frozen stable RECONCILE receipt;
- the fixture adapter's existing `expected_rowcount=1` contract makes any stale/substituted pre-state roll back atomically.

This deliberately refuses to synthesize receipt/head/epoch authority for arbitrary sibling PREPARED digests. The historical synthetic `c0..df` head remains non-authoritative.

## Persisted tamper contract

Added non-discoverable `red_intent_lab099_confirmed_row_cross_binding.py` to freeze fixture-level cases against the exact persisted CONFIRMED reference:

1. exact persisted reference is accepted by the test-only verifier;
2. changed receipt binding fails closed;
3. changed confirmed position fails closed;
4. changed externally supplied confirmed-head authority fails closed;
5. changed PREPARED digest ancestry fails closed.

The suite is intentionally not named `test_*.py` and is not production proof. It should be executed only after an exact repository materialization is available.

## Validation actually observed

Locally authored source for the updated fixture-vector module and the new non-discoverable contract both passed `python -m py_compile` before publication. Because no supported connector-to-local byte materialization exists in this run, that is syntax evidence for the authored source, not a claim that the exact published branch bytes were imported/executed.

The updated published fixture-vector blob is `73406169990849327774fc46682747a14222bd9d`.

## Audit note

The frozen CONFIRMED bridge is an **exact reference**, while `atomic_prepared_plan()` is deliberately capable of deriving provider/tail from an arbitrary valid fixture database. Therefore the CONFIRMED plan must remain exact/fail-closed rather than silently adapting the reference receipt/head to dynamic provider/tail values. A future broader executable fixture needs a separately authenticated derivation contract; it must not be invented inside the adapter.

## Integration boundary

Keep PR #186 draft/test-only. Do not add production LAB-099 behavior until exact repository execution is available and an actual production RED is observed.
