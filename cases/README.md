# Cases

This directory is the canonical shared corpus layout.

Each case directory owns:

- `case.json` for the case metadata contract
- `invariants.json` for the correctness contract
- a checked-in source fixture, `profile.json`, or `acquisition.json` as
  appropriate
- an optional `README.md` for case-specific notes or narratives

The main subtrees are:

- `conformance/v2_0/` for reviewed normative conformance fixtures
- `conformance/synthetic/` for supplemental generated conformance coverage
- `operations/` for medium-size real-data operation kernels
- `workloads/` for synthetic stress fixtures and real-data I/O workloads
- `invalid/` for negative fixtures

Conformance, invalid, and operation cases form the **correctness corpus**.
The default gate is the reviewed normative subset; the correctness index also
includes supplemental generated conformance cases for broader interaction
coverage. Each correctness case defines invariants that consuming tools must
satisfy (e.g. roundtrip fidelity, expected validation errors).
`artifacts/correctness-index.json` is a derived index of these cases,
rendered by `just sync-catalog`.

Workload cases are for **benchmark performance** measurement — throughput and
latency under synthetic stress or real-data I/O loads.

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
