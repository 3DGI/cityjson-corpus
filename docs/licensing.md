# Licensing

This repository uses a dual-license model for repository-authored content.
It does not change the license of any upstream data source.

## Scope

- `Apache-2.0` applies to repository-authored code, scripts, schemas, and
  build logic. See the root `LICENSE` file.
- `CC BY 4.0` applies to repository-authored docs, metadata, and synthetic
  corpus content. See the root `LICENSE-DATA` file.
- Acquired third-party data keeps the upstream license named in the case's
  `acquisition.json`.

## Why The Split Exists

This repo mixes software and reusable data.

- `Apache-2.0` fits code and build logic.
- `CC BY 4.0` fits shared docs and corpus content.
- Upstream data keeps its original terms instead of being relicensed here.

## Practical Rule

Before reusing or redistributing an acquired artifact, read that case's
`acquisition.json`.
