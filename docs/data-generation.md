# Data Generation

`cityjson-benchmarks` keeps the canonical corpus contract under `cases/` and
renders a derived machine-readable index at `catalog/cases.json`. Synthetic
`profile.json` fixtures live inside their owning case directories. Generated
benchmark data is not checked in. The `just generate-data` command
materializes current synthetic cases into `artifacts/generated/` and writes a
machine-readable index at
`artifacts/benchmark-index.json`.

Real-data corpus members are kept separate. Their acquisition metadata
references the `cjindex` 3DBAG preparation flow until this repository
publishes its own pinned release artifacts.

The corpus also carries per-case invariants and invalid fixtures under
[`cases/`](cases/index.md).

## Requirements

- `just`
- `jq`
- `cargo`
- A local sibling checkout of `../cjfake`, or an override via
  `CJFAKE_CARGO_MANIFEST`

## Generate The Data

1. Validate the manifest fixtures: `just validate-profiles`.
2. Generate the benchmark data: `just generate-data`.
3. Inspect `artifacts/benchmark-index.json` for the generated case list and
   `artifacts/generated/` for the CityJSON outputs.

Generation is deterministic: each synthetic fixture carries a seed and a fixed
manifest.

## What Is Generated

- Synthetic cases with a `profile.json` entry in `cases/` are emitted as one
  CityJSON file per case.
- Real-geometry and invalid cases are listed in the benchmark index but remain
  external for now. They need a separate acquisition or rejection-fixture
  pipeline.

## Integration Plan

The generated index is the handoff point to downstream CityJSON crates.

- `serde_cityjson` consumes the generated synthetic cases for benchmark
  fixtures instead of maintaining its own benchmark taxonomy.
- `cjlib` uses the same generated index for parse, serialize, and roundtrip
  benchmarks to measure the same corpus as `serde_cityjson`.
- `cjindex` consumes the synthetic cases from the shared index and reuses the
  shared real-data acquisition contract for 3DBAG-derived cases instead of
  maintaining a separate corpus model.

One corpus contract is shared across these tools. The benchmark repository
is not a Cargo dependency of those crates.
