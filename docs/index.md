# cityjson-benchmarks

`cityjson-benchmarks` is the ecosystem-independent benchmark corpus repository
for CityJSON tooling.

It owns the benchmark catalog, corpus design notes, corpus manifests,
correctness invariants, and released benchmark artifacts. It does
not replace tool-specific benchmark harnesses. Those tools consume this corpus.
The repository is not part of the `cityjson-rs` ecosystem; it is intended to
serve any CityJSON implementation that wants common benchmark inputs.

## Repository Structure

- `catalog/`
  Canonical benchmark case definitions and the machine-readable catalog in
  `catalog/corpus.json`.
- `profiles/`
  Corpus-defined profiles and manifests plus the machine-readable
  `cjfake-manifest.schema.json`, first consumed by `cjfake` to generate
  benchmark data.
- `profiles/cases/`
  Concrete manifest fixtures that correspond to catalog entries.
- `pipelines/`
  Build steps that run generation, acquisition, packaging, and publication.
- `invariants/`
  Correctness expectations used by roundtrip and operation checks.
- `artifacts/`
  Published or release-ready corpus outputs.
- `docs/`
  Design notes and repository documentation.

## Responsibility Split

- `cjfake`
  First generator implementation for repository-defined manifests.
- `cityjson-benchmarks`
  Canonical corpus catalog, manifests, invariants, and released artifacts.
- `cjindex`, `serde_cityjson`, `cjlib`, `cityarrow`, `cityjson-rs`
  Consumers of the published benchmark data.

The benchmark contract belongs to this repository. Generator and consumer
projects should conform to it without imposing implementation-specific
assumptions on the catalog.

Use [`scripts/validate_profiles.sh`](../scripts/validate_profiles.sh) to check
that the repository profiles still validate and still match the catalog.

## Design Notes

- [ADR 0009: CityJSON Benchmark Corpus Design](adr/0009-cityjson-benchmark-corpus-design.md)
