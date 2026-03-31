# ops_3dbag_base

## Intent

Medium-sized real-geometry case for common object-model operations.

## Why This Shape

The shape stays close to real-world 3DBAG structure but keeps the dataset
small enough that traversal, filtering, and bounding-box style operations do
not get drowned out by raw file size.

## Performance Signal

This case surfaces:

- hierarchy traversal cost,
- object filtering cost,
- geometry access cost,
- bounding-box and extent computation cost.

## Recommended Use

Use this as the baseline operation kernel for real geometry.

