"""IsAligned interface for N-dimensional rectangles with defined shapes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import TYPE_CHECKING

from ndrect._typing import DimensionLength, DimensionName

if TYPE_CHECKING:
    from ndrect.ndrect import NDRect
    from ndrect.ndrect_complex import NDRectComplex


class IsAligned[TSingular: NDRect, TComplex: NDRectComplex](ABC):
    """An interface for N-dimensional rectangles that have a defined shape."""

    @property
    @abstractmethod
    def shape(self) -> MappingProxyType[DimensionName, DimensionLength]:
        """Mapping of dimension names to their lengths.

        Returns:
            An immutable mapping of dimension names to lengths.

        """
        ...

    @property
    def ndim(self) -> int:
        """Number of unique dimensions.

        Returns:
            The number of unique dimensions in the shape.

        """
        return len(self.shape)

    def fill_into(
        self,
        bounding: Mapping[DimensionName, DimensionLength],
        fill_order: Sequence[DimensionName] | None = None,
    ) -> TComplex:
        """Fill the current rectangle until it matches the bounding shape.

        Args:
            bounding: The target bounding shape to fill into.
            fill_order: The order in which to fill dimensions.
                If None, uses the order of the current shape's keys.

        Returns:
            A new :class:`NDRectComplex` representing the filled rectangle.

        """
        filled = self
        fill_order = fill_order or self.shape.keys()
        prv_shape = []
        nxt_shape = list(self.shape.keys())
        for name in fill_order:
            prv_fill = {d: s for d, s in bounding.items() if d in prv_shape}
            nxt_fill = {d: s for d, s in self.shape.items() if d in nxt_shape}
            filled += self._singular_type(
                {
                    **prv_fill,
                    **nxt_fill,
                    name: bounding[name] - self.shape[name],
                },
            )
            filled @= name
            prv_shape.append(nxt_shape.pop(0))
        return filled

    def _as_sequence_object(
        self,
    ) -> tuple[TSingular | TComplex, ...]:
        if isinstance(self, self._singular_type) or (
            isinstance(self, self._complex_type) and self.aligned
        ):
            return (self,)
        elif isinstance(self, self._complex_type):
            return tuple(self.rects)
        raise TypeError

    def then(self, other: IsAligned) -> TComplex:
        """Sequences the other rectangle after this one.

        Args:
            other: Another rectangle to sequence after this one.

        Returns:
            A new :class:`NDRectComplex` representing the sequence.

        """
        return self._complex_type(
            rects=self._as_sequence_object() + other._as_sequence_object()
        )

    def repeat(self, n: int = 2) -> TComplex:
        """Repeats the current rectangle n times in sequence.

        Args:
            n: Number of times to repeat. n=1 returns the same rectangle,
                n=2 returns two in sequence, etc.

        Returns:
            A new :class:`NDRectComplex` representing the repeated sequence.

        """
        return self._complex_type(rects=self._as_sequence_object() * n)

    def elevate(self) -> TComplex:
        """Elevates the dimensionality by 1 by wrapping in a complex type.

        Returns:
            A new :class:`NDRectComplex` representing the elevated rectangle.

        """
        if isinstance(self, self._singular_type):
            rects = self._as_sequence_object()
        elif isinstance(self, self._complex_type):
            rects = (self,)
        else:
            raise TypeError
        return self._complex_type(rects=rects)

    def along(self, align_dim: DimensionName) -> TComplex:
        """Aligns this along a dimension to create a complex type.

        Args:
            align_dim: The dimension name along which to align the rectangles.

        Returns:
            A new complex type aligned along the specified dimension.

        """
        return self._complex_type(
            rects=self._as_sequence_object(), align_dim=align_dim
        )

    @property
    @abstractmethod
    def _singular_type(self) -> type[TSingular]: ...

    @property
    @abstractmethod
    def _complex_type(self) -> type[TComplex]: ...

    def __mul__(self, n: int) -> TComplex:
        """Shorthand for :meth:`repeat`.

        Repeats the current rectangle n times.

        Args:
            n: Number of times to repeat.

        Returns:
            A new :class:`NDRectComplex` representing the repeated sequence.

        """
        return self.repeat(n)

    def __add__(self, other: IsAligned) -> TComplex:
        """Shorthand for :meth:`then`.

        Sequences the other rectangle after this one.

        Args:
            other: Another rectangle to sequence after this one.

        Returns:
            A new :class:`NDRectComplex` representing the sequence.

        """
        return self.then(other)

    def __pos__(self) -> TComplex:
        """Shorthand for :meth:`elevate`.

        Returns:
            A new :class:`NDRectComplex` representing the elevated rectangle.

        """
        return self.elevate()

    def __matmul__(self, align_dim: DimensionName) -> TComplex:
        """Shorthand for :meth:`along`.

        Aligning the complex rectangle along the specified dimension.

        Args:
            align_dim: The dimension name along which to align the rectangles.

        Returns:
            A new complex type aligned along the specified dimension.

        """
        return self.along(align_dim=align_dim)
