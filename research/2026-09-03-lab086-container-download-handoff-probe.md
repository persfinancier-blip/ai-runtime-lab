# LAB-086 machine-download handoff probe — 2026-09-03

## Objective

Probe a new byte-preserving fallback for the pending LAB-086 publication: obtain the exact authoritative predecessor directly into the execution filesystem, apply the retained patch locally, verify the candidate Git blob hash, and only then publish through the normal GitHub Contents API.

The required lineage remains:

- predecessor blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`
- retained patch blob: `61841b58be42b01b97ca223567cbf9f428f7f0ce`
- required candidate blob: `b78e7c98e35138719f77c482c7f1aab36b702de7`

## Probe performed

A filesystem download was attempted for the exact raw GitHub predecessor URL rather than copying connector-returned source text through the model. The download facility rejected the operation because that exact raw URL had not been successfully opened through its required web-safety preflight. A direct web open of the raw URL returned a cache-miss/fetch failure, so the download tool could not be authorized for the transfer.

A second independent machine-network probe used `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`. It failed before repository access with:

`Could not resolve host: github.com`

An additional direct Python `urllib` fetch of the raw GitHub URL also failed on temporary DNS resolution.

## Result

The new machine-download fallback is **not available in this run**. This closes one previously untested possibility, but does not change the safety boundary: security-critical `strict_fence.py` must not be reconstructed by copying connector text through the model.

No LAB-086 source was mutated and no new behavioral PASS is claimed.

## Next safe action

On the next run, probe again for any supported connector/file materialization or machine-download route that transfers the authoritative predecessor and patch as bytes into the local filesystem. If one succeeds:

1. apply only the retained patch to the exact predecessor bytes;
2. compute Git blob identity locally and require `b78e7c98e35138719f77c482c7f1aab36b702de7`;
3. conflict-check PR #165 still contains the predecessor state expected by the patch;
4. publish via normal Contents API;
5. re-fetch and hash-verify;
6. execute the retained LAB-086 regression/full gate before changing draft status.
