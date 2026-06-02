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
  3D tile via the PDOK OGC API.

## Requirements

You need:

- `just`
- `jq`
- `cargo`
- `curl`, `gunzip`, `python3`, and `uvx`
- a sibling checkout containing `../cityjson-rs/crates/cityjson-fake`, or
  `CJFAKE_CARGO_MANIFEST`

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
  `artifacts/acquired/basisvoorziening-3d/2022/`. The 3DBAG command emits
  CityJSON, JSONL, feature-files, and a compact operation subset.
- Acquisition manifests record provenance, validation roles, checksums, byte
  sizes, and machine-readable CityJSON summaries per artifact.

## Generated Acquisition Manifests

Each acquisition command writes an ignored `manifest.json` next to its outputs.
These generated manifests use `version: 1` and record `case_ids`, provenance,
checksum, byte size, and a `summary` for every output. Summaries include feature
and CityObject counts, CityObject types, vertex count, geometry types, LoDs,
semantic surface types, attribute keys, CRS, and geographical extent.

File artifacts use their SHA-256 digest. Directory artifacts use a deterministic
SHA-256 digest over sorted relative paths and file bytes; `byte_size` is the sum
of contained file sizes. Run `just clean` when older ignored acquisitions should
be removed after the output set changes.

## How This Fits The Repo

The source of truth stays in `cases/`. Data generation only materializes the
bytes and updates the derived indexes used by consumers.

This keeps the repo readable:

- `cases/` explains intent;
- `artifacts/` holds built outputs;
- `catalog/` and the indexes tell consumers where to look.
