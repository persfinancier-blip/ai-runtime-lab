# LAB-092 — migration completion marker is pre-seedable through the pre-LAB-092 supported ledger

Date: 2026-09-03

## Finding

PR #177 treats one deterministic row in `shared_anchor_intents` as authenticated evidence that the LAB-092 activation-schema migration protocol completed:

- intent id: `migration:provider-generation-activation-schema:v1`
- component: `provider-generation-activation-schema`
- type: `migration`
- payload: `{"schema":"provider-generation-activation","version":1}`
- status: `CONFIRMED`

However, the underlying LAB-080 public `Intent` contract already allows arbitrary non-empty `intent_id` / `component_id`, allows the generic `migration` intent type, and does not reserve the LAB-092 identifier/component namespace. `SharedAnchorLedger.execute()` can therefore create and externally confirm this exact row before LAB-092 exists.

The resulting receipt proves only that the generic shared-anchor operation was confirmed. It does **not** prove the LAB-092 ordering predicate "exact activation DDL was installed/verified first, then this marker was reserved and confirmed by the explicit migration path".

## Concrete schedule

1. Start from a legitimate pre-LAB-092 database whose shared-anchor ledger is operational.
2. Through the supported pre-LAB-092 ledger API, execute an ordinary `Intent` whose fields are byte-for-byte equal to PR #177 `_completion_intent()`.
3. The row becomes `CONFIRMED` and receives a valid external-anchor receipt. No LAB-092 migration protocol has run.
4. Separately, reach a database state with exact LAB-090 activation table + trigger. This is realistic on the PR dependency lineage because LAB-090 itself owns/installs that DDL before LAB-092 changes startup provenance semantics.
5. Start the LAB-092 surface.
6. `_marker_state()` accepts the pre-seeded row solely from its generic row contents/status. `_classify()` therefore returns `COMPLETE` when the DDL is exact.
7. Constructor confirmation reauthentication validates the generic ledger receipt, but still cannot establish that the row was created *after and inside* the explicit LAB-092 DDL-installation transaction/protocol.

Thus `COMPLETE` can be assembled from two individually legitimate historical facts that were never causally linked by the migration protocol.

## Why this is distinct from retained LAB-092 findings

- Not the carrier-schema-authentication gap: even an exact `shared_anchor_intents` schema is vulnerable.
- Not a check/use TOCTOU: no concurrent mutation is required.
- Not post-install deletion: all rows and DDL can be intact.
- This is a provenance confused-deputy / namespace-domain-separation defect: a generic preexisting authorization surface can mint the exact token later interpreted as special migration authority.

## Security/correctness consequence

LAB-092's marker authenticates row contents and external-anchor history, but not the **protocol event** it is intended to attest. A pre-LAB-092 caller with ordinary supported migration-intent authority can manufacture a future LAB-092 completion token without executing LAB-092's DDL-first migration path.

A second compatibility consequence also exists: any historical use of the same fixed `intent_id` with different content permanently makes `_marker_state()` raise `HistoricalVerificationError`, so rollout correctness also depends on an identifier namespace that was never previously reserved.

## Regression-first contract

Add a deterministic regression that:

1. constructs the pre-LAB-092 supported ledger;
2. confirms the exact future LAB-092 completion intent through the ordinary inherited `execute()` path;
3. establishes exact LAB-090 activation DDL independently of `migrate_activation_schema_v1()`;
4. demonstrates the pre-fix LAB-092 classifier/startup accepts the assembled state as `COMPLETE`;
5. post-fix requires fail-closed or an explicit migration transition that can prove the completion authorization was minted by the LAB-092 migration protocol, not merely by a generic historical ledger writer.

Also add a namespace-collision regression with the same intent id but different legitimate historical content.

## Design constraint

Do not fix this only by changing the magic intent-id string. Any publicly mintable generic row shape remains pre-seedable.

The completion evidence needs domain-separated authority that was unavailable to the pre-LAB-092 generic ledger surface, or must be cryptographically/durably bound to an authenticated migration transition containing the exact DDL/schema identity and ordering evidence. That proof must compose with the already-retained requirement that carrier-schema proof and provenance checks share the consequential serialization/authority boundary.

## Source evidence

PR #177 `activation_schema_provenance.py`:
- `_completion_intent()` defines the fixed generic `Intent`.
- `_marker_state()` accepts it by component/type/payload digest/status only.
- `_classify()` returns `COMPLETE` for exact DDL + that `CONFIRMED` row.
- constructor reuses inherited `execute(_completion_intent())` for reauthentication.

Main `experiments/shared_anchor_intent_ledger/protocol.py`:
- `ALLOWED_INTENT_TYPES` already includes `migration`.
- `Intent.validate()` imposes no reserved namespace/domain rule on `intent_id` or `component_id`.
- `SharedAnchorLedger.execute()` can reserve, externally advance, reauthenticate, and confirm any such valid generic intent.

No exact branch behavioral execution is claimed in this run; this is a source-level authority/provenance proof. LAB-086 remains priority #1.
