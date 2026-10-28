"""I3-R02 ingress preflight; no observation here is an evidence witness."""

from dataclasses import replace

import pytest

from dgca_next.contracts import Region
from dgca_next.dynamics.numeric import SpecBlocked
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph import SparseNetwork
from dgca_next.learning.observation import preflight
from dgca_next.peripheral.sic import project


def explicit_fixture_H(cells):
    return Homeostasis(
        {i: 1.0 for i in cells},
        {i: 0.0 for i in cells},
        {Region.LANGUAGE: 0.2},
        {Region.LANGUAGE: 0.03},
    )


def test_all_sixteen_qualify_but_capacity_selection_is_unspecified():
    graph = GraphSnapshot.capture(SparseNetwork())
    features = tuple((f, "1") for f in ("a", "ab", "c", "d"))
    p = project(features)
    assert len(p.X_fixed) == 16 and all(u == 1_000_000 for _, u in p.X_fixed)
    h = explicit_fixture_H(i for i, _ in p.X_fixed)
    with pytest.raises(SpecBlocked, match="I3-S01"):
        preflight(graph, h, features)
    assert not graph.committed_ids and not graph.synapses()


def test_newborn_homeostasis_must_be_explicit_and_draft_not_an_admission():
    graph = GraphSnapshot.capture(SparseNetwork())
    p = project((("a", "1"),))
    with pytest.raises(SpecBlocked, match="I3-S02"):
        preflight(graph, explicit_fixture_H(()), (("a", "1"),))
    h = explicit_fixture_H(tuple(i for i, _ in p.X_fixed))
    draft = preflight(graph, h, (("a", "1"),))
    assert draft.eligible_uncommitted == p.X_fixed
    assert not draft.previously_committed and not graph.committed_ids
    assert not hasattr(draft, "witness_id") and not hasattr(draft, "exposure_id")


def test_exact_admission_epsilon_and_separate_salience():
    graph = GraphSnapshot.capture(SparseNetwork())
    h = explicit_fixture_H(())
    result = preflight(graph, h, (("a", "0.000001"),))
    assert result.projection.X_fixed and result.eligible_uncommitted == ()
    with pytest.raises(SpecBlocked, match="I3-S02"):
        preflight(graph, h, (("a", "0.000002"),))
    assert preflight(graph, h, (("a", "1"),), salience="0").eligible_uncommitted == ()


def test_reject_forged_graph_or_invalid_input_without_side_effects():
    network = SparseNetwork()
    graph = GraphSnapshot.capture(network)
    h = explicit_fixture_H(())
    before = network.structural_hash
    with pytest.raises(ValueError, match="UNVERIFIED_GRAPH_SNAPSHOT"):
        preflight(replace(graph, structural_hash="fake"), h, ())
    with pytest.raises(ValueError):
        preflight(graph, h, (("a", "NaN"),))
    with pytest.raises(ValueError):
        preflight(graph, h, (("\ud800", "1"),))
    assert network.structural_hash == before
