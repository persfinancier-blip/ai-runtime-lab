# LAB-086 — current connector patch-capability probe

Date: 2026-09-03

Status: capability evidence only. No LAB-086 source mutation or behavioral PASS is claimed.

## Question

Can the current run safely publish the retained hidden-rowid delta onto the exact LAB-086 predecessor without model/manual reserialization of the security-critical `strict_fence.py`?

Authoritative lineage remains:

- predecessor blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`;
- retained patch blob: `61841b58be42b01b97ca223567cbf9f428f7f0ce`;
- required composed target blob: `b78e7c98e35138719f77c482c7f1aab36b702de7`.

## Observed capabilities in this run

Direct repository transport was re-probed with:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

It failed before repository execution with:

`Could not resolve host: github.com`

The GitHub connector was then inspected for file mutation capabilities. It currently exposes:

- fetch complete/partial file content;
- create a new UTF-8 file;
- delete an existing file;
- replace an existing UTF-8 file through the normal Contents API, with the current blob SHA as a conflict guard;
- read PR/file patches and compare refs.

The replacement operation requires the **complete replacement UTF-8 text**. No supported operation is exposed that takes an existing Git blob plus a unified diff/patch and performs the composition inside the connector/GitHub boundary. The PR-patch actions are read-only.

## Consequence

The normal Contents API remains a valid publication endpoint only after exact candidate bytes already exist. It is not, in the current connector surface, a byte-preserving patch engine.

Therefore the pending hidden-rowid publication must remain blocked rather than reconstructing the complete security-critical file in model text. This is a tool/capability constraint, not an unresolved design choice.

## Safe next path

Re-probe for any future supported machine composition/materialization path. If one appears:

1. verify the live branch file is still exact predecessor `d4a6a40f...`;
2. machine-apply only patch `61841b58...`;
3. require candidate Git blob exactly `b78e7c98...` before publication;
4. publish with normal Contents API using predecessor SHA conflict protection;
5. re-fetch/hash-verify;
6. execute the retained focused and full LAB-086 gates.

Until then, do not mutate `strict_fence.py` and do not claim a new LAB-086 behavioral PASS.
