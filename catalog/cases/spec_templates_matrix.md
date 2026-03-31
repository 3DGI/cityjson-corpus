# spec_templates_matrix

Deterministic synthetic template case (`seed 1003`) with 16 `Building` city
objects, `MultiSurface` and `Solid` geometries, LoDs 2-3, and geometry
templates enabled. Materials, textures, attributes, and semantics are all
disabled so template reuse stays isolated.

## Signals

- template lookup
- instance indirection or expansion
- reuse versus duplication
- serializer behavior for shared geometry sources

## Use

Spec atom for template support, instance indirection, and repeated-instance
memory behavior.
