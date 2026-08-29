# LAB-091 foreign-key cascade reachability audit

Date: 2026-08-29

## Question

Can an incoming SQLite foreign key turn an otherwise authorized LAB-091 mutation of a protected table into an unauthorized confused-deputy write to some other durable table?

## Mechanism probe

A focused SQLite probe demonstrated the generic mechanism when foreign-key enforcement is enabled:

- parent table: `component_anchor_watermarks(component_id, position)`;
- extra legacy `UNIQUE(component_id, position)` parent key;
- external child table references that composite key with `ON UPDATE CASCADE`;
- an authorized parent watermark update from position `1` to `2` also changes the child row from `1` to `2`.

Observed probe result: before `('c1', 1, 'x')`; after the single parent update `('c1', 2, 'x')`.

This establishes that incoming FK cascades can be a confused-deputy surface in SQLite in general.

## Reachability check against the actual LAB-091 candidate

The current final LAB-091 connection factory in `operation_scoped_integration.py` opens `sqlite3.connect(..., factory=PermitConnection)`, sets only `PRAGMA busy_timeout=5000`, and installs the LAB-091 UDFs. It does **not** enable `PRAGMA foreign_keys=ON`.

SQLite foreign-key enforcement is connection-local rather than a durable database-file setting. The current supported writer therefore does not execute incoming FK cascade actions merely because a legacy database contains FK declarations.

A second focused local probe confirmed the generic cascade only after explicitly enabling `PRAGMA foreign_keys=ON`; without that connection setting it is not an active mutation path.

## Decision

Do **not** add a LAB-091 adoption guard that rejects all incoming foreign keys at this time. The hypothesized cascade bypass is not reachable through the current supported connection semantics, so such a guard would widen the schema contract without a demonstrated security benefit.

This is a negative audit result, not a global claim that foreign keys are harmless. If the supported writer later enables foreign-key enforcement, this exact mechanism becomes relevant and must be re-audited before that change is accepted.

## Residual alternate-write audit

Continue only with durable SQLite mechanisms that are reachable under the actual connection configuration. In particular, avoid adding speculative guards for views, FK declarations, or other schema objects unless an executable path from a supported LAB-091 statement to an unauthorized durable mutation is reproduced.
