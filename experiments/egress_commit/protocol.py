from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from urllib.parse import urlsplit, urlunsplit

PERMIT_VERSION = 1

class PolicyError(RuntimeError): pass
class PermitError(PolicyError): pass
class ReplayError(PermitError): pass
class UnknownOutcome(PermitError): pass


def canonical_destination(url: str) -> str:
    p = urlsplit(url)
    if p.scheme.lower() != 'https' or not p.hostname:
        raise PolicyError('destination must be absolute https URL')
    host = p.hostname.lower()
    port = p.port
    netloc = host if port in (None, 443) else f'{host}:{port}'
    path = p.path or '/'
    return urlunsplit(('https', netloc, path, p.query, ''))


def payload_digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

@dataclass(frozen=True)
class TrustedAuthorization:
    authorization_id: str
    issuer: str
    payload_digest: str
    destination: str
    purpose: str
    authorization_generation: int
    signature: str

    def unsigned(self) -> dict:
        return {
            'authorization_id': self.authorization_id,
            'issuer': self.issuer,
            'payload_digest': self.payload_digest,
            'destination': self.destination,
            'purpose': self.purpose,
            'authorization_generation': self.authorization_generation,
        }

@dataclass(frozen=True)
class EgressPermit:
    version: int
    permit_id: str
    issuer: str
    payload_digest: str
    destination: str
    purpose: str
    policy_generation: int
    authorization_generation: int
    authorization_id: str
    nonce: str
    expires_at: int
    effect_key: str
    signature: str

    def unsigned(self) -> dict:
        d = asdict(self)
        d.pop('signature')
        return d

class PermitAuthority:
    def __init__(self, secret: bytes, issuer='trusted-control'):
        self.secret = secret
        self.issuer = issuer

    def _sign(self, values: dict) -> str:
        raw = json.dumps(values, sort_keys=True, separators=(',', ':')).encode()
        return hmac.new(self.secret, raw, hashlib.sha256).hexdigest()

    def issue_authorization(self, *, payload: bytes, destination: str, purpose: str, authorization_generation: int) -> TrustedAuthorization:
        unsigned = {
            'authorization_id': str(uuid.uuid4()),
            'issuer': self.issuer,
            'payload_digest': payload_digest(payload),
            'destination': canonical_destination(destination),
            'purpose': purpose,
            'authorization_generation': authorization_generation,
        }
        return TrustedAuthorization(**unsigned, signature=self._sign(unsigned))

    def verify_authorization(self, authorization: TrustedAuthorization) -> bool:
        return authorization.issuer == self.issuer and hmac.compare_digest(authorization.signature, self._sign(authorization.unsigned()))

    def prepare(self, *, payload: bytes, destination: str, purpose: str,
                policy_generation: int, authorization: TrustedAuthorization,
                ttl_seconds: int = 60, now: Optional[int] = None) -> EgressPermit:
        now = int(time.time()) if now is None else now
        dest = canonical_destination(destination)
        pd = payload_digest(payload)
        if not self.verify_authorization(authorization):
            raise PolicyError('authorization is not authentic trusted control-plane authority')
        if authorization.payload_digest != pd:
            raise PolicyError('authorization payload mismatch')
        if canonical_destination(authorization.destination) != dest:
            raise PolicyError('authorization destination mismatch')
        if authorization.purpose != purpose:
            raise PolicyError('authorization purpose mismatch')
        unsigned = {
            'version': PERMIT_VERSION,
            'permit_id': str(uuid.uuid4()),
            'issuer': self.issuer,
            'payload_digest': pd,
            'destination': dest,
            'purpose': purpose,
            'policy_generation': policy_generation,
            'authorization_generation': authorization.authorization_generation,
            'authorization_id': authorization.authorization_id,
            'nonce': str(uuid.uuid4()),
            'expires_at': now + ttl_seconds,
            'effect_key': f'egress:{pd}:{hashlib.sha256((dest+"|"+purpose).encode()).hexdigest()[:16]}',
        }
        return EgressPermit(**unsigned, signature=self._sign(unsigned))

    def verify_signature(self, permit: EgressPermit) -> bool:
        return hmac.compare_digest(permit.signature, self._sign(permit.unsigned()))

class EffectLedger:
    def __init__(self):
        self.effects: Dict[str, dict] = {}
        self.apply_count = 0

    def lookup(self, effect_key: str) -> Optional[dict]:
        return self.effects.get(effect_key)

    def apply(self, *, effect_key: str, payload: bytes, destination: str, purpose: str,
              timeout_after_commit=False) -> dict:
        if effect_key in self.effects:
            return self.effects[effect_key]
        receipt = {
            'receipt_id': f'receipt:{effect_key}',
            'payload_digest': payload_digest(payload),
            'destination': canonical_destination(destination),
            'purpose': purpose,
        }
        self.effects[effect_key] = receipt
        self.apply_count += 1
        if timeout_after_commit:
            raise UnknownOutcome('transport timeout after commit')
        return receipt

class CommitExecutor:
    def __init__(self, authority: PermitAuthority, ledger: EffectLedger):
        self.authority = authority
        self.ledger = ledger
        self.consumed_permits: Dict[str, dict] = {}

    def commit(self, permit: EgressPermit, *, payload: bytes, destination: str, purpose: str,
               policy_generation: int, authorization: TrustedAuthorization,
               now: Optional[int] = None, timeout_after_commit=False) -> dict:
        now = int(time.time()) if now is None else now
        dest = canonical_destination(destination)
        pd = payload_digest(payload)
        if permit.version != PERMIT_VERSION:
            raise PermitError('unsupported permit version')
        if permit.issuer != self.authority.issuer or not self.authority.verify_signature(permit):
            raise PermitError('untrusted or invalid permit issuer/signature')
        if now > permit.expires_at:
            raise PermitError('expired permit')
        expected = {
            'payload_digest': pd,
            'destination': dest,
            'purpose': purpose,
            'policy_generation': policy_generation,
            'authorization_generation': authorization.authorization_generation,
            'authorization_id': authorization.authorization_id,
        }
        for key, actual in expected.items():
            if getattr(permit, key) != actual:
                raise PermitError(f'commit-time binding mismatch: {key}')
        if not self.authority.verify_authorization(authorization):
            raise PermitError('authorization is not authentic trusted-control authority')
        if authorization.payload_digest != pd or canonical_destination(authorization.destination) != dest or authorization.purpose != purpose:
            raise PermitError('authorization no longer matches request')
        if permit.permit_id in self.consumed_permits:
            previous = self.consumed_permits[permit.permit_id]
            if previous['effect_key'] == permit.effect_key:
                return previous['receipt']
            raise ReplayError('permit replay changed effect identity')
        existing = self.ledger.lookup(permit.effect_key)
        if existing:
            self.consumed_permits[permit.permit_id] = {'effect_key': permit.effect_key, 'receipt': existing}
            return existing
        try:
            receipt = self.ledger.apply(effect_key=permit.effect_key, payload=payload,
                                        destination=dest, purpose=purpose,
                                        timeout_after_commit=timeout_after_commit)
        except UnknownOutcome:
            existing = self.ledger.lookup(permit.effect_key)
            if existing:
                self.consumed_permits[permit.permit_id] = {'effect_key': permit.effect_key, 'receipt': existing}
            raise
        self.consumed_permits[permit.permit_id] = {'effect_key': permit.effect_key, 'receipt': receipt}
        return receipt

class UnsafeCheckThenUse:
    def __init__(self, ledger: EffectLedger): self.ledger = ledger
    def check(self, *, payload: bytes, destination: str) -> bool:
        return canonical_destination(destination).endswith('trusted.example/upload') and bool(payload)
    def use(self, *, payload: bytes, destination: str, purpose: str) -> dict:
        return self.ledger.apply(effect_key=str(uuid.uuid4()), payload=payload,
                                 destination=destination, purpose=purpose)
