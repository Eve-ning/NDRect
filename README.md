# N-Dimensional Hyper-Rectangle Data Structure

`ndrect` is a library that provides a data structure to work with sequencing hyper-rectangles in an N-dimensional space.
We provide some minimally useful tools and syntax to help with sequencing and some handy geometrical calculations.

- **Hyper-rectangle (N-Dim Rectangle)** is a mathematical term for any rectangular geometry that exists in N dimensions
  where N >= 1. All of their edges must lie parallel to the global orthogonal axes.
- **Sequencing** in this case implies placing these Hyper-rectangles flush with each other. For example, in 2D, "flush"
  hyper-rectangles would have one of their sides intersect each other; in 3D, "flush" hyper-rectangles would have a face
  intersect with another's face.

## The `NDRect` class

An `NDRect` is a representation of an atomic hyper-rectangle. Its constructor takes in a mapping of
`{<DimensionName>: <DimensionLength>}` to define its shape.

```python
from ndrect import NDRect

r = NDRect({0: 1, 1: 2})
assert r.shape == {0: 1, 1: 2}
```

Notice that because the shape is defined as a mapping (dictionary), this is because we do not restrict `NDRect` to fall
in sequential integer dimensions. That is, you can define `NDRect` like so too:

```python
from ndrect import NDRect

# Dimension 0: Length 1
# Dimension 2: Length 4
NDRect({0: 1, 2: 4})

# Dimension A: Length 1
# Dimension B: Length 4
NDRect({"A": 1, "B": 4})
```

## Sequencing `NDRect` into Complex Hyper-rectangles

Up to now, this is no more than just a dictionary, its power comes when we sequence them together.

When sequenced with one another, will form a Unaligned Complex Hyper-rectangle. This Unaligned Complex Hyper-rectangle
must be aligned along a single axis to resolve into a Complex Hyper-rectangle

- **Unaligned** would mean there's no axis that the sequence of `NDRect` objects are aligned along. Therefore, an **Aligned**
  implies a certain axis that the sequence of `NDRect` objects are aligned along.
- **Complex** means an object containing multiple `NDRect` objects.

For example, given two `NDRect` rectangles:

```  
R1  R2
┌─┐ ┌───┐    
│ │ │   │    
└─┘ └───┘    
```

We can sequence them in 2 different axes

```
R1 + R2 Along Axis 0 (Horizontal)
┌─┬───┐   
│ │   │   
└─┴───┘   

R1 + R2 Along Axis 1 (Vertical)
┌───┐   
│   │   
├─┬─┘   
│ │     
└─┘       
```

In `NDRect`, we code it like so:

```python
from ndrect import NDRect

r1 = NDRect({0: 1, 1: 2})
r2 = NDRect({0: 2, 1: 2})

# Align along axis 0
assert r1.then(r2).along(0).shape == {0: 3, 1: 2}

# Align along axis 1
assert r1.then(r2).along(1).shape == {0: 2, 1: 4}
```

Notice that when we sequence them along axis 1, its shape is the shape of minimal bounding rectangle that contains both `R1` and `R2`.

## String Representations

All objects have custom representations that displays compactly on the terminal.

### ``NDRect`` Representation

This is the template representation of an ``NDRect``:

```text
/<Dim A Name>: <Dim A Length>,
 <Dim B Name>: <Dim B Length>,
 ..., 
 <Dim Z Name>: <Dim Z Length>/
```

For example a 2D rectangle of size $3\times4$ ($\text{Height}\times\text{Width}$) would be represented like so: 

```pycon
>>> from ndrect import NDRect
... NDRect({"Height": 3, "Width": 4})

/'Height': 3, 'Width': 4/
```

### ``NDRectComplex`` Representation

This is the template representation of an ``NDRectComplex``:

```text
<Composite NDRect Representation>@D<Aligned Dim Name>
```

As ``NDRectComplex`` objects can contain ``NDRectComplex`` or ``NDRect`` objects, the representation is recursive. We use the placeholder `<Composite NDRect Representation>` to represent.

To represent two ``NDRect`` or ``NDRectComplex`` instances sequenced together, a ``+`` sign is used.

For example two 2D rectangle of size $3\times4$ ($\text{Height}\times\text{Width}$) aligned along the $\text{Height}$ axis would be represented like so:

```pycon
>>> from ndrect import NDRect
... NDRect({"Height": 3, "Width": 4}) * 2 @ "Height"

(/'Height': 3, 'Width': 4/+/'Height': 3, 'Width': 4/@DHeight)
```

... and if they were not aligned at all, the ``<Aligned Dim Name>`` will be replaced by a ``?``.

```pycon
>>> from ndrect import NDRect
... NDRect({"Height": 3, "Width": 4}) * 2

(/'Height': 3, 'Width': 4/+/'Height': 3, 'Width': 4/@D?)
```

If we then doubled the size of this complex rectangle, along the "Width" axis, the representation will recurse itself.

```pycon
>>> from ndrect import NDRect
... NDRect({"Height": 3, "Width": 4}) * 2 @ "Height" * 2 @ "Width"

((/'Height': 3, 'Width': 4/+/'Height': 3, 'Width': 4/@DHeight)+
(/'Height': 3, 'Width': 4/+/'Height': 3, 'Width': 4/@DHeight)@DWidth)
```

As expected, the console will be cluttered with many ``NDRect`` components.
