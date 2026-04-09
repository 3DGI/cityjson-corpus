# Schemas

This directory holds the JSON Schemas for the corpus contracts.

The canonical schemas are:

- [case.schema.json](case.schema.json)
- [invariants.schema.json](invariants.schema.json)
- [acquisition.schema.json](acquisition.schema.json)
- [cjfake-manifest.schema.json](cjfake-manifest.schema.json)

`cases/` owns the concrete per-case JSON files, and these schemas describe the
repository-level contracts those files must satisfy. Profile fixtures still
live inside their owning case directories under [`cases/`](../cases/README.md),
but the generator manifest schema that validates them lives here.
