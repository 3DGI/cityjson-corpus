# spec_geometry_matrix

## Intent

Small synthetic case that covers the core CityJSON geometry variants in one
controlled data shape.

## Why This Shape

The geometry set is intentionally broad, but each object is tiny. That keeps
the case focused on geometry decoding and boundary normalization instead of on
attribute size, hierarchy depth, or layout overhead.

## Performance Signal

This case surfaces:

- geometry parser branching,
- boundary array handling,
- geometry-type dispatch cost,
- allocation behavior for nested geometry containers.

## Recommended Use

Use this as a spec atom for geometry correctness and as a baseline for parser
behavior across geometry families.

