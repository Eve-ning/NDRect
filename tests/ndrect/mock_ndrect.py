from types import MappingProxyType

from attrs import define

from ndrect import NDRect
from ndrect._ndrect_base import NDRectBase
from ndrect._typing import DimensionLength, DimensionName
from ndrect.ndrect_complex import NDRectComplex


class MockNDRectBase(NDRectBase):
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
class MockNDRect(NDRect):
    @property
    def _singular_type(self) -> type[MockNDRect]:
        return MockNDRect

    @property
    def _complex_type(self) -> type[MockNDRectComplex]:
        return MockNDRectComplex


@define
class MockNDRectComplex(NDRectComplex):
    @property
    def _singular_type(self) -> type[MockNDRect]:
        return MockNDRect

    @property
    def _complex_type(self) -> type[MockNDRectComplex]:
        return MockNDRectComplex
