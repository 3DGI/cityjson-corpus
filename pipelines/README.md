# Pipelines

This directory describes how generated and acquired artifacts are materialized.
For the full command flow, read `docs/data-generation.md`.

## Main Commands

- `just sync-catalog`: rebuild derived case indexes.
- `just generate-data`: build generated workload artifacts.
- `just acquire-3dbag`: materialize the pinned 3DBAG dataset slice.
- `just acquire-basisvoorziening-3d`: materialize the pinned Basisvoorziening 3D
  dataset slice.

## How To Change It

Edit pipeline logic when you need to change how generated or acquired data is
materialized. After that, rerun the owning command and verify the output in
`artifacts/`.
