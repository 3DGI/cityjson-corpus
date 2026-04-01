# stress_deep_boundary

Deterministic synthetic stress case (`seed 2005`) with 32 `Building` city
objects and `Solid`, `MultiSolid`, and `CompositeSolid` geometries at LoDs
2-3. Materials, textures, attributes, semantics, and templates are disabled so
deep boundary nesting is the only major cost center.

## Signals

- boundary parsing
- recursive descent
- nested-vector allocation and copy cost
- error-path sensitivity for malformed or deep nesting

## Use

Test deep geometry boundary handling and normalization cost.
