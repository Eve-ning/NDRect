import pytest

from ndrect import NDRect, NDRectComplex, UnalignedError
from tests.ndrect.mock_ndrect import MockNDRectComplex


def test_repr_wraps_in_paran_fslashes_and_shows_dim() -> None:
    shape = {0: 1}
    rect = NDRectComplex([NDRect(shape)], align_dim=0)
    assert repr(rect) == f"(/{str(rect.shape)[1:-1]}/@D{rect.align_dim})"


@pytest.mark.parametrize("shape_with_dim_1", ({0: 1}, {0: 1, 1: 1}))
def test_init_pass_if_all_rect_includes_aligned_dim(
    shape_with_dim_1: dict,
) -> None:
    dim = 0
    shape_with_dim_0 = {dim: 1}
    _ = NDRectComplex(
        [
            NDRect(shape_with_dim_0),
            NDRect(shape_with_dim_1),
        ],
        align_dim=dim,
    )


@pytest.mark.parametrize(
    "shape_without_dim", ({}, {1: 1}, {1: 1, 2: 1}, {"0": 1})
)
def test_init_fails_if_any_rect_dont_include_aligned_dim(
    shape_without_dim: dict,
) -> None:
    dim = 0
    error_match = (
        "Cannot construct ([^\s]+) "
        f"where Alignment Dimension {dim} doesn't "
        "exist in all rectangles. "
        "Found dimensions in rectangles: "
        "([^\s]+)"
    )

    with pytest.raises(ValueError, match=error_match):
        NDRectComplex(
            [
                NDRect(shape_without_dim),
            ],
            align_dim=dim,
        )

    shape_with_dim = {dim: 1}
    with pytest.raises(ValueError, match=error_match):
        NDRectComplex(
            [
                NDRect(shape_with_dim),
                NDRect(shape_without_dim),
            ],
            align_dim=dim,
        )


def test_shape_passes_if_aligned_is_true() -> None:
    obj = MockNDRectComplex([NDRect({0: 1})], align_dim=0)
    assert obj.aligned is True
    _ = obj.shape


def test_shape_fails_if_aligned_is_false() -> None:
    obj = MockNDRectComplex([NDRect({0: 1})])
    assert obj.aligned is False
    with pytest.raises(
        UnalignedError,
        match="Cannot get shape of unaligned NDRectComplex. "
        "Align it along a dimension using the `along` method.",
    ):
        _ = obj.shape
