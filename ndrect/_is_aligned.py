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


class IsAligned(ABC):
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
    ) -> NDRectComplex:
        """Fill the current rectangle until it matches the bounding shape.

        Args:
            bounding: The target bounding shape to fill into.
            fill_order: The order in which to fill dimensions.
                If None, uses the order of the current shape's keys.

        Returns:
            A new :class:`NDRectComplex` representing the filled rectangle.

        """
        from ndrect.ndrect import NDRect

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
                    name: bounding[name] - self.shape[name],
                },
            )
            filled @= name
            prv_shape.append(nxt_shape.pop(0))
        return filled

    def then(self, other: IsAligned) -> NDRectComplex:
        """Sequences the other rectangle after this one.

        Notes:
            The returned object is a NDRectComplexUnaligned, which can be
            aligned later through :meth:`along`.

        Args:
            other: Another rectangle to sequence after this one.

        Returns:
            A new :class:`NDRectComplexUnaligned` representing the sequence.

        """
        rects = []
        if isinstance(self, self._singular_type):
            rects.append(self)
        elif isinstance(self, self._complex_type):
            rects.extend(self.rects)
        else:
            raise TypeError()

        if isinstance(other, self._singular_type):
            rects.append(other)
        elif isinstance(other, self._complex_type):
            rects.extend(other.rects)
        else:
            raise TypeError()

        from ndrect.ndrect_complex import NDRectComplex

        return NDRectComplex(rects=rects)

    def repeat(self, n: int = 2) -> NDRectComplex:
        """Repeats the current rectangle n times in sequence.

        Args:
            n: Number of times to repeat. n=1 returns the same rectangle,
                n=2 returns two in sequence, etc.

        Returns:
            A new :class:`NDRectComplexUnaligned` representing the repeated
            sequence.

        """
        if isinstance(self, self._singular_type):
            return self._complex_type(rects=[self] * n)
        elif isinstance(self, self._complex_type):
            return self._complex_type(rects=self.rects * n)
        else:
            raise TypeError

    @property
    def _singular_type(self) -> type[NDRect]:
        from ndrect.ndrect import NDRect

        return NDRect

    @property
    def _complex_type(self) -> type[NDRectComplex]:
        from ndrect.ndrect_complex import NDRectComplex

        return NDRectComplex

    def __mul__(self, n: int) -> NDRectComplex:
        """Shorthand for :meth:`repeat`.

        Repeats the current rectangle n times.

        Args:
            n: Number of times to repeat.

        Returns:
            A new :class:`NDRectComplexUnaligned` representing the repeated
            sequence.

        """
        return self.repeat(n)

    def __add__(self, other: IsAligned) -> NDRectComplex:
        """Shorthand for :meth:`then`.

        Sequences the other rectangle after this one.

        Args:
            other: Another rectangle to sequence after this one.

        Returns:
            A new :class:`NDRectComplexUnaligned` representing the sequence.

        """
        return self.then(other)
