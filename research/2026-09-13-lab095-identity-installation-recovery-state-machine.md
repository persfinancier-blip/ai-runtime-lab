# LAB-095 identity installation/recovery state machine

Date: 2026-09-13

## Context
LAB-095 needs two independent protections: a construction-bound physical SQLite target and a path-independent authenticated logical database/history identity. The earlier RED-intent reference froze the logical digest construction but left crash/retry custody and migration ordering unspecified. LAB-099 depends on this identity and therefore must not synthesize its own precursor authority.

LAB-086 was re-probed first in this run. Direct `git clone` again failed before repository execution with `Could not resolve host: github.com` (exit 128), so no new LAB-086 executable gate result is claimed.

## Source audit
The LAB-092 migration path provides the closest production precedent. Its explicit migration routine atomically installs local schema + reserves a deterministic shared-anchor PREPARED marker under `BEGIN IMMEDIATE`, then performs external confirmation through the inherited ledger. A PREPARED marker is recoverable by rerunning the explicit migration path; ordinary startup remains read-only/fail-closed.

That pattern is suitable for LAB-095 identity custody with one additional requirement: the fresh random nonce must be persisted before any external call and must never be regenerated for a retry of the same logical installation.

## Frozen installation states
A test-only state machine was added on draft PR #187. It is deliberately not production authority.

- `LEGACY_ABSENT`: no nonce custody row, no identity intent, no receipt, no confirmed digest. Permitted action: `BEGIN_INSTALL`.
- `PREPARED`: custody row and deterministic shared-anchor identity intent exist with exactly matching payload digest, both still PREPARED. Permitted action: `RECONCILE_SAME_REQUEST`.
- `CONFIRMED_NEEDS_FINALIZE`: shared-anchor intent is externally CONFIRMED with receipt binding, while local custody remains PREPARED and no logical identity digest is stored. Permitted action: `FINALIZE_LOCALLY` after reauthenticating the confirmed evidence.
- `COMPLETE`: externally confirmed intent/receipt and local confirmed identity digest agree. Permitted action: read-only verification/startup.
- `CORRUPT`: every asymmetric or contradictory partial state. Permitted action: fail closed only.

## Nonce custody and retry contract
1. Generate exactly 32 random bytes inside `BEGIN IMMEDIATE` only after re-reading and observing `LEGACY_ABSENT`.
2. The production migration API must not accept a caller-supplied nonce or logical identity digest.
3. Persist nonce/bootstrap/payload custody and the deterministic shared-anchor PREPARED identity intent in the same SQLite transaction.
4. Crash before transaction commit leaves `LEGACY_ABSENT`; crash after commit leaves `PREPARED`.
5. Provider timeout/UNKNOWN from `PREPARED` never generates a new nonce and never reserves a second request. Retry reconciles the same deterministic request identity.
6. If external confirmation became durable but the process crashed before storing the derived logical identity digest, restart reauthenticates the CONFIRMED shared-anchor row + persisted receipt and finalizes locally. It must not increment the provider again.
7. A concurrent installer is serialized by `BEGIN IMMEDIATE`. The loser re-reads the winner's state and resumes the same PREPARED request; it must not create a second nonce.
8. Existing valid legacy history reserves exactly the next shared-anchor position under the currently verified provider generation.

## Fail-closed partial states
The contract rejects, rather than repairs by invention:
- custody without the matching deterministic identity intent;
- identity intent without nonce/bootstrap custody;
- payload-digest mismatch between custody and intent;
- local CONFIRMED state while the external intent is still PREPARED;
- CONFIRMED intent without the persisted authenticated receipt binding;
- receipt/digest evidence appearing while the intent remains PREPARED.

A clone taken after completed identity installation intentionally represents the same logical lineage because the identity is path-independent. This does not authorize two concurrent writable copies; whole-store fork/freshness remains an external monotonic-anchor/process-boundary concern.

## Executed evidence
Authored locally before publication:
- `lab095_identity_installation_reference.py`: `py_compile` PASS; local Git blob `91b69a16d1a8d25d4c0af15becd320fdad95d682`.
- `test_lab095_identity_installation_reference.py`: `py_compile` PASS; local standalone unittest 5/5 PASS; local standalone-source blob before package-import adjustment `a790a6e1947b4545a9ddc15111884773a48a2b25`.

Published branch commits:
- state-machine reference: `d3832c3672e1f54b61e0507f48d88358fba43531`;
- package-aware regression: `aa7ae4eeb2d1f8228dae30c15fa9621a2b51550e`.

The published regression import path differs from the standalone local harness only so it resolves correctly inside the repository package. Full repository behavioral execution remains pending because this runtime still lacks byte-exact repository materialization.

## Decision / next implementation boundary
The crash/retry contract is frozen enough to permit the next smallest production slice, but production code must independently implement it and must not import the test reference.

Next LAB-095 work after the mandatory LAB-086 probe:
1. define the minimal custody table/DDL and independent production classifier;
2. implement explicit identity migration using `BEGIN IMMEDIATE` + atomic custody/PREPARED reservation;
3. generate nonce internally with a CSPRNG only after lock acquisition and absent-state recheck;
4. recover PREPARED by same-request reconciliation and CONFIRMED_NEEDS_FINALIZE by local derivation after external reauthentication;
5. bind physical DB path privately/immutably across shared ledger + provider history;
6. add real repository RED/GREEN regressions for crash, UNKNOWN, concurrent installers, corrupt partial states, DB-A→DB-B rebinding, and legacy migration before integrating downstream LAB-092/LAB-099.
