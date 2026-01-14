"""N-dimensional complex rectangles."""

from __future__ import annotations

from collections import defaultdict
from typing import override

from attrs import define

from ndrect._is_aligned import IsAligned
from ndrect._typing import DimensionLength, DimensionName
from ndrect.ndrect import NDRectComplexUnaligned


@define(repr=False, frozen=True)
class NDRectComplex(NDRectComplexUnaligned, IsAligned):
    """Aligned complex n-dim rectangle of multiple rectangles in sequence."""

    align_dim: DimensionName

    def __attrs_post_init__(self) -> None:  # noqa: D105
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

    @override
    def __repr__(self) -> str:
        return (
            "("
            + "+".join(repr(e) for e in self.rects)
            + f"@D{self.align_dim!s})"
        )
