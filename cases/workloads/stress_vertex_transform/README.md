# stress_vertex_transform

Deterministic synthetic stress case (`seed 2002`) with 32 `Building`/`Bridge`
city objects, `MultiSurface` geometry at LoD 2, and exactly 256 vertices per
geometry in the `[0, 100000]` coordinate range. Materials, textures,
attributes, semantics, and templates are disabled.

## Signals

- vertex import throughput
- transform application
- numeric conversion
- memory locality during coordinate materialization

## Use

Measure vertex-heavy parse, import, and transform paths.
