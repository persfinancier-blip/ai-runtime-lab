"""Supported LAB-076 sink-registry authority-lifecycle surface.

Use these classes for integrations. Raw protocol/integration modules remain
available for failure-injection and audit history, but callers should not assemble
their own verifier or worker composition around them.
"""

from experiments.sink_registry_authority_lifecycle.audit_fixes import (
    ConsistentDurableRegistryAuthority as DurableRegistryAuthority,
    CorrectedLifecycleRegistryBoundJournal as LifecycleRegistryBoundJournal,
    CorrectedLifecycleRegistryBrokerWorker as LifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_authority_lifecycle.protocol import (
    AuthorityRollback,
    AuthoritySubstitution,
    EntryAuthError,
    HistoricalAuthorityMissing,
    LifecycleError,
    UnsafeRecovery,
)
from experiments.sink_registry_binding.supported import RegistryEntry, RuntimeAdapter

__all__ = [
    "AuthorityRollback",
    "AuthoritySubstitution",
    "DurableRegistryAuthority",
    "EntryAuthError",
    "HistoricalAuthorityMissing",
    "LifecycleError",
    "LifecycleRegistryBoundJournal",
    "LifecycleRegistryBrokerWorker",
    "RegistryEntry",
    "RuntimeAdapter",
    "UnsafeRecovery",
]
