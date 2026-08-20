import json
import tempfile
import unittest
from pathlib import Path

from experiments.ctv2_bundle_replica_convergence.protocol import (
    AuthenticatedHistory,
    BundleEvent,
    DuplicateReplicaIdentity,
    Replica,
    ReplicaStore,
    RollbackError,
    RootEvent,
    SplitViewDetected,
    UnknownReplica,
    ViewPolicy,
    key_id,
    make_view,
)

ROOT_KEY = b"root-authority"
ALT_ROOT_KEY = b"unauthorized-root-authority"
BUNDLE1 = b"bundle-one"
BUNDLE2 = b"bundle-two"
ROOT_KEYS = {key_id(ROOT_KEY): ROOT_KEY, key_id(ALT_ROOT_KEY): ALT_ROOT_KEY}
BUNDLE_KEYS = {key_id(BUNDLE1): BUNDLE1, key_id(BUNDLE2): BUNDLE2}


def bootstrap():
    r1 = RootEvent.issue(
        provider_id="provider-A", version=1, epoch=1, predecessor_root=None,
        root_material_digest="root-material-1", root_key=ROOT_KEY, bundle_key=BUNDLE1,
    )
    b1 = BundleEvent.issue(
        bundle_id="bundle-A", version=1, generation=1,
        root_event_id=r1.event_id, predecessor_bundle=None,
        payload_digest="payload-1", bundle_key=BUNDLE1,
    )
    return AuthenticatedHistory(root_keys=ROOT_KEYS, bundle_keys=BUNDLE_KEYS, events=[r1, b1])


def bundle_successor(history, payload="payload-next"):
    current = history.validate()
    root_event = next(e for e in reversed(history.events) if isinstance(e, RootEvent))
    prior_bundle = next(e for e in reversed(history.events) if isinstance(e, BundleEvent))
    key = BUNDLE1 if root_event.bundle_signer_id == key_id(BUNDLE1) else BUNDLE2
    return BundleEvent.issue(
        bundle_id="bundle-A", version=current.bundle_version + 1,
        generation=current.bundle_generation + 1, root_event_id=root_event.event_id,
        predecessor_bundle=prior_bundle.event_id, payload_digest=payload, bundle_key=key,
    )


def root_successor(history, material, bundle_key=BUNDLE2, epoch=None):
    current_root = next(e for e in reversed(history.events) if isinstance(e, RootEvent))
    return RootEvent.issue(
        provider_id=current_root.provider_id, version=current_root.version + 1,
        epoch=current_root.epoch if epoch is None else epoch,
        predecessor_root=current_root.event_id, root_material_digest=material,
        root_key=ROOT_KEY, bundle_key=bundle_key,
    )


class ReplicaConvergenceTests(unittest.TestCase):
    def test_same_head_converges_trivially(self):
        h = bootstrap()
        a, b = Replica(replica_id="a", history=h.copy()), Replica(replica_id="b", history=h.copy())
        self.assertEqual(a.exchange(b), "SAME")
        self.assertEqual(a.head.head_id, b.head.head_id)

    def test_stale_replica_catches_up_through_authenticated_prefix(self):
        old = bootstrap()
        new = old.copy(); new.append(bundle_successor(new))
        a, b = Replica(replica_id="a", history=old), Replica(replica_id="b", history=new)
        self.assertEqual(a.exchange(b), "CAUGHT_UP_SELF")
        self.assertEqual(a.head.head_id, b.head.head_id)

    def test_rollback_is_rejected_for_current_service(self):
        current = bootstrap(); current.append(bundle_successor(current))
        replica = Replica(replica_id="a", history=current)
        stale = bootstrap()
        with self.assertRaises(RollbackError):
            replica.receive(stale)
        self.assertEqual(replica.head.history_length, 3)
        self.assertEqual(stale.validate().history_length, 2)

    def test_same_predecessor_root_successors_detect_equivocation(self):
        base = bootstrap(); left, right = base.copy(), base.copy()
        left.append(root_successor(left, "root-left")); right.append(root_successor(right, "root-right"))
        with self.assertRaises(SplitViewDetected) as ctx:
            Replica(replica_id="a", history=left).exchange(Replica(replica_id="b", history=right))
        details = json.loads(str(ctx.exception))
        self.assertEqual(details["left_kind"], "root")
        self.assertTrue(details["same_predecessor"])

    def test_same_root_divergent_bundle_successors_detected(self):
        base = bootstrap(); left, right = base.copy(), base.copy()
        left.append(bundle_successor(left, "payload-left")); right.append(bundle_successor(right, "payload-right"))
        with self.assertRaises(SplitViewDetected) as ctx:
            Replica(replica_id="a", history=left).exchange(Replica(replica_id="b", history=right))
        details = json.loads(str(ctx.exception))
        self.assertEqual(details["left_kind"], "bundle")
        self.assertTrue(details["same_predecessor"])

    def test_restart_preserves_watermark_and_head(self):
        with tempfile.TemporaryDirectory() as td:
            history = bootstrap(); history.append(bundle_successor(history))
            store = ReplicaStore(Path(td) / "replica.json")
            original = Replica(replica_id="a", history=history, store=store)
            restarted = Replica.restart(store=store, root_keys=ROOT_KEYS, bundle_keys=BUNDLE_KEYS)
            self.assertEqual(restarted.replica_id, "a")
            self.assertEqual(restarted.head.head_id, original.head.head_id)

    def test_split_view_is_only_detected_after_views_meet(self):
        base = bootstrap(); left, right = base.copy(), base.copy()
        left.append(bundle_successor(left, "left")); right.append(bundle_successor(right, "right"))
        a, b = Replica(replica_id="a", history=left), Replica(replica_id="b", history=right)
        self.assertNotEqual(a.head.head_id, b.head.head_id)
        with self.assertRaises(SplitViewDetected):
            a.exchange(b)

    def test_duplicate_replica_identity_does_not_inflate_quorum(self):
        h = bootstrap(); a = Replica(replica_id="a", history=h.copy())
        keys = {"a": b"replica-a", "b": b"replica-b"}
        view = make_view(a, keys["a"])
        with self.assertRaises(UnknownReplica):
            ViewPolicy(keys, threshold=2).verify([view, view])

    def test_conflicting_same_replica_identity_is_rejected(self):
        base = bootstrap(); left, right = base.copy(), base.copy()
        left.append(bundle_successor(left, "left")); right.append(bundle_successor(right, "right"))
        with self.assertRaises(DuplicateReplicaIdentity):
            Replica(replica_id="same", history=left).exchange(Replica(replica_id="same", history=right))

    def test_authenticated_but_unauthorized_root_signer_cannot_extend_lineage(self):
        h = bootstrap()
        current = next(e for e in reversed(h.events) if isinstance(e, RootEvent))
        unauthorized = RootEvent.issue(
            provider_id=current.provider_id, version=2, epoch=1,
            predecessor_root=current.event_id, root_material_digest="evil-root",
            root_key=ALT_ROOT_KEY, bundle_key=BUNDLE2,
        )
        with self.assertRaises(Exception):
            h.append(unauthorized)

    def test_bundle_cannot_advance_across_root_boundary_without_root_transition(self):
        base = bootstrap(); r2 = root_successor(base, "root-2", BUNDLE2)
        prior = next(e for e in reversed(base.events) if isinstance(e, BundleEvent))
        forged = BundleEvent.issue(
            bundle_id="bundle-A", version=2, generation=2, root_event_id=r2.event_id,
            predecessor_bundle=prior.event_id, payload_digest="new-root-payload", bundle_key=BUNDLE2,
        )
        with self.assertRaises(Exception):
            base.append(forged)

    def test_valid_root_transition_then_bundle_advances(self):
        h = bootstrap(); r2 = root_successor(h, "root-2", BUNDLE2); h.append(r2)
        prior = next(e for e in reversed(h.events) if isinstance(e, BundleEvent))
        b2 = BundleEvent.issue(
            bundle_id="bundle-A", version=2, generation=2, root_event_id=r2.event_id,
            predecessor_bundle=prior.event_id, payload_digest="payload-2", bundle_key=BUNDLE2,
        )
        head = h.append(b2)
        self.assertEqual(head.root_version, 2)
        self.assertEqual(head.bundle_version, 2)

    def test_evidence_quorum_requires_distinct_authenticated_replica_ids(self):
        h = bootstrap(); a, b = Replica(replica_id="a", history=h.copy()), Replica(replica_id="b", history=h.copy())
        keys = {"a": b"replica-a", "b": b"replica-b"}
        verified = ViewPolicy(keys, 2).verify([make_view(a, keys["a"]), make_view(b, keys["b"])])
        self.assertEqual(verified, ("a", "b"))

    def test_convergence_is_not_consensus_prevention(self):
        base = bootstrap(); left, right = base.copy(), base.copy()
        left.append(root_successor(left, "fork-left")); right.append(root_successor(right, "fork-right"))
        self.assertEqual(left.validate().root_version, 2)
        self.assertEqual(right.validate().root_version, 2)
        self.assertNotEqual(left.validate().root_event_id, right.validate().root_event_id)


if __name__ == "__main__":
    unittest.main()
