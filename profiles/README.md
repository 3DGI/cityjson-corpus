# Profiles

This directory holds the manifest schema and the profile fixtures used to
generate benchmark cases.

The canonical contract is
[cjfake-manifest.schema.json](cjfake-manifest.schema.json). Every manifest
here should validate against it, and each file in [cases/](cases/) should map
to exactly one catalog case. `just generate-data` consumes those fixtures and
materializes the synthetic benchmark outputs.

Profiles describe how to produce a case, not the artifact produced by running
that case.
