# Current Lab State

Last updated: 2026-09-13

## Active objective
LAB-086 remains priority #1: finish the exact executable/security gate for asymmetric break-glass history migration. LAB-099 is the permitted fallback when byte-exact LAB-086 execution cannot be materialized safely.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165. Keep draft.
- LAB-092: #176 / draft PR #177, pinned head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-095 prerequisite: #180 — READY; now concretely blocks LAB-099 PREPARED authority under the frozen contract.
- LAB-099: #184 / branch `lab-099-precursor-cutover-red-intent` / draft PR #186, head includes first production slice `d40aea8c48efe587b273650a3756ca782ba81472`.
- Other retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PR state. Resumed LAB-086 first, then used LAB-099 fallback only after the exact materialization path remained unavailable.

### LAB-086 current-run evidence
- Executable pin remains `1f90830fca21e2f43fc241012cdd34fd187ba96d`.
- Connector can read pinned UTF-8 blobs, but there is still no supported programmatic connector->filesystem byte stream in this run.
- Probed an additional direct raw-GitHub download fallback; transfer was blocked before bytes were materialized, so it cannot satisfy the exact Git-blob gate.
- No new LAB-086 unittest/security/compile/conflict PASS is claimed. PR #165 remains draft.

### LAB-099 source-audit result
Source-audited production LAB-092 completion/provenance, LAB-090 activation records, provider-generation transitions/history, and the current LAB-099 frozen precursor/cutover contract.

New prerequisite finding:
- frozen LAB-099 PREPARED/precursor storage requires authenticated `logical_database_identity_digest` and `parent_chain_link_digest`;
- production LAB-092/LAB-090 does not currently create/authenticate either value;
- current `main` code search found no production implementation of either identity;
- LAB-095/#180 already owns the missing construction-bound logical database/history identity problem;
- existing provider transitions + activation rows are sufficient for the ticket-specific cryptographic half once that database/chain identity exists.

Rejected unsafe fallbacks: copy test-only synthetic digests, hash mutable `path`, self-hash mutable SQLite contents, relabel the LAB-092 completion digest as DB identity, or accept caller-supplied root digests.

No LAB-099 production code was changed in this slice because all currently available ways to populate those authority fields would manufacture authority and weaken the frozen contract.

Durable evidence:
- `research/2026-09-13-lab099-prepared-authority-prerequisite-gap.md`
- main commit `6cc69baf41d3ddcfd1cb3cc7167a0c3ac025a203`
- #184 comment `5652675960`
- #180 comment `5652676875`

## Known failures / blockers
- LAB-086 exact complete real-ledger gate remains unexecuted because byte-exact repository materialization is unavailable; do not manually reconstruct the 50+ file closure.
- PRs #172/#173/#175/#177/#186 remain draft until retained exact gates execute.
- LAB-099 migration/resume remains intentionally fail-closed.
- Under the currently frozen LAB-099 schema, authenticated PREPARED migration now depends on a production construction-bound DB/history identity from LAB-095 (or an explicit re-freeze of the LAB-099 contract; do not silently weaken it).

## Exact next action
LAB-086 first: re-probe for a supported byte-preserving materialization path. If available, reconstruct only pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, require local `git hash-object` match for every manifest/test/helper/transitive file, then run all normal LAB-086 tests, unsafe expected-failure separately, downstream/helper tests, compileall, `*_for_test_only` audit, security/reconciliation audit, and current-main conflict audit.

If exact LAB-086 materialization is still unavailable, do not repeat manual source-transfer attempts. Advance LAB-095 regression-first far enough to define a construction-bound logical database/history identity and deterministic parent-chain-link derivation that cannot be rebound via mutable `path`. Then return to LAB-099 and derive precursor PREPARED authority from that identity + verified provider-generation transitions/activation rows + LAB-092 completion state. Do not import or derive production authority from `tests/lab099_*`.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact executable gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #180 / LAB-095 — READY and now prerequisite for frozen LAB-099 PREPARED authority.
- #178..185 / LAB-093..100 — remaining design/source follow-ups with executable gates pending.
- #184 / LAB-099 — classifier/startup slice published; PREPARED authority waits on LAB-095 identity prerequisite.
