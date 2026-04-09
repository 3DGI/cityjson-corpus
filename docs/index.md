# cityjson-benchmarks

`cityjson-benchmarks` is the shared benchmark corpus for CityJSON tooling.
The repository defines the corpus contract. Benchmark inputs, validation rules,
and release artifacts are separate from generator and consumer implementations.

## Documentation Map

- [Repository overview](repository/index.md)
- [Catalog overview](catalog/index.md)
- [Derived case catalog](reference/cases.md)
- [Case layout](cases/index.md)
- [Conformance cases](cases/conformance/index.md)
- [Operation cases](cases/operations/index.md)
- [Workload cases](cases/workloads/index.md)
- [Invalid cases](cases/invalid/index.md)
- [Schemas and value glossary](schemas/index.md)
- [Pipelines](pipelines/index.md)
- [Data Generation](data-generation.md)
- [Artifacts](artifacts/index.md)
- [Derived case catalog reference](reference/cases.md)
- [CJFake manifest schema](reference/cjfake-manifest-schema.md)
- [Case schema](reference/case-schema.md)
- [Invariants schema](reference/invariants-schema.md)
- [Acquisition schema](reference/acquisition-schema.md)
- [ADR 0009: CityJSON Benchmark Corpus Design](adr/0009-cityjson-benchmark-corpus-design.md)
- [ADR 0010: Correctness Corpus Coverage and Generated Cases](adr/0010-correctness-corpus-coverage-and-generated-cases.md)

## Local Workflow

- `just lint` validates the case tree, catalog sync, profile fixtures, runs
  ruff check, and checks each checked-in `cases/conformance/v2_0/*.city.json`
  file with `cjval -q`.
- `just sync-catalog` refreshes `catalog/cases.json` and
  `artifacts/correctness-index.json`.
- `just acquire-3dbag` downloads the published 3DBAG slice into
  `artifacts/acquired/`.
- `just generate-data` materializes the synthetic cases into
  `artifacts/generated/` and writes `artifacts/benchmark-index.json`.
