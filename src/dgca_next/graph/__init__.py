"""I1 sparse physical anatomy; fixture construction is not learning."""

from dgca_next.graph.cell import Cell
from dgca_next.graph.geometry import (
    Microcolumn,
    microcolumn_neighborhood,
    microcolumn_of,
    same_microcolumn,
)
from dgca_next.graph.latent import LatentSlot, SlotCategory, UnresolvedLatentPolicy
from dgca_next.graph.network import FixtureBuilder, SparseNetwork

__all__ = [
    "Cell",
    "FixtureBuilder",
    "LatentSlot",
    "Microcolumn",
    "SlotCategory",
    "SparseNetwork",
    "UnresolvedLatentPolicy",
    "microcolumn_neighborhood",
    "microcolumn_of",
    "same_microcolumn",
]
