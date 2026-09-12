# LAB-091 — Mutable shared-anchor writer authorization

## Question

How can LAB-080/LAB-082 keep mutating the shared-anchor ledger after later security cutoffs without leaving ordinary raw SQL able to corrupt the same durable authority state?

## Existing required writes

The supported runtime must continue to perform four classes of mutation:

1. reserve a fresh intent and advance the exact reserved tail;
2. confirm exactly one existing `PREPARED` intent as `CONFIRMED` without changing its identity/content;
3. advance a component watermark monotonically;
4. append a fresh asymmetric provider receipt while preserving prior receipts as immutable evidence.

Making these tables globally immutable is therefore not viable.

## Experiment

The reference implementation gives the broker-owned SQLite connection a connection-local SQL function `lab091_writer_authorized()`. It returns true only inside an audited `BEGIN IMMEDIATE` writer context. Triggers enforce the exact allowed transition shape.

There is no durable writer flag. The authorization bit lives only in the broker process and is reset before commit and on every rollback path.

### Failure found during development

The first receipt rule allowed `INSERT OR REPLACE` while the writer context was active. SQLite conflict handling cannot be treated as if it necessarily traverses a separately defined DELETE guard. The fix makes each creation trigger reject an identity that already exists, even for an authorized writer. The same fresh-identity rule is applied to intents and component watermarks.

## Results

Exact published corrected protocol/test blobs were verified against the locally executed bytes:

- `protocol.py`: `f0a3e284823a723a049f32d2ac7603c7997afc72`;
- corrected tests: `1bd08f1b216a7bd8c785812b37514ab223340d6d`.

Corrected suite: 11/11 PASS. Compileall passed.

The exact unsafe seed blob `e4c1bc62a102f7bb3ad91c4f2db176a181b87aac` failed as intended: unrestricted SQL changed `shared_anchor_meta.reserved_position` from 0 to 99.

## Security boundary

A connection-local UDF plus triggers is not a security boundary against a process that already owns another unrestricted writable connection. The negative control registers a same-name UDF returning true on such a connection and successfully mutates the ledger.

Therefore LAB-091 composes with LAB-087 rather than replacing it:

- LAB-087: broker/process/filesystem ownership ensures workers do not possess arbitrary writable DB connections;
- LAB-091: the broker's writable connection exposes only audited state transitions and fails closed for accidental/stale raw DML on that handle.

This layer does not claim protection from root, broker UID compromise, `CAP_DAC_OVERRIDE`, arbitrary DDL/schema authority, or privileged namespace replacement.

## Next integration gate

Move the writer context behind the actual `SupportedSharedAnchorLedger` / LAB-082 mutation paths rather than a parallel reference schema. The supported object must not expose its raw writable connection. Prove reserve/confirm/watermark/provider-receipt flow, restart, concurrent writers, crash rollback, `UNKNOWN` reconciliation, and composition with the LAB-087 restricted worker boundary.
