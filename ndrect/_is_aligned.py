"""IsAligned interface for N-dimensional rectangles with defined shapes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import TYPE_CHECKING

from ndrect._typing import DimensionLength, DimensionName

if TYPE_CHECKING:
    from ndrect.ndrect import NDRectComplex


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
