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
- `schemas/` - JSON Schemas for case, invariants, acquisition metadata, and
  generator manifests.
- `scripts/` - validation, rendering, and data-pipeline scripts.
- `docs/` - repository documentation and the design ADRs.

## Corpus Use Cases

The corpus serves two purposes:

- **Correctness testing.** Conformance, invalid, and operation cases define
  invariants that consuming tools must satisfy. The default correctness corpus
  is the reviewed, pinned set of checked-in or acquired fixtures. Supplemental
  generated conformance cases are also indexed for opt-in coverage.
  `artifacts/correctness-index.json` is a derived index of these cases,
  rendered by `just sync-catalog`.
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

Normative conformance, invalid, and operation cases are ready to use
immediately after cloning. Supplemental generated conformance cases require
`just generate-data` before their artifacts are materialized.

After step 3, `artifacts/benchmark-index.json` lists all workload cases and
their output paths.

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
- [CJFake manifest schema](schemas/cjfake-manifest.schema.json)
- [Case layout](cases/README.md)
- [Data generation](docs/data-generation.md)
- [Corpus design ADR](docs/adr/0009-cityjson-benchmark-corpus-design.md)

## Benchmark Consumers

Tools such as `serde_cityjson`, `cjlib`, and `cjindex` consume this corpus.
These crates read the shared corpus index and reuse the same synthetic fixtures
instead of defining separate benchmark models. Published 3DBAG CityJSON,
cityarrow, and cityparquet artifacts are acquired here and consumed directly
by downstream crates.
