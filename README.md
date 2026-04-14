# cityjson-benchmarks

Shared test and benchmark corpus for CityJSON data handling software.

This repository keeps the corpus contract in one place.

## Read In The Docs Site

If you are reading the repository through the docs site, start with:

- `docs/index.md`
- `docs/shared-corpus.md`
- `cases/README.md`
- `docs/contributing.md`
- `docs/independent-use.md`
- `docs/licensing.md`

## Repository Layout

- `cases/`: source of truth. Each case folder contains the case metadata, the
  expected result, and the source or instructions for the artifact.
- `catalog/`: derived machine-readable index built from `cases/`.
- `schemas/`: JSON Schemas and the short glossary for controlled values.
- `scripts/`: validation, catalog rendering, docs generation, and acquisition
  helpers.
- `pipelines/`: notes about how derived benchmark outputs are built.
- `artifacts/`: generated files, acquired files, and derived indexes.
- `docs/`: hand-written docs and architecture notes.

## Working Rules

- `cases/` is the source of truth.
- `catalog/` and `artifacts/` are derived outputs.
- Do not edit derived files by hand when a source file or build command owns
  them.
- If you remove a case, run `just clean` before rebuilding docs so stale
  generated case pages do not remain in the site output.

## Main Commands

- `just fmt`: format Python files with ruff.
- `just lint`: validate the repo.
- `just sync-catalog`: rebuild `catalog/cases.json` and
  `artifacts/correctness-index.json`.
- `just generate-data`: materialize generated workload data and refresh
  `artifacts/benchmark-index.json`.
- `just acquire-3dbag`: materialize the pinned 3DBAG workload artifacts.
- `just acquire-basisvoorziening-3d`: materialize the pinned Basisvoorziening
  3D workload artifacts.
- `just clean`: remove generated outputs and generated docs pages.
- `just docs-build`: build the ProperDocs site.
- `just docs-serve`: serve the ProperDocs site locally.

## Licensing

This repository now uses a dual-license model for repository-authored content:

- `LICENSE`: `Apache-2.0` for repository-authored code, scripts, schemas, and
  build logic.
- `LICENSE-DATA`: `CC BY 4.0` for repository-authored docs, metadata, and
  synthetic corpus content.
- Acquired third-party data keeps the upstream license named in its
  `acquisition.json`.
