# cityjson-benchmarks

Shared benchmark corpus for CityJSON tooling.

This repository defines benchmark cases, profile fixtures, correctness
invariants, and derived artifacts that other CityJSON projects can consume.
It keeps the corpus contract in one place so generators and benchmark harnesses
do not each invent their own model.

## Repository Layout

- `catalog/` - canonical case definitions and the machine-readable corpus
  catalog.
- `profiles/` - manifest schema plus the concrete profile fixtures referenced
  by the catalog.
- `pipelines/` - corpus build and publication scripts.
- `invariants/` - correctness checks that belong to the corpus, not to a
  specific implementation.
- `artifacts/` - derived benchmark outputs and release metadata.
- `docs/` - repository documentation and the design ADRs.

## Local Workflow

- `just validate-profiles` checks that the catalog and profile fixtures still
  match.
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
- [Corpus design ADR](docs/adr/0009-cityjson-benchmark-corpus-design.md)

## Benchmark Consumers

This corpus is meant to be consumed by tools such as `serde_cityjson`,
`cjlib`, and `cjindex`. Each consumer should adapt to the corpus contract
instead of defining a separate benchmark model.
