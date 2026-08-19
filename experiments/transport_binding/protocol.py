from __future__ import annotations
import ipaddress
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlsplit, urlunsplit

class TransportPolicyError(RuntimeError): pass
class UnknownOutcome(TransportPolicyError): pass

def canonical_https_url(url: str) -> str:
    p=urlsplit(url)
    if p.scheme.lower()!='https' or not p.hostname:
        raise TransportPolicyError('absolute https URL required')
    host=p.hostname.lower().rstrip('.')
    try:
        ip=ipaddress.ip_address(host)
        host=f'[{ip.compressed}]' if isinstance(ip, ipaddress.IPv6Address) else ip.compressed
    except ValueError:
        pass
    port=p.port
    netloc=host if port in (None,443) else f'{host}:{port}'
    return urlunsplit(('https',netloc,p.path or '/',p.query,''))

def normalize_ip(value: str):
    text=value.strip()
    if '%' in text:
        text=text.split('%',1)[0]
    ip=ipaddress.ip_address(text)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        return ip.ipv4_mapped
    return ip

def is_allowed_public_ip(value: str) -> bool:
    ip=normalize_ip(value)
    return bool(ip.is_global and not ip.is_multicast and not ip.is_unspecified)

@dataclass(frozen=True)
class RequestIdentity:
    permit_id: str
    effect_key: str
    payload_digest: str
    destination: str
    purpose: str
    policy_generation: int

@dataclass
class Resolution:
    host: str
    addresses: List[str]
    aliases: List[str]=field(default_factory=list)

class FakeResolver:
    def __init__(self, sequences: Dict[str,List[Resolution]]):
        self.sequences=sequences
        self.calls: Dict[str,int]={}
    def resolve(self, host: str) -> Resolution:
        host=host.lower().rstrip('.')
        seq=self.sequences.get(host)
        if not seq:
            raise TransportPolicyError(f'no resolution for {host}')
        idx=self.calls.get(host,0)
        self.calls[host]=idx+1
        return seq[min(idx,len(seq)-1)]

class FakeRedirector:
    def __init__(self, redirects: Dict[str,str]):
        self.redirects={canonical_https_url(k):v for k,v in redirects.items()}
    def target(self, url: str) -> Optional[str]:
        return self.redirects.get(canonical_https_url(url))

class FakeConnector:
    def __init__(self):
        self.connections=[]
        self.effects={}
    def connect_and_apply(self, *, endpoint: str, url: str, identity: RequestIdentity,
                          timeout_after_commit: bool=False):
        if identity.effect_key in self.effects:
            return self.effects[identity.effect_key]
        receipt={'effect_key':identity.effect_key,'endpoint':str(normalize_ip(endpoint)),
                 'url':canonical_https_url(url),'permit_id':identity.permit_id,
                 'payload_digest':identity.payload_digest,'purpose':identity.purpose,
                 'policy_generation':identity.policy_generation}
        self.connections.append(receipt)
        self.effects[identity.effect_key]=receipt
        if timeout_after_commit:
            raise UnknownOutcome('connection committed but acknowledgement was lost')
        return receipt
    def lookup(self, effect_key: str):
        return self.effects.get(effect_key)

@dataclass(frozen=True)
class EndpointPolicy:
    allowed_hosts: frozenset[str]
    max_redirects: int=4
    def allows_url(self,url:str)->bool:
        p=urlsplit(canonical_https_url(url))
        return p.hostname.lower().rstrip('.') in self.allowed_hosts

class SafeTransportExecutor:
    def __init__(self, policy: EndpointPolicy, resolver: FakeResolver,
                 redirector: FakeRedirector, connector: FakeConnector):
        self.policy=policy; self.resolver=resolver; self.redirector=redirector; self.connector=connector

    def _validate_resolution(self, host: str) -> Resolution:
        res=self.resolver.resolve(host)
        # DNS aliases are resolution metadata, not independent authority.
        # The original authorized hostname remains authoritative; every returned
        # connection address must independently pass endpoint classification.
        if not res.addresses:
            raise TransportPolicyError('empty resolution')
        normalized=[]
        for raw in res.addresses:
            ip=normalize_ip(raw)
            if not is_allowed_public_ip(str(ip)):
                raise TransportPolicyError(f'forbidden endpoint: {ip}')
            normalized.append(str(ip))
        return Resolution(host=host, addresses=normalized, aliases=res.aliases)

    def execute(self, *, prepared_destination: str, current_destination: str,
                identity: RequestIdentity, timeout_after_commit: bool=False):
        prepared=canonical_https_url(prepared_destination)
        current=canonical_https_url(current_destination)
        if current!=prepared or canonical_https_url(identity.destination)!=prepared:
            raise TransportPolicyError('LAB-022 request identity mismatch')
        if not self.policy.allows_url(current):
            raise TransportPolicyError('hostname not allowed')
        existing=self.connector.lookup(identity.effect_key)
        if existing:
            return existing
        url=current
        redirects=0
        while True:
            if not self.policy.allows_url(url):
                raise TransportPolicyError('redirect destination not allowed')
            host=urlsplit(url).hostname.lower().rstrip('.')
            self._validate_resolution(host)
            nxt=self.redirector.target(url)
            if nxt is None:
                final_res=self._validate_resolution(host)
                endpoint=final_res.addresses[0]
                try:
                    return self.connector.connect_and_apply(endpoint=endpoint,url=url,identity=identity,timeout_after_commit=timeout_after_commit)
                except UnknownOutcome:
                    raise
            redirects+=1
            if redirects>self.policy.max_redirects:
                raise TransportPolicyError('redirect limit exceeded')
            candidate=canonical_https_url(urljoin(url,nxt))
            # LAB-022 binds the authorized destination host. Transport-layer
            # redirect handling must not silently broaden that authority.
            if urlsplit(candidate).hostname.lower().rstrip('.') != urlsplit(prepared).hostname.lower().rstrip('.'):
                raise TransportPolicyError('cross-host redirect requires new authorization')
            url=candidate

class UnsafeResolveOnceExecutor:
    def __init__(self, resolver: FakeResolver, connector: FakeConnector):
        self.resolver=resolver; self.connector=connector
    def execute(self, *, url: str, identity: RequestIdentity):
        host=urlsplit(canonical_https_url(url)).hostname.lower()
        checked=self.resolver.resolve(host)
        if not all(is_allowed_public_ip(ip) for ip in checked.addresses):
            raise TransportPolicyError('initial resolution rejected')
        actual=self.resolver.resolve(host)
        return self.connector.connect_and_apply(endpoint=actual.addresses[0],url=url,identity=identity)
