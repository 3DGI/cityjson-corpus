# Cases

This directory is the canonical shared corpus layout.

Each case directory owns:

- `case.json` for the case metadata contract
- `invariants.json` for the correctness contract
- a checked-in source fixture, `profile.json`, or `acquisition.json` as
  appropriate
- an optional `README.md` for case-specific notes or narratives

The canonical meaning of schema values such as `layer`, `artifact_mode`,
`source_kind`, `representation`, `geometry_kind`, `family`, and
`status` is documented in [`schemas/README.md`](../schemas/README.md).

The main subtrees are:

- `conformance/v2_0/` for checked-in conformance fixtures
- `conformance/synthetic/` for generated conformance coverage
- `operations/` for medium-size real-data operation kernels
- `workloads/` for synthetic stress fixtures and real-data I/O workloads
- `invalid/` for negative fixtures

Conformance, invalid, and operation cases form the **correctness corpus**.
Each correctness case defines invariants that consuming tools must satisfy
(e.g. roundtrip fidelity, expected validation errors).
Generated conformance cases are part of the same corpus when their artifacts
are materialized.
`artifacts/correctness-index.json` is a derived index of these cases,
rendered by `just sync-catalog`.

Workload cases are for **benchmark performance** measurement — throughput and
latency under synthetic stress or real-data I/O loads.

Acquired workload metadata can declare multiple published outputs. The
acquisition contract marks which one is the canonical shared input and which
ones are benchmark-only derived artifacts.

`catalog/cases.json` is a derived index rendered from this tree. Run
`just sync-catalog` after changing case metadata, or use `just lint`
to check that the catalog is in sync.

## Adding Or Removing Cases

To add a case, create a new directory under the appropriate subtree and add
the files that match the case type:

- `case.json` and `invariants.json` are required for every case
- checked-in fixtures use a source file in the case directory
- synthetic workload cases use `profile.json`
- real-data workload or operation cases use `acquisition.json`

After adding the case, run:

- `just sync-catalog`
- `just generate-data` for workload cases that need generated or acquired outputs
- `uv run python ./scripts/generate_docs.py` or `just docs-build`
- `just lint`

To remove a case, delete the case directory and its generated docs page under
`docs/cases/...`, then rerun the same regeneration steps. Stale generated docs
pages are not removed automatically.
