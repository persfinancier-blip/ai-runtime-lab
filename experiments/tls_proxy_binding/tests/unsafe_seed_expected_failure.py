import unittest

from experiments.tls_proxy_binding.protocol import (
    EndpointEvidence,
    ProxyObservation,
    RequestIdentity,
    RoutePermit,
    TLSObservation,
    UnsafeCertOnlyProxyTransport,
    UnsafeIpOnlyTransport,
)


class UnsafeSeeds(unittest.TestCase):
    def test_ip_only_wrong_tls_identity_should_block_but_does_not(self):
        req = RequestIdentity('payload', 'trusted.example', 443, 'report', 'effect', 1)
        permit = RoutePermit(req, EndpointEvidence('trusted.example', '93.184.216.34', 1), 'direct')
        tls = TLSObservation('attacker.example', ('attacker.example',), '93.184.216.34')
        self.assertFalse(UnsafeIpOnlyTransport().send(permit, tls), 'IP-only transport accepted wrong TLS identity')

    def test_cert_only_proxy_drift_should_block_but_does_not(self):
        req = RequestIdentity('payload', 'trusted.example', 443, 'report', 'effect', 1)
        permit = RoutePermit(req, EndpointEvidence('trusted.example', '93.184.216.34', 1), 'proxy', 'proxy-a', '198.51.100.10:8080', 1)
        proxy = ProxyObservation('proxy-a', '198.51.100.10:8080', 1, 'attacker.example:443', '127.0.0.1')
        tls = TLSObservation('trusted.example', ('trusted.example',), '93.184.216.34')
        self.assertFalse(UnsafeCertOnlyProxyTransport().send(permit, proxy, tls), 'certificate-only transport accepted proxy drift')


if __name__ == '__main__':
    unittest.main()
