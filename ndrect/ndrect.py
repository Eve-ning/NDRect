"""N-dimensional rectangles."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from types import MappingProxyType
from typing import TYPE_CHECKING, override

from attrs import define, field

from ndrect._ndrect_base import NDRectBase
from ndrect._typing import DimensionLength, DimensionName

if TYPE_CHECKING:
    from ndrect.ndrect_complex import NDRectComplex


@define(repr=False)
class NDRect[TSingular: NDRect, TComplex: NDRectComplex](
    NDRectBase[TSingular, TComplex]
):
    """An n-dim rectangle defined by its shape."""

    shape: Mapping[DimensionName, DimensionLength] = field(
        converter=lambda _: MappingProxyType(deepcopy(_)),
    )

    @property
    @override
    def _singular_type(self) -> type[TSingular]:
        return NDRect

    @property
    @override
    def _complex_type(self) -> type[TComplex]:
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
