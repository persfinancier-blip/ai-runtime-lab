# LAB-091 — Mutable shared-anchor writer authorization

LAB-080/LAB-082 contain state that must remain mutable after later trust cutoffs:

- `shared_anchor_meta`: the reserved monotonic tail advances;
- `shared_anchor_intents`: new `PREPARED` intents are appended and may make exactly one `PREPARED -> CONFIRMED` transition;
- `component_anchor_watermarks`: per-component positions advance monotonically;
- `asymmetric_provider_receipts`: new request IDs are appended, while committed receipts are immutable.

Blanket post-cutoff immutability would break legitimate runtime work. This experiment instead places those writes behind a broker-owned writable SQLite connection. A connection-local `lab091_writer_authorized()` function is true only during an audited `BEGIN IMMEDIATE` mutation. Triggers constrain the exact state transitions allowed during that interval and reject raw DML otherwise.

## Supported transition model

- reserve: append a fresh intent identity and atomically advance `reserved_position` from its exact predecessor;
- confirm: change only `status=PREPARED, receipt=NULL` to `status=CONFIRMED, receipt=<non-null>` while every identity/content field remains unchanged;
- watermark: insert a fresh component watermark or advance an existing one monotonically;
- provider receipt: append a fresh request ID; existing receipts are immutable and non-deletable.

`INSERT OR REPLACE` is explicitly treated as an attack surface. A first prototype relied on UPDATE/DELETE guards and allowed a committed receipt to be replaced. The corrected insert guards reject any already-existing intent/request/position/component identity even while the broker writer context is active.

## Trust boundary

The SQL function and triggers are **not** a standalone sandbox. A process that already has an unrestricted writable SQLite connection can register its own function named `lab091_writer_authorized` and spoof the predicate. The corrected model therefore composes with LAB-087:

1. the broker/process owns the only writable database handle/file authority;
2. workers receive only the LAB-087 restricted/read-only boundary;
3. LAB-091 constrains which DML transitions the broker-owned writable connection may perform.

Root, broker UID, `CAP_DAC_OVERRIDE`, privileged filesystem/namespace replacement, and arbitrary DDL/schema authority remain outside the LAB-091 claim. LAB-087 owns that external boundary.

## Current evidence

The exact published reference protocol and tests passed 11/11 locally after blob identity verification. Coverage includes normal reserve/confirm/watermark/receipt flow, raw DML rejection, missing-UDF fail-closed behavior, immutable confirmed intents/receipts, watermark rollback, `INSERT OR REPLACE`, rollback after an interrupted authorized transaction, nested authorization rejection, and the deliberate writable-connection/UDF-spoof negative control.

This is still a reference layer. The next gate is to integrate the writer context into the actual LAB-080/LAB-082 supported mutation paths and prove restart/concurrency behavior without exposing the raw broker connection.
