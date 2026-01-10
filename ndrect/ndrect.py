from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from copy import deepcopy
from numbers import Real
from types import MappingProxyType
from typing import Sequence, Iterator, Mapping, Any, TypeAlias

from attrs import define, field

DimensionName: TypeAlias = Any
DimensionLength: TypeAlias = Real


class IsAligned(ABC):
    """An interface for N-dimensional rectangles that have a defined shape."""
    @property
    @abstractmethod
    def shape(self) -> MappingProxyType[DimensionName, DimensionLength]:
        """Mapping of dimension names to their lengths.

        Returns: An immutable mapping of dimension names to lengths.
        """
        ...

    @property
    def ndim(self) -> int:
        """Number of unique dimensions.

        Returns: The number of unique dimensions in the shape.
        """
        return len(self.shape)

    def fill_into(
        self,
        bounding: Mapping[DimensionName, DimensionLength],
        fill_order: Sequence[DimensionName] = None,
    ) -> NDRectComplex:
        """Fills the current rectangle until it matches the bounding shape.

        Args:
            bounding: The target bounding shape to fill into.
            fill_order: The order in which to fill dimensions.
                If None, uses the order of the current shape's keys.

        Returns: A new NDRectComplex representing the filled rectangle.
        """
        filled = self
        fill_order = fill_order or self.shape.keys()
        prv_shape = []
        nxt_shape = list(self.shape.keys())
        for name in fill_order:
            prv_fill = {d: s for d, s in bounding.items() if d in prv_shape}
            nxt_fill = {d: s for d, s in self.shape.items() if d in nxt_shape}
            filled += NDRect(
                {
                    **prv_fill,
                    **nxt_fill,
                    **{name: bounding[name] - self.shape[name]},
                }
            )
            filled @= name
            prv_shape.append(nxt_shape.pop(0))
        return filled


class IsSequenceable(ABC):
    """An interface for N-dimensional rectangles that can be sequenced."""
    def then(self, other: IsAligned) -> NDRectComplexUnaligned:
        """Sequences the other rectangle after this one.

        Notes:
            The returned object is a NDRectComplexUnaligned, which can be
            aligned later through .along().

        Args:
            other: Another rectangle to sequence after this one.

        Returns: A new NDRectComplexUnaligned representing the sequence.
        """
        if isinstance(self, (NDRectComplex, NDRect)):
            if isinstance(other, (NDRectComplex, NDRect)):
                return NDRectComplexUnaligned(rects=[self, other])
            elif isinstance(other, NDRectComplexUnaligned):
                return NDRectComplexUnaligned(rects=[self, *other])
        elif isinstance(self, NDRectComplexUnaligned):
            if isinstance(other, (NDRectComplex, NDRect)):
                return NDRectComplexUnaligned(rects=[*self, other])
            elif isinstance(other, NDRectComplexUnaligned):
                return NDRectComplexUnaligned(rects=[*self, *other])
        raise TypeError(
            f"Unsupported types for then(): {type(self)} and {type(other)}"
        )

    def repeat(self, n: int = 2) -> NDRectComplexUnaligned:
        """Repeats the current rectangle n times in sequence.

        Args:
            n: Number of times to repeat. n=1 returns the same rectangle,
                n=2 returns two in sequence, etc.

        Returns: A new NDRectComplexUnaligned representing the repeated
            sequence.
        """
        if isinstance(self, (NDRectComplex, NDRect)):
            return NDRectComplexUnaligned(rects=[self] * n)
        elif isinstance(self, NDRectComplexUnaligned):
            return NDRectComplexUnaligned(rects=list(self.rects) * n)
        raise TypeError(f"Unsupported type for repeat(): {type(self)}")

    def __mul__(self, n: int) -> NDRectComplexUnaligned:
        """Shorthand for .repeat(n), repeating the rectangle n times.

        Args:
            n: Number of times to repeat.

        Returns: A new NDRectComplexUnaligned representing the repeated
            sequence.
        """
        return self.repeat(n)

    def __add__(self, other: IsAligned) -> NDRectComplexUnaligned:
        """Shorthand for .then(other), sequencing the other rectangle after
        this one.

        Args:
            other: Another rectangle to sequence after this one.

        Returns: A new NDRectComplexUnaligned representing the sequence.
        """
        return self.then(other)


@define(repr=False)
class NDRect(IsSequenceable, IsAligned):
    """An N-dimensional rectangle defined by its shape."""

    shape: Mapping[DimensionName, DimensionLength] = field(
        converter=lambda _: MappingProxyType(deepcopy(_))
    )

    def __repr__(self) -> str:
        return f"/{str(self.shape)[1:-1]}/"

    def __hash__(self) -> int:
        # To make NDRect hashable, we hash its shape by expanding the mapping
        # into a sorted tuple of items.
        return hash(tuple(sorted(self.shape.items())))


@define(repr=False, frozen=True)
class NDRectComplexUnaligned(IsSequenceable, Sequence):
    """A complex N-dimensional rectangle made up of multiple rectangles
    in sequence, without a defined alignment dimension."""

    rects: Sequence[NDRect | NDRectComplex] = field(converter=tuple)

    def along(self, align_dim: DimensionName) -> NDRectComplex:
        return NDRectComplex(rects=self, align_dim=align_dim)

    def __repr__(self) -> str:
        return "(" + "+".join(repr(e) for e in self.rects) + "@D?)"

    def __getitem__(self, item) -> NDRect | NDRectComplex:
        return self.rects[item]

    def __len__(self) -> int:
        return len(self.rects)

    def __iter__(self) -> Iterator[NDRect | NDRectComplex]:
        yield from self.rects

    def __matmul__(self, align_dim: int) -> NDRectComplex:
        return self.along(align_dim=align_dim)


@define(repr=False, frozen=True)
class NDRectComplex(NDRectComplexUnaligned, IsAligned):
    """A complex N-dimensional rectangle made up of multiple rectangles
    in sequence, aligned along a specified dimension."""
    align_dim: DimensionName

    def __attrs_post_init__(self) -> None:
        # Validate that all rectangles contain the alignment dimension
        if not all([self.align_dim in r.shape for r in self.rects]):
            raise ValueError(
                f"Cannot construct {self.__class__.__name__} "
                f"where Alignment Dimension {self.align_dim} doesn't "
                "exist in all rectangles. "
                "Found dimensions in rectangles: "
                f"{set().union(*(r.shape.keys() for r in self.rects))}"
            )

    @property
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

    def __repr__(self) -> str:
        return (
            "("
            + "+".join(repr(e) for e in self.rects)
            + f"@D{str(self.align_dim)})"
        )
