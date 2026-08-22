"""Supported LAB-077 threshold-publication surface.

New sink-registry publication requires ``ThresholdEnvelope``. The historical
single-signature LAB-076 publication methods remain available only in older
experiment modules for audit history and backwards regression; this module does
not export them as a supported publication path.
"""

from experiments.sink_registry_authority_lifecycle.audit_fixes import (
    ConsistentDurableRegistryAuthority as DurableRegistryAuthority,
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
from experiments.sink_registry_threshold_publication.integration import (
    ThresholdHistoricalMissing,
    ThresholdLifecycleRegistryBoundJournal,
    ThresholdLifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_threshold_publication.protocol import (
    AuthorityMismatch,
    InvalidSignatureSet,
    ProofSubstitution,
    ThresholdEnvelope,
    ThresholdProof,
    make_envelope,
    publication_entry,
    sign_publication,
    verify_envelope,
)

__all__ = [
    "AuthorityMismatch",
    "AuthorityRollback",
    "AuthoritySubstitution",
    "DurableRegistryAuthority",
    "EntryAuthError",
    "HistoricalAuthorityMissing",
    "InvalidSignatureSet",
    "LifecycleError",
    "ProofSubstitution",
    "RegistryEntry",
    "RuntimeAdapter",
    "ThresholdEnvelope",
    "ThresholdHistoricalMissing",
    "ThresholdLifecycleRegistryBoundJournal",
    "ThresholdLifecycleRegistryBrokerWorker",
    "ThresholdProof",
    "UnsafeRecovery",
    "make_envelope",
    "publication_entry",
    "sign_publication",
    "verify_envelope",
]
