# Artifacts

This directory is for derived benchmark outputs, release packages, and release
metadata.

These files are outputs of the corpus pipeline, not the source of truth. The
catalog, profiles, and pipelines define how they are reproduced.

Current generated outputs are written to `artifacts/generated/`, the published
3DBAG acquired artifacts live under `artifacts/acquired/3dbag/v20250903/`
(including the single-tile baseline and the merged `cluster_4x.city.json`
stress workload, each with sibling `.cjarrow` live-stream and `.cjparquet`
package files), and the workload benchmark index produced by
`just generate-data` lives at `artifacts/benchmark-index.json`. The shared
correctness index consumed by downstream test suites lives at
`artifacts/correctness-index.json`.
