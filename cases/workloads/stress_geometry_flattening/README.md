# stress_geometry_flattening

Deterministic synthetic stress case (`seed 2001`) with 64 `Building`/`Bridge`
city objects, `MultiSurface`/`Solid`/`MultiSolid`/`CompositeSurface`/
`CompositeSolid` geometries, LoDs 2-3, 16-32 vertices, and coordinates in
`[0, 10000]`. Materials, textures, attributes, and semantics are disabled.

## Signals

- recursive geometry traversal
- temporary allocation churn
- vector growth and copy cost
- geometry normalization overhead

## Use

Stress geometry normalization, flattening, and related parser or serializer
paths.
