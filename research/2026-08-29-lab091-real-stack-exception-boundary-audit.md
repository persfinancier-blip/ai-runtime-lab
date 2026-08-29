# LAB-091 real-stack exception-boundary audit — 2026-08-29

## Scope

Fallback audit while LAB-086 exact byte-preserving publication remains tool-limited.

The current run re-read the durable control plane and inspected the exact published LAB-091 real-stack timeout regression plus the final supported class inheritance path on branch `lab/091-mutable-shared-anchor-writer`.

## Per-run capability observations

- `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed with `Could not resolve host: github.com`.
- GitHub connector reads and normal Contents writes are available.
- No supported machine-to-machine bridge was observed that can transfer the exact 949-line LAB-086 `strict_fence.py` predecessor, apply the retained patch byte-preservingly, and feed the resulting exact bytes to Contents `update_file` without model/manual reserialization.
- Therefore no LAB-086 branch mutation was attempted.

## Exact-source audit

Published real-stack timeout regression:

- `experiments/mutable_shared_anchor_writer/tests/test_real_stack_timeout_unknown_convergence.py`
- blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`

The test requires:

1. provider increment commits exactly once;
2. the first reconciliation becomes unavailable;
3. first `execute(..., timeout_after_commit=True)` returns `PendingIntent` with durable PREPARED state and no persisted receipt;
4. retry reconciles the already-committed request without re-increment;
5. exactly one asymmetric provider receipt is persisted;
6. restart returns the same CONFIRMED entry and still does not re-increment.

Final supported class path inspected:

`SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`
-> `SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger`
-> `SupportedConvergentOperationScopedAsymmetricSharedAnchorLedger`
-> `SupportedOperationScopedAsymmetricSharedAnchorLedger`.

The important exception boundary is in `convergent_operation_scoped.py`: the final convergence path catches only `ProviderUnavailable` and `UnknownOutcome` around provider catch-up / reauthentication and maps only those retryable external-outcome classes to `PendingIntent`. It does **not** swallow arbitrary integrity, substitution, history-verification, SQL, or programming failures. This is materially stronger than the broader predecessor integration surface and is consistent with the published real-stack timeout regression's intent.

The inspected final `_con()` surface remains an exact `PermitConnection`, installs one-shot permit and row-token UDFs, and uses `BEGIN IMMEDIATE` for consequential writes. Provider/network calls occur outside one-shot permit scope. No new reachable alternate-write/reentrancy bypass was established in this audit.

## Result

No new code change is justified by this pass. In particular, do not broaden the final convergence exception handler: doing so would risk converting security/integrity defects into apparently retryable UNKNOWN outcomes.

The missing acceptance evidence remains **execution**, not another narrow static patch: the exact real-stack timeout blob `92133cdc...` and process concurrency/crash blob `93887747...` still need to execute against their complete published dependency closure.

## Next action

1. LAB-086 remains first priority: publish only exact hidden-rowid target `b78e7c98...` when a supported byte-preserving composition bridge exists, then run its full security gate.
2. If LAB-086 remains transport-limited, obtain a supported branch-to-executable-filesystem path and execute exact LAB-091 timeout/UNKNOWN `92133cdc...` and process concurrency/crash `93887747...` regressions against the final supported class.
3. Do not substitute additional static/narrow probes for those two missing real-stack gates unless a newly demonstrated reachable mutation mechanism is found.
