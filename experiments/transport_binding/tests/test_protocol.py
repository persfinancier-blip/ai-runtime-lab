import unittest
from experiments.transport_binding.protocol import *

PUB='93.184.216.34'
PUB2='151.101.1.69'

def ident(dest='https://trusted.example/upload', gen=7):
    return RequestIdentity('permit-1','effect-abc','payload-hash',canonical_https_url(dest),'report',gen)

class TransportBindingTests(unittest.TestCase):
    def make(self, seq, redirects=None, hosts=None):
        r=FakeResolver(seq); c=FakeConnector()
        p=EndpointPolicy(frozenset(hosts or {'trusted.example','cdn.trusted.example'}))
        e=SafeTransportExecutor(p,r,FakeRedirector(redirects or {}),c)
        return e,c,r

    def test_public_allowed_hostname_commits(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',[PUB]),Resolution('trusted.example',[PUB])]})
        rec=e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())
        self.assertEqual(rec['endpoint'],PUB); self.assertEqual(len(c.connections),1)

    def test_dns_rebind_public_to_loopback_blocked(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',[PUB]),Resolution('trusted.example',['127.0.0.1'])]})
        with self.assertRaises(TransportPolicyError): e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())
        self.assertFalse(c.connections)

    def test_redirect_to_disallowed_host_blocked(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',[PUB])]}, {'https://trusted.example/upload':'https://evil.example/x'})
        with self.assertRaises(TransportPolicyError): e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())
        self.assertFalse(c.connections)

    def test_allowed_same_host_redirect_revalidated(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',[PUB]), Resolution('trusted.example',[PUB2])]}, {'https://trusted.example/upload':'https://trusted.example/final'})
        rec=e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())
        self.assertEqual(rec['endpoint'],PUB2)
        self.assertEqual(rec['url'],'https://trusted.example/final')

    def test_alias_chain_landing_on_forbidden_endpoint_blocked(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',['169.254.169.254'],aliases=['metadata.internal'])]})
        with self.assertRaises(TransportPolicyError): e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())
        self.assertFalse(c.connections)

    def test_special_ranges_and_normalized_literals_blocked(self):
        bad=['127.1.2.3','10.0.0.1','169.254.169.254','0.0.0.0','::1','fe80::1','fc00::1','::ffff:127.0.0.1']
        for ip in bad: self.assertFalse(is_allowed_public_ip(ip),ip)
        self.assertTrue(is_allowed_public_ip(PUB))

    def test_unknown_retry_reconciles_without_reresolve(self):
        e,c,r=self.make({'trusted.example':[Resolution('trusted.example',[PUB]),Resolution('trusted.example',[PUB]), Resolution('trusted.example',['127.0.0.1'])]})
        with self.assertRaises(UnknownOutcome):
            e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident(),timeout_after_commit=True)
        calls_before=r.calls['trusted.example']
        rec=e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())
        self.assertEqual(rec['endpoint'],PUB); self.assertEqual(r.calls['trusted.example'],calls_before); self.assertEqual(len(c.connections),1)

    def test_request_identity_composition_blocks_destination_drift(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',[PUB])]})
        with self.assertRaises(TransportPolicyError): e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident('https://trusted.example/other'))
        self.assertFalse(c.connections)

    def test_private_and_linklocal_ipv6_blocked(self):
        for ip in ['fd00:ec2::254','fd20:ce::254','fe80::abcd','::1']: self.assertFalse(is_allowed_public_ip(ip))

    def test_unsafe_resolve_once_is_falsified(self):
        r=FakeResolver({'trusted.example':[Resolution('trusted.example',[PUB]),Resolution('trusted.example',['127.0.0.1'])]})
        c=FakeConnector(); u=UnsafeResolveOnceExecutor(r,c)
        rec=u.execute(url='https://trusted.example/upload',identity=ident())
        self.assertEqual(rec['endpoint'],'127.0.0.1')

    def test_multiple_answers_any_forbidden_blocks(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',[PUB,'10.0.0.4'])]})
        with self.assertRaises(TransportPolicyError): e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())

    def test_cross_host_redirect_requires_new_authorization(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',[PUB])]}, {'https://trusted.example/upload':'https://cdn.trusted.example/final'})
        with self.assertRaises(TransportPolicyError): e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())
        self.assertFalse(c.connections)

    def test_same_host_redirect_endpoint_rebinding_blocked(self):
        e,c,_=self.make({'trusted.example':[Resolution('trusted.example',[PUB]),Resolution('trusted.example',['169.254.169.254'])]}, {'https://trusted.example/upload':'https://trusted.example/final'})
        with self.assertRaises(TransportPolicyError): e.execute(prepared_destination='https://trusted.example/upload',current_destination='https://trusted.example/upload',identity=ident())
        self.assertFalse(c.connections)
