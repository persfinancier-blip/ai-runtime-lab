# LAB-092 confirmation race + restart pre-authentication audit

Date: 2026-09-01

## Confirmation race audit
Exact source shows two independent closures against confirming a migration marker under changed provider authority:

1. `SupportedHistoricalSharedAnchorLedger.rotate_provider()` takes `BEGIN IMMEDIATE` and rejects rotation while any shared-anchor intent is `PREPARED`; the LAB-092 marker therefore fences normal LAB-090 rotation during confirmation.
2. Historical `_reauthenticate(entry)` rejects an unreceipted marker whose `(provider_id, provider_generation)` no longer matches durable current provider history.

So the suspected `DDL+PREPARED -> authority changes -> old marker CONFIRMED` race is closed by existing LAB-080/LAB-090 composition.

## Restart ordering defect
`ProvenancedHistoricalSharedAnchorLedger.__init__()` previously called full LAB-090 construction before externally re-authenticating the locally CONFIRMED migration marker. LAB-090 construction may run `_recover_pending_activation()`, so activation recovery could occur before fail-closed provenance verification.

Regression commit: `7c2700394e3bb5e24cacd3fa62423046eace40d1`.

Initial fix commit: `25bd75b652a3a525fda69bc55264a547ecbc1284` moved re-authentication ahead of `super().__init__()`.

## Self-audit correction: legacy startup must remain mutation-free
The first fix exposed a second issue during audit: calling the non-mutating object-construction bridge's inherited `execute()` before classifying the DB is not mutation-free on an absent marker, because `execute()` calls `reserve()`. A legitimate legacy DB could therefore acquire a PREPARED provenance marker during ordinary startup, violating the explicit-migration contract.

Regression commit: `4cf690d60db17947430f956aea61c20d59ff7ce9` adds `test_activation_schema_restart_precheck.py`, requiring legacy startup to raise `ActivationSchemaMigrationRequired` while leaving marker, activation table and trigger absent.

Corrected implementation commit/current PR #177 head: `4dfd91b2a346b2f68eb73b2f2cca463743500567`.
Current provenance blob: `c1e46235bc703cfd8ac718b04bb43e19637a94f1`.

Corrected restart ordering:
1. `_classify(path)` performs read-only local classification first;
2. legacy/unmarked/PREPARED states raise migration-required before `execute()` can reserve anything;
3. only `COMPLETE` proceeds to non-constructor external re-authentication;
4. only after successful re-authentication does LAB-090 `super().__init__()` run activation recovery;
5. completion intent is checked again after constructor recovery.

## Validation actually performed
- GitHub branch writes succeeded through the normal Contents API.
- PR diff was re-fetched during the run and audited for the intended ordering.
- Fresh exact checkout was attempted with `git clone --depth 1 --branch lab-092-activation-schema-provenance ...`; transport failed before repository code execution with `Could not resolve host: github.com`.
- No branch-level RED/GREEN or whole-suite PASS is claimed.

## Conclusion
The authority-change confirmation race is closed. Restart provenance is now ordered before activation recovery, while legacy startup remains read-only and cannot implicitly reserve a migration marker. Exact behavioral execution remains pending.
