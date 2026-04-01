# Catalog

This directory holds the derived machine-readable case index in
[cases.json](cases.json).

The source of truth lives under [`cases/`](../cases/README.md). Each catalog
entry is rendered from a case directory and adds the repo-relative pointers
that downstream consumers need:

- the case directory path
- the owning `case.json`
- the owning `invariants.json`
- optional `README.md`
- artifact paths for checked-in fixtures, generated outputs, profiles, or
  acquisition metadata

Run `just sync-catalog` after changing the case tree. `just validate-cases`
checks that `cases.json` is in sync.
