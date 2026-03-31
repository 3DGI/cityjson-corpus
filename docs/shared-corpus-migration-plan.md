# Shared Corpus Migration Plan

`cityjson-benchmarks` is the canonical shared corpus repo for CityJSON
tooling. This page describes how the current benchmark catalog should be
treated as a shared contract rather than as a repo-local benchmark stash.

## What This Repository Owns

This repository owns the corpus contract:

- canonical case ids
- case metadata
- correctness invariants
- synthetic profiles
- real-data acquisition metadata
- released benchmark artifacts

It does not own parser or serializer implementation code, generator internals,
or downstream harness logic.

## Current State

The repository already has the right shape for the shared contract:

- `catalog/corpus.json` is the canonical case catalog
- `catalog/cases/` contains the human-readable case narratives
- `invalid/` contains the negative fixtures used for rejection paths
- `invariants/corpus.json` contains the machine-readable correctness checks
- `profiles/cases/` contains the synthetic manifests
- `docs/adr/0009-cityjson-benchmark-corpus-design.md` defines the corpus
  architecture

The gaps are now mostly operational:

- the release/index layer is still only partially specified
- real-data provenance is described, but not yet published as release
  artifacts
- downstream consumers still carry local benchmark wording that predates the
  shared-corpus split

## Reuse Paths

Two existing projects already provide the hard parts of the pipeline.

### `cjfake`

Use `cjfake` as the synthetic generator behind the profile fixtures in this
repository.

### `cjindex`

Use the existing 3DBAG prep flow in `cjindex` as the first real-data
acquisition path, or extract it into a shared helper if that turns out to be
cleaner.

The important boundary is that this repository owns the acquisition contract
and the published release artifacts, not a second competing prep
implementation.

## Migration Phases

### Phase 1. Freeze ids and metadata

- keep the current benchmark ids stable
- add explicit metadata for every case
- make the current synthetic profiles and real-data entries the source of
  truth for the catalog

### Phase 2. Add corpus invariants

- publish and maintain machine-readable invariants for the existing cases
- keep the first invalid corpus tranche in sync with the catalog
- make correctness expectations corpus-owned rather than consumer-owned

### Phase 3. Publish releases

- materialize synthetic artifacts under a pinned release index
- publish real-data artifacts with checksums and provenance
- document the release boundary so downstream crates can consume pinned inputs
  without rerunning generators

### Phase 4. Trim duplicates

- remove repo-local benchmark taxonomy from consumers
- keep only temporary bootstrap copies where they are needed for transition

## Consumer Boundary

Downstream crates should consume the shared corpus, not recreate it.

- `serde_cityjson` should use the shared corpus for correctness fixtures and
  benchmark inputs
- `cjlib` should use the same case ids for facade-level tests and benchmarks
- `cjindex` should reuse the shared real-data acquisition path for corpus
  preparation
- future `arrow` and `parquet` crates should use the same ids and invariants
  for import/export coverage

## Immediate Next Steps

1. extend invariants as new catalog entries land
2. grow the invalid tranche with additional rejection cases
3. publish a release index for synthetic outputs
4. reuse the `cjindex` 3DBAG prep flow for the first real-data artifact release
5. point downstream docs and benches at the shared corpus ids
