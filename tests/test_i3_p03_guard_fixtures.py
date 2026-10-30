"""Isolated guard mechanics; these fixtures are not production novelty evidence."""

from dataclasses import replace
from types import MappingProxyType

import pytest

from dgca_next.graph.latent import LATENT_POLICY_VERSION, SlotAssignment
from dgca_next.learning.novelty import _inspect_recycling


@pytest.mark.parametrize(
    ("guard", "expected"),
    [
        ("pin", "RECYCLE_BLOCKED_CANDIDATE"),
        ("protected", "RECYCLE_BLOCKED_LIVE_OR_PROTECTED"),
        ("reserved", "RECYCLE_BLOCKED_LIVE_OR_PROTECTED"),
    ],
)
def test_reverse_occurrence_guards_are_bilateral(graph_pair, key_factory, guard, expected):
    graph, builder = graph_pair
    builder.inject_slot(8193, 0, 8192)
    if guard == "pin":
        builder.pin_slot(8193, 0, 8192)
    elif guard == "protected":
        builder.protect_slot(8193, 0)
    else:
        builder.reserve(key_factory(8193, 8192), 8193)
    before = graph.structural_hash
    decision = _inspect_recycling(graph, 0, 8192, 0, None, None, 0)
    assert decision.reason == expected
    assert len(decision.occurrences) == 2
    assert decision.replacements == ()
    assert graph.structural_hash == before


def test_one_sided_occurrence_is_inspected_without_inventing_a_reverse_slot(graph_pair):
    graph, _ = graph_pair
    before = graph.structural_hash
    decision = _inspect_recycling(graph, 0, 8192, 0, None, None, 0)
    assert len(decision.occurrences) == 1
    assert decision.reason == "CONFIRMATION_WINDOW_NOT_ELAPSED"
    assert decision.replacements == ()
    assert graph.structural_hash == before


def test_one_recent_reverse_assignment_blocks_both_sides(graph_pair):
    # Simulated ages exercise only the pure guard; the production age trial
    # separately creates all 100 completed external roots through RootStore.
    graph, builder = graph_pair
    builder.inject_slot(8193, 0, 8192)
    slots = dict(graph._state.slots)
    for owner, serial in ((8192, 0), (8193, 1)):
        assignment = SlotAssignment(serial, 1, 1, 0, True, LATENT_POLICY_VERSION)
        layout = slots[owner]
        slots[owner] = (replace(layout[0], assignment=assignment), *layout[1:])
    graph._state = replace(graph._state, slots=MappingProxyType(slots))
    before = graph.structural_hash
    decision = _inspect_recycling(graph, 100, 8192, 0, None, None, 0)
    assert [occurrence.age for occurrence in decision.occurrences] == [100, 99]
    assert decision.reason == "CONFIRMATION_WINDOW_NOT_ELAPSED"
    assert decision.replacements == ()
    assert graph.structural_hash == before
