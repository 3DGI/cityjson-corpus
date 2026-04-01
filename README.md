# cityjson-benchmarks

Shared benchmark corpus for CityJSON tooling.

This repository defines benchmark cases, profile fixtures, correctness
invariants, and derived artifacts for other CityJSON projects to consume.
The corpus contract is kept in one place so generators and benchmark harnesses
share a single model instead of each defining their own.

The migration plan for the shared corpus is at
[docs/shared-corpus-migration-plan.md](docs/shared-corpus-migration-plan.md).

## Repository Layout

- `catalog/` - canonical case definitions and the machine-readable corpus
  catalog.
- `profiles/` - manifest schema plus the concrete profile fixtures referenced
  by the catalog.
- `pipelines/` - corpus build and publication scripts.
- `invalid/` - syntactically valid negative fixtures for testing rejection
  paths.
- `cases/` - migrated shared case layout, starting with the conformance
  fixtures from `serde_cityjson`.
- `invariants/` - machine-readable correctness checks that belong to the
  corpus, not to a specific implementation.
- `artifacts/` - derived benchmark outputs and release metadata.
- `docs/` - repository documentation and the design ADRs.

## Local Workflow

- `just validate-profiles` checks that the catalog and profile fixtures still
  match.
- `just bootstrap-cases` refreshes the migrated shared case layout under
  `cases/`.
- `just generate-data` materializes the synthetic cases into
  `artifacts/generated/` and writes `artifacts/benchmark-index.json`.
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
- [Corpus catalog](catalog/corpus.json)
- [Profile schema](profiles/cjfake-manifest.schema.json)
- [Corpus invariants](invariants/corpus.json)
- [Invalid fixtures](invalid/index.md)
- [Case layout](cases/README.md)
- [Data generation](docs/data-generation.md)
- [Shared corpus migration plan](docs/shared-corpus-migration-plan.md)
- [Corpus design ADR](docs/adr/0009-cityjson-benchmark-corpus-design.md)

## Benchmark Consumers

Tools such as `serde_cityjson`, `cjlib`, and `cjindex` consume this corpus.
These crates read the shared corpus index and reuse the same synthetic fixtures
instead of defining separate benchmark models. Real-data preparation reuses the
`cjindex` 3DBAG flow until this repository publishes its own pinned artifacts.
