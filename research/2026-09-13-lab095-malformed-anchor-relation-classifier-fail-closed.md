# LAB-095 malformed anchor relation classifier fail-closed fix

Date: 2026-09-13

## Context

LAB-086 remained the first priority probe in this run. Direct shell clone of the repository again failed before repository execution with `Could not resolve host: github.com` / exit 128, so no LAB-086 byte-exact gate was weakened and no new PASS is claimed.

The permitted fallback was LAB-095 / #180 / draft PR #187.

## Audit finding

The public read-only `classify_identity_custody()` had already been hardened for orphan LAB-095 intents, but its no-custody branch still treated a malformed same-name `shared_anchor_intents` relation as `ABSENT`.

Specifically, if custody was absent and `sqlite_master` contained `shared_anchor_intents` as a `VIEW`, the classifier skipped the table-only orphan check and returned `ABSENT`. That is not fail-closed: a malformed replacement of an authority-bearing relation must not be indistinguishable from a genuine legacy database with no LAB-095 custody.

## Fix

PR #187 production now distinguishes:

- no custody + no `shared_anchor_intents` relation -> `ABSENT`;
- no custody + exact `shared_anchor_intents` table with no LAB-095 intent -> `ABSENT`;
- no custody + exact table containing the LAB-095 identity intent -> `CORRUPT`;
- no custody + same-name non-table relation -> `CORRUPT`.

Production commit: `eb7ddca749eaa92f08af0211a23d2484b6644883`.
Production blob: `bac58a48c576001370144cc10cfab8e0cfd129e3`.

Regression added to `test_database_identity_orphan_intent_classifier.py` in commit `b1bfd7d54b568d3c3f1a935945550499e505fa05`, blob `4cfd6f6f8902cde415d86e37a3a25c1a7fdf960a`.

## Executed evidence

A narrow local file-backed SQLite semantic probe was executed for the exact new condition:

1. genuine legacy DB with no custody and no anchor relation -> `ABSENT`;
2. no custody plus same-name `shared_anchor_intents` VIEW -> `CORRUPT`.

Result: 2/2 PASS.

This probe validates the branch condition semantically; it is not a claim that the exact repository regression or full LAB-095/downstream suite is GREEN. Shell transport still cannot safely materialize the exact dependency closure.

## Audit boundary / next action

Keep PR #187 draft. The next retained gate remains execution of the already-committed crash-before-commit, partial-state, concurrent-installer, and legacy-prefix migration regressions on the smallest byte-exact closure that can be safely materialized, followed by DB-A -> DB-B and LAB-080/LAB-081/LAB-090/LAB-092 downstream gates.
