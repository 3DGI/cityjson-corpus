# cityjson-benchmarks

`cityjson-benchmarks` is the shared benchmark corpus for CityJSON tooling.
The repository defines the corpus contract and keeps benchmark inputs,
validation rules, and release artifacts separate from generator and consumer
implementations.

## Documentation Map

- [Repository overview](repository/index.md)
- [Corpus catalog](catalog/index.md)
- [Case catalog](catalog/cases/index.md)
- [Case layout](cases/index.md)
- [Profiles](profiles/index.md)
- [Profile fixtures](profiles/cases/index.md)
- [Pipelines](pipelines/index.md)
- [Data Generation](data-generation.md)
- [Shared Corpus Migration Plan](shared-corpus-migration-plan.md)
- [Invariants](invariants/index.md)
- [Corpus invariants](invariants/corpus.md)
- [Invalid fixtures](invalid/index.md)
- [Artifacts](artifacts/index.md)
- [Corpus catalog reference](reference/corpus.md)
- [CJFake manifest schema](reference/cjfake-manifest-schema.md)
- [ADR 0009: CityJSON Benchmark Corpus Design](adr/0009-cityjson-benchmark-corpus-design.md)

## Local Workflow

- `just validate-profiles` checks that catalog entries and profile fixtures
  still match.
- `just generate-data` materializes the synthetic cases into
  `artifacts/generated/` and writes `artifacts/benchmark-index.json`.
- `just audit-corpus` runs validation and writes a summary artifact to
  `artifacts/corpus-audit.json`.
