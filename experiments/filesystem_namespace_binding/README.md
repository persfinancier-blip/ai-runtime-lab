# LAB-065 filesystem namespace binding

Linux reference path: obtain a trusted root directory FD, open the archive directory
with `openat2(RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS)`, then do
all publication and verification relative to the held archive directory FD.

A path string is diagnostic after authorization. Consequential authority is the held
directory object (`st_dev`, `st_ino`, live FD) plus exact content digest.

Run:

```bash
python -m unittest experiments.filesystem_namespace_binding.tests.test_protocol -v
python -m unittest experiments.filesystem_namespace_binding.tests.unsafe_lexical_expected_failure -v
```
