# LAB-090 / LAB-092 semantic integration audit — 2026-09-01

## Scope

This audit follows the durable fallback in `state/CURRENT.md`: when exact checkout/execution remains unavailable, inspect PR #175 against current `main` at the file/semantic level, then inspect PR #177's cumulative dependency on LAB-090 for inherited API/signature conflicts. No new LAB-092 contract is introduced here.

## Per-run capability observation

A fresh local probe was attempted:

```text
git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
```

Repository code therefore did not execute in this run. No behavioral PASS is claimed.

## PR #175 versus current main

PR #175 remains draft with:

- base branch: `main`;
- base SHA recorded by GitHub: `6cc7a04496187075db1c02f3e27c1d394da53026`;
- head SHA: `d9a381dd4607a928cd1315adef6431e239995bc1`;
- 21 changed files.

An exact GitHub compare from `6cc7a044...` to current `main` reports current main **98 commits ahead** and **0 behind**. The complete compare file list contains only:

- `research/**` evidence files; and
- `state/CURRENT.md`.

No production module, test module, schema source, or protocol source changed on main across that divergence. In particular, none of PR #175's 21 changed files overlap the current-main divergence.

### Result

No reachable file-level or semantic dependency conflict was found between PR #175's production/test delta and the current main-side divergence. The branch is stale in commit count, but the observed main divergence is control-plane/evidence-only. This does **not** substitute for a final conflict/rebase check immediately before integration, and does not make the draft ready without behavioral gates.

## PR #177 cumulative dependency on PR #175

PR #177 remains draft with:

- base branch: `lab-090-provider-activation-fencing`;
- base SHA: exactly `d9a381dd4607a928cd1315adef6431e239995bc1`, which is PR #175's current head;
- head SHA: `cc50513cfd867d8711fb29db8f33490200390d0d`;
- 9 changed files, all LAB-092 additions (`activation_schema_provenance.py` plus eight test modules).

The LAB-092 production module imports or calls inherited LAB-090 surfaces including:

- `CoordinatorOnlyProviderHistory`;
- `SupportedHistoricalSharedAnchorLedger`;
- `_ACTIVATION_TABLE_NAME`, `_ACTIVATION_TABLE_SQL`, `_ACTIVATION_TRIGGER_NAME`, `_ACTIVATION_TRIGGER_SQL`, `_normalized_sql`;
- ledger `_con()`, `entry()`, `_request_id()`, `execute()` and `_descriptor_from_attested()`;
- provider-history `_verify_durable_locked(q)`;
- LAB-090 `_verify_activation_records()`.

Inspection of PR #175 exact head source confirms the required LAB-090 class/constants and `_verify_activation_records(self)` surface are present with the signatures used by LAB-092. PR #177 is based directly on that exact head, so there is no intervening inherited-method/signature delta to reconcile.

### Result

No reachable inherited-method/signature conflict was found for PR #177 relative to its LAB-090 base. The remaining integration risk is behavioral, not an observed source/API mismatch: PR #175 must first pass its exact focused/integration/downstream gates, and PR #177 must then run its own exact migration/restart/provenance gates on the published head.

## LAB-086 priority check

LAB-086 remains priority #1. The authoritative publication contract is unchanged: predecessor `d4a6a40f...` + retained hidden-rowid patch blob `61841b58...` must produce exact target blob `b78e7c98...`, then be published through normal Contents API and re-fetched/hash-verified before the full security gate.

The connector can fetch source and perform Contents writes, but no supported operation observed in this run accepts a fetched blob plus a unified patch and produces a byte-preserving replacement payload automatically. Low-level tree/ref manipulation and manual/model reserialization remain prohibited. No LAB-086 branch mutation was attempted.

## Decision

1. Leave PR #175 and PR #177 draft.
2. Do not rebase either merely to reduce stale commit count; no production overlap was observed.
3. Do not claim any behavioral pass from this audit.
4. If exact source execution becomes available, run PR #175 gates first, then PR #177 gates.
5. If execution remains unavailable, continue with the next reachable mutation-boundary audit rather than adding speculative contracts.
