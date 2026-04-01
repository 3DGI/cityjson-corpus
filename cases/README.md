# Cases

This directory is the canonical shared corpus layout.

Each case directory owns:

- `case.json` for the case metadata contract
- `invariants.json` for the correctness contract
- a checked-in source fixture, `profile.json`, or `acquisition.json` as
  appropriate
- an optional `README.md` for case-specific notes or narratives

The main subtrees are:

- `conformance/v2_0/` for migrated `serde_cityjson` conformance fixtures,
  materialized as minimal valid CityJSON documents
- `conformance/synthetic/` for generated conformance and omnibus profiles
- `operations/` for medium-size real-data operation kernels
- `workloads/` for synthetic stress fixtures and real-data I/O workloads
- `invalid/` for negative fixtures

`catalog/cases.json` is a derived index rendered from this tree. Run
`just sync-catalog` after changing case metadata, or use `just validate-cases`
to check that the catalog is in sync.

Use `just bootstrap-cases` to refresh the migrated `serde_cityjson`
conformance fixtures from the source repository.
