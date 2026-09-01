# LAB-092 public provenance verification vs concurrent rotation — negative audit

Date: 2026-09-01

## Objective

Audit the next reachable LAB-092 post-construction mutation/revalidation boundary without inventing a new contract: `verify_activation_schema_provenance()` may run while another actor advances provider generation / activation state.

## Exact surfaces inspected

LAB-092 current draft head `cc50513cfd867d8711fb29db8f33490200390d0d`, production source blob `fe9322800c41e5cbb641b4d86810e8f2cf0e8b0a`.

`verify_activation_schema_provenance()` currently performs:

1. local COMPLETE classification;
2. full provider-history + runtime-generation verification;
3. LAB-090 activation-record integrity verification;
4. `execute()` of the deterministic migration completion intent.

Inherited LAB-090 `_reauthenticate()` was inspected on exact base head `d9a381dd4607a928cd1315adef6431e239995bc1`, source blob `8140d6e180c3e97085830b872cea7d87f8433144`.

## Race analysis

The relevant race is a provider rotation after LAB-092's explicit authority/integrity checks but before marker `execute()`.

Two inherited paths exist:

### Marker already has a historical receipt

`_reauthenticate()` returns the stored receipt binding. This path performs no external reconcile and no new durable receipt mutation. A concurrent provider-generation advance can make the caller's runtime stale after the earlier read-only verification, but the marker operation itself does not create or rewrite authority/evidence in this path.

This is ordinary point-in-time concurrency rather than a demonstrated mutation-before-revalidation defect. Adding an exactly-at-return runtime-freshness contract would require a stronger linearizability requirement not currently stated by LAB-092 and would still need an explicit synchronization design.

### Marker receipt is absent

`_reauthenticate()` reads `provider_history.current()` again. If the migration entry's `(provider_id, provider_generation)` no longer equals the durable current generation, it raises `HistoricalVerificationError("historical ledger entry has no signed receipt evidence")` before external reconcile and before `store_receipt()`.

If generation remains current, `_runtime_matches_entry()` is then required before the external reconcile. Only a verified exact-position/request reconciliation can reach `store_receipt()`.

Therefore the concrete mutation hazard audited here — recreating a missing migration receipt after a concurrent provider rotation invalidated its generation authority — is already fail-closed.

## Decision

No LAB-092 production or regression change is justified by this boundary.

Do **not** add a regression that merely requires provider/runtime state to remain unchanged across an unsynchronized public verification call. That would create a new concurrency contract rather than reproduce a correctness/security violation.

The existing pre-auth checks remain necessary because they reject malformed provider history and activation records before a missing marker receipt can be recreated; this audit does not weaken those checks.

## Capability observation

LAB-086 was probed first. Local `git ls-remote` again failed before repository execution with `Could not resolve host: github.com`. The live LAB-086 `strict_fence.py` still conflict-checks to exact predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and the retained semantic patch is still exact blob `61841b58be42b01b97ca223567cbf9f428f7f0ce` on the LAB-086 branch.

The connector can return line-ranged exact source and full patch text, but the observed write action still accepts a complete UTF-8 replacement body rather than an executable file/reference. There is no supported automatic data-plane bridge from connector-fetched bytes/local reconstructed candidate into `update_file`; manual/model reserialization of security-critical `strict_fence.py` remains prohibited. No LAB-086 branch mutation was attempted.

## Next action

LAB-086 remains priority #1. Probe for a supported byte-preserving transfer/composition bridge first on the next run.

If unavailable and exact execution also remains unavailable, continue LAB-092 only at another concrete mutation/revalidation boundary. Prefer a path where durable state can actually be mutated before a required validation; record negative audits instead of adding speculative contracts.