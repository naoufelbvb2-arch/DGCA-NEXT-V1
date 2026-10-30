"""One-sided production recycling using genuine external roots only."""

from pathlib import Path

from dgca_next.persistence.store import RootStore

ROOT = Path(__file__).resolve().parents[2]


def test_one_sided_actual_replacement_does_not_create_a_reverse_occurrence(tmp_path):
    path = tmp_path / "one-sided.sqlite"
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    store.begin(1)
    first = store.event(1, 0, (("a", "1"),)).born
    store.end(1)
    store.begin(2)
    second = store.event(2, 0, (("a", "1"), ("ab", "1"))).born
    store.end(2)
    graph = store.graph()
    eligible = [
        (source, slot.index, slot.target_id)
        for source in second
        for slot in graph.latent_slots(source)
        if slot.recyclable_category
        and slot.target_id in first
        and not any(s.target_id == source for s in graph.latent_slots(slot.target_id))
    ]
    source, index, old = min(eligible)
    assert old is not None
    for root in range(3, 102):
        store.begin(root)
        store.event(root, 0, (("a", "0.000001"),))
        store.end(root)
    assert store.view().completed_closes == 101
    store.begin(102)
    store.event(102, 0, (("a", "0.2"), ("ac", "1")))
    store.request_recycling(102, 0, source, index)
    store.end(102)
    assert store.recycling_request(102)[-1] == "RECYCLED"
    graph = store.graph()
    changes = graph.recycling_log()[-1].changes
    assert len(changes) == 1 and changes[0][:3] == (source, index, old)
    assert (source, index) not in graph.reverse_latent(old)
    assert not any(slot.target_id == source for slot in graph.latent_slots(old))
    new = changes[0][3]
    assert (source, index) in graph.reverse_latent(new)
    store.close()
    store = RootStore(path, repository_root=ROOT, code_revision="a" * 40)
    assert store.graph().recycling_log()[-1].changes == changes
    store.close()
