# ADR 0009: CityJSON Benchmark Corpus Design

## Status

Accepted.

## Context

This repository defines a shared CityJSON benchmark corpus with three goals:

1. exercise the CityJSON specification surface as completely as practical,
2. provide realistic data shapes for correctness testing of common 3D city
   model operations, and
3. expose the system costs that matter in CityJSON tooling: I/O, allocation,
   memory use, and de/serialization.

Existing projects already provide the main building blocks:

- `cjfake` can generate deterministic synthetic CityJSON from manifests.
- `serde_cityjson` already uses a manifest-driven synthetic benchmark setup.
- `3DBAG` is a strong real-geometry source for geometry-sensitive workloads.

The missing piece is a corpus with a clear systems taxonomy and a strict
ownership boundary between the generator, the shared benchmark catalog, and
downstream consumers. The corpus should stay ecosystem-independent.

## Decision

The corpus lives in its own shared repository. This repository owns:

- the canonical benchmark catalog,
- corpus design notes,
- corpus profiles,
- correctness invariants, and
- released benchmark artifacts.

Generator logic belongs elsewhere, and the public contract stays independent
from any single implementation's internal model.

## Source Kinds

- `synthetic-controlled` - generated from manifests when the benchmark needs
  tight control over data shape, allocation behavior, or serialization
  structure.
- `real-geometry` - untouched `3DBAG` slices when geometry correctness and
  realistic object structure matter.
- `real-geometry-enriched` - `3DBAG` geometry augmented with synthetic
  attributes, metadata, appearance, or other non-geometric surfaces.

## Taxonomy

The benchmark taxonomy is organized by primary system bottleneck, not by
CityJSON feature category.

The top-level benchmark families are:

- I/O-bound cases
- allocation-bound cases
- memory-efficiency cases
- de/serialization cases

Spec coverage still matters, but it is a control variable rather than the
primary benchmark axis.

Each benchmark case should have one dominant cost center and only a few
secondary ones. If a case changes geometry depth, attribute depth, hierarchy,
appearance, and storage layout all at once, it stops being diagnostic.

## Corpus Layers

The corpus has four layers.

### 1. Spec atoms

Small, focused cases that each exercise one spec surface or one narrow
combination of surfaces. They answer questions such as whether a reader
handles `transform` correctly, a writer preserves appearance or semantics,
hierarchy survives a roundtrip, or feature-stream and extension paths still
work.

### 2. Spec complete omnibus

A single deterministic fake dataset should cover the full CityJSON surface as
far as the generator and post-processing pipeline allow. It is a correctness
fixture, not a primary performance benchmark. The existing `serde_cityjson`
test data `cityjson_fake_complete` is a good starting point.

### 3. Operation kernels

Medium-sized cases are designed around common 3D city model operations:

- bounding box and extent queries,
- object filtering and traversal,
- hierarchy navigation,
- feature extraction and split or merge workflows,
- vertex compaction and reindexing,
- semantic surface queries, and
- layout conversion.

These cases should be realistic enough to exercise implementation code paths
while remaining controlled enough to attribute cost and correctness failures.

### 4. Stress workloads

Large cases are used for throughput and memory pressure:

- large `3DBAG` scans,
- `feature-files` and other layout variants,
- dense synthetic attribute or relation workloads,
- repeated-instance and template-heavy workloads, and
- appearance-heavy serialization workloads.

## Systems Programming Principles

The corpus should surface the costs that matter when implementing CityJSON
software:

- I/O behavior and storage-layout sensitivity,
- allocation count and allocation shape,
- peak and steady-state memory use,
- parse and write throughput, and
- roundtrip stability under realistic object graphs.

The catalog should make the intended cost center explicit for every case.

## Role Split

Repository boundaries should stay strict:

- `cjfake` is the first generator implementation and owns manifest ingestion
  plus corpus generation work.
- `cityjson-benchmarks` owns the canonical catalog, source manifests,
  correctness invariants, and released artifacts.
- benchmark consumers such as `cjindex`, `serde_cityjson`, `cjlib`,
  `cityarrow`, and `cityjson-rs` consume the published benchmark data and
  should not own corpus generation.

`cjfake` should ingest manifests directly for both library and CLI use and
produce the benchmark data described by those manifests. The repository keeps
that contract explicit in `profiles/cjfake-manifest.schema.json`.

Concrete profile fixtures should live under `profiles/cases/` and be checked by
the repository-side validation script before release.

## Catalog Model

Each benchmark case should declare enough metadata to stay diagnostic and
reusable across tools.

The minimum catalog model is:

- source kind: `synthetic-controlled`, `real-geometry`, or
  `real-geometry-enriched`
- primary cost: `io`, `allocation`, `memory`, `deserialize`, or `serialize`
- secondary costs
- geometry validity: `dummy` or `real-preserved`
- representation: `cityjson`, `cityjsonfeature`, `jsonl`, `feature-files`, or
  another layout variant
- working-set scale
- supported operations
- correctness assertions

## Consequences

Positive:

- the benchmark corpus has a clear engineering purpose,
- the benchmark corpus remains usable outside the `cityjson-rs` ecosystem,
- correctness and performance concerns stay separated,
- real geometry remains available where it matters,
- synthetic generation remains useful for controlled isolation and stress, and
- multiple tools can consume the same pinned corpus versions.

Tradeoffs:

- the benchmark pipeline needs its own repository and release process,
- some corpora may still be sourced from real datasets or hand-authored
  fixtures, and
- manifests and released artifacts need to stay aligned.
