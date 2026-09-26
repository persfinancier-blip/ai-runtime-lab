# LAB-086 combined thaw fix — published exact evidence

Date: 2026-08-27

## Publication

The combined NULL-safe/history-key thaw candidate was reconstructed from the exact prior runtime blob `cea0ca3b42723790971ba9415b70a7e9fa0c7368` and staged through the normal GitHub Contents API before touching runtime.

- staged file blob returned by GitHub: `080eb9454437932a8ab419d66a4f2a69ed17c7ce`;
- runtime update commit: `4570a19fb92f1222db64cb07f7e4ce6312630879`;
- runtime `experiments/asymmetric_break_glass_history/strict_fence.py` blob returned by GitHub: `080eb9454437932a8ab419d66a4f2a69ed17c7ce`;
- temporary staging file was then removed in commit `9cc464d156df95967d8019d10a5279515d54e7bf`.

The published bytes are therefore byte-identical to the previously focused-tested candidate.

## Exact post-publication focused gate

The following published test blobs were reconstructed locally and verified with `git hash-object` before execution:

- `test_strict_fence.py` — `97048a325c4cc1ed78612bdbb4cfec42146a43f6`;
- `test_thaw_null_proof_key_regression.py` — `fce5c57c8cfaa18f6761ae9b47c211813801aae0`;
- `test_thaw_history_key_collision_regression.py` — `88ba35e933c123d10af65597d6bb51f4f11068ec`;
- `test_thaw_proof_replace_regression.py` — `c511ccfc4b88b050910561b3b8f7e99be5f33e93`.

Published runtime + exact tests: **14/14 PASS**. `python -m compileall` over the focused reconstructed package also passed.

Coverage includes:

- NULL proof identities denied during thaw;
- existing proof keys cannot be replaced during thaw;
- existing public/root/provider/threshold history keys cannot be replaced during thaw;
- NULL identities on the seven INSERT-thawed history surfaces are denied;
- new unique non-NULL history/proof keys remain creatable by the legitimate thaw path;
- existing strict-fence DELETE/UPSERT/head/reinstall/rollback behavior remains green.

A small additional semantic smoke run of the three new thaw regression classes also passed 4/4 before the byte-exact combined run; the 14/14 exact run above is the evidence that counts.

## Gate consequence

The two known thaw identity blockers are resolved in published runtime. The next executable snapshot for the full branch-local LAB-080→086 gate must be pinned to runtime commit `4570a19fb92f1222db64cb07f7e4ce6312630879` (later note-only commits do not alter executable bytes). Keep PR #165 draft until the remaining full real-ledger suite, unsafe seed, compileall and final security/reconciliation audit are clean.
