"""ndrect - A Python library for N-dimensional rectangles (hyperrectangles)."""

from ndrect.ndrect import NDRect
from ndrect.ndrect_complex import NDRectComplex, UnalignedError

__all__ = ["NDRect", "NDRectComplex"]
