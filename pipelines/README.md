# Pipelines

This directory holds corpus build and publication scripts.

The executable pipeline is `just generate-data`, which materializes synthetic
cases into `artifacts/generated/` and writes `artifacts/benchmark-index.json`
with canonical-artifact and benchmark-only artifact metadata for each
workload.

This directory contains work that converts the canonical `cases/` tree into
reproducible benchmark outputs.
