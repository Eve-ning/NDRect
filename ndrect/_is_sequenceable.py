"""An interface for N-dimensional rectangles that can be sequenced."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ndrect._is_aligned import IsAligned

if TYPE_CHECKING:
    from ndrect.ndrect import NDRectComplexUnaligned


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
        from ndrect.ndrect import NDRect, NDRectComplex, NDRectComplexUnaligned

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
        from ndrect.ndrect import NDRect, NDRectComplex, NDRectComplexUnaligned

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
