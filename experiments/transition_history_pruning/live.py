from .core import *

class LiveHistoryCore:
    """
    LAB-061 reference model.

    The live authority after compaction is the authenticated compaction_base row plus
    the retained transition suffix. Archive bytes are not required for normal restart;
    they are required only for explicit forensic archive audit.
    """
    def __init__(self,path,archive_dir,*,checkpoint_key=b"checkpoint-key",external_anchor_id="anchor-A"):
        self.path=str(path); self.archive_dir=Path(archive_dir); self.archive_dir.mkdir(parents=True,exist_ok=True)
        self.key=checkpoint_key; self.anchor=external_anchor_id
        self.signer_id=hashlib.sha256(checkpoint_key).hexdigest()[:16]
        q=sqlite3.connect(self.path)
        q.execute("PRAGMA journal_mode=WAL")
        q.executescript("""
        CREATE TABLE IF NOT EXISTS bootstrap(singleton INTEGER PRIMARY KEY CHECK(singleton=1),root_id TEXT NOT NULL,recovery_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS head(singleton INTEGER PRIMARY KEY CHECK(singleton=1),root_id TEXT NOT NULL,recovery_id TEXT NOT NULL,sequence INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS transitions(
          sequence INTEGER PRIMARY KEY,proposal_id TEXT NOT NULL UNIQUE,transition_digest TEXT NOT NULL UNIQUE,
          kind TEXT NOT NULL,predecessor_root_id TEXT NOT NULL,predecessor_recovery_id TEXT NOT NULL,
          successor_root_id TEXT NOT NULL,successor_recovery_id TEXT NOT NULL,proof_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS compact_checkpoints(checkpoint_id TEXT PRIMARY KEY,sequence INTEGER NOT NULL UNIQUE,body_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS compact_checkpoint_watermark(singleton INTEGER PRIMARY KEY CHECK(singleton=1),sequence INTEGER NOT NULL,checkpoint_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS archives(archive_id TEXT PRIMARY KEY,end_sequence INTEGER NOT NULL UNIQUE,manifest_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS compaction_base(singleton INTEGER PRIMARY KEY CHECK(singleton=1),
          base_sequence INTEGER NOT NULL,root_id TEXT NOT NULL,recovery_id TEXT NOT NULL,
          prefix_commitment TEXT NOT NULL,archive_id TEXT,checkpoint_id TEXT);
        """)
        q.commit(); q.close()

    def _con(self):
        q=sqlite3.connect(self.path,timeout=5,isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    def initialize(self,root_id,recovery_id):
        strict_hex(root_id,"root_id"); strict_hex(recovery_id,"recovery_id")
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            if q.execute("SELECT 1 FROM bootstrap").fetchone() is None:
                q.execute("INSERT INTO bootstrap VALUES(1,?,?)",(root_id,recovery_id))
                q.execute("INSERT INTO head VALUES(1,?,?,0)",(root_id,recovery_id))
                q.execute("INSERT INTO compaction_base VALUES(1,0,?,?,?,NULL,NULL)",
                          (root_id,recovery_id,seed_commitment(root_id,recovery_id)))
            q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

    def history_id(self,q):
        b=q.execute("SELECT root_id,recovery_id FROM bootstrap WHERE singleton=1").fetchone()
        if not b: raise IntegrityError("missing bootstrap")
        return sha(canon({"kind":"lab061-history","bootstrap_root_id":b[0],
                         "bootstrap_recovery_id":b[1],"protocol":PROTOCOL,
                         "external_anchor_id":self.anchor}))

    def append(self,proposal_id,kind,successor_root_id,successor_recovery_id,proof=None):
        strict_hex(successor_root_id,"successor_root_id"); strict_hex(successor_recovery_id,"successor_recovery_id")
        if kind not in ("rotate_recovery","recover_root"): raise IntegrityError("kind")
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            old=q.execute("SELECT transition_digest FROM transitions WHERE proposal_id=?",(proposal_id,)).fetchone()
            if old:
                q.commit(); return old[0]
            r0,c0,seq=q.execute("SELECT root_id,recovery_id,sequence FROM head WHERE singleton=1").fetchone()
            if kind=="rotate_recovery" and successor_root_id!=r0: raise IntegrityError("root changed during recovery rotation")
            if kind=="recover_root" and successor_recovery_id!=c0: raise IntegrityError("recovery changed during root recovery")
            td=sha(canon({"proposal_id":proposal_id,"kind":kind,"predecessor_root_id":r0,
                          "predecessor_recovery_id":c0,"successor_root_id":successor_root_id,
                          "successor_recovery_id":successor_recovery_id}))
            pj=json.dumps(proof or {"proposal_id":proposal_id,"transition_digest":td},sort_keys=True,separators=(",",":"))
            q.execute("INSERT INTO transitions VALUES(?,?,?,?,?,?,?,?,?)",
                      (seq+1,proposal_id,td,kind,r0,c0,successor_root_id,successor_recovery_id,pj))
            q.execute("UPDATE head SET root_id=?,recovery_id=?,sequence=? WHERE singleton=1",
                      (successor_root_id,successor_recovery_id,seq+1))
            q.commit(); return td
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

    def _base(self,q):
        r=q.execute("SELECT base_sequence,root_id,recovery_id,prefix_commitment,archive_id,checkpoint_id FROM compaction_base WHERE singleton=1").fetchone()
        if not r: raise IntegrityError("missing compaction base")
        return r

    def _verify_suffix_locked(self,q,through_sequence=None):
        base_seq,root,rec,commitment,archive_id,checkpoint_id=self._base(q)
        head=q.execute("SELECT root_id,recovery_id,sequence FROM head WHERE singleton=1").fetchone()
        if not head: raise HeadMismatch("missing head")
        end=head[2] if through_sequence is None else through_sequence
        if end<base_seq or end>head[2]: raise IntegrityError("verification range")
        rows=q.execute("""SELECT sequence,proposal_id,transition_digest,kind,predecessor_root_id,
          predecessor_recovery_id,successor_root_id,successor_recovery_id,proof_json
          FROM transitions WHERE sequence>? AND sequence<=? ORDER BY sequence""",(base_seq,end)).fetchall()
        expected=base_seq+1
        for row in rows:
            seq,pid,td,kind,r0,c0,r1,c1,pj=row
            if seq!=expected: raise IntegrityError("suffix sequence gap")
            if (r0,c0)!=(root,rec): raise IntegrityError("suffix predecessor")
            expected_td=sha(canon({"proposal_id":pid,"kind":kind,"predecessor_root_id":r0,
                                   "predecessor_recovery_id":c0,"successor_root_id":r1,
                                   "successor_recovery_id":c1}))
            if td!=expected_td: raise IntegrityError("transition digest")
            proof=json.loads(pj)
            if proof.get("proposal_id")!=pid or proof.get("transition_digest")!=td:
                raise IntegrityError("proof identity")
            if kind=="rotate_recovery":
                if r1!=root: raise IntegrityError("rotation root")
                rec=c1
            elif kind=="recover_root":
                if c1!=rec: raise IntegrityError("recovery root")
                root=r1
            else: raise IntegrityError("kind")
            commitment=advance_commitment(commitment,row)
            expected+=1
        if expected-1!=end: raise IntegrityError("suffix missing tail")
        if through_sequence is None and head!=(root,rec,end): raise HeadMismatch("head/suffix mismatch")
        return {"root_id":root,"recovery_id":rec,"sequence":end,"prefix_commitment":commitment,
                "base_sequence":base_seq,"archive_id":archive_id,"checkpoint_id":checkpoint_id,
                "rows_verified":len(rows)}

    def _verify_base_checkpoint_locked(self,q,base):
        base_seq,base_root,base_rec,base_commitment,archive_id,checkpoint_id=base
        if base_seq==0:
            if checkpoint_id is not None or archive_id is not None:
                raise AuthenticationError("bootstrap base carries archive/checkpoint")
            return
        if checkpoint_id is None:
            raise AuthenticationError("compacted base missing checkpoint")
        row=q.execute("SELECT body_json FROM compact_checkpoints WHERE checkpoint_id=?",(checkpoint_id,)).fetchone()
        if not row: raise AuthenticationError("base checkpoint missing")
        cp=CompactCheckpoint.parse(row[0])
        if cp.checkpoint_id!=checkpoint_id:
            raise AuthenticationError("base checkpoint content identity")
        if cp.history_id!=self.history_id(q) or cp.external_anchor_id!=self.anchor:
            raise AuthenticationError("base checkpoint history/anchor")
        if cp.signer_id!=self.signer_id or not hmac.compare_digest(mac(self.key,cp.unsigned),cp.signature):
            raise AuthenticationError("base checkpoint signature")
        if (cp.sequence,cp.root_id,cp.recovery_id,cp.prefix_commitment)!=(base_seq,base_root,base_rec,base_commitment):
            raise AuthenticationError("base/checkpoint mismatch")

    def verify_restart(self):
        q=self._con()
        try:
            q.execute("BEGIN")
            base=self._base(q)
            self._verify_base_checkpoint_locked(q,base)
            if base[4] is not None:
                m=q.execute("SELECT manifest_json FROM archives WHERE archive_id=?",(base[4],)).fetchone()
                if not m: raise ArchiveError("base references missing archive manifest")
                manifest=ArchiveManifest.parse(m[0])
                if manifest.history_id!=self.history_id(q):
                    raise ArchiveError("base/archive history identity mismatch")
                manifest_unsigned=asdict(manifest); manifest_unsigned.pop("archive_id")
                if sha(canon(manifest_unsigned))!=manifest.archive_id:
                    raise ArchiveError("archive manifest content identity mismatch")
                if (manifest.archive_id,manifest.end_sequence,manifest.end_root_id,manifest.end_recovery_id,
                    manifest.end_commitment)!=(base[4],base[0],base[1],base[2],base[3]):
                    raise ArchiveError("base/archive manifest mismatch")
            out=self._verify_suffix_locked(q)
            q.commit(); return out
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

    def create_checkpoint(self):
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            v=self._verify_suffix_locked(q)
            base=self._base(q)
            unsigned={"schema_version":SCHEMA,"protocol_version":PROTOCOL,"history_id":self.history_id(q),
                      "sequence":v["sequence"],"root_id":v["root_id"],"recovery_id":v["recovery_id"],
                      "prefix_commitment":v["prefix_commitment"],"base_sequence":base[0],
                      "base_archive_id":base[4],"external_anchor_id":self.anchor,"signer_id":self.signer_id}
            cp=CompactCheckpoint(**unsigned,signature=mac(self.key,unsigned))
            wm=q.execute("SELECT sequence,checkpoint_id FROM compact_checkpoint_watermark WHERE singleton=1").fetchone()
            if wm and cp.sequence<wm[0]: raise StaleCheckpoint("behind watermark")
            if wm and cp.sequence==wm[0]:
                raw=q.execute("SELECT body_json FROM compact_checkpoints WHERE checkpoint_id=?",(wm[1],)).fetchone()
                if not raw: raise AuthenticationError("missing checkpoint")
                old=CompactCheckpoint.parse(raw[0])
                if old.checkpoint_id!=cp.checkpoint_id: raise AuthenticationError("same-sequence substitution")
                q.commit(); return old
            body=json.dumps(asdict(cp),sort_keys=True,separators=(",",":"))
            q.execute("INSERT INTO compact_checkpoints VALUES(?,?,?)",(cp.checkpoint_id,cp.sequence,body))
            q.execute("""INSERT INTO compact_checkpoint_watermark VALUES(1,?,?)
              ON CONFLICT(singleton) DO UPDATE SET sequence=excluded.sequence,checkpoint_id=excluded.checkpoint_id""",
                      (cp.sequence,cp.checkpoint_id))
            q.commit(); return cp
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

    def _verify_checkpoint_locked(self,q,cp):
        cp=CompactCheckpoint.parse(asdict(cp))
        if cp.schema_version!=SCHEMA or cp.protocol_version!=PROTOCOL: raise AuthenticationError("version")
        if cp.history_id!=self.history_id(q) or cp.external_anchor_id!=self.anchor: raise AuthenticationError("history/anchor")
        if cp.signer_id!=self.signer_id or not hmac.compare_digest(mac(self.key,cp.unsigned),cp.signature):
            raise AuthenticationError("signature")
        wm=q.execute("SELECT sequence,checkpoint_id FROM compact_checkpoint_watermark WHERE singleton=1").fetchone()
        if wm is None: raise AuthenticationError("missing watermark")
        if cp.sequence<wm[0]: raise StaleCheckpoint("stale checkpoint")
        if (cp.sequence,cp.checkpoint_id)!=wm: raise AuthenticationError("watermark mismatch")
        raw=q.execute("SELECT body_json FROM compact_checkpoints WHERE checkpoint_id=?",(cp.checkpoint_id,)).fetchone()
        if not raw or CompactCheckpoint.parse(raw[0])!=cp: raise AuthenticationError("checkpoint persistence")
        base=self._base(q)
        if (cp.base_sequence,cp.base_archive_id)!=(base[0],base[4]): raise StaleCheckpoint("checkpoint base changed")
        derived=self._verify_suffix_locked(q,through_sequence=cp.sequence)
        if (derived["root_id"],derived["recovery_id"],derived["prefix_commitment"]) != (
            cp.root_id,cp.recovery_id,cp.prefix_commitment):
            raise AuthenticationError("checkpoint derived state")
        return cp
