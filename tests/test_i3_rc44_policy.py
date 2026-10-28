"""Pure RC4.4 policy checks; these do not mint external EVENT witnesses."""

from dataclasses import replace

import pytest

from dgca_next.contracts import Region
from dgca_next.dynamics.homeostasis import adapt
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph import FixtureBuilder, SparseNetwork
from dgca_next.learning.homeostasis_profile import (
    PROFILE_HASH,
    LanguageHomeostasis,
    preview_pre_event_adaptation,
)
from dgca_next.learning.observation import preflight


def draft(features, graph=None, *, salience="1"):
    graph = graph or GraphSnapshot.capture(SparseNetwork())
    h = LanguageHomeostasis.initial().overrides
    return preflight(graph, h, tuple(features), salience=salience)


def test_sensory_capacity_exact_ties_and_deferrals():
    result = draft((f, "1") for f in ("a", "ab", "c", "d"))
    assert [i for i, _ in result.accepted] == [
        8286,
        8465,
        8606,
        8649,
        8694,
        9227,
        9345,
        9902,
        9912,
        10128,
        10273,
        10513,
    ]
    assert [i for i, _ in result.deferred] == [11524, 11641, 11795, 12181]
    assert result.diagnostics == tuple(
        ("SENSORY_BIRTH_CAPACITY_DEFERRED", i) for i, _ in result.deferred
    )
    assert all(x == 1_000_000 for _, x in result.accepted + result.deferred)
    assert not hasattr(result, "witness_id")


def test_feature_reordering_nfc_and_duplicate_canonicalization():
    first = draft((("é", "0.5"), ("e\u0301", "0.5"), ("a", "1")))
    second = draft((("a", "1"), ("é", "0.5"), ("e\u0301", "0.5")))
    assert first == second and first.projection.digest == second.projection.digest
    assert len({i for i, _ in first.accepted}) == len(first.accepted)


def test_merged_support_controls_ranking_and_committed_exclusion():
    inputs = (("a", "0.2"), ("ab", "0.8"), ("c", "0.5"), ("d", "1"))
    initial = draft(inputs, salience="0.5")
    assert initial.accepted + initial.deferred == tuple(
        sorted(initial.eligible_uncommitted, key=lambda p: (-p[1], p[0]))
    )
    g = SparseNetwork()
    committed = tuple(i for i, _ in initial.accepted[:4])
    FixtureBuilder(g).commit_cells(committed, committed_event=0)
    later = draft(inputs, GraphSnapshot.capture(g), salience="0.5")
    assert {i for i, _ in later.previously_committed} == set(committed)
    assert not set(committed) & {i for i, _ in later.accepted}
    assert len(later.accepted) <= 12


def test_zero_and_strict_epsilon_cause_no_births():
    assert draft(()).accepted == ()
    assert draft((("a", "0.000001"),)).accepted == ()
    assert len(draft((("a", "0.000002"),)).accepted) == 4
    assert draft((("a", "1"),), salience="0").accepted == ()


@pytest.mark.parametrize("remaining", [0, 1, 8, 12, 13, 16])
def test_capacity_for_distinct_eligible_counts(remaining):
    features = (("a", "1"), ("ab", "1"), ("c", "1"), ("d", "1"))
    ids = tuple(i for i, _ in draft(features).eligible_uncommitted)
    g = SparseNetwork()
    FixtureBuilder(g).commit_cells(ids[: 16 - remaining], committed_event=0)
    result = draft(features, GraphSnapshot.capture(g))
    assert len(result.eligible_uncommitted) == remaining
    assert len(result.accepted) == min(12, remaining)
    assert len(result.deferred) == max(0, remaining - 12)


def test_profile_defaults_are_virtual_and_canonical():
    profile = LanguageHomeostasis.initial()
    raw = profile.encode()
    assert len(PROFILE_HASH) == 32
    h = profile.materialize(frozenset({8606, 9345}))
    assert h.gains == {8606: 1.0, 9345: 1.0}
    assert h.rates == {8606: 0.05, 9345: 0.05}
    assert h.thresholds == {Region.LANGUAGE: 0.20}
    assert h.region_rates == {Region.LANGUAGE: 0.030}
    assert profile.encode() == raw and LanguageHomeostasis.decode(raw) == profile


def test_sparse_prior_overrides_and_later_birth_do_not_reset_region():
    sparse = LanguageHomeostasis(
        Homeostasis({8606: 1.1}, {8606: 0.4}, {Region.LANGUAGE: 0.3}, {Region.LANGUAGE: 0.1})
    )
    saved = sparse.encode()
    expanded = sparse.materialize(frozenset({8606, 9345}))
    assert expanded.gains == {8606: 1.1, 9345: 1.0}
    assert expanded.rates == {8606: 0.4, 9345: 0.05}
    assert expanded.thresholds[Region.LANGUAGE] == 0.3
    assert expanded.region_rates[Region.LANGUAGE] == 0.1
    assert LanguageHomeostasis.decode(saved).encode() == saved
    with pytest.raises(ValueError, match="H_OVERRIDE_NOT_COMMITTED"):
        sparse.materialize(frozenset({9345}))


def test_virtual_defaults_feed_existing_pure_adaptation_without_mutating_profile():
    profile = LanguageHomeostasis.initial()
    before = profile.encode()
    graph = SparseNetwork()
    FixtureBuilder(graph).commit_cells([8606], committed_event=0)
    snapshot = GraphSnapshot.capture(graph)
    expanded = profile.materialize(snapshot.committed_ids)
    result = adapt(expanded, {8606: 0.8}, graph=snapshot)
    assert result.rates[8606] == (1 - 0.05) * 0.05 + 0.05
    assert profile.encode() == before
    assert LanguageHomeostasis(result).materialize(snapshot.committed_ids) == result
    preview = preview_pre_event_adaptation(profile, snapshot, {8606: 0.8})
    assert preview.materialize(snapshot.committed_ids) == result
    assert profile.encode() == before


def test_empty_population_preview_skips_adaptation_and_ignores_uncommitted_activity():
    profile = LanguageHomeostasis.initial()
    snapshot = GraphSnapshot.capture(SparseNetwork())
    assert preview_pre_event_adaptation(profile, snapshot, {8606: 0.8}) == profile


def test_corrupt_profile_and_unsupported_region_fail_closed():
    raw = LanguageHomeostasis.initial().encode()
    with pytest.raises(ValueError, match="UNSUPPORTED_H_PROFILE"):
        LanguageHomeostasis.decode(raw[:10] + bytes([raw[10] ^ 1]) + raw[11:])
    with pytest.raises(ValueError):
        LanguageHomeostasis.decode(raw[:-1])
    with pytest.raises(ValueError, match="UNSUPPORTED_H_REGION"):
        LanguageHomeostasis.initial().materialize(frozenset({0}))
    with pytest.raises(ValueError, match="INCOMPLETE_H_OVERRIDE"):
        replace(
            LanguageHomeostasis.initial(),
            overrides=Homeostasis({8606: 1.0}, {}, {Region.LANGUAGE: 0.2}, {Region.LANGUAGE: 0.03}),
        )
