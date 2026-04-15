# Data Generation

This repo stores case definitions in `cases/`, but not every case artifact is
checked into git.

## Artifact Modes

Each case uses one of these modes:

- `checked-in`: the file already lives in the case folder.
- `generated`: the case folder stores a `profile.json`, and the built output is
  written to `artifacts/generated/`.
- `acquired`: the case folder stores an `acquisition.json`, and a command
  materializes the published file into `artifacts/acquired/`.

## Main Commands

- `just generate-data`: build synthetic workload data and refresh
  `artifacts/benchmark-index.json`.
- `just acquire-3dbag`: materialize the pinned 3DBAG slice.
- `just acquire-basisvoorziening-3d`: materialize the pinned Basisvoorziening
  3D tile.

## Requirements

You need:

- `just`
- `jq`
- `cargo`
- `curl`, `gunzip`, `unzip`, and `sha256sum`
- a sibling checkout of `../cityjson-fake`, or `CJFAKE_CARGO_MANIFEST`
- a sibling checkout of `../cityjson-lib`, or
  `CORPUS_CITYJSON_LIB_CARGO_MANIFEST`

`just lint` and `just docs-build` use the checked-in
`schemas/cityjson-fake-manifest.schema.json`, so they do not require the
`cityjson-fake` checkout.

## Typical Flow

1. Acquire any published real-data cases you need:
   `just acquire-3dbag` and/or `just acquire-basisvoorziening-3d`.
2. Validate generator profiles with `./scripts/validate_profiles.sh`.
3. Run `just generate-data`.
4. Inspect `artifacts/benchmark-index.json`.

Generation is deterministic. Synthetic cases use fixed manifests and seeds.

## Outputs

- Synthetic cases with a `profile.json` entry in `cases/` are emitted as one
  CityJSON file per case.
- Published real-data cases point at the acquired artifacts under
  `artifacts/acquired/3dbag/v20250903/` and
  `artifacts/acquired/basisvoorziening-3d/2022/`, including CityJSON,
  cityjson-arrow, and cityjson-parquet forms for the published workloads, with explicit
  provenance and validation-role metadata per artifact.
- Cases without a published acquisition remain metadata-only until their
  consumer-owned pipeline publishes concrete artifacts.

## How This Fits The Repo

The source of truth stays in `cases/`. Data generation only materializes the
bytes and updates the derived indexes used by consumers.

This keeps the repo readable:

- `cases/` explains intent;
- `artifacts/` holds built outputs;
- `catalog/` and the indexes tell consumers where to look.
