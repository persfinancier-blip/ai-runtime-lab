import unittest

from experiments.tls_proxy_binding.protocol import (
    BindingError,
    EffectLedger,
    EndpointEvidence,
    ProxyObservation,
    RequestIdentity,
    RoutePermit,
    SafeTransport,
    TLSObservation,
    UnknownOutcome,
    dns_id_matches,
)


class TLSProxyBindingTests(unittest.TestCase):
    def setUp(self):
        req = RequestIdentity('payload-v1', 'trusted.example', 443, 'report', 'effect-1', 7)
        endpoint = EndpointEvidence('trusted.example', '93.184.216.34', 3)
        self.direct = RoutePermit(req, endpoint, 'direct')
        self.proxy = RoutePermit(req, endpoint, 'proxy', 'proxy-a', '198.51.100.10:8080', 11)
        self.tls = TLSObservation('trusted.example', ('trusted.example',), '93.184.216.34')
        self.proxy_obs = ProxyObservation('proxy-a', '198.51.100.10:8080', 11, 'trusted.example:443', '93.184.216.34')

    def test_pinned_ip_and_valid_origin_identity_allowed(self):
        ledger = EffectLedger()
        receipt = SafeTransport(ledger).send_direct(self.direct, self.tls)
        self.assertEqual(receipt.effect_id, 'effect-1')
        self.assertEqual(ledger.apply_count, 1)

    def test_correct_ip_wrong_sni_blocked(self):
        bad = TLSObservation('attacker.example', ('trusted.example',), '93.184.216.34')
        with self.assertRaises(BindingError):
            SafeTransport(EffectLedger()).send_direct(self.direct, bad)

    def test_correct_ip_wrong_certificate_blocked(self):
        bad = TLSObservation('trusted.example', ('attacker.example',), '93.184.216.34')
        with self.assertRaises(BindingError):
            SafeTransport(EffectLedger()).send_direct(self.direct, bad)

    def test_certificate_match_but_wrong_socket_endpoint_blocked(self):
        bad = TLSObservation('trusted.example', ('trusted.example',), '10.0.0.8')
        with self.assertRaises(BindingError):
            SafeTransport(EffectLedger()).send_direct(self.direct, bad)

    def test_proxy_connect_target_must_match_authorized_origin(self):
        bad = ProxyObservation('proxy-a', '198.51.100.10:8080', 11, 'attacker.example:443', '93.184.216.34')
        with self.assertRaises(BindingError):
            SafeTransport(EffectLedger()).send_via_proxy(self.proxy, bad, self.tls)

    def test_proxy_side_reresolution_must_match_validated_endpoint(self):
        bad = ProxyObservation('proxy-a', '198.51.100.10:8080', 11, 'trusted.example:443', '127.0.0.1')
        with self.assertRaises(BindingError):
            SafeTransport(EffectLedger()).send_via_proxy(self.proxy, bad, self.tls)

    def test_proxy_identity_and_generation_are_bound(self):
        for bad in (
            ProxyObservation('proxy-b', '198.51.100.10:8080', 11, 'trusted.example:443', '93.184.216.34'),
            ProxyObservation('proxy-a', '198.51.100.11:8080', 11, 'trusted.example:443', '93.184.216.34'),
            ProxyObservation('proxy-a', '198.51.100.10:8080', 12, 'trusted.example:443', '93.184.216.34'),
        ):
            with self.assertRaises(BindingError):
                SafeTransport(EffectLedger()).send_via_proxy(self.proxy, bad, self.tls)

    def test_direct_to_proxy_fallback_cannot_reuse_same_effect_without_reauthorization(self):
        ledger = EffectLedger()
        transport = SafeTransport(ledger)
        transport.send_direct(self.direct, self.tls)
        with self.assertRaises(BindingError):
            transport.send_via_proxy(self.proxy, self.proxy_obs, self.tls)
        self.assertEqual(ledger.apply_count, 1)

    def test_unknown_reconciles_same_route_before_retry(self):
        ledger = EffectLedger()
        transport = SafeTransport(ledger)
        with self.assertRaises(UnknownOutcome):
            transport.send_via_proxy(self.proxy, self.proxy_obs, self.tls, timeout_after_commit=True)
        receipt = transport.reconcile(self.proxy)
        self.assertIsNotNone(receipt)
        self.assertEqual(ledger.apply_count, 1)

    def test_unknown_cannot_reconcile_after_route_generation_change(self):
        ledger = EffectLedger()
        transport = SafeTransport(ledger)
        with self.assertRaises(UnknownOutcome):
            transport.send_via_proxy(self.proxy, self.proxy_obs, self.tls, timeout_after_commit=True)
        changed = RoutePermit(self.proxy.request, self.proxy.endpoint, 'proxy', 'proxy-a', '198.51.100.10:8080', 12)
        with self.assertRaises(BindingError):
            transport.reconcile(changed)

    def test_payload_purpose_and_effect_identity_remain_part_of_request_identity(self):
        changed_req = RequestIdentity('payload-v2', 'trusted.example', 443, 'other-purpose', 'effect-2', 7)
        changed = RoutePermit(changed_req, self.direct.endpoint, 'direct')
        ledger = EffectLedger()
        transport = SafeTransport(ledger)
        r1 = transport.send_direct(self.direct, self.tls)
        r2 = transport.send_direct(changed, self.tls)
        self.assertNotEqual(r1.effect_id, r2.effect_id)
        self.assertEqual(ledger.apply_count, 2)

    def test_same_effect_id_cannot_be_reused_for_changed_payload_or_purpose(self):
        ledger = EffectLedger()
        transport = SafeTransport(ledger)
        transport.send_direct(self.direct, self.tls)
        changed_req = RequestIdentity('payload-v2', 'trusted.example', 443, 'other-purpose', 'effect-1', 7)
        changed = RoutePermit(changed_req, self.direct.endpoint, 'direct')
        with self.assertRaises(BindingError):
            transport.send_direct(changed, self.tls)
        self.assertEqual(ledger.apply_count, 1)

    def test_endpoint_evidence_must_belong_to_authorized_origin(self):
        endpoint = EndpointEvidence('attacker.example', '93.184.216.34', 3)
        permit = RoutePermit(self.direct.request, endpoint, 'direct')
        with self.assertRaises(BindingError):
            SafeTransport(EffectLedger()).send_direct(permit, self.tls)

    def test_wildcard_is_single_label_only(self):
        self.assertTrue(dns_id_matches('api.example.com', '*.example.com'))
        self.assertFalse(dns_id_matches('deep.api.example.com', '*.example.com'))


if __name__ == '__main__':
    unittest.main()
