# Shared Corpus

This repository keeps one shared set of cases for test and benchmark work.
Many tools can use the same inputs and the same case meaning.

## Why This Repo Exists

Without a shared corpus, each tool ends up with its own copy of test files,
benchmark inputs, and case naming. That makes results hard to compare and hard
to trust.

This repo avoids that problem by separating:

- the data contract in this repository;
- the code that generates some files;
- the code that consumes the files.

That split keeps the corpus tool-neutral. A parser, validator, converter,
storage engine, viewer, or benchmark harness can all use the same inputs.

## Design Rationale

The corpus follows a few simple rules:

- One case, one folder.
- `case.json` says what the case is.
- `invariants.json` says what must hold true.
- The bytes are checked in, generated, or acquired.
- Derived indexes are rebuilt from the case tree.

This keeps the repo easy to read. You can inspect a case folder and understand
its purpose, source, and expected result without reading generator code.

## Corpus Layers

The corpus has four layers:

- `conformance`: small valid cases that check whether software handles a known
  part of the format correctly.
- `invalid`: small broken cases that should be rejected.
- `operation`: medium cases for common tasks such as filtering, traversal, or
  layout conversion.
- `workload`: larger cases used to measure throughput, memory use, or storage
  layout effects.

The first three layers form the correctness corpus. The last layer is mainly
for performance work.

## How The Corpus Is Created

Each case artifact comes from one of three modes:

- `checked-in`: the file is stored in the case folder.
- `generated`: the case folder stores a profile, and the built file is written
  to `artifacts/generated/`.
- `acquired`: the case folder stores acquisition metadata, and a script
  downloads or materializes the published artifact into `artifacts/acquired/`.

This lets the corpus mix small source-controlled fixtures with large generated
or published files.

## Source And Outputs

- `cases/` is the source of truth.
- `catalog/` and `artifacts/` are derived outputs.
- `schemas/` defines the metadata contract.

## Further Reading

- [Repository Overview](repository/index.md)
- [Case Layout](cases/index.md)
- [Catalog Overview](catalog/index.md)
- [Schemas](schemas/index.md)
- [Artifacts](artifacts/index.md)
- [Contributing](contributing.md)
- [Independent Use](independent-use.md)
- [ADR 0009](adr/0009-cityjson-benchmark-corpus-design.md)
- [ADR 0010](adr/0010-correctness-corpus-coverage-and-generated-cases.md)
