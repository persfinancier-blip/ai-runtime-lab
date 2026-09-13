from __future__ import annotations

from pathlib import Path


class CanonicalDatabaseBinding:
    """Construction-bound canonical SQLite path for supported runtime objects.

    The public ``path`` attribute remains readable for diagnostics/compatibility,
    but both it and the private source of truth become non-rebindable after the
    first assignment performed by an existing base constructor.
    """

    _DATABASE_PATH_SLOT = "_canonical_database_path"

    @staticmethod
    def _canonicalize_database_path(value) -> str:
        return str(Path(value).expanduser().resolve(strict=False))

    def __setattr__(self, name, value):
        if name in {"path", self._DATABASE_PATH_SLOT} and hasattr(
            self, self._DATABASE_PATH_SLOT
        ):
            raise AttributeError("database path is construction-bound")
        super().__setattr__(name, value)

    @property
    def path(self) -> str:
        try:
            return object.__getattribute__(self, self._DATABASE_PATH_SLOT)
        except AttributeError as exc:
            raise AttributeError("database path is not initialized") from exc

    @path.setter
    def path(self, value) -> None:
        if hasattr(self, self._DATABASE_PATH_SLOT):
            raise AttributeError("database path is construction-bound")
        object.__setattr__(
            self,
            self._DATABASE_PATH_SLOT,
            self._canonicalize_database_path(value),
        )
