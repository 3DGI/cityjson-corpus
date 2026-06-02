# Prepare Real-Data Layouts And Summaries

## Summary

Extend on-demand acquisition to prepare all published 3DBAG layouts, replace
overlapping operation cases with one compact fixture, and write machine-readable
summaries into generated acquisition manifests. Keep Basisvoorziening 3D
I/O-only.

## Interfaces

- Standardize ignored `artifacts/acquired/**/manifest.json` files with
  `version: 1` and per-output `case_ids`, provenance, checksum, byte size, and
  `summary`.
- Define `summary` fields: `cityjson_version`, `reference_system`,
  `geographical_extent`, `feature_count`, `cityobject_count`,
  `cityobject_types`, `vertex_count`, `geometry_types`, `lods`,
  `semantic_surface_types`, and `attribute_keys`.
- Define `feature_count` as root CityObject count. For JSONL and feature-files,
  aggregate all feature packages.
- Add `subset` to the acquisition derivation vocabulary.

## Implementation

- Add a typed standard-library Python helper under `scripts/` with:
  - `describe`: summarize CityJSON, JSONL, or feature-file directories and
    compute SHA-256 plus byte size.
  - `split-feature-files`: split validated JSONL into `metadata.json` and
    `features/<id>.city.jsonl`.
  - Deterministic directory checksums over sorted relative paths and file bytes.
- Update `scripts/acquire_3dbag.sh`:
  - Resolve `CORPUS_CJIO_SPEC`, defaulting to `cjio==0.10.1`.
  - Keep the raw tile and merged cluster.
  - Export `10-758-50.city.jsonl`.
  - Materialize `10-758-50.feature-files/`.
  - Create `ops_3dbag.city.json` with
    `cjio subset --id NL.IMBAG.Pand.0928100000037540`.
  - Emit descriptors and summaries for all five outputs.
- Update `scripts/acquire_basisvoorziening_3d.py` to emit the same descriptor
  and summary shape for its CityJSON output only.
- Replace `ops_3dbag_base`, `ops_3dbag_enriched`, and
  `ops_3dbag_semantic_surfaces` with one `ops_3dbag` case. Preserve their useful
  assertions in the consolidated fixture.
- Publish concrete JSONL and feature-files acquisitions. Remove stale `cjarrow`
  and `cjparquet` promises from case metadata and docs.
- Refresh the derived catalog and correctness index. Document the generated
  manifest contract and note that `just clean` removes older unreferenced
  acquired outputs.

## Test Plan

- Add helper unit tests for CityJSON summaries, JSONL aggregation, feature-file
  splitting, deterministic directory hashes, malformed headers, duplicate IDs,
  and unsafe feature IDs.
- Run `just sync-catalog`, `just lint`, `just test`, and `just docs-build`.
- Smoke-test both acquisition commands and inspect generated manifests.
- Verify default 3DBAG results:
  - Raw tile: `1,898` CityObjects and `949` root features.
  - JSONL and feature-files: equivalent aggregate counts and `949` feature
    packages.
  - Compact ops fixture: `2` CityObjects, `16` vertices, attributes, hierarchy,
    LoDs, and semantic surfaces.
  - Cluster: `6,924` CityObjects.
- Verify Basisvoorziening summary: `49,663` CityObjects and `40,313` root
  features.

## Assumptions

- Actual summaries belong only in generated manifests, not duplicated in
  checked-in acquisitions.
- JSONL and feature-files remain benchmark-only derived layouts.
- Basisvoorziening 3D does not gain operation cases.
