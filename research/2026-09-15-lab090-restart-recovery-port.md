# LAB-090 restart/historical recovery port — 2026-09-15

## Capability probe
Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS or exact-repository test PASS is claimed.

## Donor
PR #175 (`lab-090-provider-activation-fencing`) was inspected as the semantic donor. Its restart contract reconciles the durable current generation against provider activation state and then rejects any historical `SQL_COMMITTED` activation.

## Port to PR #187
Added `_recover_pending_activation()` to the already-composed `ActivationCoordinatorMixin` and invoked it from `SupportedHistoricalSharedAnchorLedger.__init__` only after `_require_runtime_matches_durable_head()`.

The recovery uses private `_history().current()` as durable generation authority and preserves the construction-bound provider-history strategy.

Current-generation reconciliation:
- durable `SQL_COMMITTED` + provider `PREPARED`: finish provider commit, durable exact-ticket acknowledgement, release;
- durable `SQL_COMMITTED` + `COMMITTED_FENCED`: durable acknowledgement then release;
- durable `SQL_COMMITTED` + `RELEASED`: fail closed as premature release;
- durable `SQL_COMMITTED` + `ABSENT`: fail closed as lost reservation;
- durable `COMMITTED` + `COMMITTED_FENCED`: finish release;
- durable `COMMITTED` + `RELEASED`: accept;
- other combinations fail closed.

After current-generation reconciliation, any other generation still carrying `SQL_COMMITTED` fails closed as historical unresolved activation. This prevents restart into a permanently blocked global-writer state.

## Commits
- activation recovery primitive: `ce6bdab3eb3c34a9d9165fad8d3b522197d21527`
- supported-ledger startup wiring: `af8a22e520f1a2aab30e72f899aad04b25a07935`

## Validation status
Source-level donor/target audit completed. Exact branch execution is unavailable in this run because no byte-preserving connector-to-executable-filesystem bridge is exposed. No pytest/compileall GREEN is claimed.

## Next
Add focused source regressions for the two recoverable restart windows, premature release, ABSENT reservation, and historical unresolved activation; separately audit whether startup recovery must be gated behind LAB-092 COMPLETE activation-schema classification before constructor use.