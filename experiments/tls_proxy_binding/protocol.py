from __future__ import annotations

from dataclasses import dataclass


class BindingError(RuntimeError):
    pass


class UnknownOutcome(RuntimeError):
    pass


@dataclass(frozen=True)
class RequestIdentity:
    payload_digest: str
    origin_host: str
    origin_port: int
    purpose: str
    effect_id: str
    authorization_generation: int

    @property
    def origin_authority(self) -> str:
        return f"{self.origin_host}:{self.origin_port}"


@dataclass(frozen=True)
class EndpointEvidence:
    origin_host: str
    resolved_ip: str
    endpoint_generation: int


@dataclass(frozen=True)
class RoutePermit:
    request: RequestIdentity
    endpoint: EndpointEvidence
    route_kind: str  # direct|proxy
    proxy_id: str | None = None
    proxy_endpoint: str | None = None
    proxy_policy_generation: int = 0


@dataclass(frozen=True)
class TLSObservation:
    sni: str
    certificate_dns_ids: tuple[str, ...]
    connected_ip: str


@dataclass(frozen=True)
class ProxyObservation:
    proxy_id: str
    proxy_endpoint: str
    proxy_policy_generation: int
    connect_authority: str
    target_resolved_ip: str


@dataclass(frozen=True)
class EffectReceipt:
    effect_id: str
    route_fingerprint: str


def canonical_host(host: str) -> str:
    value = host.strip().rstrip('.').lower()
    if not value or '/' in value or ':' in value:
        raise BindingError(f"invalid DNS host {host!r}")
    return value


def dns_id_matches(reference_host: str, dns_id: str) -> bool:
    ref = canonical_host(reference_host)
    presented = canonical_host(dns_id)
    if presented.startswith('*.'):
        suffix = presented[1:]
        return ref.endswith(suffix) and ref.count('.') == presented.count('.')
    return ref == presented


def require_tls_identity(permit: RoutePermit, tls: TLSObservation) -> None:
    reference = canonical_host(permit.request.origin_host)
    if canonical_host(permit.endpoint.origin_host) != reference:
        raise BindingError("validated endpoint evidence belongs to a different origin")
    if canonical_host(tls.sni) != reference:
        raise BindingError("TLS SNI drifted from authorized origin")
    if tls.connected_ip != permit.endpoint.resolved_ip:
        raise BindingError("TLS socket endpoint differs from validated endpoint")
    if not any(dns_id_matches(reference, dns_id) for dns_id in tls.certificate_dns_ids):
        raise BindingError("certificate does not authenticate authorized origin")


def require_proxy_path(permit: RoutePermit, proxy: ProxyObservation) -> None:
    if permit.route_kind != 'proxy':
        raise BindingError("proxy observation supplied for direct permit")
    if proxy.proxy_id != permit.proxy_id or proxy.proxy_endpoint != permit.proxy_endpoint:
        raise BindingError("proxy identity/path drift")
    if proxy.proxy_policy_generation != permit.proxy_policy_generation:
        raise BindingError("proxy policy generation changed")
    if proxy.connect_authority.lower() != permit.request.origin_authority.lower():
        raise BindingError("CONNECT authority differs from authorized origin")
    if proxy.target_resolved_ip != permit.endpoint.resolved_ip:
        raise BindingError("proxy-side target resolution differs from validated endpoint")


def route_fingerprint(permit: RoutePermit) -> str:
    parts = [
        permit.request.effect_id,
        permit.request.payload_digest,
        permit.request.purpose,
        str(permit.request.authorization_generation),
        permit.request.origin_authority.lower(),
        permit.endpoint.resolved_ip,
        str(permit.endpoint.endpoint_generation),
        permit.route_kind,
    ]
    if permit.route_kind == 'proxy':
        parts.extend([
            permit.proxy_id or '',
            permit.proxy_endpoint or '',
            str(permit.proxy_policy_generation),
        ])
    return '|'.join(parts)


class EffectLedger:
    def __init__(self):
        self._receipts: dict[str, EffectReceipt] = {}
        self.apply_count = 0

    def lookup(self, effect_id: str) -> EffectReceipt | None:
        return self._receipts.get(effect_id)

    def apply(self, effect_id: str, route_fp: str, *, timeout_after_commit: bool = False) -> EffectReceipt:
        existing = self._receipts.get(effect_id)
        if existing is not None:
            if existing.route_fingerprint != route_fp:
                raise BindingError("effect identity was already committed on a different route")
            return existing
        receipt = EffectReceipt(effect_id=effect_id, route_fingerprint=route_fp)
        self._receipts[effect_id] = receipt
        self.apply_count += 1
        if timeout_after_commit:
            raise UnknownOutcome("transport failed after commit")
        return receipt


class SafeTransport:
    def __init__(self, ledger: EffectLedger):
        self.ledger = ledger

    def send_direct(self, permit: RoutePermit, tls: TLSObservation, *, timeout_after_commit: bool = False) -> EffectReceipt:
        if permit.route_kind != 'direct':
            raise BindingError("route kind mismatch")
        require_tls_identity(permit, tls)
        return self.ledger.apply(permit.request.effect_id, route_fingerprint(permit), timeout_after_commit=timeout_after_commit)

    def send_via_proxy(
        self,
        permit: RoutePermit,
        proxy: ProxyObservation,
        tls: TLSObservation,
        *,
        timeout_after_commit: bool = False,
    ) -> EffectReceipt:
        require_proxy_path(permit, proxy)
        require_tls_identity(permit, tls)
        return self.ledger.apply(permit.request.effect_id, route_fingerprint(permit), timeout_after_commit=timeout_after_commit)

    def reconcile(self, permit: RoutePermit) -> EffectReceipt | None:
        receipt = self.ledger.lookup(permit.request.effect_id)
        if receipt is None:
            return None
        if receipt.route_fingerprint != route_fingerprint(permit):
            raise BindingError("UNKNOWN outcome cannot be reconciled after route drift")
        return receipt


class UnsafeIpOnlyTransport:
    """Seed: accepts the right socket IP while ignoring SNI/certificate identity."""

    def send(self, permit: RoutePermit, tls: TLSObservation) -> bool:
        return tls.connected_ip == permit.endpoint.resolved_ip


class UnsafeCertOnlyProxyTransport:
    """Seed: accepts matching certificate while proxy CONNECT/endpoint can drift."""

    def send(self, permit: RoutePermit, proxy: ProxyObservation, tls: TLSObservation) -> bool:
        reference = permit.request.origin_host
        return any(dns_id_matches(reference, dns_id) for dns_id in tls.certificate_dns_ids)
