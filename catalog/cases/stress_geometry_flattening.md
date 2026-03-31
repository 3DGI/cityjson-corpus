# stress_geometry_flattening

## Intent

Synthetic stress case with many geometry objects that require flattening or
normalization.

## Why This Shape

Flattening cost becomes visible when there is enough repeated nested geometry
to make recursion, container growth, and normalization work dominate. The case
should stay geometry-heavy and attribute-light.

## Performance Signal

This case surfaces:

- recursive geometry traversal cost,
- temporary allocation churn,
- vector growth and copy cost,
- geometry normalization overhead.

## Recommended Use

Use this to stress geometry flattening and related parser or serializer paths.

