# LAB-064 archive publication durability

The reference POSIX/Linux publication boundary is:

`write temp -> flush -> fsync(file) -> atomic replace -> fsync(parent directory)`

LAB-062 must receive a durable publication receipt for both archive artifact and manifest before its SQL transaction may commit an authoritative archive reference.

Atomic rename and durable rename are intentionally treated as different properties. A visible filename after `os.replace()` is not sufficient evidence for the power-loss durability model.

Run the focused suite once exact branch source is available locally:

```bash
python -m unittest experiments.archive_publication_durability.tests.test_protocol -v
python -m unittest experiments.archive_publication_durability.tests.test_signed_compaction_integration -v
```

This experiment does not claim universal durability across filesystems, storage devices, mount options, virtualized storage stacks, or non-POSIX platforms.
