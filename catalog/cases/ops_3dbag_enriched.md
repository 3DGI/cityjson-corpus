# ops_3dbag_enriched

## Intent

Real 3DBAG geometry enriched with synthetic non-geometric data.

## Why This Shape

The geometry stays realistic, but the object graph becomes more demanding. The
extra attributes and metadata increase the amount of owned state and the number
of code paths touched during traversal and serialization.

## Performance Signal

This case surfaces:

- allocation behavior from mixed object graphs,
- attribute lookup and conversion cost,
- traversal cost when geometry and metadata both matter,
- roundtrip stability on realistic but richer objects.

## Recommended Use

Use this case for realistic operation kernels where the benchmark should
exercise both geometry and non-geometry state.

