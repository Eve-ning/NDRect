from __future__ import annotations

from collections.abc import Sequence
from types import MappingProxyType
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from attrs import define

from ndrect import NDRect
from ndrect._is_aligned import NDRectBase
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


@patch.object(MockNDRectBase, "shape", new_callable=PropertyMock)
def test_ndim_is_len_of_shape(mock_shape: PropertyMock) -> None:
    obj = MockNDRectBase()
    ndim = obj.ndim
    mock_shape.assert_called_once()
    assert ndim == len(obj.shape)


def test_singular__as_sequence_object_is_a_sequence_of_itself() -> None:
    obj = MockNDRect(MagicMock())
    obj_seq = obj._as_sequence_object()
    assert isinstance(obj_seq, Sequence)
    assert obj_seq[0] == obj
    assert len(obj_seq) == 1


def test_complex__as_sequence_object_is_itself() -> None:
    mock_rects = MagicMock()
    obj = MockNDRectComplex(mock_rects)
    obj_seq = obj._as_sequence_object()
    assert isinstance(obj_seq, Sequence)
    assert obj_seq == obj.rects
    assert len(obj_seq) == mock_rects.__len__()


@pytest.mark.parametrize("type_a", [MockNDRect, MockNDRectComplex])
@pytest.mark.parametrize("type_b", [MockNDRect, MockNDRectComplex])
def test_then_adds__as_sequence_objects_together(
    type_a: Mock, type_b: Mock
) -> None:
    obj_a = type_a(MagicMock())
    obj_b = type_b(MagicMock())
    obj_then = obj_a.then(obj_b)
    assert obj_then == MockNDRectComplex(
        rects=obj_a._as_sequence_object() + obj_b._as_sequence_object(),
        align_dim=obj_then.align_dim,
    )


@pytest.mark.parametrize("type_", [MockNDRect, MockNDRectComplex])
def test_repeat_mul__as_sequence_objects_together(type_: Mock) -> None:
    obj = type_(MagicMock())
    n = MagicMock()
    obj_repeat = obj.repeat(n)
    assert obj_repeat == MockNDRectComplex(
        rects=obj_repeat._as_sequence_object() * n,
        align_dim=obj_repeat.align_dim,
    )


def test_elevate_on_singular_returns_complex_of__as_sequence() -> None:
    obj = MockNDRect(MagicMock())
    obj_elevate = obj.elevate()
    assert obj_elevate == obj._complex_type(
        obj._as_sequence_object(), align_dim=obj_elevate.align_dim
    )


def test_elevate_on_complex_returns_complex_of_collection() -> None:
    obj = MockNDRect(MagicMock())
    obj_elevate = obj.elevate()
    assert obj_elevate == obj._complex_type(
        (obj,), align_dim=obj_elevate.align_dim
    )


@pytest.mark.parametrize(
    "obj",
    [
        MockNDRect({0: 1}),
        MockNDRectComplex([MockNDRect({0: 1})]),
    ],
)
def test_along_creates_complex_with_align_dim_using_as_sequence_object(
    obj,
) -> None:
    assert obj.along(0) == obj._complex_type(
        obj._as_sequence_object(), align_dim=0
    )


def test___add__calls_then() -> None:
    with patch.object(MockNDRectBase, "then") as mock_then:
        obj_a = MockNDRectBase()
        obj_b = MockNDRectBase()
        assert obj_a + obj_b == mock_then.return_value
        mock_then.assert_called_once_with(obj_b)


def test___mul__calls_repeat() -> None:
    with patch.object(MockNDRectBase, "repeat") as mock_repeat:
        obj = MockNDRectBase()
        n = MagicMock()
        assert obj * n == mock_repeat.return_value
        mock_repeat.assert_called_once_with(n)


def test__pos__calls_elevate() -> None:
    with patch.object(MockNDRectBase, "elevate") as mock_elevate:
        obj = MockNDRectBase()
        assert +obj == mock_elevate.return_value
        mock_elevate.assert_called_once()


def test__matmul__calls_along() -> None:
    with patch.object(MockNDRectBase, "along") as mock_along:
        obj = MockNDRectBase()
        dim = MagicMock()
        assert obj @ dim == mock_along.return_value
        mock_along.assert_called_once_with(align_dim=dim)


@pytest.mark.parametrize(
    "type_", [MockNDRect, lambda shape: MockNDRect(shape) @ 0]
)
@pytest.mark.parametrize("len_initial", [0, 1, 2])
@pytest.mark.parametrize("len_target", [0, 1, 2])
def test_fill_into_fills_to_shape(
    type_: Mock,
    len_initial: DimensionLength,
    len_target: DimensionLength,
) -> None:
    shape_initial = {0: len_initial, 1: len_initial}
    shape_target = {0: len_target, 1: len_target}
    obj = type_(shape_initial)
    assert obj.fill_into(shape_target).shape == shape_target
