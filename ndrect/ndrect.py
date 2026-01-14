"""N-dimensional rectangles."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from copy import deepcopy
from types import MappingProxyType
from typing import TYPE_CHECKING, override

from attrs import define, field

from ndrect._is_aligned import IsAligned
from ndrect._is_sequenceable import IsSequenceable
from ndrect._typing import DimensionLength, DimensionName

if TYPE_CHECKING:
    from ndrect.ndrect_complex import NDRectComplex


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


@define(repr=False, frozen=True)
class NDRectComplexUnaligned(IsSequenceable, Sequence):
    """Unaligned complex n-dim rectangle of multiple rectangles in sequence."""

    rects: Sequence[NDRect | NDRectComplex] = field(converter=tuple)

    def along(self, align_dim: DimensionName) -> NDRectComplex:
        """Aligns this along a dimension to create a NDRectComplex.

        Args:
            align_dim: The dimension name along which to align the rectangles.

        Returns:
            A new :class:`NDRectComplex` aligned along the specified dimension.

        """
        from ndrect.ndrect_complex import NDRectComplex

        return NDRectComplex(rects=self, align_dim=align_dim)

    @override
    def __repr__(self) -> str:
        return "(" + "+".join(repr(e) for e in self.rects) + "@D?)"

    @override
    def __getitem__(self, item: int) -> NDRect | NDRectComplex:
        return self.rects[item]

    @override
    def __len__(self) -> int:
        return len(self.rects)

    @override
    def __iter__(self) -> Iterator[NDRect | NDRectComplex]:
        yield from self.rects

    def __matmul__(self, align_dim: int) -> NDRectComplex:
        """Shorthand for :meth:`along`.

        Aligning the complex rectangle along the specified dimension.

        Args:
            align_dim: The dimension name along which to align the rectangles.

        Returns:
            A new :class:`NDRectComplex` aligned along the specified dimension.

        """
        return self.along(align_dim=align_dim)
