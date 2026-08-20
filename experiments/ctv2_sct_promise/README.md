# CT v2 SCT Promise-to-Inclusion Reference

LAB-045 binds four layers that are easy to confuse:

1. a strict RFC 9162 SCT v2 wire object;
2. the exact `x509_entry_v2` / `precert_entry_v2` bytes authenticated by the SCT signature;
3. exact-leaf inclusion under an authenticated LAB-043 STH through LAB-044;
4. the log's configured Maximum Merge Delay (MMD) audit deadline.

The reference status model is intentionally fail-closed:

- `FULFILLED` — exact SCT↔leaf binding is authenticated and exact inclusion is proved, or a complete authenticated tree snapshot contains that exact leaf;
- `NOT_YET_AUDITABLE` — the selected authenticated STH predates the MMD deadline and no inclusion is yet proved;
- `INCONCLUSIVE_AFTER_DEADLINE` — the deadline has passed, but the caller supplied neither inclusion evidence nor authenticated complete-tree evidence of absence;
- `MMD_VIOLATION` — an authenticated complete tree snapshot at/after the deadline reconstructs the STH root and proves the exact promised leaf is absent.

A post-deadline STH that *does* include the exact leaf is not by itself proof of late insertion. RFC 9162 explicitly allows auditing an SCT against an STH dated after `SCT timestamp + MMD`.

## Run

```bash
python -m unittest discover -s experiments/ctv2_sct_promise/tests -p 'test_*.py' -v
python -m unittest experiments.ctv2_sct_promise.tests.unsafe_inclusion_only_expected_failure -v
python -m compileall -q experiments/ctv2_sct_promise
```

The unsafe seed is expected to fail because it verifies inclusion while never proving that the presented SCT promised the included artifact.

## Non-goals

This is not browser CT policy, certificate-chain validation, SCT transport, monitor networking, or a generic non-membership proof. The complete-tree absence path is monitor-style evidence: the full leaf set must reconstruct the authenticated STH root.
