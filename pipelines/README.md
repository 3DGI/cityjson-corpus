# Pipelines

This directory holds corpus build and publication scripts.

The executable pipelines are `just generate-data` and
[`audit_corpus.sh`](audit_corpus.sh). Generation materializes synthetic cases
into `artifacts/generated/` and writes `artifacts/benchmark-index.json`. Audit
validates the case tree, checks generated manifests, and writes a summary to
`artifacts/corpus-audit.json`.

This directory contains work that converts the canonical `cases/` tree into
reproducible benchmark outputs.
