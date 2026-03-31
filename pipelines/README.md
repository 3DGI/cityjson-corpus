# Pipelines

This directory holds corpus build and derivation workflow definitions.

Use it for the steps that turn profiles and source data into published
benchmark inputs.

Typical responsibilities:

- generate synthetic cases from manifests
- import and slice real datasets such as `3DBAG`
- enrich real geometry with synthetic non-geometric surfaces
- emit multiple storage layouts from the same semantic content

Keep ownership boundaries clear:

- generation belongs here or in tools called from here
- benchmark execution does not

