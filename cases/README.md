# Cases

This directory is the canonical shared corpus layout.

Each case directory owns:

- `case.json` for the case metadata contract
- `invariants.json` for the correctness contract
- a checked-in source fixture, `profile.json`, or `acquisition.json` as
  appropriate
- an optional `README.md` for case-specific notes or narratives

The main subtrees are:

- `conformance/v2_0/` for canonical conformance fixtures, minimal valid
  CityJSON 2.0 documents
- `conformance/synthetic/` for generated conformance and omnibus profiles
- `operations/` for medium-size real-data operation kernels
- `workloads/` for synthetic stress fixtures and real-data I/O workloads
- `invalid/` for negative fixtures

Conformance, invalid, and operations cases form the **correctness corpus**.
Each defines invariants that consuming tools must satisfy (e.g. roundtrip
fidelity, expected validation errors). `artifacts/correctness-index.json` is
a derived index of these cases, rendered by `just sync-catalog`.

Workload cases are for **benchmark performance** measurement — throughput and
latency under synthetic stress or real-data I/O loads.

`catalog/cases.json` is a derived index rendered from this tree. Run
`just sync-catalog` after changing case metadata, or use `just lint`
to check that the catalog is in sync.
