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

Existing projects provide the necessary building blocks:

- `cjfake` generates deterministic synthetic CityJSON from manifests.
- `cityjson-json` uses a manifest-driven synthetic benchmark setup.
- `3DBAG` and `Basisvoorziening 3D` provide real-geometry data for
  geometry-sensitive workloads.

A corpus with clear systems taxonomy and strict ownership boundaries between
the generator, shared benchmark catalog, and downstream consumers is needed.
The corpus must remain independent of any ecosystem.

## Decision

The corpus resides in its own shared repository. This repository owns:

- the canonical benchmark catalog,
- corpus design notes,
- corpus profiles,
- correctness invariants, and
- released benchmark artifacts.

Generator logic belongs elsewhere. The public contract is independent of any
single implementation's internal model.

## Source Kinds

- `synthetic-controlled` - controlled synthetic fixtures generated from
  manifests when the benchmark needs tight control over data shape,
  allocation behavior, or serialization structure.
- `real-geometry` - preserved real-data slices, typically from `3DBAG` or
  `Basisvoorziening 3D`, when geometry correctness and realistic object
  structure matter.
- `real-geometry-enriched` - preserved real geometry with synthetic
  attributes, metadata, appearance, or other non-geometric surfaces layered
  on top.

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

A single deterministic fake dataset covers the full CityJSON surface to the
extent the generator and post-processing pipeline allow. It is a correctness
fixture, not a primary performance benchmark. The existing `cityjson-json`
test data `cityjson_fake_complete` serves as a starting point.

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

Large cases exercise throughput and memory pressure:

- large `3DBAG` or `Basisvoorziening 3D` scans,
- `feature-files` and other layout variants,
- dense synthetic attribute or relation workloads,
- repeated-instance and template-heavy workloads, and
- appearance-heavy serialization workloads.

## Systems Programming Principles

The corpus surfaces the costs that matter when implementing CityJSON
software:

- I/O behavior and storage-layout sensitivity,
- allocation count and allocation shape,
- peak and steady-state memory use,
- parse and write throughput, and
- roundtrip stability under realistic object graphs.

The catalog makes the intended cost center explicit for each case.

## Role Split

Repository boundaries remain strict:

- `cjfake` is the first generator implementation. It owns manifest ingestion
  and corpus generation.
- `cityjson-benchmarks` owns the canonical catalog, source manifests,
  correctness invariants, and released artifacts.
- Benchmark consumers such as `cjindex`, `cityjson-json`, `cityjson-lib`,
  `cityjson-arrow`, and `cityjson-rs` consume published benchmark data. They do not
  own corpus generation.

`cjfake` ingests manifests directly for both library and CLI use and produces
the benchmark data described by those manifests. The repository specifies this
contract in the `cjfake` manifest schema.

Concrete profile fixtures reside under their owning case directories and are
checked by the repository-side validation script before release.

## Integration Plan

The corpus repository does not own downstream benchmark harnesses. It owns the
shared data package those harnesses consume.

- `cityjson-benchmarks` publishes a generated benchmark index and the
  materialized synthetic outputs from `just generate-data`.
- `cityjson-json` and `cityjson-arrow` stop curating their own conformance subsets
  and instead point their correctness suites at the shared correctness index.
- `cityjson-lib` consumes the same generated synthetic cases for parse, serialize, and
  roundtrip benchmarks.
- `cjindex` consumes the shared synthetic cases and can reuse the shared
  repository acquisition paths for real-geometry data once those inputs are
  published here.

The benchmark contract is centralized without making the corpus repository a
code dependency of the consumer crates.

## Catalog Model

Each benchmark case declares sufficient metadata to remain diagnostic and
reusable across tools.

The minimum catalog model includes:

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
- correctness and performance concerns remain separated,
- real geometry remains available where it matters,
- synthetic generation enables controlled isolation and stress testing, and
- multiple tools consume the same pinned corpus versions.

Tradeoffs:

- the benchmark pipeline needs its own repository and release process,
- some corpora may still be sourced from real datasets or hand-authored
  fixtures, and
- manifests and released artifacts need to stay aligned.
