"""N-dimensional rectangles."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator, Mapping, Sequence
from copy import deepcopy
from types import MappingProxyType
from typing import override

from attrs import define, field

from ndrect._is_aligned import IsAligned
from ndrect._typing import DimensionLength, DimensionName


class IsSequenceable:
    """An interface for N-dimensional rectangles that can be sequenced."""

    def then(self, other: IsAligned) -> NDRectComplexUnaligned:
        """Sequences the other rectangle after this one.

        Notes:
            The returned object is a NDRectComplexUnaligned, which can be
            aligned later through :meth:`along`.

        Args:
            other: Another rectangle to sequence after this one.

        Returns:
            A new :class:`NDRectComplexUnaligned` representing the sequence.

        """
        if isinstance(self, (NDRectComplex, NDRect)):
            if isinstance(other, (NDRectComplex, NDRect)):
                return NDRectComplexUnaligned(rects=[self, other])
            if isinstance(other, NDRectComplexUnaligned):
                return NDRectComplexUnaligned(rects=[self, *other])
        elif isinstance(self, NDRectComplexUnaligned):
            if isinstance(other, (NDRectComplex, NDRect)):
                return NDRectComplexUnaligned(rects=[*self, other])
            if isinstance(other, NDRectComplexUnaligned):
                return NDRectComplexUnaligned(rects=[*self, *other])
        msg = f"Unsupported types for then(): {type(self)} and {type(other)}"
        raise TypeError(
            msg,
        )

    def repeat(self, n: int = 2) -> NDRectComplexUnaligned:
        """Repeats the current rectangle n times in sequence.

        Args:
            n: Number of times to repeat. n=1 returns the same rectangle,
                n=2 returns two in sequence, etc.

        Returns:
            A new :class:`NDRectComplexUnaligned` representing the repeated
            sequence.

        """
        if isinstance(self, (NDRectComplex, NDRect)):
            return NDRectComplexUnaligned(rects=[self] * n)
        if isinstance(self, NDRectComplexUnaligned):
            return NDRectComplexUnaligned(rects=list(self.rects) * n)
        msg = f"Unsupported type for repeat(): {type(self)}"
        raise TypeError(msg)

    def __mul__(self, n: int) -> NDRectComplexUnaligned:
        """Shorthand for :meth:`repeat`.

        Repeats the current rectangle n times.

        Args:
            n: Number of times to repeat.

        Returns:
            A new :class:`NDRectComplexUnaligned` representing the repeated
            sequence.

        """
        return self.repeat(n)

    def __add__(self, other: IsAligned) -> NDRectComplexUnaligned:
        """Shorthand for :meth:`then`.

        Sequences the other rectangle after this one.

        Args:
            other: Another rectangle to sequence after this one.

        Returns:
            A new :class:`NDRectComplexUnaligned` representing the sequence.

        """
        return self.then(other)


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
