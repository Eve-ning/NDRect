"""N-dimensional complex rectangles."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, override

from attrs import define, field

from ndrect._is_aligned import IsAligned
from ndrect._typing import DimensionLength, DimensionName

if TYPE_CHECKING:
    from ndrect.ndrect import NDRect


class NoAlignment:
    """Sentinel class representing no alignment."""

    def __repr__(self) -> str:
        """Sentinel representation for no alignment."""
        return "?"


@define(repr=False, frozen=True)
class NDRectComplex(IsAligned):
    """Aligned complex n-dim rectangle of multiple rectangles in sequence."""

    rects: Sequence[NDRect | NDRectComplex] = field(converter=tuple)
    align_dim: DimensionName = field(factory=NoAlignment)

    def __attrs_post_init__(self) -> None:  # noqa: D105
        if isinstance(self.align_dim, NoAlignment):
            return
        # Validate that all rectangles contain the alignment dimension
        if not all(self.align_dim in r.shape for r in self.rects):
            msg = (
                f"Cannot construct {self.__class__.__name__} "
                f"where Alignment Dimension {self.align_dim} doesn't "
                "exist in all rectangles. "
                "Found dimensions in rectangles: "
                f"{set().union(*(r.shape.keys() for r in self.rects))}"
            )
            raise ValueError(msg)

    @property
    @override
    def shape(self) -> dict[DimensionName, DimensionLength]:
        shape = defaultdict(lambda: 0)
        for rect in self.rects:
            for name, size in rect.shape.items():
                shape[name] = (
                    shape[name] + size
                    if name == self.align_dim
                    else max(shape[name], size)
                )
        return dict(shape)

    def along(self, align_dim: DimensionName) -> NDRectComplex:
        """Aligns this along a dimension to create a NDRectComplex.

        Args:
            align_dim: The dimension name along which to align the rectangles.

        Returns:
            A new :class:`NDRectComplex` aligned along the specified dimension.

        """
        return self._complex_type(
            rects=[self._complex_type(rects=self.rects, align_dim=align_dim)]
        )

    @override
    def __repr__(self) -> str:
        return (
            "("
            + "+".join(repr(e) for e in self.rects)
            + f"@D{self.align_dim!s})"
        )

    def __getitem__(self, item: int) -> NDRect | NDRectComplex:
        """Get the rectangle at the specified index."""
        return self.rects[item]

    def __len__(self) -> int:
        """Count of rectangles in this alignment."""
        return len(self.rects)

    def __iter__(self) -> Iterator[NDRect | NDRectComplex]:
        """Iterate over the rectangles in this complex rectangle."""
        yield from self.rects

    def __matmul__(self, align_dim: DimensionName) -> NDRectComplex:
        """Shorthand for :meth:`along`.

        Aligning the complex rectangle along the specified dimension.

        Args:
            align_dim: The dimension name along which to align the rectangles.

        Returns:
            A new :class:`NDRectComplex` aligned along the specified dimension.

        """
        return self.along(align_dim=align_dim)
