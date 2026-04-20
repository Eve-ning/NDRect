from types import MappingProxyType

from attrs import define

from ndrect import NDRect, NDRectComplex
from ndrect._ndrect_base import NDRectBase
from ndrect._typing import DimensionLength, DimensionName


class MockNDRectBase(NDRectBase["MockNDRect", "MockNDRectComplex"]):
    @property
    def shape(self) -> MappingProxyType[DimensionName, DimensionLength]:
        return ...

    @property
    def _singular_type(self) -> type[MockNDRect]:
        return MockNDRect

    @property
    def _complex_type(self) -> type[MockNDRectComplex]:
        return MockNDRectComplex


@define
class MockNDRect(NDRect["MockNDRect", "MockNDRectComplex"]):
    @property
    def _singular_type(self) -> type[MockNDRect]:
        return MockNDRect

    @property
    def _complex_type(self) -> type[MockNDRectComplex]:
        return MockNDRectComplex


@define
class MockNDRectComplex(NDRectComplex["MockNDRect", "MockNDRectComplex"]):
    @property
    def _singular_type(self) -> type[MockNDRect]:
        return MockNDRect

    @property
    def _complex_type(self) -> type[MockNDRectComplex]:
        return MockNDRectComplex
