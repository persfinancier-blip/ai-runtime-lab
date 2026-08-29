# LAB-091 timeout/UNKNOWN provider mechanism probe — 2026-08-29

## Scope

This run attempted the exact next action from `state/CURRENT.md`: execute published branch blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e` (`test_real_stack_timeout_unknown_convergence.py`) against the real LAB-080/LAB-082 dependency closure.

The exact branch HEAD was confirmed as `5a72cbc3c1dda94d7ef3da19b776ab3afebc7c20`. Connector reads can retrieve exact UTF-8 source, but the executable shell still cannot resolve `api.github.com` or `raw.githubusercontent.com`; a direct Python `urllib.request` probe failed with `Temporary failure in name resolution`. The available connector does not mount the branch checkout into the executable filesystem. Therefore the full branch-local unittest was **not** executed and is not counted as PASS.

## Source inspection

The published regression uses real:

- `SignedAnchorProvider`, `AttestedCatchup`, `AttestationVerifier` from LAB-036;
- `GenerationSigner` and asymmetric provider history from LAB-082;
- final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` from LAB-091.

The critical external sequence is determined by current exact `experiments/anchor_attestation/protocol.py` blob `15d8b7cf8ff093490ccb75679030d3a0fe41e401`:

1. `SignedAnchorProvider.increment()` increments `increment_calls`, commits `value += 1`, stores `_request_results[request_id]`, then raises `UnknownOutcome` when `timeout_after_commit=True`.
2. `AttestedCatchup.catch_up_one()` catches `UnknownOutcome` and immediately calls `reconcile_increment()`.
3. The regression's provider subclass makes only that first reconciliation unavailable.
4. On retry, `catch_up_one()` performs an authenticated READ. Because provider position already equals `db_sequence`, it returns without calling `increment()` again.
5. LAB-091 then performs `_reauthenticate()`, whose reconciliation can recover the stored request result and persist the asymmetric RECONCILE receipt.

## Executed focused mechanism probe

A local executable semantic probe reproduced exactly that state transition ordering and asserted:

- first call commits provider position `0 -> 1`;
- first reconciliation raises provider-unavailable after the commit;
- provider `increment_calls == 1`;
- retry sees position `1 == db_sequence` and does not increment again;
- later reconciliation returns the stored request result;
- provider remains position `1`, `increment_calls == 1`.

Observed result:

`PASS timeout-unknown provider mechanism: committed once, first reconcile unavailable, retry observes target without reincrement, later reconcile succeeds`

This is mechanism evidence only. It does **not** prove SQLite PREPARED/receipt/CONFIRMED persistence, restart verification, LAB-091 trigger/permit behavior, or the full final-class dependency composition.

## Audit finding

Static inspection found no contradiction between the published real-stack regression and LAB-036 timeout semantics. In particular, the retry does not depend on provider idempotent re-increment: it takes the `current.position == db_sequence` READ path, then the ledger's explicit reconciliation path supplies RECONCILE evidence.

## Next action

Keep PR #173 draft. At the first supported branch-to-executable-filesystem bridge, execute exact test blob `92133cdc...` at branch HEAD (or repin if HEAD changes) and require the behavioral unittest itself to pass before claiming the timeout/UNKNOWN real-stack gate. If it passes, proceed to the analogous final-class two-worker/crash regression with real LAB-080/LAB-082 dependencies.
