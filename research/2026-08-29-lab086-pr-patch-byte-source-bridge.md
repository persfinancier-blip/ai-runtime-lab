# LAB-086 PR patch byte-source bridge audit — 2026-08-29

## Context

LAB-086 remains blocked on publication of the previously tested hidden-rowid hardening candidate for `experiments/asymmetric_break_glass_history/strict_fence.py`.

Required lineage:

- live predecessor blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`;
- stored patch: `research/2026-08-28-lab086-hidden-rowid-replace.patch`;
- previously derived/tested target blob: `b78e7c98e35138719f77c482c7f1aab36b702de7`.

The publication rule remains strict: do not publish unless the complete replacement is byte-preserved and the re-fetched Git blob equals the target.

## Current-run observation

The GitHub connector's `fetch_pr_file_patch` was executed for PR #165 and `experiments/asymmetric_break_glass_history/strict_fence.py`.

Because this file is an addition relative to `main`, GitHub returned a complete unified addition patch covering the current 949-line branch file (`@@ -0,0 +1,949 @@`). This proves the exact predecessor source is retrievable as one authoritative PR payload even though ordinary UTF-8/base64 fetch responses are display-truncated.

The stored hidden-rowid patch was separately re-fetched from branch `lab/086-asymmetric-break-glass-history` and remains blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`.

A direct runtime network probe still failed DNS resolution for `raw.githubusercontent.com`, so shell/Python cannot currently compose the two GitHub payloads by downloading them itself.

## Safety decision

Do **not** manually retype or model-reserialize the 949-line security-critical source into the Contents API. Although the complete predecessor is visible through the PR patch endpoint, the available tools still do not expose a byte-preserving server-side composition operation that takes `full predecessor payload + stored unified patch -> replacement file`.

This narrows the blocker: source retrieval is no longer the missing capability; the missing capability is exact composition/transfer into the writer without human/model transcription.

No branch mutation was attempted.

## LAB-091 side audit

While LAB-086 remained transport-limited, the LAB-091 persisted-trigger hypothesis was rechecked. `install_full_operation_guards()` explicitly drops the legacy/v2 trigger names before recreating the v2 definitions, and `validate_protected_trigger_surface()` requires the exact protected trigger-name set after installation. Therefore the narrower idea of persisting malicious v2 trigger SQL under an expected v2 name is not currently reachable through first adoption: the installer overwrites those names before validation. No speculative guard was added.

## Exact next action

1. LAB-086 first: if a supported byte-preserving composition/transfer path appears, reconstruct `strict_fence.py` from the exact 949-line PR payload plus `2026-08-28-lab086-hidden-rowid-replace.patch`, require target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, publish with predecessor conflict check, re-fetch, and execute the complete LAB-086 gate.
2. If exact composition remains unavailable, continue only evidence-driven LAB-091 audit/execution; do not add speculative schema guards.
