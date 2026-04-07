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
- `profiles/` - manifest schema for synthetic profile fixtures.
- `pipelines/` - corpus build and publication scripts.
- `artifacts/` - derived benchmark outputs, raw acquired slices, and release
  metadata.
- `schemas/` - JSON Schemas for case, invariants, and acquisition metadata.
- `scripts/` - validation, rendering, and data-pipeline scripts.
- `docs/` - repository documentation and the design ADRs.

## Corpus Use Cases

The corpus serves two purposes:

- **Correctness testing.** Conformance, invalid, and operations cases define
  invariants that consuming tools must satisfy. Their fixtures are checked in
  or acquired, never generated. `artifacts/correctness-index.json` is a
  derived index of these cases, rendered by `just sync-catalog`.
- **Benchmark performance.** Workload cases provide synthetic stress fixtures
  and real-data I/O workloads for measuring throughput and latency.
  `artifacts/benchmark-index.json` lists their output paths after
  `just generate-data` materializes them.

## Getting Started

Prerequisites: `just`, `uv`, `jq`, `cargo`, and a sibling checkout of
`../cjfake` (or override via `CJFAKE_CARGO_MANIFEST`).

1. `just lint` - verify the case tree and profiles are healthy.
2. `just acquire-3dbag` - download the 3DBAG slice into `artifacts/acquired/`.
3. `just generate-data` - materialize synthetic workloads into
   `artifacts/generated/`.

Conformance and invalid cases are checked-in fixtures that need no generation.
They are ready to use for correctness testing immediately after cloning.

After step 3, `artifacts/benchmark-index.json` lists all workload cases and
their output paths.

## Recipes

- `just fmt` formats Python files with ruff.
- `just lint` runs ruff check and validates the case tree, catalog sync, and
  profile fixtures.
- `just sync-catalog` rewrites `catalog/cases.json` and
  `artifacts/correctness-index.json` from `cases/`.
- `just acquire-3dbag` materializes the published September 3, 2025 3DBAG
  slice under `artifacts/acquired/3dbag/v20250903/`, including the sibling
  cityarrow and cityparquet benchmark artifacts.
- `just generate-data` materializes the synthetic workload cases into
  `artifacts/generated/` and writes the benchmark-only export at
  `artifacts/benchmark-index.json`.
- `just docs-build` builds the MkDocs site through `uv`.
- `just docs-serve` starts a local docs server through `uv`.

## Documentation

- [Documentation home](docs/index.md)
- [Derived case catalog](catalog/cases.json)
- [Profile schema](profiles/cjfake-manifest.schema.json)
- [Case layout](cases/README.md)
- [Data generation](docs/data-generation.md)
- [Corpus design ADR](docs/adr/0009-cityjson-benchmark-corpus-design.md)

## Benchmark Consumers

Tools such as `serde_cityjson`, `cjlib`, and `cjindex` consume this corpus.
These crates read the shared corpus index and reuse the same synthetic fixtures
instead of defining separate benchmark models. Published 3DBAG CityJSON,
cityarrow, and cityparquet artifacts are acquired here and consumed directly
by downstream crates.
