"""Private production sensory graph shadow. This module creates no synapses."""

from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType

from dgca_next.contracts import CellAddress, Region
from dgca_next.graph.audit import validate_state
from dgca_next.graph.cell import Cell, ProductionAdmission
from dgca_next.graph.latent import LATENT_POLICY_VERSION, SlotAssignment, empty_slots
from dgca_next.graph.network import SparseNetwork, _State
from dgca_next.graph.policy import InitializationRecord, local_targets, q6, topographic_targets


def _admit_sensory_cohort(
    network: SparseNetwork,
    *,
    admission: ProductionAdmission,
    born: tuple[tuple[int, int], ...],
    frontier: Mapping[int, float],
    completed_closes: int,
) -> SparseNetwork:
    """Construct one audited shadow. Authority comes from the caller's root journal."""
    if type(network) is not SparseNetwork or type(admission) is not ProductionAdmission:
        raise ValueError("INVALID_PRODUCTION_ADMISSION")
    network.validate_graph()
    base = network._state
    if any(c.fixture_only for c in base.cells.values()) or base.synapses or base.reservations:
        raise ValueError("NONPRODUCTION_GRAPH")
    ids = tuple(i for i, _ in born)
    if len(ids) > 12 or len(set(ids)) != len(ids) or any(i in base.cells for i in ids):
        raise ValueError("INVALID_PRODUCTION_COHORT")
    if any(
        CellAddress.from_cell_id(i).region is not Region.LANGUAGE
        or type(value) is not int
        or not 1 < value <= 1_000_000
        for i, value in born
    ):
        raise ValueError("INVALID_PRODUCTION_RECEIVER")
    if any(i not in base.cells for i in frontier):
        raise ValueError("UNCOMMITTED_PRODUCTION_FRONTIER")
    scores = {i: q6(value) for i, value in frontier.items()}
    scores.update({i: q6(value / 1_000_000) for i, value in born})
    assignment = SlotAssignment(
        completed_closes,
        admission.exposure_id,
        admission.event_id,
        admission.event_order,
        True,
        LATENT_POLICY_VERSION,
        False,
        admission,
    )
    cells, slots, reverse = dict(base.cells), dict(base.slots), dict(base.reverse)
    initializations = dict(base.initializations)
    wiring = list(base.wiring_log)
    for owner in sorted(ids):
        cells[owner] = Cell(
            CellAddress.from_cell_id(owner), True, admission.event_id, False, frozenset(), admission
        )
    for owner in sorted(ids):
        address = CellAddress.from_cell_id(owner)
        layout = list(empty_slots(address.region))
        selected = {owner}
        local = local_targets(owner, frozenset(selected))
        selected.update(local)
        topo = topographic_targets(owner, frozenset(selected))
        selected.update(topo)
        for index, target in zip((*range(6, 12), *range(18, 24)), local + topo, strict=True):
            layout[index] = replace(layout[index], target_id=target, assignment=assignment)
        for slot in layout:
            if not slot.recyclable_category:
                continue
            candidates = sorted(
                (i for i in scores if CellAddress.from_cell_id(i).region is slot.permitted_region),
                key=lambda i: (-scores[i], i),
            )
            chosen = next((i for i in candidates if i not in selected), None)
            if chosen is not None:
                selected.add(chosen)
                layout[slot.index] = replace(slot, target_id=chosen, assignment=assignment)
        slots[owner] = tuple(layout)
        for slot in layout:
            if slot.target_id is not None:
                reverse[slot.target_id] = reverse.get(slot.target_id, frozenset()) | {
                    (owner, slot.index)
                }
                wiring.append((owner, slot.index, -1, slot.target_id))
        initializations[owner] = InitializationRecord(
            owner, admission.observation_digest, False, (), assignment, LATENT_POLICY_VERSION
        )
    state = _State(
        cells=MappingProxyType(cells),
        slots=MappingProxyType(slots),
        reverse=MappingProxyType(reverse),
        synapses=base.synapses,
        reservations=base.reservations,
        outgoing=base.outgoing,
        wiring_log=tuple(wiring),
        initializations=MappingProxyType(initializations),
        recycling_log=base.recycling_log,
    )
    validate_state(state)
    result = SparseNetwork()
    result._state = state
    return result
