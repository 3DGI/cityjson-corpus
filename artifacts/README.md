# Artifacts

This directory is for derived benchmark outputs, release packages, and release
metadata.

These files are outputs of the corpus pipeline, not the source of truth. The
catalog, profiles, and pipelines define how they are reproduced.

Current generated outputs are written to `artifacts/generated/`, the published
raw 3DBAG slice lives under `artifacts/acquired/3dbag/v20250903/`, and the
workload benchmark index produced by `just generate-data` lives at
`artifacts/benchmark-index.json`.
