# LAB-086 target-blob object-database probe

Date: 2026-09-03

## Question

Can the pending LAB-086 hidden-rowid publication avoid model/manual whole-file reserialization by reusing an already-existing exact Git blob or commit object for the required target `b78e7c98e35138719f77c482c7f1aab36b702de7`?

## Observed result

Using the current authenticated GitHub connector against `persfinancier-blip/ai-runtime-lab`:

- `fetch_blob(d4a6a40fb94455d357328bdcd10cf077a2dfc2cd)` succeeded and returned the complete predecessor `strict_fence.py` blob content.
- `fetch_blob(61841b58be42b01b97ca223567cbf9f428f7f0ce)` succeeded and returned the retained hidden-rowid unified patch content.
- `fetch_blob(b78e7c98e35138719f77c482c7f1aab36b702de7)` returned GitHub `404 Not Found`.

Therefore the desired composed target blob is not currently reusable from this repository's Git object database through the normal blob-read surface. There is no existing exact target blob to reference/copy at the object level.

## Consequence

This closes one previously plausible safe fallback: server-side reuse of an already-existing exact target object. The remaining publication problem is still a byte-preserving composition problem:

`d4a6a40f... + 61841b58... -> b78e7c98...`

The connector can read both exact inputs, and the normal Contents API can write a complete UTF-8 replacement with current-blob conflict protection, but no supported connector operation observed in this run applies the retained patch to the predecessor inside the GitHub/connector boundary. Supplying a manually/model-reserialized 949-line replacement remains prohibited by the LAB-086 handoff because it would weaken byte-identity assurance for a security-critical source.

No branch mutation and no behavioral PASS are claimed from this probe.

## Next safe probe

Look specifically for a supported machine transform/materialization path that can consume the exact predecessor and exact patch as machine inputs and emit the composed bytes, then require Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7` before any Contents API publication. Do not use low-level tree/ref manipulation as a substitute.
