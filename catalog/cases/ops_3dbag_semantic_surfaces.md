# ops_3dbag_semantic_surfaces

## Intent

Real-geometry case with stable semantic surfaces such as roof, wall, and
ground.

## Why This Shape

Semantic surfaces are one of the common operations that should remain
correctness-sensitive without turning the case into a full omnibus. The data
shape needs enough structure to support semantic queries while still keeping
geometry real.

## Performance Signal

This case surfaces:

- semantic-surface traversal cost,
- boundary-to-semantics mapping cost,
- object-to-surface lookup cost,
- serializer behavior when semantics are preserved explicitly.

## Recommended Use

Use this for semantic queries, surface-preservation checks, and geometry plus
semantics roundtrips.

