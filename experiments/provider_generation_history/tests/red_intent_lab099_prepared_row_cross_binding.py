"""LAB-099 non-discoverable persisted PREPARED fixture cross-binding checks.

These checks exercise only test-owned fixture/oracle code. They deliberately do not
import the future LAB-099 production module, so they can validate that the RED-intent
crash fixture itself persists one exact cross-bound PREPARED pair and that durable row
tampering fails closed before production implementation begins.
"""

from __future__ import annotations

import unittest

from experiments.provider_generation_history.tests import (
    lab099_precursor_fixture_adapter as fixture,
)
from experiments.provider_generation_history.tests import (
    lab099_prepared_fixture_row_verifier as persisted,
)
from experiments.provider_generation_history.tests.red_intent_lab099_precursor_cutover import (
    Lab099PrecursorCutoverRedIntentTests,
    attested,
)


class Lab099PreparedFixtureCrossBindingIntentTests(unittest.TestCase):
    def _prepared_fixture(self):
        base = Lab099PrecursorCutoverRedIntentTests()
        td, path, key, provider, g1 = base._legacy_lab092_complete()
        runtime = attested(provider, 1, key)
        prepared = fixture.install_atomic_prepared_cutover(path, runtime, g1)
        return td, path, runtime, prepared

    def test_atomic_prepared_fixture_rows_cross_bind_exactly(self):
        td, path, runtime, prepared = self._prepared_fixture()
        with td:
            self.assertTrue(
                persisted.verify_installed_prepared_cutover(
                    path,
                    runtime,
                    prepared_event_digest=prepared.prepared_event_digest,
                )
            )

    def test_persisted_prepared_tamper_cases_fail_closed(self):
        for field in (
            "confirmation_nonce",
            "prepared_digest",
            "provider_generation",
            "predecessor_position",
            "position",
            "request_id",
        ):
            with self.subTest(field=field):
                td, path, runtime, prepared = self._prepared_fixture()
                with td:
                    persisted.tamper_prepared_fixture_for_test_only(
                        path,
                        prepared_event_digest=prepared.prepared_event_digest,
                        field=field,
                    )
                    with self.assertRaises(
                        persisted.PreparedFixtureRowVerificationError
                    ):
                        persisted.verify_installed_prepared_cutover(
                            path,
                            runtime,
                            prepared_event_digest=prepared.prepared_event_digest,
                        )


if __name__ == "__main__":
    unittest.main()
