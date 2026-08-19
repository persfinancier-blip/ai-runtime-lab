import unittest

from experiments.credential_scope.protocol import (
    CookieCredential,
    CredentialRouter,
    OriginCredential,
    ProxyCredential,
    ReconcileRequired,
    RequestBinding,
    ScopeError,
    StaleCredentialError,
)


def req(url="https://api.example.com/private/report", generation=1, route="direct:v7"):
    return RequestBinding(url=url, payload_digest="payload-v1", purpose="report", effect_id="effect-1", route_fingerprint=route, request_generation=generation)


class CredentialScopeTests(unittest.TestCase):
    def setUp(self):
        self.r = CredentialRouter()
        self.r.origin_credentials["origin"] = OriginCredential("origin", "Bearer ORIGIN", "https", "api.example.com", 443, "/private", generation=3)
        self.r.cookies["session"] = CookieCredential("session", "sid=abc", "api.example.com", "/private", generation=2)
        self.r.proxy_credentials["proxy-a"] = ProxyCredential("proxy-a", "Basic PROXYA", "proxy-a", 4, credential_generation=6)
        self.r.proxy_credentials["proxy-b"] = ProxyCredential("proxy-b", "Basic PROXYB", "proxy-b", 9, credential_generation=1)

    def test_same_origin_uses_intended_origin_credential_and_cookie(self):
        q = req()
        p = self.r.issue_permit(q, origin_credential_id="origin", cookie_ids=("session",))
        origin, proxy = self.r.materialize_headers(q, p)
        self.assertEqual(origin["Authorization"], "Bearer ORIGIN")
        self.assertEqual(origin["Cookie"], "sid=abc")
        self.assertEqual(proxy, {})

    def test_cross_origin_redirect_requires_new_permit_and_drops_origin_secrets(self):
        q = req()
        p = self.r.issue_permit(q, origin_credential_id="origin", cookie_ids=("session",))
        redirected = self.r.redirect(q, "https://attacker.example/private/report")
        with self.assertRaises(ScopeError):
            self.r.materialize_headers(redirected, p)

    def test_same_origin_redirect_preserves_only_path_valid_credentials(self):
        q = req()
        p = self.r.issue_permit(q, origin_credential_id="origin", cookie_ids=("session",))
        redirected = self.r.redirect(q, "https://api.example.com/public")
        with self.assertRaises(ScopeError):
            self.r.materialize_headers(redirected, p)
        clean = self.r.issue_permit(redirected)
        origin, _ = self.r.materialize_headers(redirected, clean)
        self.assertEqual(origin, {})

    def test_proxy_authorization_is_separate_from_origin_headers(self):
        q = req(route="proxy-a:v4")
        p = self.r.issue_permit(q, origin_credential_id="origin", proxy_id="proxy-a", proxy_generation=4, proxy_credential_id="proxy-a")
        origin, proxy = self.r.materialize_headers(q, p)
        self.assertIn("Authorization", origin)
        self.assertNotIn("Proxy-Authorization", origin)
        self.assertEqual(proxy, {"Proxy-Authorization": "Basic PROXYA"})

    def test_origin_credential_cannot_be_used_as_proxy_credential(self):
        q = req(route="proxy-a:v4")
        with self.assertRaises(ScopeError):
            self.r.issue_permit(q, proxy_id="proxy-a", proxy_generation=4, proxy_credential_id="origin")

    def test_proxy_fallback_requires_new_proxy_credential_and_route_binding(self):
        q = req(route="proxy-a:v4")
        p = self.r.issue_permit(q, proxy_id="proxy-a", proxy_generation=4, proxy_credential_id="proxy-a")
        fallback = RequestBinding(q.url, q.payload_digest, q.purpose, q.effect_id, "proxy-b:v9", q.request_generation)
        with self.assertRaises(ScopeError):
            self.r.materialize_headers(fallback, p)
        p2 = self.r.issue_permit(fallback, proxy_id="proxy-b", proxy_generation=9, proxy_credential_id="proxy-b")
        _, proxy = self.r.materialize_headers(fallback, p2)
        self.assertEqual(proxy["Proxy-Authorization"], "Basic PROXYB")

    def test_origin_credential_rotation_invalidates_existing_permit(self):
        q = req()
        p = self.r.issue_permit(q, origin_credential_id="origin")
        self.r.origin_credentials["origin"] = OriginCredential("origin", "Bearer NEW", "https", "api.example.com", 443, "/private", generation=4)
        with self.assertRaises(StaleCredentialError):
            self.r.materialize_headers(q, p)

    def test_proxy_credential_rotation_invalidates_existing_permit(self):
        q = req(route="proxy-a:v4")
        p = self.r.issue_permit(q, proxy_id="proxy-a", proxy_generation=4, proxy_credential_id="proxy-a")
        self.r.proxy_credentials["proxy-a"] = ProxyCredential("proxy-a", "Basic NEW", "proxy-a", 4, credential_generation=7)
        with self.assertRaises(StaleCredentialError):
            self.r.materialize_headers(q, p)

    def test_request_generation_change_invalidates_permit(self):
        q = req(generation=1)
        p = self.r.issue_permit(q, origin_credential_id="origin")
        newer = req(generation=2)
        with self.assertRaises(StaleCredentialError):
            self.r.materialize_headers(newer, p)

    def test_unknown_effect_requires_reconciliation_before_route_or_credential_refresh(self):
        q = req()
        self.r.begin_or_resume(q)
        self.r.mark_unknown(q)
        with self.assertRaises(ReconcileRequired):
            self.r.begin_or_resume(q)
        self.r.reconcile(q.effect_id, "receipt-1")
        self.assertEqual(self.r.begin_or_resume(q).status, "CONFIRMED")

    def test_origin_credential_can_be_request_bound_like_sender_constrained_token(self):
        q = req()
        base = self.r.origin_credentials["origin"]
        self.r.origin_credentials["bound"] = OriginCredential("bound", "DPoP TOKEN", base.scheme, base.host, base.port, base.path_prefix, generation=1, request_fingerprint=q.fingerprint)
        p = self.r.issue_permit(q, origin_credential_id="bound")
        self.assertEqual(self.r.materialize_headers(q, p)[0]["Authorization"], "DPoP TOKEN")
        changed = RequestBinding(q.url, "payload-v2", q.purpose, q.effect_id, q.route_fingerprint, q.request_generation)
        with self.assertRaises(ScopeError):
            self.r.issue_permit(changed, origin_credential_id="bound")

    def test_cookie_secure_and_host_scope_enforced(self):
        insecure = req("http://api.example.com/private/report")
        with self.assertRaises(ScopeError):
            self.r.issue_permit(insecure, cookie_ids=("session",))
        other = req("https://other.example.com/private/report")
        with self.assertRaises(ScopeError):
            self.r.issue_permit(other, cookie_ids=("session",))

    def test_effect_and_route_identity_are_in_request_fingerprint(self):
        a = req(route="direct:v7")
        b = RequestBinding(a.url, a.payload_digest, a.purpose, "effect-2", a.route_fingerprint, a.request_generation)
        c = RequestBinding(a.url, a.payload_digest, a.purpose, a.effect_id, "proxy-a:v4", a.request_generation)
        self.assertNotEqual(a.fingerprint, b.fingerprint)
        self.assertNotEqual(a.fingerprint, c.fingerprint)

    def test_cookie_path_match_uses_segment_boundary_not_naive_prefix(self):
        tricky = req("https://api.example.com/private2/report")
        with self.assertRaises(ScopeError):
            self.r.issue_permit(tricky, cookie_ids=("session",))

    def test_unknown_blocks_new_permit_on_changed_route_until_reconciled(self):
        q = req()
        self.r.mark_unknown(q)
        changed = RequestBinding(q.url, q.payload_digest, q.purpose, q.effect_id, "proxy-a:v4", q.request_generation)
        with self.assertRaises(ReconcileRequired):
            self.r.issue_permit(changed, proxy_id="proxy-a", proxy_generation=4, proxy_credential_id="proxy-a")
        self.r.reconcile(q.effect_id, None)
        p = self.r.issue_permit(changed, proxy_id="proxy-a", proxy_generation=4, proxy_credential_id="proxy-a")
        self.assertEqual(p.proxy_id, "proxy-a")

    def test_proxy_route_identity_mismatch_is_rejected(self):
        q = req(route="proxy-b:v9")
        with self.assertRaises(ScopeError):
            self.r.issue_permit(q, proxy_id="proxy-a", proxy_generation=4, proxy_credential_id="proxy-a")


if __name__ == "__main__":
    unittest.main()
