# Pipelines

This directory holds corpus build and publication scripts.

The executable pipelines are `just generate-data` and
[`audit_corpus.sh`](audit_corpus.sh). Generation materializes synthetic cases
into `artifacts/generated/` and writes `artifacts/benchmark-index.json`. Audit
validates the catalog/profile contract, checks the generated fixtures, and
writes a summary to `artifacts/corpus-audit.json`.

This directory contains work that converts profiles and source data into
reproducible benchmark outputs.
