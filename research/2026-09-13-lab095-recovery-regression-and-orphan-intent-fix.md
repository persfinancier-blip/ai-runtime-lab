# LAB-095 recovery regressions and orphan-intent fail-closed fix

Date: 2026-09-13

## Context

LAB-086 remained priority #1 and was re-probed first. Direct shell clone of `https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com` / exit 128. The LAB-086 byte-exact gate was not weakened and no new LAB-086 PASS is claimed.

Per `state/CURRENT.md`, work therefore continued on LAB-095/#180 draft PR #187.

## Recovery regression slice added

Added `experiments/provider_generation_history/tests/test_database_identity_migration_recovery.py` with focused contracts for:

1. **Crash before PREPARED commit** — inject failure at `secrets.token_bytes()` after `BEGIN IMMEDIATE` and custody DDL, requiring rollback of the custody relation, zero identity intent, and unchanged shared-anchor tail.
2. **Partial state: orphan CONFIRMED identity intent** — persisted identity intent without custody must fail as corruption before CSPRNG nonce generation and without durable mutation.
3. **Concurrent installers** — two simultaneous installers must serialize and converge on one custody row, one nonce/request identity, one PREPARED intent, and one tail increment.
4. **Legacy-history migration** — with an existing confirmed shared-anchor prefix, identity installation must reserve exactly the next position while preserving the prefix.

Commit adding the regression file on PR #187: `884d7ea40d60cf5e5f8c2cb8a25a730240aff3ac`.

## Defect found during the regression audit

The existing `_classify_locked()` in `database_identity_migration.py` returned `ABSENT` whenever the custody table existed but had zero rows, without first checking whether the reserved LAB-095 identity intent already existed.

Consequences:

- orphan PREPARED intent happened to be rejected later by the generic `status='PREPARED'` guard;
- orphan CONFIRMED intent bypassed that guard, causing a new CSPRNG nonce to be generated and only then failing on duplicate `intent_id` insertion;
- this violated the frozen LAB-095 state-machine rule that `intent without custody` is `CORRUPT` and must fail closed before generating a replacement identity candidate.

## Production fix

Updated `database_identity_migration._classify_locked()` so zero custody rows now query specifically for `IDENTITY_INTENT_ID`:

- no custody + no identity intent -> `ABSENT`;
- no custody + existing identity intent in any status -> `CORRUPT`.

The fix is intentionally identity-specific rather than treating unrelated historical shared-anchor rows as corruption, preserving legacy migration from a valid existing prefix.

Published production blob: `816afb8c3e6bd96ee5ba30061f304fd104dc7a5b`.
Branch commit: `ac16e417cea6bfb930cb38e1755d205926c083a9`.

## Executed evidence

The complete repository dependency closure is still not safely materialized in this runtime, so the new repository regression file is **not** claimed GREEN.

A focused SQLite semantic probe was executed for the exact new classifier slice:

- empty custody/no LAB-095 intent -> `ABSENT`;
- empty custody/orphan CONFIRMED LAB-095 intent -> `CORRUPT`;
- SQLite transactional DDL created after `BEGIN IMMEDIATE` and followed by rollback leaves no custody relation, confirming the crash-before-commit rollback premise used by the regression.

This is narrow semantic evidence only, not a substitute for the exact repository test gate.

## Audit follow-up

The public read-only `database_identity.classify_identity_custody()` still returns `ABSENT` on zero custody rows before checking for an orphan LAB-095 identity intent. That is now inconsistent with the migration's locked classifier. This should be corrected next with a dedicated public-classifier regression so both classifiers share the same fail-closed partial-state semantics.

PR #187 remains draft. Full DB-A/DB-B and LAB-080/LAB-081/LAB-090/LAB-092 downstream gates remain required before integration.
