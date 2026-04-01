# stress_attribute_tree

Deterministic synthetic stress case (`seed 2003`) with 16 `Building` city
objects, `MultiSurface` geometry at LoD 2, and deep nested attributes enabled.
Materials, textures, templates, and semantics are disabled so attribute shape
is the main variable.

## Signals

- recursive conversion
- hash map and vector growth
- short-lived allocation churn
- serializer cost for deep non-geometric data

## Use

Observe attribute-heavy payloads in memory and during de/serialization.
