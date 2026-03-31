# Artifacts

This directory is for derived benchmark outputs, release packages, and release
metadata.

These files are outputs of the corpus pipeline, not the source of truth. The
catalog, profiles, and pipelines define how they are reproduced.

Current generated outputs are written to `artifacts/generated/`, and the corpus
index produced by `just generate-data` lives at
`artifacts/benchmark-index.json`.
