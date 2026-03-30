# Implementation Plan

## Goal

Measure end-to-end overhead for:

- Rust `cjlib`
- Python FFI
- C++ FFI
- wasm-facing wrapper through Node

The benchmark must use:

- real datasets from `~/Development/serde_cityjson`
- synthetic datasets generated from `~/Development/cjfake`
- `cjval` as the validity gate for all produced CityJSON outputs

## Operations

Each target must implement the same benchmark operations:

1. `probe`
2. `summary`
3. `roundtrip`

`roundtrip` means parse the input, serialize a CityJSON document, write one
materialized output artifact, and make that artifact available for `cjval`.

## Datasets

The first benchmark matrix includes:

- `3dbag` from `serde_cityjson/tests/data/downloaded/10-356-724.city.json`
- `3d_basisvoorziening` from `serde_cityjson/tests/data/downloaded/30gz1_04.city.json`
- synthetic `cjfake` cases derived from the `serde_cityjson` benchmark profiles

## Parallel Worktree Split

### Trunk

Ownership:

- shared manifest and benchmark contract
- dataset preparation
- validation and reporting
- integration and merge

### Worktree: `native-bindings`

Ownership:

- Python benchmark driver
- C++ benchmark driver
- native build glue

### Worktree: `rust-wasm`

Ownership:

- Rust baseline driver
- Node and wasm benchmark driver
- wasm packaging glue

## Output

The benchmark run must emit:

- machine-readable results
- a Markdown summary with per-target overhead ratios and peak RSS
- roundtrip output files for inspection
- validation status per target and dataset
