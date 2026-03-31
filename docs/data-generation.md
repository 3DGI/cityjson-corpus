# Data Generation

`cityjson-benchmarks` keeps the benchmark catalog in `catalog/corpus.json`,
the migrated shared case layout under `cases/`, and the synthetic generation
fixtures in `profiles/cases/`. Generated benchmark data is not checked in.
Instead, `just generate-data` materializes the current synthetic cases into
`artifacts/generated/` and writes a machine-readable index at
`artifacts/benchmark-index.json`.

Real-data corpus members are handled separately. Their acquisition metadata
should point at the reusable `cjindex` 3DBAG preparation flow until the corpus
repo can publish its own pinned release artifacts.

The corpus also carries machine-readable invariants in
[`invariants/corpus.md`](invariants/corpus.md), a negative fixture tranche
under [`invalid/`](invalid/index.md), and a schema-backed case bootstrap path
under [`cases/`](cases/index.md).

## Requirements

- `just`
- `jq`
- `cargo`
- a local sibling checkout of `../cjfake`, or an override via
  `CJFAKE_CARGO_MANIFEST`

## Generate The Data

1. Validate the manifest fixtures with `just validate-profiles`.
2. Generate the benchmark data with `just generate-data`.
3. Inspect `artifacts/benchmark-index.json` for the generated case list and
   `artifacts/generated/` for the CityJSON outputs.

The generation step is deterministic because each synthetic fixture carries a
seed and a fixed manifest.

## What Is Generated

- Synthetic cases with a `profile` entry in `catalog/corpus.json` are emitted
  as one CityJSON file per case.
- Real-geometry and invalid cases are listed in the benchmark index but remain
  external for now. They need a separate acquisition or rejection-fixture
  pipeline.

## Integration Plan

The generated index is the handoff point to downstream CityJSON crates.

- `serde_cityjson` should consume the generated synthetic cases for its
  benchmark fixtures instead of maintaining its own benchmark taxonomy.
- `cjlib` should use the same generated index for parse, serialize, and
  roundtrip benches so it measures the same corpus as `serde_cityjson`.
- `cjindex` should consume the synthetic cases from the shared index first and
  reuse the shared real-data acquisition contract for 3DBAG-derived cases
  rather than maintaining a separate corpus model.

The intent is to share one corpus contract, not to make the benchmark
repository a Cargo dependency of those crates.
