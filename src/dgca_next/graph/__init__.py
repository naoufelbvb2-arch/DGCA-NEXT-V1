"""I1 sparse physical anatomy; fixture construction is not learning."""

from dgca_next.graph.audit import AuditReport, GraphInvariantError, validate_graph
from dgca_next.graph.cell import Cell
from dgca_next.graph.geometry import (
    Microcolumn,
    microcolumn_neighborhood,
    microcolumn_of,
    same_microcolumn,
)
from dgca_next.graph.latent import LatentSlot, SlotCategory, UnresolvedLatentPolicy
from dgca_next.graph.network import FixtureBuilder, MutationStage, SparseNetwork
from dgca_next.graph.synapse import Synapse, SynapseState, quality
from dgca_next.graph.transaction import FixtureTransaction, InjectedFailure

__all__ = [
    "Cell",
    "AuditReport",
    "FixtureBuilder",
    "FixtureTransaction",
    "GraphInvariantError",
    "InjectedFailure",
    "LatentSlot",
    "Microcolumn",
    "MutationStage",
    "SlotCategory",
    "SparseNetwork",
    "Synapse",
    "SynapseState",
    "UnresolvedLatentPolicy",
    "microcolumn_neighborhood",
    "microcolumn_of",
    "same_microcolumn",
    "quality",
    "validate_graph",
]
