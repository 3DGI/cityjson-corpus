# Cases

This directory is the bootstrap layout for the shared corpus case files.

The first tranche currently mirrors the handcrafted fixtures from
`serde_cityjson/tests/data/v2_0` plus the invalid fixtures used by the corpus
audit. Each case directory owns:

- `case.json` for the case metadata contract
- `invariants.json` for the correctness contract
- the source fixture itself, checked in next to the metadata

The layout is intentionally separate from `catalog/corpus.json`, which remains
the benchmark taxonomy and release index.

Use `just bootstrap-cases` to refresh the migrated fixture tree from the
source repository.
