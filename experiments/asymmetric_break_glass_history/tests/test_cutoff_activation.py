import unittest

from experiments.asymmetric_break_glass_history.cutoff_activation import (
    CutoffActivationError,
    require_public_authority_active_at_cutoff,
)


class CutoffActivationTests(unittest.TestCase):
    def test_current_successor_is_active_at_rotation_root_version(self):
        self.assertTrue(
            require_public_authority_active_at_cutoff(
                "public-2",
                3,
                ("public-1", "public-2"),
                (("public-1", "public-2", 3),),
            )
        )

    def test_old_authority_is_stale_at_rotation_root_version(self):
        with self.assertRaises(CutoffActivationError):
            require_public_authority_active_at_cutoff(
                "public-1",
                3,
                ("public-1", "public-2"),
                (("public-1", "public-2", 3),),
            )

    def test_old_authority_is_active_before_rotation(self):
        self.assertTrue(
            require_public_authority_active_at_cutoff(
                "public-1",
                2,
                ("public-1", "public-2"),
                (("public-1", "public-2", 3),),
            )
        )

    def test_multiple_same_root_rotations_leave_only_last_successor_active(self):
        history = ("public-1", "public-2", "public-3")
        edges = (
            ("public-1", "public-2", 4),
            ("public-2", "public-3", 4),
        )
        with self.assertRaises(CutoffActivationError):
            require_public_authority_active_at_cutoff(
                "public-2", 4, history, edges
            )
        self.assertTrue(
            require_public_authority_active_at_cutoff(
                "public-3", 4, history, edges
            )
        )

    def test_transition_root_version_rollback_is_rejected(self):
        with self.assertRaises(CutoffActivationError):
            require_public_authority_active_at_cutoff(
                "public-3",
                5,
                ("public-1", "public-2", "public-3"),
                (
                    ("public-1", "public-2", 5),
                    ("public-2", "public-3", 4),
                ),
            )

    def test_transition_continuity_and_cardinality_are_strict(self):
        with self.assertRaises(CutoffActivationError):
            require_public_authority_active_at_cutoff(
                "public-2",
                3,
                ("public-1", "public-2"),
                (),
            )
        with self.assertRaises(CutoffActivationError):
            require_public_authority_active_at_cutoff(
                "public-2",
                3,
                ("public-1", "public-2"),
                (("wrong", "public-2", 3),),
            )

    def test_bool_is_not_accepted_as_root_version(self):
        with self.assertRaises(CutoffActivationError):
            require_public_authority_active_at_cutoff(
                "public-1", True, ("public-1",), ()
            )


if __name__ == "__main__":
    unittest.main()
