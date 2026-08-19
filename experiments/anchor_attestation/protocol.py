from __future__ import annotations
import hashlib, hmac, json, secrets
from dataclasses import dataclass

class AttestationError(RuntimeError): pass
class ForgedObservation(AttestationError): pass
class ReplayObservation(AttestationError): pass
class WrongProvider(AttestationError): pass
class StaleGeneration(AttestationError): pass
class ChallengeMismatch(AttestationError): pass
class ProviderUnavailable(AttestationError): pass
class UnknownOutcome(AttestationError): pass
class AnchorMismatch(AttestationError): pass

@dataclass(frozen=True)
class ProviderIdentity:
    provider_id: str
    generation: int

@dataclass(frozen=True)
class SignedObservation:
    provider_id: str
    generation: int
    position: int
    challenge: str
    kind: str
    request_id: str
    mac: str

def _canonical(provider_id,generation,position,challenge,kind,request_id):
    return json.dumps({
        "challenge":str(challenge),"generation":int(generation),"kind":str(kind),
        "position":int(position),"provider_id":str(provider_id),"request_id":str(request_id)
    }, sort_keys=True, separators=(",",":")).encode()

def _sign(key, **kw):
    return hmac.new(key, _canonical(**kw), hashlib.sha256).hexdigest()

def receipt_ref(obs: SignedObservation) -> str:
    raw=_canonical(obs.provider_id,obs.generation,obs.position,obs.challenge,obs.kind,obs.request_id)+obs.mac.encode()
    return hashlib.sha256(raw).hexdigest()

class SignedAnchorProvider:
    def __init__(self, provider_id="anchor-A", generation=1, key=b"k1", value=0):
        self.provider_id=provider_id; self.generation=int(generation); self.key=key
        self.value=int(value); self.available=True; self.increment_calls=0
        self._request_results={}
    def rotate(self, provider_id, generation, key):
        self.provider_id=provider_id; self.generation=int(generation); self.key=key
        self._request_results={}
    def _obs(self, *, challenge, kind, request_id, position=None):
        p=self.value if position is None else int(position)
        mac=_sign(self.key,provider_id=self.provider_id,generation=self.generation,
                  position=p,challenge=challenge,kind=kind,request_id=request_id)
        return SignedObservation(self.provider_id,self.generation,p,challenge,kind,request_id,mac)
    def read(self, *, challenge, request_id):
        if not self.available: raise ProviderUnavailable("attestation path unavailable")
        return self._obs(challenge=challenge,kind="READ",request_id=request_id)
    def increment(self, *, expected, challenge, request_id, timeout_after_commit=False):
        if not self.available: raise ProviderUnavailable("attestation path unavailable")
        self.increment_calls+=1
        if request_id in self._request_results:
            return self._request_results[request_id]
        if self.value != int(expected): raise AnchorMismatch(f"expected={expected} current={self.value}")
        self.value += 1
        obs=self._obs(challenge=challenge,kind="INCREMENT",request_id=request_id)
        self._request_results[request_id]=obs
        if timeout_after_commit: raise UnknownOutcome("increment committed; receipt lost")
        return obs
    def reconcile_increment(self, *, challenge, request_id):
        if not self.available: raise ProviderUnavailable("attestation path unavailable")
        obs=self._request_results.get(request_id)
        if obs is None: return None
        return self._obs(challenge=challenge,kind="RECONCILE",request_id=request_id,position=obs.position)

class AttestationVerifier:
    def __init__(self, keyring, expected: ProviderIdentity):
        self.keyring=dict(keyring); self.expected=expected
        self._seen=set()
    def verify(self, obs: SignedObservation, *, expected_challenge, allowed_kinds, consume=True):
        if obs.provider_id != self.expected.provider_id: raise WrongProvider("wrong provider identity")
        if obs.generation != self.expected.generation: raise StaleGeneration("stale provider generation")
        if obs.challenge != expected_challenge: raise ChallengeMismatch("challenge mismatch")
        if obs.kind not in set(allowed_kinds): raise AttestationError("unexpected observation kind")
        key=self.keyring.get((obs.provider_id,obs.generation))
        if key is None: raise ForgedObservation("verification key unavailable")
        expected=_sign(key,provider_id=obs.provider_id,generation=obs.generation,position=obs.position,
                       challenge=obs.challenge,kind=obs.kind,request_id=obs.request_id)
        if not hmac.compare_digest(expected,obs.mac): raise ForgedObservation("observation authentication failed")
        token=(obs.provider_id,obs.generation,obs.challenge,obs.kind,obs.request_id,obs.position,obs.mac)
        if token in self._seen: raise ReplayObservation("observation replayed")
        if consume: self._seen.add(token)
        return obs

class AttestedCatchup:
    def __init__(self, provider, verifier):
        self.provider=provider; self.verifier=verifier
    @staticmethod
    def challenge(): return secrets.token_hex(16)
    def authenticated_read(self, *, challenge=None, request_id="read"):
        c=challenge or self.challenge()
        obs=self.provider.read(challenge=c,request_id=request_id)
        return self.verifier.verify(obs,expected_challenge=c,allowed_kinds={"READ"})
    def catch_up_one(self, *, db_sequence, request_id, timeout_after_commit=False):
        c1=self.challenge()
        current=self.verifier.verify(self.provider.read(challenge=c1,request_id=f"{request_id}:read"),
                                     expected_challenge=c1,allowed_kinds={"READ"})
        if current.position > db_sequence: raise AnchorMismatch("anchor ahead of DB")
        if current.position == db_sequence: return receipt_ref(current)
        if current.position != db_sequence-1: raise AnchorMismatch("unsafe gap")
        c2=self.challenge()
        try:
            obs=self.provider.increment(expected=current.position,challenge=c2,request_id=request_id,
                                        timeout_after_commit=timeout_after_commit)
            verified=self.verifier.verify(obs,expected_challenge=c2,allowed_kinds={"INCREMENT"})
        except UnknownOutcome:
            c3=self.challenge()
            obs=self.provider.reconcile_increment(challenge=c3,request_id=request_id)
            if obs is None: raise
            verified=self.verifier.verify(obs,expected_challenge=c3,allowed_kinds={"RECONCILE"})
        if verified.position != db_sequence: raise AnchorMismatch("authenticated position does not match DB")
        return receipt_ref(verified)

class UnsafeUnauthenticatedRead:
    def allow(self, db_sequence, claimed_position):
        return int(claimed_position)==int(db_sequence)
