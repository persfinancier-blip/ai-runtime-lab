import os
import threading

from .core import *
from .verify import VerifyMixin
from .archive import ArchiveMixin
from experiments.filesystem_namespace_binding.integration import NamespaceBoundArchiveMixin


class SignedPrunableHistory(NamespaceBoundArchiveMixin, ArchiveMixin, VerifyMixin):
    def __init__(self, store: HistoryStore, archive_dir, *, checkpoint_key=b"checkpoint-key", external_anchor_id="anchor-A"):
            self._namespace_thread_state = threading.local()
            self.store = store
            # Bind a relative configured path to the process namespace at construction.
            # Later cwd changes must not silently retarget archive publication authority.
            self.archive_dir = Path(os.path.abspath(os.fspath(archive_dir)))
            # Do not use Path.mkdir(parents=True): it follows path-prefix symlinks and
            # can create external state before LAB-065's namespace authorization.
            self._ensure_archive_directory_exists()
            self.key = checkpoint_key
            self.anchor = external_anchor_id
            if not self.key or not self.anchor:
                raise ValueError("checkpoint identity")
            self.signer_id = hashlib.sha256(self.key).hexdigest()[:16]
            q = self.store._con()
            try:
                q.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS signed_compact_checkpoints(
                      checkpoint_id TEXT PRIMARY KEY, sequence INTEGER NOT NULL UNIQUE, body_json TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS signed_checkpoint_watermark(
                      singleton INTEGER PRIMARY KEY CHECK(singleton=1), sequence INTEGER NOT NULL, checkpoint_id TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS signed_archives(
                      archive_id TEXT PRIMARY KEY, end_sequence INTEGER NOT NULL UNIQUE, manifest_json TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS signed_compaction_base(
                      singleton INTEGER PRIMARY KEY CHECK(singleton=1), base_sequence INTEGER NOT NULL,
                      root_id TEXT NOT NULL, recovery_id TEXT NOT NULL, prefix_commitment TEXT NOT NULL,
                      archive_id TEXT, checkpoint_id TEXT);
                    """
                )
                if q.execute("SELECT 1 FROM signed_compaction_base WHERE singleton=1").fetchone() is None:
                    root_id, recovery_id = q.execute(
                        "SELECT root_id,recovery_id FROM bootstrap WHERE singleton=1"
                    ).fetchone()
                    q.execute(
                        "INSERT INTO signed_compaction_base VALUES(1,0,?,?,?,NULL,NULL)",
                        (root_id, recovery_id, seed_commitment(root_id, recovery_id)),
                    )
            finally:
                q.close()

    @property
    def _active_namespace_handle(self):
        return getattr(self._namespace_thread_state, "handle", None)

    @_active_namespace_handle.setter
    def _active_namespace_handle(self, handle):
        if handle is None:
            if hasattr(self._namespace_thread_state, "handle"):
                del self._namespace_thread_state.handle
        else:
            self._namespace_thread_state.handle = handle


class UnsafeDeleteFirst:
    def prune(self, db_path, through):
        q = sqlite3.connect(str(db_path))
        try:
            q.execute("DELETE FROM transitions WHERE sequence<=?", (through,))
            q.commit()
        finally:
            q.close()
