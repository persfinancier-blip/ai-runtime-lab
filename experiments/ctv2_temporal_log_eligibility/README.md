# CT v2 temporal log eligibility reference

LAB-048 adds time-aware eligibility/operator attribution on top of authenticated LAB-047 trust history.

Core rules:

- lifecycle and operator histories are normalized to non-overlapping `[start_inclusive, end_exclusive)` intervals;
- `HISTORICAL` mode evaluates lifecycle at `evidence_time` so later retirement/distrust does not rewrite an earlier attribution;
- `CURRENT_POLICY` mode evaluates lifecycle at `policy_time`, so a now-ineligible log cannot keep contributing merely because the SCT is old;
- operator identity is always resolved at `evidence_time`;
- the evaluator derives the authoritative trust snapshot from `policy_time`; callers cannot cherry-pick an older accepted snapshot;
- frozen/expired trust metadata and future-dated evidence fail closed;
- every decision persists policy time, evidence times, and exact authenticated snapshot identity.

The reference model uses strict `[start,end)` boundaries because Chromium CT log metadata exposes `start_inclusive`/`end_exclusive` temporal intervals. This is a LAB convention for lifecycle/operator interval compilation, not a claim that every PKI validity primitive uses that convention (RFC 5280 certificate validity, for example, includes both notBefore and notAfter endpoints).

`SnapshotLog.operator_since` represents authenticated operator-history metadata. LAB-047's minimal model did not yet expose this field; LAB-048 makes the missing temporal authority explicit rather than guessing operator changes from current ownership.

Run corrected tests:

```bash
PYTHONPATH=. python -m unittest discover -s experiments/ctv2_temporal_log_eligibility/tests -p 'test_*.py' -v
```

Run the deliberately unsafe stale-snapshot baseline separately; it is expected to fail:

```bash
PYTHONPATH=. python -m unittest experiments.ctv2_temporal_log_eligibility.tests.unsafe_stale_snapshot_expected_failure
```
