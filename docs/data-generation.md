# Data Generation

`cityjson-benchmarks` keeps the canonical corpus contract under `cases/` and
renders a derived machine-readable index at `catalog/cases.json`. Synthetic
`profile.json` fixtures live inside their owning case directories. Generated
benchmark data is not checked in. The `just generate-data` command
materializes current synthetic workload cases into `artifacts/generated/` and
writes a machine-readable workload index at
`artifacts/benchmark-index.json`.

Real-data corpus members are kept separate. Their acquisition metadata points
at the shared 3DBAG raw-slice acquisition, and `just acquire-3dbag`
materializes the pinned September 3, 2025 release slice under
`artifacts/acquired/3dbag/v20250903/` without checking the CityJSON files into
git. That acquisition now includes both the baseline `10-758-50.city.json`
tile and the published merged `cluster_4x.city.json` stress workload, plus
native `.cjarrow` live-stream files and `.cjparquet` package files for each
workload.

The corpus also carries per-case invariants and invalid fixtures under
[`cases/`](cases/index.md).

## Requirements

- `just`
- `jq`
- `cargo`
- A local sibling checkout of `../cjfake`, or an override via
  `CJFAKE_CARGO_MANIFEST`
- `curl`, `gunzip`, and `sha256sum` for the published 3DBAG acquisition
- A local sibling checkout of `../cjlib`, or an override via
  `CORPUS_CJLIB_CARGO_MANIFEST`, to export the native cityarrow and
  cityparquet artifacts

## Generate The Data

1. Acquire the raw 3DBAG slice: `just acquire-3dbag`.
2. Validate the manifest fixtures: `just validate-profiles`.
3. Generate the benchmark data: `just generate-data`.
4. Inspect `artifacts/benchmark-index.json` for the workload case list and the
   generated/acquired output paths.

Generation is deterministic: each synthetic fixture carries a seed and a fixed
manifest.

## What Is Generated

- Synthetic cases with a `profile.json` entry in `cases/` are emitted as one
  CityJSON file per case.
- Published real-data cases point at the acquired artifacts under
  `artifacts/acquired/3dbag/v20250903/`, including the single-tile baseline
  and merged 4-tile stress case in CityJSON, cityarrow, and cityparquet
  forms.
- Cases without a published acquisition remain metadata-only until their
  consumer-owned pipeline publishes concrete artifacts.

## Integration Plan

The generated index is the handoff point to downstream CityJSON crates.

- `serde_cityjson` consumes the shared benchmark index directly and reads the
  published workload artifacts from this repository.
- `cjlib` can reuse the same shared index for parse, serialize, and roundtrip
  benchmarks.
- `cjindex` keeps its own layout-building prep pipeline and can reuse the raw
  3DBAG acquisition output as its source data.

One corpus contract is shared across these tools. The benchmark repository
is not a Cargo dependency of those crates.
