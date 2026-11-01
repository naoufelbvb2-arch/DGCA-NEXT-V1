"""P00 read-only RootStore inspection; no close hook, codec or graph writer."""

import hashlib
from dataclasses import dataclass
from itertools import combinations

from dgca_next.contracts import Region, SynapseScope
from dgca_next.graph.assembly_support import ReciprocalPairDiagnostic, _pair
from dgca_next.graph.cell import nonnegative_integer
from dgca_next.graph.merge_split_analysis import MergeMath, SplitMath, analyze_merge, analyze_split
from dgca_next.graph.native_lifecycle import parameter
from dgca_next.persistence.native_store import NativeLifecycleRootStore, NativeRootStore
from dgca_next.persistence.store import RootStore

COOLDOWN_DECISION = "I4-R04-COOLDOWN-SPEC_DECISION_REQUIRED"


@dataclass(frozen=True, slots=True)
class CompletedRootClock:
    root_id: int
    close_serial: int
    event_count: int
    cumulative_completed_events: int


@dataclass(frozen=True, slots=True)
class CooldownAlternatives:
    last_close_reference: int | None
    elapsed_roots: int | None
    elapsed_events: int | None
    roots_interpretation_passes: bool | None
    events_interpretation_passes: bool | None
    status: str


def cooldown_alternatives(
    history: tuple[CompletedRootClock, ...], last_close: int | None
) -> CooldownAlternatives:
    """A close timestamp can index an event prefix; do not choose its unit."""
    events = 0
    last_root = -1
    prefixes = {0: 0}
    for serial, row in enumerate(history, 1):
        if (
            type(row) is not CompletedRootClock
            or type(row.event_count) is not int
            or row.event_count < 1
            or row.close_serial != serial
            or row.root_id <= last_root
        ):
            raise ValueError("INVALID_COMPLETED_CLOCK_HISTORY")
        events += row.event_count
        if row.cumulative_completed_events != events:
            raise ValueError("INVALID_COMPLETED_EVENT_PREFIX")
        prefixes[serial] = events
        last_root = row.root_id
    if last_close is None:
        return CooldownAlternatives(None, None, None, None, None, "NOT_PREVIOUSLY_EDITED")
    nonnegative_integer(last_close, "last_close")
    if last_close not in prefixes:
        raise ValueError("UNKNOWN_COMPLETED_CLOSE_REFERENCE")
    roots_delta, events_delta = len(history) - last_close, events - prefixes[last_close]
    threshold = int(parameter("T_c"))
    return CooldownAlternatives(
        last_close,
        roots_delta,
        events_delta,
        roots_delta >= threshold,
        events_delta >= threshold,
        COOLDOWN_DECISION,
    )


@dataclass(frozen=True, slots=True)
class NativeIdentitySnapshot:
    assembly_id: int
    generation: int
    members: tuple[int, ...]
    birth_close_serial: int
    last_mutation_close_serial: int
    last_merge_split_close_serial: int | None


@dataclass(frozen=True, slots=True)
class NativeMergeInspection:
    first: NativeIdentitySnapshot
    second: NativeIdentitySnapshot
    numbers: MergeMath
    cooldown: tuple[CooldownAlternatives, CooldownAlternatives]
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NativeSplitInspection:
    identity: NativeIdentitySnapshot
    numbers: SplitMath
    cooldown: CooldownAlternatives
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReachabilityInspection:
    source_kind: str
    W_sha256: str
    H_sha256: str
    R_sha256: str
    completed_closes: int
    clock_history: tuple[CompletedRootClock, ...]
    aborted_event_count: int
    open_event_count: int
    identities: tuple[NativeIdentitySnapshot, ...]
    pairs: tuple[ReciprocalPairDiagnostic, ...]
    merges: tuple[NativeMergeInspection, ...]
    splits: tuple[NativeSplitInspection, ...]
    merge_status: str
    split_status: str
    cooldown_policy_status: str = COOLDOWN_DECISION

    @property
    def mutation_authorized(self) -> bool:
        return False


def inspect_reachability(
    store: RootStore, *, merge_ids: tuple[int, int] | None = None, split_id: int | None = None
) -> ReachabilityInspection:
    """Only journal-validated actual LIVE IDs may be production subjects."""
    if type(store) is not RootStore or type(store._backend) not in (
        NativeRootStore,
        NativeLifecycleRootStore,
    ):
        raise ValueError("NATIVE_ROOTSTORE_REQUIRED")
    backend = store._backend
    with backend._read_snapshot():
        backend._validate()
        metadata = backend._metadata()
        graph = backend._decode_graph(metadata[8])
        graph.validate_graph()
        identities = tuple(
            NativeIdentitySnapshot(
                r.assembly_id,
                r.structural_generation,
                r.member_cell_ids,
                r.birth_close_serial,
                r.last_mutation_close_serial,
                r.last_merge_split_close_serial,
            )
            for r in graph.native_assemblies()
            if r.status == "LIVE"
        )
        live = {a.assembly_id: a for a in identities}
        if merge_ids is not None and (
            type(merge_ids) is not tuple
            or len(merge_ids) != 2
            or any(type(i) is not int or i not in live for i in merge_ids)
            or merge_ids[0] >= merge_ids[1]
        ):
            raise ValueError("ACTUAL_DISTINCT_LIVE_IDS_REQUIRED")
        if split_id is not None and (type(split_id) is not int or split_id not in live):
            raise ValueError("ACTUAL_LIVE_ID_REQUIRED")
        clock = []
        aborted = opened = event_total = 0
        rows = backend._connection.execute(
            "SELECT exposure_id,status,next_order,close_serial,close_record "
            "FROM p01_roots ORDER BY exposure_id"
        ).fetchall()
        for root, status, count, serial, raw in rows:
            if status == "COMPLETED":
                event_total += count
                close = backend._decode_close(raw)
                if close.event_clock != event_total:
                    raise ValueError("INVALID_COMPLETED_EVENT_CLOCK")
                clock.append(CompletedRootClock(root, serial, count, event_total))
            elif status == "ABORTED":
                aborted += count
            else:
                opened += count
        history = tuple(clock)
        cooldown_alternatives(history, None)
        keys = sorted(
            {
                tuple(sorted((s.key.source.cell_id, s.key.target.cell_id)))
                for s in graph.synapses()
                if s.key.scope is SynapseScope.LOCAL
                and s.key.source.region is s.key.target.region is Region.LANGUAGE
            }
        )
        pairs = tuple(_pair(graph, i, j, False) for i, j in keys)
        supports: dict[int, dict[int, float]] = {}
        for pair in pairs:
            if pair.forward.reason == pair.reverse.reason == "QUALIFIED":
                supports.setdefault(pair.first, {})[pair.second] = pair.support
                supports.setdefault(pair.second, {})[pair.first] = pair.support
        counts = {c.cell_id: len(c.assembly_ids) for c in graph.stored_cells()}
        merges = []
        selected_pairs = (
            (merge_ids,) if merge_ids is not None else tuple(combinations(sorted(live), 2))
        )
        for first, second in selected_pairs:
            a, b = live[first], live[second]
            numbers = analyze_merge(a.members, b.members, supports, membership_counts=counts)
            timers = (
                cooldown_alternatives(history, a.last_merge_split_close_serial),
                cooldown_alternatives(history, b.last_merge_split_close_serial),
            )
            reasons = (
                *numbers.reasons,
                *(
                    (COOLDOWN_DECISION,)
                    if any(t.status == COOLDOWN_DECISION for t in timers)
                    else ()
                ),
            )
            merges.append(NativeMergeInspection(a, b, numbers, timers, reasons))
        splits = []
        for identity in identities:
            if split_id is not None and identity.assembly_id != split_id:
                continue
            numbers_split = analyze_split(identity.members, supports, membership_counts=counts)
            timer = cooldown_alternatives(history, identity.last_merge_split_close_serial)
            reasons_split = (
                *numbers_split.reasons,
                *((COOLDOWN_DECISION,) if timer.status == COOLDOWN_DECISION else ()),
            )
            splits.append(NativeSplitInspection(identity, numbers_split, timer, reasons_split))
        return ReachabilityInspection(
            "PRODUCTION_ROOTSTORE_SNAPSHOT",
            hashlib.sha256(metadata[8]).hexdigest(),
            hashlib.sha256(metadata[6]).hexdigest(),
            hashlib.sha256(metadata[7]).hexdigest(),
            len(history),
            history,
            aborted,
            opened,
            identities,
            pairs,
            tuple(merges),
            tuple(splits),
            "MERGE_NOT_APPLICABLE" if not merges else "MERGE_ANALYZED_ONLY",
            "SPLIT_NOT_APPLICABLE"
            if not splits or all(s.numbers.examined == 0 for s in splits)
            else "SPLIT_ANALYZED_ONLY",
        )
