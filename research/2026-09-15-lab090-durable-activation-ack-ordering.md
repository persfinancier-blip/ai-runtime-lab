# LAB-090 durable activation acknowledgement ordering — 2026-09-15

## Run observation

LAB-086 was probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Donor audit

PR #175 `supported.py` encodes the security-critical post-SQL ordering as:

1. activation row/generation transition is already durable as `SQL_COMMITTED`;
2. provider `commit_activation(ticket)` reaches `COMMITTED_FENCED` (or `UnknownOutcome` is reconciled through `activation_status(ticket)`);
3. the exact durable ticket row is changed to `COMMITTED` under `BEGIN IMMEDIATE`;
4. only after that durable acknowledgement may the exact provider ticket be released.

This slice does not require importing PR #175's authority-heavy supported ledger. It can be isolated from construction, database identity, provider-history strategy, schema installation, and receipt provenance.

## Composition implemented on PR #187

Added `experiments/provider_generation_history/activation_coordinator.py` with `ActivationCoordinatorMixin` containing only:

- exact activation-row lookup;
- exact-ticket durable `SQL_COMMITTED|COMMITTED -> COMMITTED` acknowledgement;
- provider commit / `UnknownOutcome` reconciliation;
- release only after durable acknowledgement.

The mixin assumes the composed ledger supplies `_con()`. It does not retain a path, provider-history object, bootstrap, attested capability, or schema authority, so it does not weaken LAB-095/LAB-096 construction-bound authority.

Added `tests/test_activation_coordinator_ordering.py` covering normal commit, `UnknownOutcome` reconciliation, and wrong-fence exact-ticket mismatch. The fake provider asserts from SQLite that status is already `COMMITTED` at release time; wrong-ticket failure leaves the row `SQL_COMMITTED` and provider `COMMITTED_FENCED`, proving fail-closed non-release semantics at the regression level.

Branch commits:
- production: `39c05ee36bf3105a68db657b434bc128a6137db9`;
- regression/current head after test: `a0404909bd144f4527ec364fac5b484f40339dea`.

## Validation boundary

Exact repository pytest is not claimed. The connector still exposes repository bytes only through control-plane responses and direct shell GitHub transport is DNS-blocked, so the exact branch closure was not executed in this run.

## Next slice

After the mandatory LAB-086 probe, compose the pre-ack coordinator transaction: prepare exact activation ticket, re-check tail/unresolved activation/PREPARED intent under `BEGIN IMMEDIATE`, insert exact `SQL_COMMITTED` ticket and rotate provider history through private `_history()._rotate_locked(q, ...)` in the same transaction. Then invoke the new acknowledgement mixin. Keep restart/historical recovery separate until this transition has focused regression coverage.