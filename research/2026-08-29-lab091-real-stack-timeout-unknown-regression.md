# LAB-091 real-stack timeout/UNKNOWN regression

Date: 2026-08-29

## Objective

Close the largest remaining proof gap in PR #173: existing timeout-after-commit/UNKNOWN coverage used a stubbed parent and did not execute the final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` against real LAB-080/LAB-082 classes.

## Source audit

The current stubbed regression `test_timeout_unknown_convergence.py` replaces both the shared-anchor protocol and the operation-scoped parent before importing the convergent class. It therefore proves the convergence algorithm only in isolation.

The real LAB-082 supported fixture already supplies the exact runtime pieces needed for a full-stack regression: `SignedAnchorProvider`, `AttestedCatchup`, `AttestationVerifier`, and `GenerationSigner`.

Current final LAB-091 class source was re-fetched from branch head and is blob `69c6b1070b1f65bb7c00b31a5c3cfce1c5d4a51f` at the time of this work. The lower operation-scoped integration source is blob `95b5a810a4dbac634ff88bc783d7a787ee769430`.

## Implemented regression

Added:

`experiments/mutable_shared_anchor_writer/tests/test_real_stack_timeout_unknown_convergence.py`

Published blob: `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`

Branch commit: `5a72cbc3c1dda94d7ef3da19b776ab3afebc7c20`

The test imports the final supported LAB-091 class directly and uses real LAB-080/LAB-082 runtime types. No module stubs are installed.

Scenario:

1. create a real file-backed final ledger with provider position 0;
2. execute one intent with `timeout_after_commit=True`;
3. provider commits the increment, then the first reconciliation path is made unavailable;
4. require `PendingIntent`, durable PREPARED state, no durable asymmetric receipt, provider position 1, and exactly one increment call;
5. retry the same intent;
6. require CONFIRMED state, exactly one durable asymmetric receipt, no second provider increment, and a clean `verify_durable()`;
7. reconstruct the final supported ledger against the same DB/provider and execute the same intent again;
8. require identical confirmed result, no second increment, and clean durable verification after restart.

This specifically exercises the interaction of LAB-080 request identity/state, LAB-082 Ed25519 historical receipts, LAB-091 one-shot DML permits, deterministic/history-binding guards, confirmation convergence, and restart-safe adoption.

## Validation actually performed

The exact test body was parsed with Python `ast.parse`: PASS.

After Contents-API publication, the file was re-fetched and is exact blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`.

The behavioral unittest was **not executed in this run**. Direct `git clone` from the executable shell failed before byte transfer because `github.com` DNS could not resolve. The available GitHub connector can read/write repository text but does not mount a checkout into the executable filesystem. An attempted raw-download bridge also could not be established for this private repository. Therefore this note does not claim a behavioral PASS.

## Decision / next action

Keep PR #173 draft.

Highest-value next action is to execute this exact published test blob against the branch-local dependency closure as soon as a supported checkout/file bridge is available. If it passes, immediately add/execute the analogous real-stack two-worker/crash regression. If it fails, fix the real-stack defect rather than weakening the test.

LAB-086 remains first priority whenever its exact candidate can be published byte-preservingly.
