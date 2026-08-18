import unittest

from experiments.capability_planner.planner import (
    CapabilityObservation,
    Planner,
    Requirement,
    Route,
)

NOW = 100


def observation(
    capability_id,
    route,
    *,
    available=True,
    observed_at=95,
    ttl=10,
    properties=None,
):
    return CapabilityObservation(
        1,
        capability_id,
        route,
        "integrate",
        observed_at,
        ttl,
        available,
        properties or {},
        f"evidence:{capability_id}",
    )


def requirement(**hard):
    return Requirement(1, "integrate", hard, {"preferred": 10, "auditable": 5})


ROUTES = [
    Route(
        "merge-api",
        "integrate",
        "merge",
        {"safe": True, "auditable": True, "preferred": True},
        5,
    ),
    Route(
        "contents-api",
        "integrate",
        "contents",
        {"safe": True, "auditable": True, "preferred": False},
        4,
    ),
    Route(
        "force-ref",
        "integrate",
        "force",
        {"safe": False, "auditable": False, "preferred": False},
        99,
    ),
]


class CapabilityPlannerTests(unittest.TestCase):
    def test_preferred_path(self):
        plan = Planner(
            ROUTES,
            [observation("merge", "merge"), observation("contents", "contents")],
        ).plan(requirement(safe=True, auditable=True), NOW)
        self.assertEqual(plan.selected, "merge-api")

    def test_safe_fallback(self):
        plan = Planner(
            ROUTES,
            [
                observation("merge", "merge", available=False),
                observation("contents", "contents"),
            ],
        ).plan(requirement(safe=True, auditable=True), NOW)
        self.assertEqual(plan.selected, "contents-api")

    def test_stale_observation_rejected(self):
        plan = Planner(
            ROUTES,
            [
                observation("merge", "merge", observed_at=1, ttl=1),
                observation("contents", "contents"),
            ],
        ).plan(requirement(safe=True, auditable=True), NOW)
        self.assertEqual(plan.selected, "contents-api")
        self.assertIn("stale_observation", plan.rejected["merge-api"])

    def test_unsafe_fallback_rejected(self):
        plan = Planner(
            ROUTES,
            [
                observation("merge", "merge", available=False),
                observation("force", "force"),
            ],
        ).plan(requirement(safe=True, auditable=True), NOW)
        self.assertIsNone(plan.selected)
        self.assertIn("hard:safe", plan.rejected["force-ref"])

    def test_deterministic_tie_breaking(self):
        routes = [
            Route("b", "integrate", "b", {"safe": True, "auditable": True}, 0),
            Route("a", "integrate", "a", {"safe": True, "auditable": True}, 0),
        ]
        plan = Planner(routes, [observation("a", "a"), observation("b", "b")]).plan(
            requirement(safe=True, auditable=True), NOW
        )
        self.assertEqual(plan.selected, "a")

    def test_no_viable_path(self):
        plan = Planner(ROUTES, []).plan(requirement(safe=True), NOW)
        self.assertIsNone(plan.selected)
        self.assertEqual(
            set(plan.rejected), {"merge-api", "contents-api", "force-ref"}
        )

    def test_explanation_is_stable(self):
        planner = Planner(ROUTES, [observation("merge", "merge")])
        a = planner.plan(requirement(safe=True), NOW)
        b = planner.plan(requirement(safe=True), NOW)
        self.assertEqual(a.explanation_id, b.explanation_id)


if __name__ == "__main__":
    unittest.main()
