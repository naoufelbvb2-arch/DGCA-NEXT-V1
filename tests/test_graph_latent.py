from collections import Counter

import pytest

from dgca_next.contracts import Region
from dgca_next.graph import SlotCategory, SparseNetwork, UnresolvedLatentPolicy


@pytest.mark.parametrize("region", Region)
def test_i1_t04_slot_schema(region):
    slots = SparseNetwork().latent_slots(4096 * region.value)
    assert tuple(s.index for s in slots) == tuple(range(24))
    assert Counter(s.category for s in slots) == dict.fromkeys(SlotCategory, 6)
    assert all(s.target_id is None and not s.protected and not s.pinned for s in slots)
    assert all(s.permitted_region is region for s in slots[:12])
    for category in (SlotCategory.COACTIVE_INTER, SlotCategory.TOPOGRAPHIC):
        counts = Counter(s.permitted_region for s in slots if s.category is category)
        assert counts == {other: 3 for other in Region if other is not region}
    assert [s.recyclable_category for s in slots] == [True] * 6 + [False] * 6 + [True] * 6 + [
        False
    ] * 6


def test_i1_t26_unresolved_policy_fails_closed_without_mutation():
    graph = SparseNetwork()
    with pytest.raises(UnresolvedLatentPolicy, match="UNRESOLVED_LATENT_POLICY"):
        graph.initialize_latent_neighborhoods()
    assert graph.stored_cell_count == 0
