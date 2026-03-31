# stress_vertex_transform

## Intent

Synthetic stress case with a large vertex set that exercises transform and
vertex import behavior.

## Why This Shape

Transform cost is easiest to see when vertex handling dominates the workload
and the rest of the object graph stays relatively quiet. That lets integer
conversion, scaling, and coordinate materialization stand out.

## Performance Signal

This case surfaces:

- vertex import throughput,
- transform application cost,
- numeric conversion cost,
- memory locality during coordinate materialization.

## Recommended Use

Use this to measure vertex-heavy parse and import paths.

