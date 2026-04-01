# Shared Corpus Migration Plan

`cityjson-benchmarks` is the canonical shared corpus repository for CityJSON
tooling. This document describes how the current benchmark catalog functions as
a shared contract rather than as a repo-local benchmark collection.

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

The repository has the correct structure for the shared contract:

- `catalog/corpus.json` is the canonical case catalog
- `catalog/cases/` contains human-readable case narratives
- `invalid/` contains negative fixtures for rejection-path testing
- `invariants/corpus.json` contains machine-readable correctness checks
- `profiles/cases/` contains synthetic manifests
- `docs/adr/0009-cityjson-benchmark-corpus-design.md` defines the corpus
  architecture

Remaining gaps are operational:

- The release/index layer is partially specified.
- Real-data provenance is documented but not yet published as release
  artifacts.
- Downstream consumers carry local benchmark documentation that precedes the
  shared-corpus split.

## Reuse Paths

Two existing projects provide pipeline components.

### `cjfake`

`cjfake` serves as the synthetic generator for the profile fixtures in this
repository.

### `cjindex`

The existing 3DBAG preparation flow in `cjindex` provides the first real-data
acquisition path. It may be extracted into a shared helper if appropriate.

This repository owns the acquisition contract and published release artifacts,
not a competing implementation.

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

Downstream crates consume the shared corpus; they do not recreate it.

- `serde_cityjson` uses the shared corpus for correctness fixtures and
  benchmark inputs.
- `cjlib` uses the same case identifiers for facade-level tests and benchmarks.
- `cjindex` reuses the shared real-data acquisition path for corpus
  preparation.
- Future `arrow` and `parquet` crates use the same identifiers and invariants
  for import/export coverage.

## Immediate Next Steps

1. extend invariants as new catalog entries land
2. grow the invalid tranche with additional rejection cases
3. publish a release index for synthetic outputs
4. reuse the `cjindex` 3DBAG prep flow for the first real-data artifact release
5. point downstream docs and benches at the shared corpus ids
