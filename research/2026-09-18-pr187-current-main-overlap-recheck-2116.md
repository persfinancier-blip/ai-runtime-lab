# PR #187 current-main overlap recheck — 21:16

Date: 2026-09-18

## Mandatory LAB-086 probe

LAB-086 remained priority #1. A fresh direct clone attempt:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

failed before repository code execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed. The byte-exact gate at authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` remains unchanged.

## PR #187 control-plane recheck

- actual `main` tip before this evidence write: `e15d2653a13d7f41737861e5ac983a9eff67d759`;
- PR #187 remains open/draft;
- PR head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`;
- PR reported base snapshot remains `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`;
- fresh compact compare from that base snapshot to actual main: `ahead_by=253`, `behind_by=0`;
- complete compact changed-file inventory contains only `research/*` additions plus `state/CURRENT.md`;
- therefore there is still no main-side `experiments/*` or `tests/*` overlap with PR #187 source/test work;
- GitHub review collection is empty; issue/PR discussion was re-read and no new concrete source/test review defect was observed.

No rebase, merge, branch mutation, or executable GREEN claim is justified by this metadata-only recheck.

## Decision / next action

Keep PR #187 draft. On the next run probe LAB-086 first. If byte-exact materialization remains unavailable, re-read actual main tip, PR #187 head/reviews, and compact changed-file overlap. React only to concrete source/test overlap, PR head drift, or a new actionable review defect. If exact materialization becomes available, verify retained blob/hash identity before executing the focused/composed/LAB-080/LAB-081 inventory, then full pytest and compileall.
