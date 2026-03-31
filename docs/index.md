# cityjson-benchmarks

`cityjson-benchmarks` is the shared benchmark corpus for CityJSON tooling.
The repository defines the corpus contract and keeps benchmark inputs,
validation rules, and release artifacts separate from generator and consumer
implementations.

## What Lives Here

- `catalog/` - canonical benchmark cases and the machine-readable corpus
  catalog.
- `profiles/` - manifest schema plus the concrete profile fixtures referenced
  by the catalog.
- `pipelines/` - corpus build and publication scripts.
- `invariants/` - correctness checks that belong to the corpus, not to a
  specific tool.
- `artifacts/` - derived benchmark outputs and release metadata.
- `docs/` - design notes and repository documentation.

## Current Workflow

- `just validate-profiles` checks that catalog entries and profile fixtures
  still match.
- `just audit-corpus` runs validation and writes a summary artifact to
  `artifacts/corpus-audit.json`.

## Design Notes

- [ADR 0009: CityJSON Benchmark Corpus Design](adr/0009-cityjson-benchmark-corpus-design.md)
