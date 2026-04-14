# Artifacts

This directory holds files produced from the source case tree.

These files are useful, but they are not the source of truth. Rebuild them
from `cases/`, `schemas/`, and the scripts when possible.

## What It Contains

- `artifacts/generated/`: synthetic files created by `just generate-data`.
- `artifacts/acquired/`: published external files materialized by the
  acquisition commands.
- `artifacts/benchmark-index.json`: workload artifact index.
- `artifacts/correctness-index.json`: correctness-only case index.

## How To Read The Outputs

Two ideas matter:

- `canonical`: the main shared artifact for the case.
- `benchmark-only`: a useful sibling format for performance work, but not the
  main correctness reference for that case.

Real-data workload cases may list both.

## How To Change It

Do not treat this directory as hand-edited source content. Change the owning
case, schema, or script, then rebuild the artifacts.
