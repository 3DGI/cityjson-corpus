# Catalog

This directory holds the canonical benchmark case catalog in
[corpus.json](corpus.json).

Each case records:
- source kind
- primary cost
- representation
- supported operations
- assertions
- profile reference (for generated cases) under `profiles/cases/`

The `just generate-data` command materializes generated synthetic cases. Real-geometry
cases remain as catalog entries until their acquisition pipeline is active.

The shared corpus contract includes explicit invariants and an invalid fixture
tranche, both located in the repository alongside positive cases.

Case narratives are in [cases/](cases/README.md). The migrated fixture layout
begins in [case layout](../cases/index.md).
