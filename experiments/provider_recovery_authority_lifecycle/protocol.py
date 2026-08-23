from __future__ import annotations

import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from experiments.provider_threshold_rotation.protocol import (
    RotationAuthority,
    Signature,
    ThresholdNotMet,
    key_id,
    mac,
    sha,
)
from experiments.provider_rotation_recovery.protocol import RecoveryAuthority


class LifecycleError(RuntimeError):
    pass


class LifecycleRollback(LifecycleError):
    pass


class LifecycleSubstitution(LifecycleError):
    pass


@dataclass(frozen=True)
class VersionedRecoveryAuthority:
    version: int
    recovery: RecoveryAuthority

    def validate(self):
        self.recovery.validate()
        if type(self.version) is not int or self.version < 1:
            raise LifecycleError("invalid recovery authority version")
        return self

    @property
    def generation(self):
        return self.recovery.generation

    @property
    def descriptor(self):
        self.validate()
        return {
            "version": self.version,
            "name": self.recovery.name,
            "generation": self.recovery.generation,
            "threshold": self.recovery.threshold,
            "keys": dict(sorted(self.recovery.keys.items())),
            "revoked": sorted(self.recovery.revoked),
        }

    @property
    def authority_id(self):
        return sha(self.descriptor)


@dataclass(frozen=True)
class RecoveryAuthorityRotationIntent:
    root_authority_id: str
    root_version: int
    root_generation: int
    old_recovery_id: str
    old_recovery_version: int
    old_recovery_generation: int
    new_recovery: dict

    @property
    def payload(self):
        return {
            "kind": "provider-recovery-authority-rotation",
            "root_authority_id": self.root_authority_id,
            "root_version": self.root_version,
            "root_generation": self.root_generation,
            "old_recovery_id": self.old_recovery_id,
            "old_recovery_version": self.old_recovery_version,
            "old_recovery_generation": self.old_recovery_generation,
            "new_recovery": self.new_recovery,
        }

    @property
    def intent_digest(self):
        return sha(self.payload)


@dataclass(frozen=True)
class RecoveryAuthorityRotationProof:
    intent_digest: str
    old_signatures: tuple[Signature, ...]
    new_signatures: tuple[Signature, ...]
    root_signatures: tuple[Signature, ...]


def _verify_recovery_threshold(authority: VersionedRecoveryAuthority, payload, signatures):
    authority.validate()
    seen=set(); valid=[]; revoked=set(authority.recovery.revoked)
    for sig in signatures:
        if sig.signer_id in seen or sig.signer_id in revoked:
            continue
        seen.add(sig.signer_id)
        hx=authority.recovery.keys.get(sig.signer_id)
        if hx and hmac.compare_digest(mac(bytes.fromhex(hx),payload),sig.signature):
            valid.append(sig.signer_id)
    if len(valid)<authority.recovery.threshold:
        raise ThresholdNotMet(
            f"recovery lifecycle valid={len(valid)} threshold={authority.recovery.threshold}"
        )
    return tuple(sorted(valid))


def _verify_root_threshold(authority: RotationAuthority, payload, signatures):
    authority.validate()
    seen=set(); valid=[]; revoked=set(authority.revoked)
    for sig in signatures:
        if sig.signer_id in seen or sig.signer_id in revoked:
            continue
        seen.add(sig.signer_id)
        hx=authority.keys.get(sig.signer_id)
        if hx and hmac.compare_digest(mac(bytes.fromhex(hx),payload),sig.signature):
            valid.append(sig.signer_id)
    if len(valid)<authority.threshold:
        raise ThresholdNotMet(
            f"root valid={len(valid)} threshold={authority.threshold}"
        )
    return tuple(sorted(valid))


class DurableRecoveryAuthorityLifecycle:
    """LAB-085 first slice: three-party recovery-authority continuity.

    Historical recovery authorities remain verification material. New authority
    requires old-recovery + new-recovery + current root authorization over one
    canonical transition. Asymmetric public-only custody is a later integration
    slice in the same LAB.
    """

    def __init__(
        self,
        path: str | Path,
        bootstrap: VersionedRecoveryAuthority,
    ):
        bootstrap.validate()
        # Pin an immutable-by-reconstruction bootstrap. RecoveryAuthority is frozen
        # but its key map is mutable, so retaining caller-owned dictionaries would
        # let later mutation change the in-memory trust anchor.
        desc = bootstrap.descriptor
        self.path=str(path)
        self.bootstrap=VersionedRecoveryAuthority(
            desc["version"],
            RecoveryAuthority(
                desc["name"],
                desc["generation"],
                desc["threshold"],
                dict(desc["keys"]),
                tuple(desc["revoked"]),
            ),
        )
        self._init()
        self.verify_durable()

    def _con(self):
        q=sqlite3.connect(self.path,timeout=5,isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    def _init(self):
        q=self._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_recovery_lifecycle_authorities(
                  authority_id TEXT PRIMARY KEY,
                  version INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  generation INTEGER NOT NULL,
                  threshold INTEGER NOT NULL,
                  keys_json TEXT NOT NULL,
                  revoked_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_recovery_lifecycle_head(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  authority_id TEXT NOT NULL,
                  version INTEGER NOT NULL,
                  generation INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_recovery_lifecycle_transitions(
                  new_authority_id TEXT PRIMARY KEY,
                  old_authority_id TEXT NOT NULL,
                  root_authority_id TEXT NOT NULL,
                  root_version INTEGER NOT NULL,
                  root_generation INTEGER NOT NULL,
                  intent_digest TEXT NOT NULL,
                  old_signatures_json TEXT NOT NULL,
                  new_signatures_json TEXT NOT NULL,
                  root_signatures_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_recovery_lifecycle_roots(
                  authority_id TEXT PRIMARY KEY,
                  authority_json TEXT NOT NULL
                );
                """
            )
            if q.execute("SELECT COUNT(*) FROM provider_recovery_lifecycle_head").fetchone()[0]==0:
                self._insert_recovery_locked(q,self.bootstrap)
                q.execute(
                    "INSERT INTO provider_recovery_lifecycle_head VALUES(1,?,?,?)",
                    (self.bootstrap.authority_id,self.bootstrap.version,self.bootstrap.generation),
                )
            q.commit()
        finally:
            q.close()

    @staticmethod
    def _encode_sigs(signatures: Iterable[Signature]):
        return json.dumps(
            [{"signer_id":s.signer_id,"signature":s.signature} for s in signatures],
            sort_keys=True,separators=(",",":"),
        )

    @staticmethod
    def _decode_sigs(raw):
        try:
            data=json.loads(raw)
            if not isinstance(data,list):
                raise ValueError()
            return tuple(Signature(x["signer_id"],x["signature"]) for x in data)
        except Exception as exc:
            raise LifecycleSubstitution("invalid persisted signature set") from exc

    def _insert_recovery_locked(self,q,authority:VersionedRecoveryAuthority):
        authority.validate()
        r=authority.recovery
        expected=(
            authority.version,r.name,r.generation,r.threshold,
            json.dumps(r.keys,sort_keys=True,separators=(",",":")),
            json.dumps(sorted(r.revoked),separators=(",",":")),
        )
        q.execute(
            "INSERT OR IGNORE INTO provider_recovery_lifecycle_authorities VALUES(?,?,?,?,?,?,?)",
            (authority.authority_id,*expected),
        )
        stored=q.execute(
            "SELECT version,name,generation,threshold,keys_json,revoked_json "
            "FROM provider_recovery_lifecycle_authorities WHERE authority_id=?",
            (authority.authority_id,),
        ).fetchone()
        if stored!=expected:
            raise LifecycleSubstitution("recovery authority content substitution")

    def _load_recovery_locked(self,q,authority_id):
        row=q.execute(
            "SELECT version,name,generation,threshold,keys_json,revoked_json "
            "FROM provider_recovery_lifecycle_authorities WHERE authority_id=?",
            (authority_id,),
        ).fetchone()
        if row is None:
            raise LifecycleSubstitution("missing recovery authority")
        authority=VersionedRecoveryAuthority(
            row[0],
            RecoveryAuthority(
                row[1],row[2],row[3],dict(json.loads(row[4])),tuple(json.loads(row[5]))
            ),
        )
        authority.validate()
        if authority.authority_id!=authority_id:
            raise LifecycleSubstitution("recovery authority digest mismatch")
        return authority

    def _insert_root_locked(self,q,root:RotationAuthority):
        root.validate()
        body=json.dumps(root.descriptor,sort_keys=True,separators=(",",":"))
        q.execute(
            "INSERT OR IGNORE INTO provider_recovery_lifecycle_roots VALUES(?,?)",
            (root.authority_id,body),
        )
        stored=q.execute(
            "SELECT authority_json FROM provider_recovery_lifecycle_roots WHERE authority_id=?",
            (root.authority_id,),
        ).fetchone()
        if stored is None or stored[0]!=body:
            raise LifecycleSubstitution("co-authorizing root substitution")

    def _load_root_locked(self,q,authority_id):
        row=q.execute(
            "SELECT authority_json FROM provider_recovery_lifecycle_roots WHERE authority_id=?",
            (authority_id,),
        ).fetchone()
        if row is None:
            raise LifecycleSubstitution("missing co-authorizing root")
        raw=json.loads(row[0])
        root=RotationAuthority(
            raw["authority_name"],raw["version"],raw["generation"],raw["threshold"],
            dict(raw["keys"]),tuple(raw.get("revoked",[])),
        )
        root.validate()
        if root.authority_id!=authority_id:
            raise LifecycleSubstitution("co-authorizing root digest mismatch")
        return root

    def current_locked(self,q):
        row=q.execute(
            "SELECT authority_id,version,generation FROM provider_recovery_lifecycle_head WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise LifecycleSubstitution("missing recovery lifecycle head")
        current=self._load_recovery_locked(q,row[0])
        if (current.version,current.generation)!=(row[1],row[2]):
            raise LifecycleSubstitution("recovery lifecycle head mismatch")
        return current

    def current(self):
        q=self._con()
        try:
            return self.current_locked(q)
        finally:
            q.close()

    @staticmethod
    def make_intent(root:RotationAuthority,old:VersionedRecoveryAuthority,new:VersionedRecoveryAuthority):
        return RecoveryAuthorityRotationIntent(
            root.authority_id,root.version,root.generation,
            old.authority_id,old.version,old.generation,new.descriptor,
        )

    def rotate_locked(
        self,q,root:RotationAuthority,new:VersionedRecoveryAuthority,
        old_signatures:tuple[Signature,...],
        new_signatures:tuple[Signature,...],
        root_signatures:tuple[Signature,...],
    ):
        old=self.current_locked(q); root.validate(); new.validate()
        if new.recovery.name!=old.recovery.name:
            raise LifecycleSubstitution("recovery authority name changed")
        if new.version!=old.version+1 or new.generation!=old.generation+1:
            raise LifecycleRollback("recovery authority must advance version/generation exactly one")
        intent=self.make_intent(root,old,new)
        proof=RecoveryAuthorityRotationProof(
            intent.intent_digest,tuple(old_signatures),tuple(new_signatures),tuple(root_signatures)
        )
        old_valid=_verify_recovery_threshold(old,intent.payload,proof.old_signatures)
        new_valid=_verify_recovery_threshold(new,intent.payload,proof.new_signatures)
        root_valid=_verify_root_threshold(root,intent.payload,proof.root_signatures)
        self._insert_root_locked(q,root)
        self._insert_recovery_locked(q,new)
        expected=(
            old.authority_id,root.authority_id,root.version,root.generation,
            intent.intent_digest,self._encode_sigs(old_signatures),
            self._encode_sigs(new_signatures),self._encode_sigs(root_signatures),
        )
        existing=q.execute(
            "SELECT old_authority_id,root_authority_id,root_version,root_generation,"
            "intent_digest,old_signatures_json,new_signatures_json,root_signatures_json "
            "FROM provider_recovery_lifecycle_transitions WHERE new_authority_id=?",
            (new.authority_id,),
        ).fetchone()
        if existing is not None and existing!=expected:
            raise LifecycleSubstitution("recovery lifecycle transition substitution")
        if existing is None:
            q.execute(
                "INSERT INTO provider_recovery_lifecycle_transitions VALUES(?,?,?,?,?,?,?,?,?)",
                (new.authority_id,*expected),
            )
        changed=q.execute(
            "UPDATE provider_recovery_lifecycle_head SET authority_id=?,version=?,generation=? "
            "WHERE singleton=1 AND authority_id=? AND version=? AND generation=?",
            (
                new.authority_id,new.version,new.generation,
                old.authority_id,old.version,old.generation,
            ),
        ).rowcount
        if changed!=1:
            raise LifecycleRollback("recovery lifecycle head changed during rotation")
        return {
            "old_recovery_signers":old_valid,
            "new_recovery_signers":new_valid,
            "root_signers":root_valid,
            "new_authority_id":new.authority_id,
        }

    def rotate(self,root,new,old_signatures,new_signatures,root_signatures):
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            out=self.rotate_locked(q,root,new,old_signatures,new_signatures,root_signatures)
            q.commit()
            return out
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

    def verify_transition_locked(self,q,old,new):
        row=q.execute(
            "SELECT old_authority_id,root_authority_id,root_version,root_generation,"
            "intent_digest,old_signatures_json,new_signatures_json,root_signatures_json "
            "FROM provider_recovery_lifecycle_transitions WHERE new_authority_id=?",
            (new.authority_id,),
        ).fetchone()
        if row is None or row[0]!=old.authority_id:
            raise LifecycleSubstitution("missing recovery lifecycle transition")
        root=self._load_root_locked(q,row[1])
        if (root.version,root.generation)!=(row[2],row[3]):
            raise LifecycleSubstitution("co-authorizing root version/generation mismatch")
        intent=self.make_intent(root,old,new)
        if row[4]!=intent.intent_digest:
            raise LifecycleSubstitution("recovery lifecycle intent digest mismatch")
        _verify_recovery_threshold(old,intent.payload,self._decode_sigs(row[5]))
        _verify_recovery_threshold(new,intent.payload,self._decode_sigs(row[6]))
        _verify_root_threshold(root,intent.payload,self._decode_sigs(row[7]))
        return root

    def historical(self,authority_id):
        q=self._con()
        try:return self._load_recovery_locked(q,authority_id)
        finally:q.close()

    def verify_durable(self):
        q=self._con()
        try:
            q.execute("BEGIN")
            rows=q.execute(
                "SELECT authority_id FROM provider_recovery_lifecycle_authorities ORDER BY version"
            ).fetchall()
            if not rows:
                raise LifecycleSubstitution("missing recovery lifecycle history")
            authorities=[self._load_recovery_locked(q,r[0]) for r in rows]
            if authorities[0].authority_id!=self.bootstrap.authority_id:
                raise LifecycleSubstitution("recovery lifecycle bootstrap changed")
            for old,new in zip(authorities,authorities[1:]):
                if new.version!=old.version+1 or new.generation!=old.generation+1:
                    raise LifecycleRollback("recovery lifecycle history gap")
                self.verify_transition_locked(q,old,new)
            current=self.current_locked(q)
            if current.authority_id!=authorities[-1].authority_id:
                raise LifecycleRollback("recovery lifecycle head rollback")
            if q.execute(
                "SELECT COUNT(*) FROM provider_recovery_lifecycle_transitions"
            ).fetchone()[0]!=len(authorities)-1:
                raise LifecycleSubstitution("orphan/duplicate lifecycle transition rows")
            q.commit()
            return True
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()


class UnsafeRecoveryOnlySwap:
    @staticmethod
    def allows(old_recovery_quorum_valid: bool):
        return bool(old_recovery_quorum_valid)
