# LAB-086 base64 range-fetch capability probe — 2026-09-04

## Objective

Re-probe for a safe supported byte-preserving materialization path for the pending LAB-086 composition without manually/model-reserializing `strict_fence.py`.

Authoritative inputs remain:

- live predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`;
- retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`;
- required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.

## Fresh observations

1. Direct repository transport was probed again with a fresh `git clone --no-checkout`. It failed before repository access with `Could not resolve host: github.com`.
2. The GitHub connector still reports the live branch `strict_fence.py` blob as exactly `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, so the publication predecessor has not drifted.
3. A previously unexercised connector mode can return `fetch_file` content as **base64 for an exact source line range**. A probe for lines 1-20 of `strict_fence.py` returned base64 plus the exact predecessor blob SHA.
4. The retained patch is connector-readable on the LAB-086 branch as base64 as well.
5. This removes the earlier assumption that the only connector representation is one presentation-truncated full UTF-8 payload. Exact source can be addressed in bounded chunks.

## What this does not solve

The current runtime still exposes no supported direct bridge that feeds those connector-returned base64 chunks into the filesystem/Python process as machine inputs. Reconstructing the entire security-critical file by copying connector chunks through model output would violate the existing LAB-086 no-manual/no-model-reserialization contract even if a final hash check were attempted.

Likewise, normal Contents `update_file` accepts a complete UTF-8 replacement body; it does not accept a predecessor blob + patch transform or a stream of exact base64 chunks.

Therefore no production mutation was attempted and no behavioral PASS is claimed.

## Decision

Keep the exact target contract unchanged. The newly observed range/base64 retrieval capability is useful only if paired with a supported connector-response-to-filesystem/materialization bridge. Do not weaken the safety rule merely because chunked exact retrieval exists.

## Exact next action

Probe specifically for a supported connector/file materialization operation that can consume a GitHub file/blob response (or exact returned chunks) without model reserialization. If such a bridge appears, reconstruct predecessor bytes mechanically, verify Git blob `d4a6a40f...`, apply retained patch mechanically, require target blob `b78e7c98...`, then publish only through normal Contents API and execute the retained LAB-086 gate.
