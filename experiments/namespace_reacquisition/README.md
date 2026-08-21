# LAB-066 namespace reacquisition

Persists an authenticated continuity record over lexical absolute path, namespace generation, boot ID, inode observations, and (when supported) Linux opaque file-handle evidence. Reacquisition reopens the configured path without following symlinks and compares opaque handle identity. If strong reopen/capture cannot be demonstrated, consequential recovery fails closed as `UNSUPPORTED_STRONG_REACQUISITION` rather than silently trusting the pathname.

Run:
`python -m unittest experiments.namespace_reacquisition.tests.test_protocol -v`
