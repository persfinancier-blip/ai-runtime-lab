# LAB-092 locked activation-provenance receipt guard

Date: 2026-09-15

## Objective

Compose the smallest LAB-092 provenance slice onto the LAB-095/LAB-096 authority base in PR #187 without reintroducing either post-construction provider-history replacement or a check/use race around historical receipt persistence.

## Runtime observation

The mandatory LAB-086 probe was attempted first:

```text
git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git
fatal: unable to access ...: Could not resolve host: github.com
exit 128
```

No repository code executed and no LAB-086 PASS is claimed.

## Source audit

LAB-092 PR #177 currently combines several concerns in `activation_schema_provenance.py`:

- exact activation table/trigger classification;
- migration-marker classification;
- explicit migration;
- construction of a reservation surface;
- live provider-history replacement with `_ProvenanceBoundCoordinatorOnlyProviderHistory`;
- locked provider-history verification through public `provider_history`.

The final two mechanisms are incompatible with LAB-096. PR #187 already provides the required transaction-owned extension point: `_guard_receipt_persistence_locked(q)` executes inside the same `BEGIN IMMEDIATE` transaction as receipt verification and insertion.

## Implemented slice

PR #187 now contains `experiments/provider_generation_history/activation_schema_provenance.py` with only the authority-neutral classifier/guard subset:

- migration intent identity/payload;
- exact activation table/trigger classification using shared `activation_schema.py` definitions;
- exact marker classification against the deterministic migration intent payload digest;
- `classify_activation_schema_provenance_locked(q)`;
- `require_complete_activation_schema_provenance_locked(q)`;
- `ActivationSchemaProvenanceReceiptGuardMixin`.

Important properties:

1. The classifier accepts the caller-owned SQLite connection and never opens, commits, rolls back, or closes a connection.
2. COMPLETE requires exact activation table DDL, exact activation trigger DDL, and exact CONFIRMED migration marker identity/payload digest.
3. PREPARED/CONFIRMED provenance with missing or mismatched DDL fails closed.
4. Marker substitution fails closed.
5. The mixin checks COMPLETE before delegating to the next receipt guard in MRO and carries no provider-history object/reference.
6. No `_bind_live_provider_history_provenance()` exists and no `_provider_history` replacement occurs.

Branch commits:

- production classifier/guard: `1620b4e76b474f38e28f022002be486282dd10de`;
- focused regressions/current head: `6fd9300a9efab730cb86342cf63a43227ea45406`.

Published production blob was re-fetched as `355bb4a32c54a9471a5b296deffa27af6f6ffd30`.

## Focused regressions added

`test_activation_schema_provenance_guard.py` covers:

- COMPLETE classification while preserving ownership of the caller's active transaction;
- CONFIRMED marker + missing DDL -> fail closed;
- CONFIRMED marker + mismatched DDL -> fail closed;
- marker payload substitution -> fail closed;
- exact but unmarked DDL -> receipt guard rejects before downstream guard invocation;
- COMPLETE -> downstream guard receives the exact same connection object.

## Executed validation

Because the exact repository closure still cannot be materialized into the executable filesystem, full branch pytest is not claimed.

An isolated SQLite behavioral probe of the authored classifier semantics was executed locally and observed:

```text
COMPLETE, transaction still active
missing DDL -> fail closed, transaction still active
mismatched DDL -> fail closed, transaction still active
marker substitution -> fail closed, transaction still active
exact unmarked DDL -> DDL_INSTALLED_UNMARKED
no activation DDL/marker -> LEGACY_ABSENT
```

A separate MRO guard probe confirmed that an incomplete provenance check prevents downstream guard invocation, while COMPLETE delegates with the same supplied object.

These are focused semantic probes, not an exact-repository GREEN.

## Security/composition decision

Do not wire the mixin into the default supported ledger yet. PR #187 does not yet contain LAB-090 activation installation/fencing behavior, so making COMPLETE mandatory for the default ledger would break legitimate pre-composition construction and could create an accidental migration policy change.

Safe composition order remains:

1. PR #187 authority base;
2. shared immutable activation schema definitions;
3. locked LAB-092 classifier/receipt guard;
4. explicit LAB-092 migration/startup semantics adapted to `_history()` and construction-bound strategy;
5. LAB-090 activation fencing semantics;
6. exact/downstream gates before leaving draft.

## Next action

After the mandatory LAB-086 transport probe, port the next smallest LAB-092 startup/migration slice onto PR #187:

- replace path-opening `_classify(path)` calls with transaction-scoped classification where mutation follows;
- construct reservation surfaces with one-time canonical path/history binding only;
- route all locked history verification through private `_history()`;
- omit `_bind_live_provider_history_provenance()` entirely;
- preserve explicit-migration-only behavior for LEGACY_ABSENT / DDL_INSTALLED_UNMARKED / DDL_INSTALLED_PREPARED;
- add focused startup/migration fail-closed tests before bringing over LAB-090 mutation/fencing behavior.
