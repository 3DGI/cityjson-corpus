# spec_geometry_matrix

Deterministic synthetic geometry case (`seed 1001`) with 8 `Building`/`Bridge`
city objects, `MultiPoint`/`MultiLineString`/`MultiSurface`/`Solid`/
`MultiSolid`/`CompositeSurface`/`CompositeSolid` geometries, LoDs 0-3,
semantics enabled for `RoofSurface`/`GroundSurface`/`WallSurface`/
`ClosureSurface`, and vertex coordinates constrained to `[-250, 250]`.
Materials, textures, and attributes are disabled.

## Signals

- geometry parser branching
- boundary array handling
- geometry-type dispatch
- nested-geometry allocation

## Use

Baseline spec atom for geometry dispatch, boundary handling, and semantics
preservation.
