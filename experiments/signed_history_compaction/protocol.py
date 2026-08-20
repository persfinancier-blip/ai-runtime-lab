from .core import *
from .verify import VerifyMixin
from .archive import ArchiveMixin

class SignedPrunableHistory(ArchiveMixin, VerifyMixin):
    def __init__(self, store: HistoryStore, archive_dir, *, checkpoint_key=b"checkpoint-key", external_anchor_id="anchor-A"):
            self.store = store
            self.archive_dir = Path(archive_dir)
            self.archive_dir.mkdir(parents=True, exist_ok=True)
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

class UnsafeDeleteFirst:
    def prune(self, db_path, through):
        q = sqlite3.connect(str(db_path))
        try:
            q.execute("DELETE FROM transitions WHERE sequence<=?", (through,))
            q.commit()
        finally:
            q.close()
