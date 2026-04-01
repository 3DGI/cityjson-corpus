# stress_composite_value

Deterministic synthetic stress case (`seed 2006`) with 24 `Building`/`Bridge`
city objects, `MultiSurface` and `Solid` geometries across LoDs 0-3, and
nested attributes enabled. Materials, textures, templates, and semantics are
disabled so the mixed geometry plus composite value shape stays focused.

## Signals

- geometry and attribute normalization
- allocation reuse versus fragmentation
- intermediate object creation
- serializer complexity under mixed payloads

## Use

Balanced stress case when you want a realistic mixture rather than one
isolated hot path.
