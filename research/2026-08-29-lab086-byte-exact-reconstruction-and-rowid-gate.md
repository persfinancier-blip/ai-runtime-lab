# LAB-086 byte-exact reconstruction and hidden-rowid candidate gate

Date: 2026-08-29

## Objective

Remove the previous uncertainty around materializing the live `strict_fence.py` bytes in an executable filesystem, then re-derive and execute the retained hidden-rowid candidate without hand-rewriting the security-critical runtime.

## Source reconstruction

The GitHub connector was used to fetch the live branch file `experiments/asymmetric_break_glass_history/strict_fence.py` from `lab/086-asymmetric-break-glass-history` in four exact line ranges (1-200, 201-400, 401-600, 601-800, 801-end). The ranges were concatenated verbatim in the executable filesystem.

Observed reconstructed source:

- lines: 949
- bytes: 37,513
- Git blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`

This exactly matches the live branch blob. The previous read-side/materialization blocker is therefore removed for this file: the connector response can be reconstructed in an executable filesystem and independently authenticated by Git blob identity.

## Candidate derivation

The durable semantic patch `research/2026-08-28-lab086-hidden-rowid-replace.patch` was re-read from the branch. It is a semantic research diff with bare `@@` markers, so GNU `patch` correctly rejected it as non-standard input. No claim was made that GNU patch applied it.

Instead, the patch was applied as nine exact-string replacements. Each replacement required exactly one match in the authenticated predecessor source; execution aborted if any match count differed from one.

All nine replacements matched exactly once.

Observed candidate:

- lines: 1,007
- bytes: 39,854
- Git blob: `b78e7c98e35138719f77c482c7f1aab36b702de7`

This exactly matches the retained previously tested hidden-rowid candidate recorded in `state/CURRENT.md`.

`python -m py_compile experiments/asymmetric_break_glass_history/strict_fence.py` passed on the re-derived candidate.

## Fresh focused execution

A minimal in-memory SQLite schema was created with:

- the LAB-086 cutoff boundary;
- `asymmetric_provider_generations` including its alternate `UNIQUE(provider_id,generation)` identity;
- one post-cutoff evidence table;
- `asymmetric_provider_receipts`.

The exact candidate internal installers were executed. Seed rows were installed before re-enabling the candidate fences. The fresh gate verified:

1. explicit hidden-rowid collision cannot replace an authenticated provider-generation row;
2. explicit hidden-rowid collision cannot replace post-cutoff evidence;
3. explicit hidden-rowid collision cannot replace a provider receipt;
4. explicit `rowid=-1` is rejected for authenticated provider-generation history;
5. explicit `rowid=-1` is rejected for provider-receipt history;
6. required rowid-sentinel triggers are present for provider-generation history, post-cutoff evidence, and provider receipts.

Result: `focused rowid mechanism: PASS` with 11 relevant triggers present in the minimal schema.

This is a fresh mechanism gate on the exact `b78e7c98...` candidate, not a substitute for the full strict/thaw or LAB-080->086 real-ledger gate.

## Publication status

The candidate is still not published to PR #165 in this run. The normal Contents API requires the complete UTF-8 replacement body in the connector call, while the executable filesystem and GitHub connector remain separate data planes and the available shell cannot resolve GitHub. The local candidate is authenticated by the expected Git blob, but there is not yet a supported direct file-reference argument for `update_file`.

Do not use low-level blob/tree/ref manipulation or force ref updates to bridge this gap.

## Decision / next action

LAB-086 remains first priority.

1. Preserve predecessor `d4a6a40f...` and candidate `b78e7c98...` as exact pins.
2. If a supported byte-preserving Contents-API bridge becomes available, conflict-check that branch `strict_fence.py` is still `d4a6a40f...`, publish the complete candidate, require returned/re-fetched blob `b78e7c98...`, then execute the four focused regressions, strict/thaw subgate, compileall, and LAB-080->086 real-ledger gate.
3. Until publication is possible, do not repeat predecessor reconstruction unless the live blob changes. The reconstruction/materialization question is now answered by exact blob evidence.
