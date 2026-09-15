# LAB-090 provider activation fence semantic port onto PR #187

Date: 2026-09-15

## Runtime observation

LAB-086 was probed first with direct `git clone --no-checkout`. Git transport failed before repository code execution because the shell could not resolve `github.com` (exit 128). No LAB-086 PASS is claimed.

## Change

Ported only the provider-owned activation fencing primitive from LAB-090 PR #175 onto the LAB-095/LAB-096 composition branch. Deliberately did not select or copy LAB-090 `supported.py` or `integration.py`.

The new `experiments/provider_generation_history/activation.py` keeps the external linearization semantics isolated from coordinator SQLite authority:

- `prepare_activation()` checks exact provider position and installs a monotonically fenced provider-owned ticket;
- ordinary `increment()` fails while a ticket is pending;
- `commit_activation()` records provider commitment but deliberately keeps the fence installed;
- only exact-ticket `release_activation()` removes a committed fence;
- `UnknownOutcome` after provider commit remains reconcilable as `COMMITTED_FENCED`;
- shared `ActivationState` models provider-side durability across coordinator reconstruction;
- stale candidates and mismatched tickets fail closed.

This slice does not access the ledger, database binding, provider-history strategy, receipt path, or LAB-092 provenance machinery. It therefore preserves PR #187's private `_history()`, construction-bound strategy, canonical database binding, least-capability public inspection, and same-transaction receipt provenance guard by remaining below those layers.

## Regression coverage

Added `tests/test_activation_fence_composed.py` covering:

1. PREPARED and COMMITTED_FENCED both block ordinary external advance until exact release;
2. stale provider position and wrong release ticket fail closed;
3. unknown commit outcome plus reconstructed provider sharing durable activation state preserves the fence.

Exact repository execution is not claimed because the current runtime still lacks a byte-preserving connector-to-executable-filesystem bridge. The source was conflict-checked by fetching the target branch path first; `activation.py` did not exist on PR #187 before creation.

## Audit

The port is intentionally narrower than PR #175. Coordinator activation-record persistence, SQL_COMMITTED/COMMITTED acknowledgement ordering, restart reconciliation against SQLite, overlapping-rotation blocking, and historical unresolved activation handling are not yet ported. Those remain the next semantic layer and must compose through PR #187 authority boundaries rather than importing LAB-090 authority-heavy files wholesale.
