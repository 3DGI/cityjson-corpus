# cityjson-benchmarks

`cityjson-benchmarks` is the shared benchmark corpus repository for CityJSON
tooling.

It owns the benchmark catalog, corpus design notes, derived corpus
definitions, correctness invariants, and released benchmark artifacts. It does
not replace tool-specific benchmark harnesses. Those tools consume this corpus.

## Repository Structure

- `catalog/`
  Canonical benchmark case definitions and manifest-level metadata.
- `profiles/`
  Synthetic and derived-data profiles that feed corpus generation.
- `pipelines/`
  Build steps that generate or derive benchmark corpora.
- `invariants/`
  Correctness expectations used by roundtrip and operation checks.
- `artifacts/`
  Published or release-ready corpus outputs.
- `docs/`
  Design notes and repository documentation.

## Responsibility Split

- `cjfake`
  Synthetic generator and manifest ingestion for synthetic-controlled cases.
- `cjindex`
  Real-data reshaping and layout derivation for benchmark preparation.
- `cityjson-benchmarks`
  Canonical corpus catalog, derived-case definitions, invariants, and released
  artifacts.

## Design Notes

- [ADR 0009: CityJSON Benchmark Corpus Design](adr/0009-cityjson-benchmark-corpus-design.md)

