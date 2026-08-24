from __future__ import annotations
import hashlib
import hmac
import json

from experiments.provider_threshold_rotation.protocol import Signature, ThresholdNotMet, mac
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import accepted_public_signatures, verify_public_threshold
from experiments.provider_recovery_authority_lifecycle.final_supported import SupportedRecoveryCustodyLedger
from experiments.provider_recovery_authority_lifecycle.supported import SupportedRecoveryAuthorityLifecycleLedger
from .strict_fence import install_public_mutation_fence_locked


class MigrationGuardError(RuntimeError):
    pass


class LegacyHistoryChanged(MigrationGuardError):
    pass


def _canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def _digest(value) -> str:
    raw = value if isinstance(value, (bytes, bytearray)) else _canon(value)
    return hashlib.sha256(raw).hexdigest()


def migration_payload(*, legacy_digest, cutoff_root, public_authority):
    return {
        'kind': 'provider-asymmetric-break-glass-boundary-v4',
        'legacy_digest': legacy_digest,
        'cutoff_root_id': cutoff_root.authority_id,
        'cutoff_root_version': cutoff_root.version,
        'cutoff_root_generation': cutoff_root.generation,
        'public_authority_id': public_authority.authority_id,
        'public_authority_version': public_authority.version,
        'public_authority_generation': public_authority.generation,
        'legacy_recovery_hmac_material': 'scrubbed',
        'root_coauthorization': 'required',
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
            f'migration root valid={len(accepted)} threshold={root.threshold}'
        )
    return tuple(accepted)


def _exact_supported_ledger(ledger):
    if type(ledger) is SupportedRecoveryCustodyLedger:
        return True
    try:
        from experiments.asymmetric_break_glass_history.suffix import SupportedAsymmetricBreakGlassLedger
    except ImportError:
        return False
    return type(ledger) is SupportedAsymmetricBreakGlassLedger


class AuthenticatedBreakGlassMigrationGuard:
    """Convert verified LAB-084/085 recovery history into a public-only cutoff.

    Before migration the complete compatibility history is checked by LAB-085.
    The cutoff signs a canonical non-secret projection of that verified state. In
    the same transaction all durable recovery HMAC key maps and recovery-HMAC proof
    bytes are destroyed. Post-cutoff verification uses only the signed projection
    plus Ed25519 public-custody history.

    A migration cutoff is consequential trust metadata, so it requires two
    independent authorizations over the exact same canonical payload:
      * the current Ed25519 public-recovery threshold; and
      * the current normal/root threshold.

    The root coauthorization prevents a stale but cryptographically valid
    historical public-recovery quorum from rebinding an already durable cutoff.

    The migration boundary also installs an unconditional SQL deny fence for every
    underlying public-recovery mutation path. Historical proof rows remain restart
    evidence only and are never interpreted by SQL as mutation authority.
    """

    def __init__(self, ledger):
        if not _exact_supported_ledger(ledger):
            raise TypeError('exact LAB-085/LAB-086 supported ledger required')
        self.ledger = ledger
        q = ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            self._ensure_schema_locked(q)
            boundary_exists = self._boundary_row_locked(q) is not None
            if type(ledger) is SupportedRecoveryCustodyLedger and (not boundary_exists):
                self._verify_inherited_locked(q)
            self.verify_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    @staticmethod
    def _ensure_schema_locked(q):
        q.execute('CREATE TABLE IF NOT EXISTS provider_asymmetric_break_glass_boundary('
                  'singleton INTEGER PRIMARY KEY CHECK(singleton=1),legacy_digest TEXT NOT NULL,'
                  'cutoff_root_id TEXT NOT NULL,cutoff_root_version INTEGER NOT NULL,cutoff_root_generation INTEGER NOT NULL,'
                  'public_authority_id TEXT NOT NULL,public_authority_version INTEGER NOT NULL,'
                  'public_authority_generation INTEGER NOT NULL,boundary_digest TEXT NOT NULL,signatures_json TEXT NOT NULL)')
        q.execute('CREATE TABLE IF NOT EXISTS provider_asymmetric_break_glass_legacy_projection('
                  'singleton INTEGER PRIMARY KEY CHECK(singleton=1),projection_json TEXT NOT NULL)')
        q.execute('CREATE TABLE IF NOT EXISTS provider_asymmetric_break_glass_root_proof('
                  'singleton INTEGER PRIMARY KEY CHECK(singleton=1),boundary_digest TEXT NOT NULL,'
                  'root_authority_id TEXT NOT NULL,root_version INTEGER NOT NULL,root_generation INTEGER NOT NULL,'
                  'root_signatures_json TEXT NOT NULL)')
        for trigger_name in (
            'provider_asymmetric_break_glass_no_legacy_hmac',
            'provider_asymmetric_break_glass_no_symmetric_lifecycle',
            'provider_asymmetric_break_glass_no_symmetric_authority',
            'provider_asymmetric_break_glass_no_compat_authority',
        ):
            q.execute(f'DROP TRIGGER IF EXISTS {trigger_name}')
        q.execute("CREATE TRIGGER provider_asymmetric_break_glass_no_legacy_hmac "
                  "BEFORE INSERT ON provider_rotation_recovery_transitions "
                  "WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1) "
                  "BEGIN SELECT RAISE(ABORT,'LAB-086 migration forbids new HMAC break-glass rows'); END")
        q.execute("CREATE TRIGGER provider_asymmetric_break_glass_no_symmetric_lifecycle "
                  "BEFORE INSERT ON provider_recovery_lifecycle_transitions "
                  "WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1) "
                  "BEGIN SELECT RAISE(ABORT,'LAB-086 migration forbids new symmetric recovery lifecycle rows'); END")
        q.execute("CREATE TRIGGER provider_asymmetric_break_glass_no_symmetric_authority "
                  "BEFORE INSERT ON provider_recovery_lifecycle_authorities "
                  "WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1) "
                  "BEGIN SELECT RAISE(ABORT,'LAB-086 migration forbids new symmetric recovery authorities'); END")
        q.execute("CREATE TRIGGER provider_asymmetric_break_glass_no_compat_authority "
                  "BEFORE INSERT ON provider_rotation_recovery_authorities "
                  "WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1) "
                  "BEGIN SELECT RAISE(ABORT,'LAB-086 migration forbids new compatibility recovery authorities'); END")
        q.execute('CREATE TABLE IF NOT EXISTS provider_asymmetric_recovery_public_root_proofs('
                  'new_public_authority_id TEXT PRIMARY KEY,old_public_authority_id TEXT NOT NULL,'
                  'root_authority_id TEXT NOT NULL,root_version INTEGER NOT NULL,root_generation INTEGER NOT NULL,'
                  'intent_digest TEXT NOT NULL,root_signatures_json TEXT NOT NULL)')
        install_public_mutation_fence_locked(q)

    @staticmethod
    def _boundary_row_locked(q):
        return q.execute(
            'SELECT legacy_digest,cutoff_root_id,cutoff_root_version,cutoff_root_generation,'
            'public_authority_id,public_authority_version,public_authority_generation,boundary_digest,signatures_json '
            'FROM provider_asymmetric_break_glass_boundary WHERE singleton=1'
        ).fetchone()

    def _verify_inherited_locked(self, q):
        SupportedRecoveryAuthorityLifecycleLedger.verify_durable(self.ledger)
        self.ledger.public_recovery_custody.verify_durable()
        self.ledger._verify_custody_bindings_locked(q)
        self.ledger._verify_break_glass_custody_locked(q)
        return True

    def _verify_preboundary_locked(self, q):
        if type(self.ledger) is SupportedRecoveryCustodyLedger:
            return self._verify_inherited_locked(q)
        return self.ledger._verify_lab086_locked(q)

    @staticmethod
    def _rows(q, sql, args=()):
        return [list(row) for row in q.execute(sql, args).fetchall()]

    def _semantic_snapshot_locked(self, q, cutoff_version):
        return {
            'compat_authorities': self._rows(
                q, 'SELECT authority_id,name,generation,threshold,revoked_json '
                   'FROM provider_rotation_recovery_authorities ORDER BY generation'
            ),
            'compat_head': self._rows(
                q, 'SELECT authority_id,generation FROM provider_rotation_recovery_head WHERE singleton=1'
            ),
            'lifecycle_authorities': self._rows(
                q, 'SELECT authority_id,version,name,generation,threshold,revoked_json '
                   'FROM provider_recovery_lifecycle_authorities ORDER BY version'
            ),
            'lifecycle_head': self._rows(
                q, 'SELECT authority_id,version,generation FROM provider_recovery_lifecycle_head WHERE singleton=1'
            ),
            'lifecycle_transitions': self._rows(
                q, 'SELECT new_authority_id,old_authority_id,root_authority_id,root_version,root_generation,intent_digest '
                   'FROM provider_recovery_lifecycle_transitions ORDER BY root_version,new_authority_id'
            ),
            'custody_bindings': self._rows(
                q, 'SELECT symmetric_authority_id,public_authority_id,version,generation '
                   'FROM provider_recovery_custody_bindings ORDER BY version'
            ),
            'legacy_recovery_edges': self._rows(
                q, 'SELECT r.new_rotation_authority_id,r.old_rotation_authority_id,r.old_rotation_version,'
                   'r.old_rotation_generation,r.recovery_authority_id,r.recovery_generation,r.intent_digest '
                   'FROM provider_rotation_recovery_transitions r '
                   'JOIN provider_rotation_authorities a ON a.authority_id=r.new_rotation_authority_id '
                   'WHERE a.version<=? ORDER BY a.version',
                (cutoff_version,),
            ),
            'custody_proofs': self._rows(
                q, 'SELECT p.new_rotation_authority_id,p.public_authority_id,p.symmetric_authority_id,'
                   'p.compatibility_intent_digest,p.custody_intent_digest,p.public_signatures_json '
                   'FROM provider_rotation_recovery_custody_proofs p '
                   'JOIN provider_rotation_authorities a ON a.authority_id=p.new_rotation_authority_id '
                   'WHERE a.version<=? ORDER BY a.version',
                (cutoff_version,),
            ),
            'custody_enablement': self._rows(
                q, 'SELECT start_rotation_authority_id,start_rotation_version,start_rotation_generation,'
                   'symmetric_authority_id,public_authority_id '
                   'FROM provider_recovery_custody_enablement WHERE singleton=1'
            ),
            'custody_enablement_proof': self._rows(
                q, 'SELECT enablement_digest,public_signatures_json '
                   'FROM provider_recovery_custody_enablement_proof WHERE singleton=1'
            ),
        }

    def _build_projection_locked(self, q, cutoff_root, public_head):
        roots = {}
        for authority_id, in q.execute(
            'SELECT authority_id FROM provider_rotation_authorities ORDER BY version'
        ).fetchall():
            candidate = self.ledger.rotation_authority._load_locked(q, authority_id)
            roots[candidate.authority_id] = candidate
        windows = self.ledger._lifecycle_windows_locked(q, roots)
        serialized_windows = []
        for recovery_id, (versioned, lower, upper) in sorted(
            windows.items(), key=lambda item: item[1][0].version
        ):
            binding = q.execute(
                'SELECT public_authority_id,version,generation '
                'FROM provider_recovery_custody_bindings WHERE symmetric_authority_id=?',
                (versioned.authority_id,),
            ).fetchone()
            serialized_windows.append({
                'recovery_authority_id': recovery_id,
                'symmetric_authority_id': versioned.authority_id,
                'version': versioned.version,
                'generation': versioned.generation,
                'activation_root_version': lower,
                'deactivation_root_version': upper,
                'public_authority_id': None if binding is None else binding[0],
            })
        return {
            'schema_version': 1,
            'cutoff_root_id': cutoff_root.authority_id,
            'cutoff_root_version': cutoff_root.version,
            'cutoff_public_authority_id': public_head.authority_id,
            'cutoff_public_version': public_head.version,
            'cutoff_public_generation': public_head.generation,
            'semantic': self._semantic_snapshot_locked(q, cutoff_root.version),
            'recovery_windows': serialized_windows,
        }

    @staticmethod
    def _encode_projection(projection):
        return _canon(projection).decode()

    @staticmethod
    def _decode_projection(raw):
        try:
            value = json.loads(raw)
        except Exception as exc:
            raise MigrationGuardError('invalid migration projection JSON') from exc
        if not isinstance(value, dict) or value.get('schema_version') != 1:
            raise MigrationGuardError('invalid migration projection schema')
        if _canon(value).decode() != raw:
            raise MigrationGuardError('noncanonical migration projection')
        return value

    @staticmethod
    def _scrub_legacy_hmac_material_locked(q):
        q.execute("UPDATE provider_rotation_recovery_transitions SET signatures_json='[]'")
        q.execute("UPDATE provider_rotation_recovery_authorities SET keys_json='{}'")
        q.execute("UPDATE provider_recovery_lifecycle_authorities SET keys_json='{}'")
        q.execute(
            "UPDATE provider_recovery_lifecycle_transitions "
            "SET old_signatures_json='[]',new_signatures_json='[]',root_signatures_json='[]'"
        )

    @staticmethod
    def _assert_legacy_hmac_material_scrubbed_locked(q):
        checks = (
            ('provider_rotation_recovery_transitions', 'signatures_json', '[]'),
            ('provider_rotation_recovery_authorities', 'keys_json', '{}'),
            ('provider_recovery_lifecycle_authorities', 'keys_json', '{}'),
            ('provider_recovery_lifecycle_transitions', 'old_signatures_json', '[]'),
            ('provider_recovery_lifecycle_transitions', 'new_signatures_json', '[]'),
            ('provider_recovery_lifecycle_transitions', 'root_signatures_json', '[]'),
        )
        for table, column, expected in checks:
            count = q.execute(
                f'SELECT COUNT(*) FROM {table} WHERE {column}!=?', (expected,)
            ).fetchone()[0]
            if count:
                raise MigrationGuardError(
                    f'legacy symmetric recovery material remains in {table}.{column}'
                )
        return True

    def payload(self):
        q = self.ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            self._ensure_schema_locked(q)
            if self._boundary_row_locked(q) is not None:
                raise MigrationGuardError('migration boundary already exists')
            self.ledger._reject_prepared_locked(q)
            self._verify_preboundary_locked(q)
            root = self.ledger.rotation_authority.current_locked(q)
            public = self.ledger.public_recovery_custody.current_locked(q)
            projection = self._build_projection_locked(q, root, public)
            out = migration_payload(
                legacy_digest=_digest(projection),
                cutoff_root=root,
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

    def establish(self, public_signatures, root_signatures):
        q = self.ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            self._ensure_schema_locked(q)
            if self._boundary_row_locked(q) is not None:
                raise MigrationGuardError('migration boundary already exists')
            self.ledger._reject_prepared_locked(q)
            self._verify_preboundary_locked(q)
            root = self.ledger.rotation_authority.current_locked(q)
            public = self.ledger.public_recovery_custody.current_locked(q)
            projection = self._build_projection_locked(q, root, public)
            legacy = _digest(projection)
            payload = migration_payload(
                legacy_digest=legacy, cutoff_root=root, public_authority=public
            )
            accepted_public = accepted_public_signatures(
                public, payload, tuple(public_signatures)
            )
            verify_public_threshold(public, payload, accepted_public)
            accepted_root = _accepted_root_signatures(
                root, payload, tuple(root_signatures)
            )
            bd = _digest(payload)
            encoded_public = self.ledger.public_recovery_custody._encode_signatures(
                accepted_public
            )
            encoded_root = self.ledger.rotation_authority._encode_signatures(
                accepted_root
            )
            q.execute(
                'INSERT INTO provider_asymmetric_break_glass_legacy_projection VALUES(1,?)',
                (self._encode_projection(projection),),
            )
            q.execute(
                'INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1,?,?,?,?,?,?,?,?,?)',
                (
                    legacy, root.authority_id, root.version, root.generation,
                    public.authority_id, public.version, public.generation,
                    bd, encoded_public,
                ),
            )
            q.execute(
                'INSERT INTO provider_asymmetric_break_glass_root_proof VALUES(1,?,?,?,?,?)',
                (
                    bd, root.authority_id, root.version, root.generation, encoded_root
                ),
            )
            self._scrub_legacy_hmac_material_locked(q)
            self.verify_locked(q)
            q.commit()
            return bd
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_locked(self, q):
        self.ledger.public_recovery_custody.verify_durable()
        row = self._boundary_row_locked(q)
        root_proof = q.execute(
            'SELECT boundary_digest,root_authority_id,root_version,root_generation,root_signatures_json '
            'FROM provider_asymmetric_break_glass_root_proof WHERE singleton=1'
        ).fetchone()
        if row is None:
            if root_proof is not None:
                raise MigrationGuardError('orphan migration root proof')
            return None
        if root_proof is None:
            raise MigrationGuardError('missing migration root coauthorization')
        legacy, rid, rv, rg, pid, pv, pg, bd, sigs = row
        projection_row = q.execute(
            'SELECT projection_json FROM provider_asymmetric_break_glass_legacy_projection WHERE singleton=1'
        ).fetchone()
        if projection_row is None:
            raise MigrationGuardError('missing migration legacy projection')
        projection = self._decode_projection(projection_row[0])
        if _digest(projection) != legacy:
            raise MigrationGuardError('legacy projection digest mismatch')
        root = self.ledger.rotation_authority._load_locked(q, rid)
        if (root.version, root.generation) != (rv, rg):
            raise MigrationGuardError('boundary root metadata mismatch')
        if (
            projection.get('cutoff_root_id') != root.authority_id
            or projection.get('cutoff_root_version') != root.version
            or projection.get('cutoff_public_authority_id') != pid
            or projection.get('cutoff_public_version') != pv
            or projection.get('cutoff_public_generation') != pg
        ):
            raise MigrationGuardError('projection/cutoff identity mismatch')
        public = self.ledger.public_recovery_custody._load_authority_locked(q, pid)
        if (public.version, public.generation) != (pv, pg):
            raise MigrationGuardError('boundary public authority metadata mismatch')
        payload = migration_payload(
            legacy_digest=legacy, cutoff_root=root, public_authority=public
        )
        if _digest(payload) != bd:
            raise MigrationGuardError('boundary digest mismatch')
        decoded_public = self.ledger.public_recovery_custody._decode_signatures(sigs)
        accepted_public = accepted_public_signatures(public, payload, decoded_public)
        verify_public_threshold(public, payload, accepted_public)
        if (
            self.ledger.public_recovery_custody._encode_signatures(accepted_public)
            != sigs
        ):
            raise MigrationGuardError('noncanonical boundary signatures')

        if tuple(root_proof[:4]) != (
            bd, root.authority_id, root.version, root.generation
        ):
            raise MigrationGuardError('migration root proof identity mismatch')
        decoded_root = self.ledger.rotation_authority._decode_signatures(
            root_proof[4]
        )
        accepted_root = _accepted_root_signatures(root, payload, decoded_root)
        if (
            self.ledger.rotation_authority._encode_signatures(accepted_root)
            != root_proof[4]
        ):
            raise MigrationGuardError('noncanonical migration root signatures')

        current_semantic = self._semantic_snapshot_locked(q, root.version)
        if current_semantic != projection.get('semantic'):
            raise LegacyHistoryChanged(
                'legacy recovery semantics changed after migration'
            )
        self._assert_legacy_hmac_material_scrubbed_locked(q)
        return {
            'boundary_digest': bd,
            'legacy_digest': legacy,
            'root_id': root.authority_id,
            'root_version': root.version,
            'public_authority_id': public.authority_id,
            'public_authority_version': public.version,
            'projection': projection,
        }

    def verify(self):
        q = self.ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            self._ensure_schema_locked(q)
            result = self.verify_locked(q)
            q.commit()
            return result
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
