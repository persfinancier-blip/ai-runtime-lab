"""Supported LAB-076 sink-registry authority-lifecycle surface.

Use these classes for integrations. The raw protocol module remains available for
failure-injection/audit history, but callers should not assemble their own verifier
or worker composition around it.
"""

from experiments.sink_registry_authority_lifecycle.integration import (
    LifecycleRegistryBoundJournal,
    LifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_authority_lifecycle.protocol import (
    AuthorityRollback,
    AuthoritySubstitution,
    DurableRegistryAuthority,
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
