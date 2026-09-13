from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.database_binding import CanonicalDatabaseBinding


class _SyntheticReservationSurface(CanonicalDatabaseBinding):
    """Mirrors LAB-092's object.__new__ + first manual path assignment pattern."""


class DatabaseBindingObjectNewSurfaceTests(unittest.TestCase):
    def test_object_new_surface_gets_one_canonical_binding_then_cannot_rebind(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_a = root / "nested" / ".." / "a.sqlite"
            db_b = root / "b.sqlite"

            surface = object.__new__(_SyntheticReservationSurface)
            with self.assertRaisesRegex(AttributeError, "not initialized"):
                _ = surface.path

            surface.path = db_a
            self.assertEqual(Path(surface.path), db_a.resolve(strict=False))

            with self.assertRaisesRegex(AttributeError, "construction-bound"):
                surface.path = db_b
            with self.assertRaisesRegex(AttributeError, "construction-bound"):
                surface._canonical_database_path = str(db_b)

            self.assertEqual(Path(surface.path), db_a.resolve(strict=False))


if __name__ == "__main__":
    unittest.main()
