# LAB-091 — legacy surface trigger persistence

## Finding

The first operation-scoped LAB-091 guard set reused trigger names that the earlier transaction-wide `SupportedMutableAsymmetricSharedAnchorLedger` installer knows and deliberately drops during upgrade/reinstallation.

That creates an alternate-surface downgrade path: an operation-scoped database can be reopened through the older supported class, which removes the exact one-shot triggers, reinstalls broad `lab091_writer_authorized()` guards, and can then authorize a transition such as `shared_anchor_meta.reserved_position 0 -> 999` that the operation-scoped state machine forbids.

A focused executable counterexample reproduced the downgrade: the exact guard rejected `0 -> 999`, then the legacy trigger reinstall plus broad authorization accepted it and persisted `999`.

## Fix

The operation-scoped trigger set now uses `lab091_v2_*` names that are intentionally outside the legacy installer's drop namespace. The installer still removes both old broad names and old exact names during upgrade, and it removes/recreates its own `v2` names idempotently.

If the legacy surface is later opened against an operation-scoped database, the `v2` triggers remain present. A real legacy connection does not register `lab091_consume_permit`, so a consequential write fails closed. On the final operation-scoped connection, the same surviving triggers continue to consume exact one-shot permits normally.

This is not a defense against arbitrary same-privilege DDL that explicitly drops the `v2` triggers; LAB-087 remains the outer broker/process/filesystem boundary for the only writable database handle.

## Evidence

- published `full_operation_guards.py` blob: `8e409d61d3d813dbf3a564ea8ea5f4d3015106fb`;
- published regression blob: `e47e2ed29e3652b2c70ec7eec1a86d8975219a1a`;
- exact existing `test_full_operation_guards.py` blob `40ec2f20cca9c878199656ef2e9337c0764a9392` plus new legacy-surface regression passed 12/12 together;
- operation-permit and row-token dependencies matched their published blobs (`637784a5...`, `801eb0fb...`);
- compileall passed.
