from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from urllib.parse import urlparse


class CredentialError(RuntimeError):
    pass


class StaleCredentialError(CredentialError):
    pass


class ScopeError(CredentialError):
    pass


class ReconcileRequired(CredentialError):
    pass


def canonical_origin(url: str) -> tuple[str, str, int]:
    p = urlparse(url)
    if not p.scheme or not p.hostname:
        raise ScopeError("absolute URL required")
    scheme = p.scheme.lower()
    host = p.hostname.lower()
    port = p.port or (443 if scheme == "https" else 80 if scheme == "http" else -1)
    if port < 0:
        raise ScopeError("unsupported scheme without known default port")
    return scheme, host, port


def path_matches(request_path: str, scope_path: str) -> bool:
    request_path = request_path or "/"
    scope_path = scope_path or "/"
    if request_path == scope_path:
        return True
    if not request_path.startswith(scope_path):
        return False
    if scope_path.endswith("/"):
        return True
    return len(request_path) > len(scope_path) and request_path[len(scope_path)] == "/"


def request_fingerprint(*, payload_digest: str, purpose: str, effect_id: str, route_fingerprint: str) -> str:
    material = "|".join([payload_digest, purpose, effect_id, route_fingerprint]).encode()
    return sha256(material).hexdigest()


@dataclass(frozen=True)
class RequestBinding:
    url: str
    payload_digest: str
    purpose: str
    effect_id: str
    route_fingerprint: str
    request_generation: int

    @property
    def origin(self) -> tuple[str, str, int]:
        return canonical_origin(self.url)

    @property
    def fingerprint(self) -> str:
        return request_fingerprint(
            payload_digest=self.payload_digest,
            purpose=self.purpose,
            effect_id=self.effect_id,
            route_fingerprint=self.route_fingerprint,
        )


@dataclass(frozen=True)
class OriginCredential:
    credential_id: str
    secret: str
    scheme: str
    host: str
    port: int
    path_prefix: str = "/"
    generation: int = 1
    request_fingerprint: str | None = None

    def matches(self, req: RequestBinding) -> bool:
        p = urlparse(req.url)
        return (
            req.origin == (self.scheme.lower(), self.host.lower(), self.port)
            and path_matches(p.path or "/", self.path_prefix)
            and (self.request_fingerprint is None or self.request_fingerprint == req.fingerprint)
        )


@dataclass(frozen=True)
class CookieCredential:
    credential_id: str
    value: str
    host: str
    path_prefix: str = "/"
    secure_only: bool = True
    generation: int = 1

    def matches(self, req: RequestBinding) -> bool:
        scheme, host, _ = req.origin
        p = urlparse(req.url)
        return (
            host == self.host.lower()
            and (not self.secure_only or scheme == "https")
            and path_matches(p.path or "/", self.path_prefix)
        )


@dataclass(frozen=True)
class ProxyCredential:
    credential_id: str
    secret: str
    proxy_id: str
    proxy_generation: int
    credential_generation: int = 1


@dataclass(frozen=True)
class CredentialPermit:
    request_fingerprint: str
    origin: tuple[str, str, int]
    origin_credential_id: str | None
    origin_credential_generation: int | None
    cookie_ids: tuple[str, ...]
    cookie_generations: tuple[int, ...]
    proxy_id: str | None
    proxy_generation: int | None
    proxy_credential_id: str | None
    proxy_credential_generation: int | None
    effect_id: str
    request_generation: int


@dataclass
class EffectRecord:
    effect_id: str
    status: str = "NEW"  # NEW, UNKNOWN, CONFIRMED
    receipt: str | None = None
    request_fingerprint: str | None = None


@dataclass
class CredentialRouter:
    origin_credentials: dict[str, OriginCredential] = field(default_factory=dict)
    cookies: dict[str, CookieCredential] = field(default_factory=dict)
    proxy_credentials: dict[str, ProxyCredential] = field(default_factory=dict)
    effects: dict[str, EffectRecord] = field(default_factory=dict)

    def issue_permit(
        self,
        req: RequestBinding,
        *,
        origin_credential_id: str | None = None,
        cookie_ids: tuple[str, ...] = (),
        proxy_id: str | None = None,
        proxy_generation: int | None = None,
        proxy_credential_id: str | None = None,
    ) -> CredentialPermit:
        effect = self.effects.get(req.effect_id)
        if effect and effect.status == "UNKNOWN":
            raise ReconcileRequired("effect outcome unknown; reconcile before issuing credential/route permit")
        if proxy_id is not None:
            if proxy_generation is None or req.route_fingerprint != f"{proxy_id}:v{proxy_generation}":
                raise ScopeError("proxy route identity does not match request route fingerprint")
        elif proxy_credential_id is not None:
            raise ScopeError("proxy credential cannot be used without proxy route")
        if origin_credential_id and origin_credential_id not in self.origin_credentials:
            raise ScopeError("unknown origin credential")
        origin_cred = self.origin_credentials.get(origin_credential_id) if origin_credential_id else None
        if origin_cred and not origin_cred.matches(req):
            raise ScopeError("origin credential outside protection scope")
        selected_cookies = []
        for cid in cookie_ids:
            c = self.cookies[cid]
            if not c.matches(req):
                raise ScopeError(f"cookie outside scope: {cid}")
            selected_cookies.append(c)
        if proxy_credential_id and proxy_credential_id not in self.proxy_credentials:
            raise ScopeError("unknown proxy credential")
        proxy_cred = self.proxy_credentials.get(proxy_credential_id) if proxy_credential_id else None
        if proxy_cred:
            if proxy_id is None or proxy_generation is None:
                raise ScopeError("proxy credential requires explicit proxy route")
            if proxy_cred.proxy_id != proxy_id or proxy_cred.proxy_generation != proxy_generation:
                raise ScopeError("proxy credential bound to another proxy route/generation")
        return CredentialPermit(
            request_fingerprint=req.fingerprint,
            origin=req.origin,
            origin_credential_id=origin_cred.credential_id if origin_cred else None,
            origin_credential_generation=origin_cred.generation if origin_cred else None,
            cookie_ids=tuple(c.credential_id for c in selected_cookies),
            cookie_generations=tuple(c.generation for c in selected_cookies),
            proxy_id=proxy_id,
            proxy_generation=proxy_generation,
            proxy_credential_id=proxy_cred.credential_id if proxy_cred else None,
            proxy_credential_generation=proxy_cred.credential_generation if proxy_cred else None,
            effect_id=req.effect_id,
            request_generation=req.request_generation,
        )

    def redirect(self, old: RequestBinding, new_url: str) -> RequestBinding:
        return RequestBinding(
            url=new_url,
            payload_digest=old.payload_digest,
            purpose=old.purpose,
            effect_id=old.effect_id,
            route_fingerprint=old.route_fingerprint,
            request_generation=old.request_generation,
        )

    def materialize_headers(self, req: RequestBinding, permit: CredentialPermit) -> tuple[dict[str, str], dict[str, str]]:
        if permit.effect_id != req.effect_id or permit.request_generation != req.request_generation:
            raise StaleCredentialError("permit not bound to current effect/request generation")
        if permit.request_fingerprint != req.fingerprint or permit.origin != req.origin:
            raise ScopeError("permit not valid for request authority/identity")
        origin_headers: dict[str, str] = {}
        proxy_headers: dict[str, str] = {}
        if permit.origin_credential_id:
            c = self.origin_credentials[permit.origin_credential_id]
            if c.generation != permit.origin_credential_generation:
                raise StaleCredentialError("origin credential rotated")
            if not c.matches(req):
                raise ScopeError("origin credential outside current request scope")
            origin_headers["Authorization"] = c.secret
        cookie_values = []
        for cid, expected_gen in zip(permit.cookie_ids, permit.cookie_generations, strict=True):
            c = self.cookies[cid]
            if c.generation != expected_gen:
                raise StaleCredentialError("cookie rotated")
            if not c.matches(req):
                raise ScopeError("cookie outside current request scope")
            cookie_values.append(c.value)
        if cookie_values:
            origin_headers["Cookie"] = "; ".join(cookie_values)
        if permit.proxy_credential_id:
            pc = self.proxy_credentials[permit.proxy_credential_id]
            if (
                pc.credential_generation != permit.proxy_credential_generation
                or pc.proxy_id != permit.proxy_id
                or pc.proxy_generation != permit.proxy_generation
            ):
                raise StaleCredentialError("proxy credential/route rotated")
            proxy_headers["Proxy-Authorization"] = pc.secret
        return origin_headers, proxy_headers

    def begin_or_resume(self, req: RequestBinding) -> EffectRecord:
        rec = self.effects.setdefault(req.effect_id, EffectRecord(effect_id=req.effect_id))
        if rec.status == "UNKNOWN":
            raise ReconcileRequired("effect outcome unknown; reconcile before credential or route changes")
        return rec

    def mark_unknown(self, req: RequestBinding) -> None:
        rec = self.effects.setdefault(req.effect_id, EffectRecord(effect_id=req.effect_id))
        rec.status = "UNKNOWN"
        rec.request_fingerprint = req.fingerprint

    def reconcile(self, effect_id: str, receipt: str | None) -> EffectRecord:
        rec = self.effects.setdefault(effect_id, EffectRecord(effect_id=effect_id))
        if receipt:
            rec.status = "CONFIRMED"
            rec.receipt = receipt
        else:
            rec.status = "NEW"
        return rec


class UnsafeForwarder:
    """Deliberately unsafe: blindly copies all caller headers across redirect/fallback."""

    @staticmethod
    def redirect(headers: dict[str, str], new_url: str) -> tuple[str, dict[str, str]]:
        return new_url, dict(headers)
