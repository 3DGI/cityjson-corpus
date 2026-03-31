# Pipelines

This directory holds corpus build and publication scripts.

The first executable pipeline is [`audit_corpus.sh`](audit_corpus.sh). It
validates the catalog/profile contract, checks the generated fixtures, and
writes a summary to `artifacts/corpus-audit.json`.

Use this directory for work that turns profiles and source data into
reproducible benchmark outputs.
