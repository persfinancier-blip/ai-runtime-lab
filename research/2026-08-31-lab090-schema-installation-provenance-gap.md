# LAB-090 activation schema installation provenance gap

Date: 2026-08-31

## Context

LAB-090 currently installs `provider_generation_activations` and `block_intent_during_provider_activation` with `IF NOT EXISTS`, then verifies the exact persisted table/trigger definitions. The retained atomic-install patch (#169 / PR #175) correctly closes the writer window between table and trigger creation by holding one `BEGIN IMMEDIATE` transaction across both definitions and both verification reads.

## Fresh audit finding

Exact-definition verification detects same-name object substitution (for example replacing the activation table with a VIEW) and detects trigger SQL tampering. It does not, and cannot with the current state model, distinguish a legitimate first LAB-090 migration from post-install deletion when both activation objects are completely absent.

On a database where both objects are absent, `CREATE TABLE IF NOT EXISTS` and `CREATE TRIGGER IF NOT EXISTS` recreate fresh objects. This behavior is required for a legitimate pre-LAB-090 database being upgraded for the first time. The same behavior also means a database that previously had LAB-090 installed but later lost the activation table/trigger is treated as a first install. Any deleted activation rows are therefore no longer observable to restart verification.

A simple rule that the activation table must already exist is not migration-safe, because historical provider-generation databases legitimately predate LAB-090. Therefore the gap cannot be safely repaired without a durable installation/provenance contract.

## Decision

Do not expand PR #175 with an ad-hoc schema marker. Keep the already-defined atomic installation fix in LAB-090. Track installation provenance/deletion detection separately as LAB-092 / issue #176, with explicit migration and authority acceptance criteria.

## Required properties for LAB-092

- first upgrade from a legitimate pre-LAB-090 database remains supported;
- successful LAB-090 installation leaves durable evidence that cannot be confused with first migration;
- marker creation is atomic with activation table/trigger installation or has deterministic crash reconciliation;
- after installation provenance exists, missing activation table/trigger fails closed or follows an explicitly justified repair protocol;
- the marker must not become an unguarded second authority surface;
- concurrent writers remain fenced throughout install/reconciliation.

## Tool/runtime observations

- GitHub connector reads/writes are available in this run.
- Direct `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed before repository execution with `Could not resolve host: github.com`.
- No exact branch behavioral/full-suite execution is claimed in this note.

## Related

- #169 / LAB-090
- PR #175
- #176 / LAB-092
- `research/patches/lab090-activation-schema-installation-transaction.patch`
