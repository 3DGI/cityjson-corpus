# Pipelines

This directory holds corpus build and publication workflow definitions.

Use it for the steps that turn profiles and source data into published
benchmark inputs.

Typical responsibilities:

- run `cjfake` against manifests
- acquire or stage real-geometry source data such as `3DBAG`
- package generated and sourced benchmark inputs into released artifacts
- emit checksums or release metadata

Keep ownership boundaries clear:

- `cjfake` performs generation
- downstream libraries and tools consume published data
- benchmark execution does not belong here
