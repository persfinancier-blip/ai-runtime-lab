# LAB-086 full-blob read bridge narrowing — 2026-09-02

## Purpose

Re-probe the exact remaining publication blocker for LAB-086 rather than carrying forward the earlier, broader assumption that GitHub connector reads necessarily truncate `strict_fence.py`.

## Per-run observations

1. `fetch_blob(d4a6a40fb94455d357328bdcd10cf077a2dfc2cd)` returned the complete predecessor source for `experiments/asymmetric_break_glass_history/strict_fence.py` in one connector response. The response reaches the final `return True` of `assert_public_mutation_fence_locked`; it is not the earlier `fetch_file` presentation-truncated form.
2. `fetch_blob(61841b58be42b01b97ca223567cbf9f428f7f0ce)` returned the complete retained hidden-rowid unified patch.
3. `fetch_blob(b78e7c98e35138719f77c482c7f1aab36b702de7)` returned 404. The previously derived target blob therefore is not currently addressable as an existing Git object through the connector and cannot simply be re-fetched and used as a pre-existing exact payload.
4. Direct raw GitHub access from the local execution environment was probed again and failed before repository execution with temporary DNS resolution failure. Thus there is still no local byte-preserving bridge that can fetch the predecessor/patch itself and feed `patch`/`git apply`/hash verification.
5. The normal Contents API writer accepts complete replacement UTF-8 text, not `(predecessor blob, unified patch)` or an existing target blob reference. The available low-level Git tree/ref operations are explicitly outside the repository's safe fallback contract for this task.

## Consequence

The LAB-086 blocker is now narrower:

- **read completeness is no longer the problem for these two retained blobs**;
- the missing capability is an auditable **machine transformation bridge** from the exact fetched predecessor bytes + exact retained patch bytes to a complete Contents API payload, with candidate hash verification before mutation.

Model/manual reserialization of the 900+ line security-critical file remains disallowed even though the full text is visible, because visibility is not equivalent to byte-preserving composition. The safe publication contract remains:

`d4a6a40f...` + only `61841b58...` -> candidate Git blob must equal `b78e7c98...` -> Contents API write -> re-fetch exact blob -> execute the complete security gate.

## No mutation performed

No branch/source mutation was attempted in this probe. No behavioral test PASS is claimed.

## Next implementation opportunity

If a future run exposes any supported operation that can consume exact blob bytes programmatically (for example materializing connector output into the execution filesystem, or a high-level apply-patch-to-contents operation), use it immediately. The full predecessor and patch are now confirmed individually retrievable; do not re-investigate ordinary source truncation unless connector behavior changes.
