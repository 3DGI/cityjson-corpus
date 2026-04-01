# stress_appearance_and_validation

Deterministic synthetic stress case (`seed 2007`) with 32 `Building`/`Bridge`
city objects, `MultiSurface` geometry at LoDs 2-3, 4-6 materials across 4
themes, 3-4 textures across 4 themes, and all appearance flags enabled. The
case keeps attributes and templates off so write-time appearance validation is
the dominant cost.

## Signals

- serializer branching
- metadata validation
- output-size growth from appearance payloads
- memory overhead from write-time checks

## Use

Serializer and validation work where write-path cost matters.
