# cityjson-benchmarks

Shared benchmark corpus for CityJSON tooling.

This repository defines benchmark cases, profile fixtures, correctness
invariants, acquisition metadata, and derived artifacts for other CityJSON
projects to consume. The corpus contract is kept in one place so generators
and benchmark harnesses share a single model instead of each defining their
own.

The migration plan for the shared corpus is at
[docs/shared-corpus-migration-plan.md](docs/shared-corpus-migration-plan.md).

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
- `docs/` - repository documentation and the design ADRs.

## Local Workflow

- `just validate-cases` validates the case tree and checks that
  `catalog/cases.json` matches it.
- `just validate-profiles` checks that generated-case profile fixtures still
  match their owning case metadata.
- `just bootstrap-cases` refreshes the migrated `serde_cityjson`
  conformance fixtures under `cases/conformance/v2_0/` and rewrites the
  derived catalog.
- `just sync-catalog` rewrites `catalog/cases.json` from `cases/`.
- `just acquire-3dbag` materializes the published September 3, 2025 3DBAG
  slice under `artifacts/acquired/3dbag/v20250903/`, including the sibling
  cityarrow and cityparquet benchmark artifacts.
- `just generate-data` materializes the synthetic workload cases into
  `artifacts/generated/` and writes the benchmark-only export at
  `artifacts/benchmark-index.json`.
- `just audit-corpus` runs validation and writes a corpus summary to
  `artifacts/corpus-audit.json`.
- `just docs-build` builds the MkDocs site through `uv`.
- `just docs-serve` starts a local docs server through `uv`.

## Requirements

- `just` for repository tasks.
- `uv` for MkDocs dependency management and docs builds.
- `jq` and `cargo` for corpus validation and auditing.
- A sibling checkout of `../cjfake` for profile validation and the corpus
  audit pipeline.

## Documentation

- [Documentation home](docs/index.md)
- [Derived case catalog](catalog/cases.json)
- [Profile schema](profiles/cjfake-manifest.schema.json)
- [Case layout](cases/README.md)
- [Data generation](docs/data-generation.md)
- [Shared corpus migration plan](docs/shared-corpus-migration-plan.md)
- [Corpus design ADR](docs/adr/0009-cityjson-benchmark-corpus-design.md)

## Benchmark Consumers

Tools such as `serde_cityjson`, `cjlib`, and `cjindex` consume this corpus.
These crates read the shared corpus index and reuse the same synthetic fixtures
instead of defining separate benchmark models. Published 3DBAG CityJSON,
cityarrow, and cityparquet artifacts are acquired here and consumed directly
by downstream crates.
