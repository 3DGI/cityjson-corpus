# Schemas

This directory holds the JSON rules for the shared corpus metadata.

## Main Files

The main schema files are:

- [case.schema.json](case.schema.json)
- [invariants.schema.json](invariants.schema.json)
- [acquisition.schema.json](acquisition.schema.json)
- [cityjson-fake-manifest.schema.json](cityjson-fake-manifest.schema.json)

`cases/` contains the actual JSON files. `schemas/` explains what shape those
files must have and what the controlled values mean.

## Value Glossary

This is the canonical place that explains the shared vocabulary. If a field is
listed here, tools should read it with the meaning given below.

### Case Schema

| Field            | Values                                                                                       | Meaning                                                                                                                                                                                                                                                                                                                                   |
|------------------|----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `layer`          | `conformance`, `operation`, `workload`, `invalid`                                            | `conformance` and `invalid` are correctness cases, `operation` covers correctness-oriented kernels, and `workload` covers performance cases.                                                                                                                                                                                              |
| `artifact_mode`  | `checked-in`, `generated`, `acquired`                                                        | `checked-in` means the source artifact lives in the case directory, `generated` means `just generate-data` materializes it, and `acquired` means the artifact is pulled from published upstream data.                                                                                                                                     |
| `source_kind`    | `synthetic`, `real-geometry`, `real-geometry-enriched`                                       | `synthetic` means a controlled synthetic fixture, `real-geometry` means preserved real data, and `real-geometry-enriched` means real geometry with synthetic additions.                                                                                                                                                                   |
| `representation` | `cityjson`, `cityjsonfeature`, `jsonl`, `feature-files`                                      | `cityjson` is a single CityJSON file, `cityjsonfeature` is CityJSON Feature, `jsonl` is a JSON Lines stream, and `feature-files` is a split feature-file layout.                                                                                                                                                                          |
| `geometry_kind`  | `dummy`, `real-preserved`                                                                    | `dummy` means the geometry is synthetic or placeholder geometry, and `real-preserved` means the original real geometry is kept intact.                                                                                                                                                                                                    |
| `family`         | current corpus labels: `spec_atom`, `omnibus`, `invalid`, `io`, `operation_kernel`, `stress` | This is a taxonomy bucket for browsing and grouping, not a control field. `spec_atom` is a single spec atom or narrow feature slice, `omnibus` is broader mixed coverage, `invalid` is negative coverage, `io` is real-data I/O, `operation_kernel` is a real-data operation kernel, and `stress` is synthetic benchmark stress coverage. |
| `assertions`     | case-specific strings                                                                        | These are human-readable correctness expectations for the case. They are not a separate controlled vocabulary and are not interpreted as machine-executable assertions.                                                                                                                                                                   |

### Acquisition Schema

| Field             | Values                                  | Meaning                                                                                                                                                                                                 |
|-------------------|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `status`          | `planned`, `published`                  | `planned` means the acquisition is described but not yet available as a published source, and `published` means the upstream source exists and can be acquired.                                      |
| `outputs[].producer` | free-form strings such as `upstream`, `cjio`, `cityjson-lib`, `cjindex` | Names the system that produced the artifact. This distinguishes upstream source files from locally derived benchmark formats.                                                                          |
| `outputs[].derivation` | `acquired`, `merged`, `exported`, `materialized` | `acquired` means the artifact is preserved from the source dataset, `merged` means multiple source artifacts were combined, `exported` means a sibling format was written from another artifact, and `materialized` means a consumer pipeline produced a benchmark layout. |
| `outputs[].validation_role` | `canonical`, `benchmark-only`        | `canonical` means consumers may treat the artifact as the authoritative shared corpus input for that case. `benchmark-only` means the artifact is a useful benchmark format, but not an independent correctness oracle for the same producer. |

### Invariants Schema

| Field  | Values                 | Meaning                                                                                                                                                                                                                                |
|--------|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `kind` | `positive`, `negative` | `positive` means the fixture is expected to be accepted and satisfy the listed checks. `negative` means the fixture is expected to be rejected, so the invariants file must also name the input fixture and expected rejection result. |

## How To Change It

1. Edit the schema file in this directory.
2. Update the glossary text if you changed a controlled value.
3. Update the matching JSON files under [`cases/`](../cases/README.md).
4. Run `just lint`.

Keep schema changes small and explicit. Most downstream consumers depend on
these fields staying stable.

The checked-in `cityjson-fake-manifest.schema.json` is the repo-local copy used
by `just lint` and `just docs-build`. Keep it aligned with the upstream
`cityjson-fake` schema when the generator contract changes.
