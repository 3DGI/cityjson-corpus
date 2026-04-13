# Artifacts

This directory is for derived benchmark outputs, release packages, and release
metadata.

These files are outputs of the corpus pipeline, not the source of truth. The
catalog, schemas, and pipelines define how they are reproduced.

Current generated outputs are written to `artifacts/generated/`, the published
3DBAG acquired artifacts live under `artifacts/acquired/3dbag/v20250903/`
(including the single-tile baseline and the merged `cluster_4x.city.json`
stress workload, each with sibling `.cjarrow` live-stream and `.cjparquet`
package files), the published Basisvoorziening 3D acquired artifacts live
under `artifacts/acquired/basisvoorziening-3d/2022/`, and the workload
benchmark index produced by `just generate-data` lives at
`artifacts/benchmark-index.json`. That index exposes each workload's
`canonical_artifact` and any sibling `artifacts` entries marked as
`benchmark-only`. The shared correctness index consumed by downstream test
suites lives at `artifacts/correctness-index.json`.
