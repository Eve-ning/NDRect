# N-Dimensional Hyper-Rectangle Data Structure

This library provides a simple class `NDRect` to do some simple shape calculations

An N-Dimensional Rectangle (or Hyper-Rectangle) is a generalization of a rectangle to N dimensions. In 2D, it's a rectangle; in 3D, it's a rectangular prism (or cuboid); and in higher dimensions, it's referred to as a hyper-rectangle.

This library focuses on this simple subset of shapes, and provides some basic operations to manipulate them.

## Quick Example

Given a rectangle in a 2D space that has lengths:
- 1 unit on axis 0
- 2 units on axis 1

In short, a $1\times2$ rectangle. 

You can define it like so:
```python
from ndrect import NDRect

rect = NDRect({0: 1, 1: 2})
```

Then, if we want to make it a square, we can add another $1\times2$ rectangle, or we can just repeat it

```python
from ndrect import NDRect

rect = NDRect({0: 1, 1: 2})
rect + rect
# Equivalent
rect.then(rect)
rect.repeat(2)
```

Notice that if you do this, it doesn't actually have defined dimensions, as we also need to define the axis were we want to repeat it on.

```python
from ndrect import NDRect

rect = NDRect({0: 1, 1: 2})
assert (rect + rect) @ 0 == {0: 2, 1: 2}
# Equivalent
assert rect.then(rect).along(0).dims == {0: 2, 1: 2}
assert rect.repeat(2).along(0).dims == {0: 2, 1: 2}
```

## Syntax

As shown above, there's some interesting quirks about `NDRect`

### Arbitrarily Named Dimensions

Dimensions are defined using a `Mapping[DimensionName, DimensionLength]`, where `DimensionName: Any`, `DimensionLength: Number`. This means that dimension names don't necessarily need to be [0, 1, 2, ...]. `NDRect`'s dimensions can be anything that's hashable; for each unique dimension (unique hash), we treat it as an orthogonal axis. So for example:

```python
from ndrect import NDRect

NDRect({"a": 1, "b": 2})
```

is also a valid `NDRect`.

### NDRect Complex Objects

"Complex" is a term coined to represent multiple geometrical objects bundled together. In this case, it's simply multiple `NDRect` objects glued together by some face w.r.t. a predefined axis.

When you join multiple `NDRect` objects together, its class type is elevated to a `NDRectComplex` or `NDRectComplexUnaligned`. These objects still act similar to an `NDRect`, however shouldn't be manually constructed (though I can't stop you).

### Unaligned NDRectComplex Objects

As you elevate an `NDRect`, it should change into a `NDRectComplexUnaligned`. This intermediary class is a temporary class that doesn't have an axis of alignment specified. For example, given $(1\times2) + (1\times2)$, it can result in either $(1\times4)$ or $(2\times2)$ dependent on the axis of joining. Thus this intermediate form doesn't have a defined dimension.

In order to specify the alignment axis, you can use `along` or `@`.

For example

```python
from ndrect import NDRect

rect = NDRect({0: 1, 1: 2})
rect_complex_unaligned = rect + rect
rect_complex = rect_complex_unaligned @ 0
assert rect_complex.dims == {0: 2, 1: 2}
```

### Operators

For `NDRect`, we can use the `+`, `*`, `@` operators to represent `.then`, `.repeat`, `.along` shorthands respectively.

```python
from ndrect import NDRect

rect = NDRect({0: 1, 1: 2})
```

