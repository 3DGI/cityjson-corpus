# Contributing

This page tells you where to make a change and what to rebuild after it.

## Core Rule

- Change the source file that owns the data.
- Rebuild derived outputs instead of editing them by hand.

## What To Edit

- `cases/`: add, change, or remove a case.
- `schemas/`: change JSON rules or controlled values.
- `scripts/` and `pipelines/`: change generation or acquisition logic.
- `docs/` and repo `README.md` files: change published docs.

## After A Case Change

- Run `just sync-catalog`.
- Run `just generate-data` if the case uses generated artifacts.
- Run the matching acquisition command if the case uses acquired artifacts.
- Run `just docs-build`.
- Run `just lint`.

If you remove a case, run `just clean` before rebuilding docs so stale
generated case pages do not remain in the site.

## After A Schema Change

- Update the affected JSON files in `cases/`.
- Run `just sync-catalog`.
- Run `just lint`.
- Run `just docs-build`.

## After A Build Logic Change

- Run the matching command such as `just generate-data`,
  `just acquire-3dbag`, or `just acquire-basisvoorziening-3d`.
- Check the outputs in `artifacts/`.
- Run `just lint`.

## After A Docs Change

- Edit `docs/` for hand-written pages.
- Edit repo `README.md` files for generated docs pages.
- Run `just docs-build`.
