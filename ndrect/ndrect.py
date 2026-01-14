"""N-dimensional rectangles."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from types import MappingProxyType
from typing import override

from attrs import define, field

from ndrect._is_aligned import IsAligned
from ndrect._is_sequenceable import IsSequenceable
from ndrect._typing import DimensionLength, DimensionName


@define(repr=False)
class NDRect(IsSequenceable, IsAligned):
    """An n-dim rectangle defined by its shape."""

    shape: Mapping[DimensionName, DimensionLength] = field(
        converter=lambda _: MappingProxyType(deepcopy(_)),
    )

    @override
    def __repr__(self) -> str:
        return f"/{str(self.shape)[1:-1]}/"

    @override
    def __hash__(self) -> int:
        # To make NDRect hashable, we hash its shape by expanding the mapping
        # into a sorted tuple of items.
        return hash(tuple(sorted(self.shape.items())))
