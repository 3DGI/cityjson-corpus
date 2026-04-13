# cityjson-benchmarks

Shared benchmark corpus for CityJSON tooling.

This repository defines benchmark cases, profile fixtures, correctness
invariants, acquisition metadata, and derived artifacts for other CityJSON
projects to consume. The corpus contract is kept in one place so generators
and benchmark harnesses share a single model instead of each defining their
own.

## Repository Layout

- `cases/` - canonical shared corpus layout. Each case directory owns its
  metadata, invariants, checked-in source fixture or profile, and optional
  acquisition notes.
- `catalog/` - derived machine-readable case index rendered from `cases/`.
- `pipelines/` - corpus build and publication scripts.
- `artifacts/` - derived benchmark outputs, raw acquired slices, and release
  metadata.
- `schemas/` - JSON Schemas and the canonical value glossary for case,
  invariants, acquisition metadata, and generator manifests.
- `scripts/` - validation, rendering, and data-pipeline scripts.
- `docs/` - repository documentation and the design ADRs.

## Corpus Use Cases

The corpus serves two purposes:

- **Correctness testing.** Conformance, invalid, and operation cases define
  invariants that consuming tools must satisfy. `artifacts/correctness-index.json`
  is the full derived index of these cases, rendered by `just sync-catalog`.
  The current index contains 36 correctness cases, including the full CityJSON
  2.0 conformance subset.
- **Benchmark performance.** Workload cases provide synthetic stress fixtures
  and real-data I/O workloads for measuring throughput and latency.
  `artifacts/benchmark-index.json` lists each workload's canonical artifact
  and any sibling benchmark-only derived formats after `just generate-data`
  materializes them.

## Getting Started

Prerequisites: `just`, `uv`, `jq`, `cargo`, and a sibling checkout of
`../cjfake` (or override via `CJFAKE_CARGO_MANIFEST`).

1. `just lint` - verify the case tree, profiles, and checked-in conformance
   fixtures are healthy.
2. `just acquire-3dbag` - download the published 3DBAG slice into
   `artifacts/acquired/`.
3. `just acquire-basisvoorziening-3d` - download the published Basisvoorziening
   3D tile into `artifacts/acquired/`.
4. `just generate-data` - materialize synthetic workloads into
   `artifacts/generated/`.

Correctness cases are ready to use once their checked-in, generated, or
acquired artifacts exist. Generated conformance cases require
`just generate-data` before their artifacts are materialized.

After step 3, `artifacts/benchmark-index.json` lists all workload cases, their
canonical artifacts, and any sibling benchmark-only derived formats.

## Adding Or Removing Cases

Case authoring happens under `cases/`, and the derived indexes and docs are
regenerated from that tree.

- Add a new case directory under the right subtree in `cases/`.
- Include `case.json` and `invariants.json`; add `profile.json` or
  `acquisition.json` only when the case type needs them.
- Run `just sync-catalog` after changing case metadata.
- Run `just generate-data` for workload cases that need generated or acquired
  outputs.
- Run `uv run python ./scripts/generate_docs.py` or `just docs-build` to
  refresh the rendered docs.
- Run `just lint` before committing.

When removing a case, delete the case directory and its generated docs page
under `docs/cases/...` before regenerating the docs. The docs generator does
not delete stale pages for removed cases.

## Recipes

- `just fmt` formats Python files with ruff.
- `just lint` runs ruff check, validates the case tree, catalog sync, profile
  fixtures, and checks each checked-in `cases/conformance/v2_0/*.city.json`
  file with `cjval -q`.
- `just sync-catalog` rewrites `catalog/cases.json` and
  `artifacts/correctness-index.json` from `cases/`.
- `just acquire-3dbag` materializes the published September 3, 2025 3DBAG
  slice under `artifacts/acquired/3dbag/v20250903/`, including the sibling
  cityjson-arrow and cityjson-parquet benchmark-only derived artifacts.
- `just acquire-basisvoorziening-3d` materializes the published 2022
  Basisvoorziening 3D tile under `artifacts/acquired/basisvoorziening-3d/2022/`,
  including the sibling cityjson-arrow and cityjson-parquet benchmark-only derived
  artifacts.
- `just generate-data` materializes the synthetic workload cases into
  `artifacts/generated/` and writes the benchmark-only export at
  `artifacts/benchmark-index.json`.
- `just clean` removes generated workload data, acquired artifacts, derived
  indexes, generated docs pages, and the built docs site.
- `just docs-build` builds the MkDocs site through `uv`.
- `just docs-serve` starts a local docs server through `uv`.

## Documentation

- [Documentation home](docs/index.md)
- [Derived case catalog](catalog/cases.json)
- [CJFake manifest schema](https://github.com/3DGI/cjfake/blob/main/src/data/cjfake-manifest.schema.json)
- [Schema value glossary](schemas/README.md)
- [Case layout](cases/README.md)
- [Data generation](docs/data-generation.md)
- [Corpus design ADR](docs/adr/0009-cityjson-benchmark-corpus-design.md)

## Benchmark Consumers

Tools such as `cityjson-json`, `cityjson-arrow`, `cityjson-lib`, and `cjindex` consume
this corpus. Correctness-oriented consumers read the full
`artifacts/correctness-index.json` set; any failing conformance case is a bug
or missing implementation detail, not a reason to trim the corpus. The shared
index currently exposes 28 conformance fixtures and 8 non-conformance
correctness cases. Workload consumers reuse the same synthetic fixtures and
acquired artifacts instead of defining separate benchmark models. Published
3DBAG and Basisvoorziening 3D CityJSON, cityjson-arrow, and cityjson-parquet artifacts
are acquired here and classified explicitly as canonical or benchmark-only in
their acquisition metadata and workload index entries.
