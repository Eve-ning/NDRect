"""N-dimensional rectangles."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from types import MappingProxyType
from typing import TYPE_CHECKING, override

from attrs import define, field

from ndrect._is_aligned import IsAligned
from ndrect._typing import DimensionLength, DimensionName

if TYPE_CHECKING:
    from ndrect.ndrect_complex import NDRectComplex


@define(repr=False)
class NDRect(IsAligned["NDRect", "NDRectComplex"]):
    """An n-dim rectangle defined by its shape."""

    shape: Mapping[DimensionName, DimensionLength] = field(
        converter=lambda _: MappingProxyType(deepcopy(_)),
    )

    @property
    @override
    def _singular_type(self) -> type[NDRect]:
        return NDRect

    @property
    @override
    def _complex_type(self) -> type[NDRectComplex]:
        from ndrect.ndrect_complex import NDRectComplex

        return NDRectComplex

    @override
    def __repr__(self) -> str:
        return f"/{str(self.shape)[1:-1]}/"

    @override
    def __hash__(self) -> int:
        # To make NDRect hashable, we hash its shape by expanding the mapping
        # into a sorted tuple of items.
        return hash(tuple(sorted(self.shape.items())))

    def __pos__(self):
        return self._complex_type(rects=self._as_sequence_object())
