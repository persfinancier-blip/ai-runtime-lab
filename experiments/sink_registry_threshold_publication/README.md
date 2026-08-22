# Threshold-authorized sink registry publication (LAB-077)

LAB-076 threshold-protects root rotation/recovery. LAB-077 closes the remaining publication gap: a new `sink -> adapter/endpoint/operation` mapping is accepted only with a threshold proof from the exact current root.

The supported surface binds, in one SQLite writer transaction:

1. current authenticated sink capability head;
2. exact LAB-076 root identity/version;
3. canonical threshold proof over one registry-entry payload;
4. LAB-075 registry row and registry head;
5. broker request `INTENT` plus capability/registry identities.

A bare legacy single-signature `RegistryEntry` cannot create new LAB-077 publication authority. It is accepted only as a read of already threshold-published historical state. `CONFIRMED` request retry is receipt-only and cannot publish a new registry mapping; pending `INTENT` cannot inherit a rotated capability; `UNKNOWN` may use newer capability only for reconciliation when explicitly authorized.

Historical threshold proof is retained and reverified against the exact historical root. Root rotation and publication serialize on the same SQLite DB, so a proof collected under root N either commits before rotation or becomes stale after root N+1 wins.

Run corrected suite:

```bash
python -m unittest discover -s experiments/sink_registry_threshold_publication/tests -p 'test_*.py' -v
```

Observed exact-source result: **27/27 passed**. Compileall passed after clearing a local stale-permission `__pycache__` created by source reconstruction.

Unsafe seed (expected failure):

```bash
python -m unittest experiments.sink_registry_threshold_publication.tests.unsafe_single_signer_expected_failure -v
```

It fails as expected because the deliberately unsafe compatibility class accepts one active signer under a threshold-2 root.

Additional exact-source regressions in this run: LAB-076 12/12, LAB-075 combined protocol/audit 43 passing test executions, and LAB-074 18/18.

## Migration boundary

LAB-077 intentionally does not auto-promote pre-existing LAB-076 single-signature registry rows into threshold-authenticated history. A legacy database requires an explicit migration/checkpoint ceremony if seamless in-place upgrade is needed. Failing closed is preferred to silently blessing old single-signature history.
