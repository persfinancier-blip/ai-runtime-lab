from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from pathlib import Path

from experiments.asymmetric_provider_history.supported import (
    SupportedAsymmetricHistoricalSharedAnchorLedger,
)
from experiments.provider_threshold_rotation.protocol import (
    InvalidAuthority,
    ProviderRotationIntent,
    Signature,
    StaleAuthority,
    ThresholdNotMet,
    ThresholdProof,
    mac,
    verify_threshold,
)
from experiments.provider_threshold_rotation.strict import require_canonical_authority
from experiments.provider_threshold_rotation.supported import (
    SupportedThresholdAuthorizedAsymmetricProviderLedger,
)
from experiments.provider_rotation_recovery.protocol import RecoveryError
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    AsymmetricRecoveryCustody,
    PublicRecoveryAuthority,
    accepted_public_signatures,
    custody_rotation_payload,
    sha as custody_sha,
    verify_public_threshold,
)
from experiments.provider_recovery_authority_lifecycle.final_supported import (
    SupportedRecoveryCustodyLedger,
)
from experiments.provider_recovery_authority_lifecycle.supported import (
    SupportedRecoveryAuthorityLifecycleLedger,
)
from .migration_guard import (
    AuthenticatedBreakGlassMigrationGuard,
    MigrationGuardError,
    _digest,
)


class AsymmetricBreakGlassError(RuntimeError):
    pass


class PublicRecoveryRotationError(AsymmetricBreakGlassError):
    pass


def asymmetric_break_glass_payload(
    *, boundary_digest, old_root, new_root, public_authority
):
    return {
        "kind": "provider-asymmetric-break-glass-v2",
        "boundary_digest": boundary_digest,
        "old_root_id": old_root.authority_id,
        "old_root_version": old_root.version,
        "old_root_generation": old_root.generation,
        "new_root": new_root.descriptor,
        "public_authority_id": public_authority.authority_id,
        "public_authority_version": public_authority.version,
        "public_authority_generation": public_authority.generation,
    }


def _accepted_root_signatures(root, payload, signatures):
    root.validate()
    seen = set()
    accepted = []
    revoked = set(root.revoked)
    for item in signatures:
        if not isinstance(item, Signature):
            continue
        if item.signer_id in revoked:
            continue
        hx = root.keys.get(item.signer_id)
        if hx is None:
            continue
        expected = mac(bytes.fromhex(hx), payload)
        if not hmac.compare_digest(expected, item.signature):
            continue
        if item.signer_id in seen:
            continue
        seen.add(item.signer_id)
        accepted.append(item)
    if len(accepted) < root.threshold:
        raise ThresholdNotMet(
            f"public recovery root coauthorization valid={len(accepted)} threshold={root.threshold}"
        )
    return tuple(accepted)


def _boundary_exists(path):
    path = str(path)
    if not Path(path).exists():
        return False
    q = sqlite3.connect(path)
    try:
        table = q.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='provider_asymmetric_break_glass_boundary'"
        ).fetchone()
        if table is None:
            return False
        return (
            q.execute(
                "SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1"
            ).fetchone()
            is not None
        )
    finally:
        q.close()


class SupportedAsymmetricBreakGlassLedger(SupportedRecoveryCustodyLedger):
    """LAB-086 surface with a public-only post-cutoff recovery authority.

    Before migration it can bootstrap through LAB-085.  After the authenticated
    cutoff, restart bypasses LAB-084/085 symmetric recovery controllers entirely:
    only LAB-083 root/provider state, the Ed25519 public recovery history and the
    signed migration projection are loaded.
    """

    def __init__(
        self,
        path,
        attested,
        bootstrap,
        signer,
        rotation_authority,
        enablement,
        recovery_authority=None,
        public_recovery_authority=None,
        custody_enablement_signatures=None,
    ):
        post_cutoff = _boundary_exists(path)
        self._lab086_initializing = True
        if post_cutoff:
            if type(public_recovery_authority) is not PublicRecoveryAuthority:
                raise TypeError("exact LAB-085 PublicRecoveryAuthority required")
            SupportedThresholdAuthorizedAsymmetricProviderLedger.__init__(
                self,
                path,
                attested,
                bootstrap,
                signer,
                rotation_authority,
                enablement,
            )
            self.public_recovery_custody = AsymmetricRecoveryCustody(
                path, public_recovery_authority
            )
        else:
            if recovery_authority is None:
                raise TypeError("pre-cutoff LAB-084 RecoveryAuthority required")
            SupportedRecoveryCustodyLedger.__init__(
                self,
                path,
                attested,
                bootstrap,
                signer,
                rotation_authority,
                enablement,
                recovery_authority,
                public_recovery_authority,
                custody_enablement_signatures=custody_enablement_signatures,
            )
        self._lab086_initializing = False
        self.migration_guard = AuthenticatedBreakGlassMigrationGuard(self)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._ensure_asymmetric_schema_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        self.verify_durable()

    @staticmethod
    def _ensure_asymmetric_schema_locked(q):
        q.execute(
            """CREATE TABLE IF NOT EXISTS provider_asymmetric_break_glass_proofs(
              new_rotation_authority_id TEXT PRIMARY KEY,old_rotation_authority_id TEXT NOT NULL,
              old_rotation_version INTEGER NOT NULL,old_rotation_generation INTEGER NOT NULL,
              public_authority_id TEXT NOT NULL,public_authority_version INTEGER NOT NULL,
              public_authority_generation INTEGER NOT NULL,boundary_digest TEXT NOT NULL,
              intent_digest TEXT NOT NULL,public_signatures_json TEXT NOT NULL)"""
        )
        q.execute(
            """CREATE TABLE IF NOT EXISTS provider_asymmetric_recovery_public_root_proofs(
              new_public_authority_id TEXT PRIMARY KEY,old_public_authority_id TEXT NOT NULL,
              root_authority_id TEXT NOT NULL,root_version INTEGER NOT NULL,root_generation INTEGER NOT NULL,
              intent_digest TEXT NOT NULL,root_signatures_json TEXT NOT NULL)"""
        )

    def _post_cutoff(self, q):
        return (
            q.execute(
                "SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1"
            ).fetchone()
            is not None
        )

    def recover_rotation_authority(self, *a, **k):
        raise AsymmetricBreakGlassError(
            "HMAC-only recovery is verification-only legacy history"
        )

    def recover_rotation_authority_with_custody(self, *a, **k):
        raise AsymmetricBreakGlassError(
            "compatibility HMAC recovery is disabled on the LAB-086 surface"
        )

    def rotate_recovery_authority_with_custody(self, *args, **kwargs):
        q = self._con()
        try:
            post = self._post_cutoff(q)
        finally:
            q.close()
        if post:
            raise PublicRecoveryRotationError(
                "post-cutoff symmetric recovery rotation is disabled; use rotate_public_recovery_authority"
            )
        return SupportedRecoveryCustodyLedger.rotate_recovery_authority_with_custody(
            self, *args, **kwargs
        )

    @staticmethod
    def _require_successor(old, new):
        if (
            new.authority_name != old.authority_name
            or new.version != old.version + 1
            or new.generation != old.generation + 1
        ):
            raise AsymmetricBreakGlassError(
                "root successor must advance version/generation exactly one"
            )

    def _provider_transitions_locked(self, q):
        enablement = self._load_enablement_locked(q)
        rows = q.execute(
            "SELECT t.provider_id,t.old_generation_id,t.new_generation_id,g.generation "
            "FROM asymmetric_provider_transitions t "
            "JOIN asymmetric_provider_generations g ON g.generation_id=t.new_generation_id "
            "WHERE g.generation>? ORDER BY g.generation",
            (enablement.start_provider_generation,),
        ).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]

    def public_recovery_rotation_payload(self, new_public):
        if type(new_public) is not PublicRecoveryAuthority:
            raise TypeError("exact PublicRecoveryAuthority required")
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._ensure_asymmetric_schema_locked(q)
            boundary = self.migration_guard.verify_locked(q)
            if boundary is None:
                raise MigrationGuardError("authenticated migration boundary required")
            old = self.public_recovery_custody.current_locked(q)
            root = self.rotation_authority.current_locked(q)
            new_public.validate()
            if (
                new_public.name != old.name
                or new_public.version != old.version + 1
                or new_public.generation != old.generation + 1
            ):
                raise PublicRecoveryRotationError(
                    "public recovery authority must advance exactly one"
                )
            payload = custody_rotation_payload(old, new_public, root.authority_id)
            q.commit()
            return payload
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def rotate_public_recovery_authority(
        self,
        new_public,
        old_public_signatures,
        new_public_signatures,
        root_signatures,
    ):
        if type(new_public) is not PublicRecoveryAuthority:
            raise TypeError("exact PublicRecoveryAuthority required")
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._reject_prepared_locked(q)
            self._ensure_asymmetric_schema_locked(q)
            boundary = self.migration_guard.verify_locked(q)
            if boundary is None:
                raise MigrationGuardError("authenticated migration boundary required")
            old = self.public_recovery_custody.current_locked(q)
            root = self.rotation_authority.current_locked(q)
            if (
                new_public.name != old.name
                or new_public.version != old.version + 1
                or new_public.generation != old.generation + 1
            ):
                raise PublicRecoveryRotationError(
                    "public recovery authority must advance exactly one"
                )
            payload = custody_rotation_payload(old, new_public, root.authority_id)
            old_valid = accepted_public_signatures(
                old, payload, tuple(old_public_signatures)
            )
            new_valid = accepted_public_signatures(
                new_public, payload, tuple(new_public_signatures)
            )
            verify_public_threshold(old, payload, old_valid)
            verify_public_threshold(new_public, payload, new_valid)
            root_valid = _accepted_root_signatures(root, payload, tuple(root_signatures))
            self.public_recovery_custody.rotate_locked(
                q, new_public, root.authority_id, old_valid, new_valid
            )
            proof = (
                old.authority_id,
                root.authority_id,
                root.version,
                root.generation,
                custody_sha(payload),
                self.rotation_authority._encode_signatures(root_valid),
            )
            existing = q.execute(
                "SELECT old_public_authority_id,root_authority_id,root_version,root_generation,"
                "intent_digest,root_signatures_json FROM provider_asymmetric_recovery_public_root_proofs "
                "WHERE new_public_authority_id=?",
                (new_public.authority_id,),
            ).fetchone()
            if existing is not None and existing != proof:
                raise PublicRecoveryRotationError("public recovery root proof substitution")
            if existing is None:
                q.execute(
                    "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES(?,?,?,?,?,?,?)",
                    (new_public.authority_id, *proof),
                )
            self._verify_public_recovery_rotations_locked(q, boundary)
            q.commit()
            return {
                "old_public_authority_id": old.authority_id,
                "new_public_authority_id": new_public.authority_id,
                "root_authority_id": root.authority_id,
                "root_signers": tuple(sorted(s.signer_id for s in root_valid)),
            }
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _verify_public_recovery_rotations_locked(self, q, boundary):
        public_rows = q.execute(
            "SELECT authority_id FROM provider_recovery_public_authorities ORDER BY version"
        ).fetchall()
        if not public_rows:
            raise PublicRecoveryRotationError("missing public recovery history")
        publics = [
            self.public_recovery_custody._load_authority_locked(q, row[0])
            for row in public_rows
        ]
        cutoff_id = boundary["public_authority_id"]
        cutoff_version = boundary["public_authority_version"]
        cutoff_index = None
        for index, public in enumerate(publics):
            if public.authority_id == cutoff_id:
                cutoff_index = index
                break
        if cutoff_index is None or publics[cutoff_index].version != cutoff_version:
            raise PublicRecoveryRotationError("cutoff public authority absent from history")
        windows = {
            cutoff_id: [boundary["root_version"], None]
        }
        required = 0
        for old, new in zip(publics[cutoff_index:], publics[cutoff_index + 1 :]):
            row = q.execute(
                "SELECT old_public_authority_id,root_authority_id,root_version,root_generation,"
                "intent_digest,root_signatures_json "
                "FROM provider_asymmetric_recovery_public_root_proofs WHERE new_public_authority_id=?",
                (new.authority_id,),
            ).fetchone()
            if row is None or row[0] != old.authority_id:
                raise PublicRecoveryRotationError(
                    "post-cutoff public recovery transition lacks root proof"
                )
            root = self.rotation_authority._load_locked(q, row[1])
            if (root.version, root.generation) != (row[2], row[3]):
                raise PublicRecoveryRotationError("public recovery root metadata mismatch")
            payload = custody_rotation_payload(old, new, root.authority_id)
            if custody_sha(payload) != row[4]:
                raise PublicRecoveryRotationError("public recovery intent digest mismatch")
            accepted = _accepted_root_signatures(
                root, payload, self.rotation_authority._decode_signatures(row[5])
            )
            if self.rotation_authority._encode_signatures(accepted) != row[5]:
                raise PublicRecoveryRotationError("noncanonical public recovery root signatures")
            windows[old.authority_id][1] = root.version
            windows[new.authority_id] = [root.version, None]
            required += 1
        count = q.execute(
            "SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs"
        ).fetchone()[0]
        if count != required:
            raise PublicRecoveryRotationError("orphan public recovery root proof")
        return {key: tuple(value) for key, value in windows.items()}

    def asymmetric_recovery_payload(self, new_authority):
        require_canonical_authority(new_authority)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._ensure_asymmetric_schema_locked(q)
            self._verify_lab086_locked(q)
            boundary = self.migration_guard.verify_locked(q)
            if boundary is None:
                raise MigrationGuardError("authenticated migration boundary required")
            old = self.rotation_authority.current_locked(q)
            public = self.public_recovery_custody.current_locked(q)
            self._require_successor(old, new_authority)
            out = asymmetric_break_glass_payload(
                boundary_digest=boundary["boundary_digest"],
                old_root=old,
                new_root=new_authority,
                public_authority=public,
            )
            q.commit()
            return out
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def recover_rotation_authority_asymmetric(
        self, new_authority, public_signatures
    ):
        require_canonical_authority(new_authority)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._reject_prepared_locked(q)
            self._ensure_asymmetric_schema_locked(q)
            self._verify_lab086_locked(q)
            boundary = self.migration_guard.verify_locked(q)
            if boundary is None:
                raise MigrationGuardError("authenticated migration boundary required")
            old = self.rotation_authority.current_locked(q)
            public = self.public_recovery_custody.current_locked(q)
            self._require_successor(old, new_authority)
            payload = asymmetric_break_glass_payload(
                boundary_digest=boundary["boundary_digest"],
                old_root=old,
                new_root=new_authority,
                public_authority=public,
            )
            accepted = accepted_public_signatures(
                public, payload, tuple(public_signatures)
            )
            verify_public_threshold(public, payload, accepted)
            encoded = self.public_recovery_custody._encode_signatures(accepted)
            intent = _digest(payload)
            self.rotation_authority._insert_authority_locked(q, new_authority)
            changed = q.execute(
                "UPDATE provider_rotation_authority_head SET authority_id=?,version=?,generation=? "
                "WHERE singleton=1 AND authority_id=? AND version=? AND generation=?",
                (
                    new_authority.authority_id,
                    new_authority.version,
                    new_authority.generation,
                    old.authority_id,
                    old.version,
                    old.generation,
                ),
            ).rowcount
            if changed != 1:
                raise StaleAuthority("root head changed during asymmetric recovery")
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_proofs VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    new_authority.authority_id,
                    old.authority_id,
                    old.version,
                    old.generation,
                    public.authority_id,
                    public.version,
                    public.generation,
                    boundary["boundary_digest"],
                    intent,
                    encoded,
                ),
            )
            self._verify_lab086_locked(q)
            q.commit()
            return {
                "old_rotation_authority_id": old.authority_id,
                "new_rotation_authority_id": new_authority.authority_id,
                "public_recovery_authority_id": public.authority_id,
                "public_recovery_signers": tuple(
                    sorted(s.signer_id for s in accepted)
                ),
                "intent_digest": intent,
            }
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _verify_asymmetric_edge_locked(
        self, q, old, new, public_windows, boundary_digest
    ):
        row = q.execute(
            "SELECT old_rotation_authority_id,old_rotation_version,old_rotation_generation,"
            "public_authority_id,public_authority_version,public_authority_generation,"
            "boundary_digest,intent_digest,public_signatures_json "
            "FROM provider_asymmetric_break_glass_proofs WHERE new_rotation_authority_id=?",
            (new.authority_id,),
        ).fetchone()
        if row is None:
            raise AsymmetricBreakGlassError("missing asymmetric proof")
        if (row[0], row[1], row[2]) != (
            old.authority_id,
            old.version,
            old.generation,
        ):
            raise AsymmetricBreakGlassError("asymmetric predecessor mismatch")
        if row[6] != boundary_digest:
            raise AsymmetricBreakGlassError("boundary mismatch")
        public = self.public_recovery_custody._load_authority_locked(q, row[3])
        if (public.version, public.generation) != (row[4], row[5]):
            raise AsymmetricBreakGlassError("public recovery metadata mismatch")
        window = public_windows.get(public.authority_id)
        if window is None:
            raise PublicRecoveryRotationError("unknown post-cutoff public recovery generation")
        lower, upper = window
        if old.version < lower:
            raise PublicRecoveryRotationError("public recovery generation used before activation")
        if upper is not None and old.version >= upper:
            raise PublicRecoveryRotationError("stale public recovery generation used after rotation")
        payload = asymmetric_break_glass_payload(
            boundary_digest=boundary_digest,
            old_root=old,
            new_root=new,
            public_authority=public,
        )
        if _digest(payload) != row[7]:
            raise AsymmetricBreakGlassError("intent digest mismatch")
        decoded = self.public_recovery_custody._decode_signatures(row[8])
        accepted = accepted_public_signatures(public, payload, decoded)
        verify_public_threshold(public, payload, accepted)
        if self.public_recovery_custody._encode_signatures(accepted) != row[8]:
            raise AsymmetricBreakGlassError("noncanonical signatures")

    def _verify_provider_thresholds_locked(self, q, by_id):
        for provider_id, old_gid, new_gid in self._provider_transitions_locked(q):
            row = q.execute(
                "SELECT authority_id,authority_version,authority_generation,intent_digest,signatures_json "
                "FROM provider_rotation_threshold_proofs WHERE new_provider_generation_id=?",
                (new_gid,),
            ).fetchone()
            if row is None:
                raise ThresholdNotMet("provider transition missing threshold proof")
            authority = by_id.get(row[0])
            if authority is None:
                raise InvalidAuthority("provider proof references unknown root")
            intent = ProviderRotationIntent(
                provider_id,
                old_gid,
                new_gid,
                authority.authority_id,
                authority.version,
                authority.generation,
            )
            proof = ThresholdProof(
                row[3],
                row[0],
                row[1],
                row[2],
                self.rotation_authority._decode_signatures(row[4]),
            )
            verify_threshold(authority, intent, proof)

    def _verify_lab086_locked(self, q):
        self._ensure_asymmetric_schema_locked(q)
        boundary = self.migration_guard.verify_locked(q)
        if boundary is None:
            # Pre-cutoff only: symmetric LAB-085 is still authoritative.
            self._verify_custody_bindings_locked(q)
            self._verify_break_glass_custody_locked(q)
            return SupportedRecoveryAuthorityLifecycleLedger._verify_mixed_authority_history_locked(
                self, q, self._provider_transitions_locked(q)
            )

        public_windows = self._verify_public_recovery_rotations_locked(q, boundary)
        rows = q.execute(
            "SELECT authority_id FROM provider_rotation_authorities ORDER BY version"
        ).fetchall()
        if not rows:
            raise InvalidAuthority("missing root history")
        authorities = [
            self.rotation_authority._load_locked(q, r[0]) for r in rows
        ]
        if authorities[0].authority_id != self.rotation_authority.bootstrap.authority_id:
            raise StaleAuthority("root bootstrap changed")
        by_id = {a.authority_id: a for a in authorities}
        total = (
            q.execute(
                "SELECT COUNT(*) FROM provider_rotation_authority_transitions"
            ).fetchone()[0]
            + q.execute(
                "SELECT COUNT(*) FROM provider_rotation_recovery_transitions"
            ).fetchone()[0]
            + q.execute(
                "SELECT COUNT(*) FROM provider_asymmetric_break_glass_proofs"
            ).fetchone()[0]
        )
        if total != len(authorities) - 1:
            raise RecoveryError("root proof count mismatch")
        legacy_projection = {
            tuple(row)
            for row in boundary["projection"]["semantic"]["legacy_recovery_edges"]
        }
        for old, new in zip(authorities, authorities[1:]):
            self._require_successor(old, new)
            normal = q.execute(
                "SELECT COUNT(*) FROM provider_rotation_authority_transitions WHERE new_authority_id=?",
                (new.authority_id,),
            ).fetchone()[0]
            legacy = q.execute(
                "SELECT old_rotation_authority_id,old_rotation_version,old_rotation_generation,"
                "recovery_authority_id,recovery_generation,intent_digest,signatures_json "
                "FROM provider_rotation_recovery_transitions WHERE new_rotation_authority_id=?",
                (new.authority_id,),
            ).fetchone()
            asym = q.execute(
                "SELECT COUNT(*) FROM provider_asymmetric_break_glass_proofs WHERE new_rotation_authority_id=?",
                (new.authority_id,),
            ).fetchone()[0]
            if normal + (0 if legacy is None else 1) + asym != 1:
                raise RecoveryError("root edge must have exactly one proof type")
            if normal:
                self._verify_normal_edge_locked(q, old, new)
            elif legacy is not None:
                projected = (
                    new.authority_id,
                    legacy[0],
                    legacy[1],
                    legacy[2],
                    legacy[3],
                    legacy[4],
                    legacy[5],
                )
                if projected not in legacy_projection:
                    raise AsymmetricBreakGlassError(
                        "legacy root edge is not committed by migration boundary"
                    )
                if legacy[6] != "[]":
                    raise AsymmetricBreakGlassError(
                        "legacy HMAC proof bytes were not scrubbed"
                    )
                if new.version > boundary["root_version"]:
                    raise AsymmetricBreakGlassError(
                        "legacy HMAC edge exists after migration cutoff"
                    )
            else:
                if old.version < boundary["root_version"]:
                    raise AsymmetricBreakGlassError("asymmetric proof before cutoff")
                self._verify_asymmetric_edge_locked(
                    q, old, new, public_windows, boundary["boundary_digest"]
                )
        if (
            self.rotation_authority.current_locked(q).authority_id
            != authorities[-1].authority_id
        ):
            raise StaleAuthority("root head rollback")
        self._verify_provider_thresholds_locked(q, by_id)
        return True

    def verify_durable(self):
        if getattr(self, "_lab086_initializing", False) or not hasattr(
            self, "migration_guard"
        ):
            return True
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable(self)
            self.public_recovery_custody.verify_durable()
            self._verify_lab086_locked(q)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
