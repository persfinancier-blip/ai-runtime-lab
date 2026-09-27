from __future__ import annotations

import unittest

from experiments.provider_generation_history.tests.lab095_identity_installation_reference import (
    IdentityInstallState,
    Snapshot,
    classify,
    retry_action,
)


def s(**kw):
    base = dict(
        custody_present=False,
        custody_status=None,
        custody_payload_digest=None,
        intent_status=None,
        intent_payload_digest=None,
        receipt_binding_present=False,
        confirmed_identity_digest_present=False,
    )
    base.update(kw)
    return Snapshot(**base)


class IdentityInstallationStateMachineTests(unittest.TestCase):
    def test_fresh_install(self):
        state = classify(s())
        self.assertEqual(state, IdentityInstallState.LEGACY_ABSENT)
        self.assertEqual(retry_action(state), "BEGIN_INSTALL")

    def test_prepared_crash_and_unknown_retry_reuse_same_request(self):
        state = classify(s(
            custody_present=True,
            custody_status="PREPARED",
            custody_payload_digest="payload",
            intent_status="PREPARED",
            intent_payload_digest="payload",
        ))
        self.assertEqual(state, IdentityInstallState.PREPARED)
        self.assertEqual(retry_action(state), "RECONCILE_SAME_REQUEST")

    def test_confirmed_restart_finalizes_without_new_increment(self):
        state = classify(s(
            custody_present=True,
            custody_status="PREPARED",
            custody_payload_digest="payload",
            intent_status="CONFIRMED",
            intent_payload_digest="payload",
            receipt_binding_present=True,
        ))
        self.assertEqual(state, IdentityInstallState.CONFIRMED_NEEDS_FINALIZE)
        self.assertEqual(retry_action(state), "FINALIZE_LOCALLY")

    def test_complete_is_verify_only(self):
        state = classify(s(
            custody_present=True,
            custody_status="CONFIRMED",
            custody_payload_digest="payload",
            intent_status="CONFIRMED",
            intent_payload_digest="payload",
            receipt_binding_present=True,
            confirmed_identity_digest_present=True,
        ))
        self.assertEqual(state, IdentityInstallState.COMPLETE)
        self.assertEqual(retry_action(state), "VERIFY_ONLY")

    def test_partial_states_fail_closed(self):
        bad = [
            s(custody_present=True, custody_status="PREPARED",
              custody_payload_digest="p", intent_status=None),
            s(intent_status="PREPARED", intent_payload_digest="p"),
            s(custody_present=True, custody_status="PREPARED",
              custody_payload_digest="p", intent_status="PREPARED",
              intent_payload_digest="other"),
            s(custody_present=True, custody_status="CONFIRMED",
              custody_payload_digest="p", intent_status="PREPARED",
              intent_payload_digest="p"),
            s(custody_present=True, custody_status="PREPARED",
              custody_payload_digest="p", intent_status="CONFIRMED",
              intent_payload_digest="p", receipt_binding_present=False),
            s(custody_present=True, custody_status="PREPARED",
              custody_payload_digest="p", intent_status="PREPARED",
              intent_payload_digest="p", receipt_binding_present=True),
        ]
        for snapshot in bad:
            with self.subTest(snapshot=snapshot):
                self.assertEqual(classify(snapshot), IdentityInstallState.CORRUPT)
                self.assertEqual(retry_action(classify(snapshot)), "FAIL_CLOSED")


if __name__ == "__main__":
    unittest.main()
