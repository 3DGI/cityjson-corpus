# Data Generation

`cityjson-benchmarks` keeps the corpus definition in `catalog/corpus.json` and
the synthetic generation fixtures in `profiles/cases/`. Generated benchmark
data is not checked in. Instead, `just generate-data` materializes the current
synthetic cases into `artifacts/generated/` and writes a machine-readable
index at `artifacts/benchmark-index.json`.

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
- Real-geometry cases are listed in the benchmark index but remain external for
  now. They need a separate acquisition or export pipeline.

## Integration Plan

The generated index is the handoff point to downstream CityJSON crates.

- `serde_cityjson` should consume the generated synthetic cases for its
  benchmark fixtures instead of maintaining its own benchmark taxonomy.
- `cjlib` should use the same generated index for parse, serialize, and
  roundtrip benches so it measures the same corpus as `serde_cityjson`.
- `cjindex` should consume the synthetic cases from the shared index first and
  keep its existing 3DBAG-specific acquisition path for the real-geometry
  cases until this repository can publish them directly.

The intent is to share one corpus contract, not to make the benchmark
repository a Cargo dependency of those crates.
