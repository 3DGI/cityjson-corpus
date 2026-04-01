# Profiles

This directory holds the manifest schema and the profile fixtures for
generating benchmark cases.

The canonical contract is
[cjfake-manifest.schema.json](cjfake-manifest.schema.json). Every manifest
validates against it. Each file in [cases/](cases/) maps to exactly one catalog
case. The `just generate-data` command consumes these fixtures and materializes
the synthetic benchmark outputs.

Profiles describe the parameters for producing a case, not the artifact that
results from running that case.
