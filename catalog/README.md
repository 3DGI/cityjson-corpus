# Catalog

This directory holds the derived machine-readable case index.

The source of truth is [`cases/`](../cases/README.md). The catalog is rebuilt
from that tree.

## Main File

- [cases.json](cases.json)

## What It Contains

Each catalog entry points to:

- the case folder;
- `case.json`;
- `invariants.json`;
- optional `README.md`;
- any checked-in, generated, or acquired artifact paths named by the case.

## How To Use It

Use the catalog when you want to:

- list all cases;
- filter by layer, family, artifact mode, or representation;
- find the files owned by a case without walking the repo tree yourself.

## How To Change It

Run `just sync-catalog` after changing `cases/`.

Do not edit `cases.json` by hand.
