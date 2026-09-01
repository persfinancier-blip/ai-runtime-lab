# LAB-092 confirmation race + restart pre-authentication audit

Date: 2026-09-01

## Scope
Audit the interval after LAB-092 atomically commits exact activation DDL + deterministic PREPARED migration marker and before/through external confirmation. Then audit normal restart ordering for a locally CONFIRMED migration marker.

## Confirmation race audit
Exact source shows two independent closures against confirming a migration marker under changed provider authority:

1. `SupportedHistoricalSharedAnchorLedger.rotate_provider()` acquires `BEGIN IMMEDIATE` and rejects provider rotation whenever any shared-anchor intent remains `PREPARED`. The LAB-092 migration marker is globally PREPARED during the confirmation interval, so a normal LAB-090 generation rotation cannot commit through that interval.
2. The inherited historical `_reauthenticate(entry)` compares an unreceipted entry's `(provider_id, provider_generation)` with durable current provider history before reconciling the external request. If recovery is attempted after durable authority has already changed, an old-generation PREPARED marker is rejected rather than silently confirmed.

Therefore the previously suspected `DDL+PREPARED -> authority changes -> old marker CONFIRMED` race is closed by existing LAB-080/LAB-090 composition. No source change was required for that race.

## New ordering defect found
A separate startup defect remained. `ProvenancedHistoricalSharedAnchorLedger.__init__()` previously called `super().__init__()` before re-authenticating the locally CONFIRMED migration marker. The LAB-090 constructor runs `_recover_pending_activation()` during `super().__init__()`. Thus a local CONFIRMED row that no longer has valid external provenance could trigger provider-activation recovery side effects before the eventual external provenance check failed.

Local `CONFIRMED` SQLite state is evidence only; it must not authorize activation recovery before external re-authentication.

## Regression-first change
Branch: `lab-092-activation-schema-provenance`, draft PR #177.

Regression commit: `7c2700394e3bb5e24cacd3fa62423046eace40d1`.

`test_restart_reauthenticates_confirmed_provenance_before_activation_recovery`:
- performs a legitimate migration to CONFIRMED;
- restarts with the same authenticated identity/key and tail but a fresh external provider instance that has no result for the migration request;
- patches LAB-090 activation recovery to raise if reached;
- requires restart to fail with `PendingIntent` from provenance re-authentication before any activation recovery runs.

## Implementation
Fix commit: `25bd75b652a3a525fda69bc55264a547ecbc1284`.

Current provenance blob: `f61828b27bf9f78e2bb05cb71cf29195b5763a1a`.

`ProvenancedHistoricalSharedAnchorLedger.__init__()` now:
1. creates the existing non-mutating reservation surface;
2. executes/re-authenticates the deterministic completion intent before constructing the LAB-090 supported surface;
3. only after a CONFIRMED externally authenticated marker calls `super().__init__()`, which may reconcile provider activation state;
4. re-checks the completion intent after constructor recovery.

This preserves the prior explicit-migration confirmation bridge and extends the same no-side-effect-before-provenance rule to ordinary restart.

## Validation actually performed
- GitHub PR diff was re-fetched after both branch writes and shows the intended regression plus pre-authentication ordering.
- Fresh exact branch checkout was attempted with `git clone --depth 1 --branch lab-092-activation-schema-provenance ...` but transport failed before repository code execution: `Could not resolve host: github.com`.
- Therefore no branch-level RED/GREEN or whole-suite PASS is claimed in this run.

## Security conclusion
The provider-generation-change race during PREPARED confirmation is closed by the global PREPARED fence plus historical re-authentication. The newly found restart side-effect ordering defect required a source fix and is now hardened in PR #177, pending exact behavioral execution.
