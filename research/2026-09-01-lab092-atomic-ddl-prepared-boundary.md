# LAB-092 — atomic activation DDL + PREPARED provenance boundary

Date: 2026-09-01

## Context

LAB-092 draft PR #177 previously installed the exact LAB-090 activation table+trigger first and reserved the deterministic authenticated migration marker in a later SQLite transaction. That left an observable interval where activation DDL was committed while the migration marker was still absent. A different shared-anchor writer could reserve the next position in that interval.

## Decision

The migration boundary is now one SQLite writer transaction:

1. acquire `BEGIN IMMEDIATE`;
2. classify the activation table/trigger and existing migration marker under that lock;
3. allow only the unambiguous recoverable states: both DDL objects absent with marker absent, both exact with marker absent, or both exact with the exact marker PREPARED;
4. reject partial/mismatched DDL, any marker/DDL mismatch, stale runtime provider identity, and any unrelated PREPARED shared-anchor intent;
5. if DDL is absent, create the exact LAB-090 table and trigger;
6. reserve the deterministic migration intent as the single PREPARED shared-anchor tail using LAB-081/LAB-080 identity primitives (`_current_locked`, `_descriptor_from_attested`, `_request_id`, exact reserved-position CAS semantics);
7. re-read exact DDL and PREPARED marker before commit;
8. commit once, making DDL and PREPARED provenance visible together;
9. only after that commit perform the external anchor effect and confirm the exact PREPARED marker through the inherited supported ledger.

This keeps external confirmation outside the SQLite transaction while preventing a durable or externally visible DDL-without-marker window.

## Published implementation

PR #177 / branch `lab-092-activation-schema-provenance`:

- atomic implementation commit `6aaab4e72144ad7fc4309f1054b4881187c2c22d`;
- crash/concurrency-boundary regression commit `3590acee6e42685524e59ce123767003cba32cc6`;
- reservation-surface hardening commit/current head `30b0ecfd92d15b84ee5565a92cb4304b581f1348`;
- current `activation_schema_provenance.py` blob `46b8edc72d76921d638c4efad35cba16777a8064`;
- regression blob `fc51685da555306326e6313182bdf1c1d0a2ebd4`.

The test models a crash immediately after the atomic SQLite commit and requires exact table + exact trigger + exactly one PREPARED migration row. A different writer must then be rejected by the inherited `PendingIntent` rule, and explicit migration must resume that same marker to CONFIRMED rather than create another row.

## Executed validation in this run

Exact repository checkout was attempted first with:

`git clone --depth 1 --branch lab-092-activation-schema-provenance https://github.com/persfinancier-blip/ai-runtime-lab.git ...`

It failed before repository code execution with `Could not resolve host: github.com`. Therefore no branch-level unittest GREEN is claimed.

A standalone file-backed SQLite visibility probe was executed for the transaction mechanism. While the installer held an uncommitted `BEGIN IMMEDIATE` transaction containing table creation, trigger creation and PREPARED insertion, a concurrent reader observed `(DDL absent, marker absent)`. After commit, the same reader observed `(DDL present, marker PREPARED)`. It never observed `(DDL present, marker absent)`. Result:

- pre-commit: `(None, None)`;
- post-commit: `(('table',), ('PREPARED',))`.

This validates SQLite visibility semantics of the chosen boundary but is not a substitute for exact branch tests.

## Reservation-surface audit

A follow-up audit found two avoidable authority/initialization ambiguities and both were tightened in commit `30b0ecfd...`:

1. `_reservation_surface` now requires `type(attested) is AttestedCatchup`, matching the exact LAB-036 type requirement used by the supported historical ledger instead of accepting any object that merely exposes `.verifier`.
2. `_classify()` no longer treats a completely absent `shared_anchor_intents` relation as a legitimate legacy activation-schema state. LAB-092 is a migration of an existing LAB-080/081 authority surface; it must not bootstrap a missing shared-anchor ledger as an incidental side effect of activation-schema repair.

The helper still constructs `CoordinatorOnlyProviderHistory` to reuse durable provider-history verification/current-generation semantics. Exact branch tests remain required before this candidate can be called GREEN.

## Security/correctness invariants retained

- ordinary startup never installs or repairs missing activation DDL;
- CONFIRMED marker + missing/mismatched DDL remains fail-closed;
- PREPARED marker + missing/mismatched DDL remains fail-closed;
- partial or same-name mismatched DDL with no marker remains fail-closed;
- unresolved LAB-090 activation must still block insertion of the migration marker through the activation trigger;
- no unauthenticated local provenance marker is introduced;
- the marker remains a normal authenticated shared-anchor `migration` intent;
- migration cannot silently bootstrap a missing shared-anchor authority surface.

## Remaining work

1. Execute exact PR #177 regressions when source checkout/execution transport is available, including atomic boundary, unresolved activation, deletion/mismatch, PREPARED recovery, and legitimate legacy migration.
2. Add and execute a stale-runtime-provider regression at the atomic migration boundary; expected result is fail-closed before DDL+marker commit.
3. Reconcile PR #177 branch/base conflict state only after behavioral gates are GREEN.
4. LAB-086 remains higher priority and must still use only exact byte-preserving predecessor+patch publication.
