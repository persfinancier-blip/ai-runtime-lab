# LAB-086 direct-IP egress probe and LAB-095 DB-binding audit

Date: 2026-09-14

## LAB-086 mandatory first probe

Direct `git clone` from the executable runtime again failed before repository execution because `github.com` could not be resolved.

A stronger transport diagnostic was then performed without changing repository state or weakening any security gate:

1. Google Public DNS was queried externally for current A records.
2. `github.com` resolved to `20.200.245.247`.
3. Git was re-run with libcurl `http.curloptResolve=github.com:443:20.200.245.247`, preserving the HTTPS hostname/SNI while bypassing only local DNS resolution.
4. The TCP connection to `20.200.245.247:443` was refused immediately; Git exited 128 before any repository content was transferred.
5. `raw.githubusercontent.com` current A records were also obtained (`185.199.111.133`, `185.199.108.133`, `185.199.110.133`, `185.199.109.133`). A `curl --resolve raw.githubusercontent.com:443:185.199.111.133 ...` byte-preserving fetch attempt was likewise refused before content transfer.

Conclusion: the current executable runtime blocker is stronger than DNS failure alone. Direct outbound TCP/443 to the tested GitHub endpoints is not usable even when name resolution is supplied explicitly. No LAB-086 executable PASS is claimed. The authoritative complete-gate pin remains `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.

This also explains why a connector-only control-plane read remains usable while a connector -> executable-filesystem byte-preserving bridge is still required for full exact execution.

## LAB-095 fallback: DB-A -> DB-B binding static audit

While exact eight-file same-run materialization remains blocked by the connector/filesystem boundary, the next committed DB-binding regression and composition were inspected on PR #187 head `835a81914c5234e68ef436e30c9837331d262432`.

### Regression shape

`test_database_path_binding.py`:

- constructs `SupportedHistoricalSharedAnchorLedger` on DB A;
- advances provider history to generation 2;
- copies DB A to DB B;
- corrupts DB B's transition MAC while preserving a superficially matching generation-2 head;
- attempts public rebinding of both `ledger.path` and `ledger.provider_history.path` to DB B;
- attempts direct rebinding of each private canonical path slot;
- requires all rebinding attempts to fail;
- re-verifies durable state on DB A;
- executes a new intent and proves only DB A changes while DB B's tail and intent set remain unchanged.

This directly exercises the acceptance criterion that a matching current head in DB B is insufficient authority when its full provider history is invalid.

### Composition audit

The binding is present transitively on the ledger MRO:

- `HistoricalSharedAnchorLedger` inherits `SupportedSharedAnchorLedger`;
- `SupportedSharedAnchorLedger` inherits `CanonicalDatabaseBinding, SharedAnchorLedger`;
- therefore `SupportedHistoricalSharedAnchorLedger(HistoricalSharedAnchorLedger)` retains the canonical binding even though its constructor calls `SupportedSharedAnchorLedger.__init__` explicitly.

The provider-history helper is independently bound:

- `CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory)`;
- `SupportedHistoricalSharedAnchorLedger.__init__` constructs exactly that helper using the same path before ledger initialization.

Internal operations continue consuming `self.path` / `provider_history` through the bound source of truth. The inspected DB-A -> DB-B regression is therefore aligned with the implementation architecture; no new path-binding defect was identified by this static audit.

This is not behavioral GREEN. The test still requires exact executable closure.

## Decision

Keep PR #187 draft. Do not weaken the requirement for same-run exact materialization and no-stub execution. The next run must probe LAB-086 first. If direct transport remains unavailable, prefer any newly exposed supported byte-preserving connector/file materialization path; otherwise continue with auditable connector-side static/security work and persist exact blockers rather than fabricating executable evidence.
