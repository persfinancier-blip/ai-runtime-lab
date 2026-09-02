# LAB-086 full-blob connector capability re-probe — 2026-09-03

## Objective
Re-probe the exact publication blocker for LAB-086 hidden-rowid hardening without manually reserializing security-critical `strict_fence.py`.

## Observed capabilities in this run

1. GitHub connector `fetch_blob` returned the complete predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` as UTF-8 text.
2. The same connector returned the complete retained unified-diff patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`.
3. The patch is the retained hidden-rowid hardening delta and includes rowid collision checks plus AFTER-insert `rowid=-1` sentinels for thawed authenticated-history/evidence/receipt surfaces.
4. Direct Git transport was re-probed with a fresh clone attempt and failed before repository access: `Could not resolve host: github.com`.
5. The available GitHub connector surface exposes read operations for blobs/diffs and normal Contents API writes, but no supported operation that applies a unified diff to an exact fetched blob and returns the resulting bytes/blob SHA.

## Decision
Do not manually/model-reserialize the 949-line security-critical source solely from displayed tool payloads. The publication contract requires a byte-preserving machine composition and exact candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7` before any Contents API write.

No branch mutation was attempted and no fresh LAB-086 behavioral PASS is claimed.

## Exact next action
When either direct Git transport or another supported byte-preserving composition bridge is available, apply only `61841b58...` to predecessor `d4a6a40f...`, require candidate blob `b78e7c98...`, conflict-check PR #165 still carries the predecessor, publish via normal Contents API, re-fetch/hash-verify, then run the retained focused/full LAB-086 gates.
