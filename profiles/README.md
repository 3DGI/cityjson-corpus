# Profiles

This directory holds the manifest schema for generated benchmark cases.

The canonical contract is
[cjfake-manifest.schema.json](cjfake-manifest.schema.json). Concrete
`profile.json` fixtures now live inside their owning case directories under
[`cases/`](../cases/README.md). The `just generate-data` command consumes
those per-case manifests and materializes the synthetic benchmark outputs.

Profiles describe the parameters for producing a case, not the artifact that
results from running that case.
