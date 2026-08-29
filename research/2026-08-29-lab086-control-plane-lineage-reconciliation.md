# LAB-086 control-plane lineage reconciliation — 2026-08-29

## Purpose
Reconcile durable task metadata with the actual live LAB-086 branch before any further security-sensitive publication.

## Exact observations in this run
- `state/CURRENT.md` names `lab/086-asymmetric-break-glass-history` / PR #165 / issue #163 as the active priority.
- Live branch `experiments/asymmetric_break_glass_history/strict_fence.py` re-fetches as blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- The retained hidden-rowid patch `research/2026-08-28-lab086-hidden-rowid-replace.patch` re-fetches as blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`.
- The previously derived and focused-tested exact post-patch target remains `b78e7c98e35138719f77c482c7f1aab36b702de7` per durable state.
- Issue #163 and PR #165 still describe the older executable lineage around `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`. That metadata is stale and must not be used as the publication predecessor.

## Capability probe
- `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed in the local runtime with `Could not resolve host: github.com`.
- The GitHub connector can retrieve the complete PR-added file, but the tool response is truncated at the presentation boundary for the whole 949-line payload. It does not expose a branch checkout or an operation that composes an exact fetched payload plus a unified patch into a byte-preserving Contents write.
- Normal Contents writes are available, but manually/model-reserializing a 949-line security-critical file would violate the existing byte-preservation requirement. No branch mutation was attempted.

## Decision
The only valid publication predecessor for the hidden-rowid change is `d4a6a40f...`; the only acceptable published result is a re-fetched `strict_fence.py` blob exactly equal to `b78e7c98...` after a predecessor conflict check. Older `eb219835...` lineage is retained only as historical evidence for the alternate-UNIQUE fix.

Until a supported byte-preserving composition/transfer path is observed, LAB-086 publication remains tool-limited rather than product-blocked. Fallback work may continue under LAB-091, but no security-sensitive LAB-086 source rewrite should be performed by reconstructing the whole file in model text.
