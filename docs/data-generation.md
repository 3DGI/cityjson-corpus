# Data Generation

`cityjson-benchmarks` keeps the canonical corpus contract under `cases/` and
renders a derived machine-readable index at `catalog/cases.json`. Synthetic
`profile.json` fixtures live inside their owning case directories. Generated
benchmark data is not checked in. The `just generate-data` command
materializes current synthetic workload cases into `artifacts/generated/` and
writes a machine-readable workload index at
`artifacts/benchmark-index.json`.

Real-data corpus members are kept separate. Their acquisition metadata points
at shared acquisition scripts rather than checked-in binaries:
`just acquire-3dbag` materializes the pinned September 3, 2025 3DBAG release
slice under `artifacts/acquired/3dbag/v20250903/`, while
`just acquire-basisvoorziening-3d` materializes the pinned 2022
Basisvoorziening 3D tile under `artifacts/acquired/basisvoorziening-3d/2022/`.
Neither workflow checks the large CityJSON files into git. The 3DBAG
acquisition includes both the baseline `10-758-50.city.json` tile and the
published merged `cluster_4x.city.json` stress workload; both real-data
acquisitions also export sibling native `.cjarrow` live-stream files and
`.cjparquet` package files. The acquisition contract now marks which outputs
are canonical shared inputs and which are benchmark-only derived formats.

The corpus also carries per-case invariants and invalid fixtures under
[`cases/`](cases/index.md).

## Requirements

- `just`
- `jq`
- `cargo`
- A local sibling checkout of `../cjfake`, or an override via
  `CJFAKE_CARGO_MANIFEST`
- `curl`, `gunzip`, `unzip`, and `sha256sum` for the published real-data
  acquisitions
- A local sibling checkout of `../cjlib`, or an override via
  `CORPUS_CJLIB_CARGO_MANIFEST`, to export the native cityarrow and
  cityparquet benchmark formats

## Generate The Data

1. Acquire any published real-data cases you need:
   `just acquire-3dbag` and/or `just acquire-basisvoorziening-3d`.
2. Validate the manifest fixtures: `./scripts/validate_profiles.sh`.
3. Generate the benchmark data: `just generate-data`.
4. Inspect `artifacts/benchmark-index.json` for the workload case list and the
   canonical artifacts and sibling benchmark-only derived paths.

Generation is deterministic: each synthetic fixture carries a seed and a fixed
manifest.

## What Is Generated

- Synthetic cases with a `profile.json` entry in `cases/` are emitted as one
  CityJSON file per case.
- Published real-data cases point at the acquired artifacts under
  `artifacts/acquired/3dbag/v20250903/` and
  `artifacts/acquired/basisvoorziening-3d/2022/`, including CityJSON,
  cityarrow, and cityparquet forms for the published workloads, with explicit
  provenance and validation-role metadata per artifact.
- Cases without a published acquisition remain metadata-only until their
  consumer-owned pipeline publishes concrete artifacts.

## Integration Plan

The generated index is the handoff point to downstream CityJSON crates.

- `serde_cityjson` consumes the shared correctness index for the full
  conformance set and reads the published workload artifacts from this
  repository.
- `cityarrow` uses the same shared correctness index for conformance
  coverage; a failing case indicates an incomplete or incorrect
  implementation.
- The current correctness index contains 36 correctness cases, including 28
  conformance fixtures and the invalid and operation cases that live
  alongside them.
- `cjlib` can reuse the same shared index for parse, serialize, and roundtrip
  benchmarks.
- `cjindex` keeps its own layout-building prep pipeline and can reuse the raw
  3DBAG and Basisvoorziening 3D canonical acquisition outputs as source data.

One corpus contract is shared across these tools. The benchmark repository
is not a Cargo dependency of those crates.
