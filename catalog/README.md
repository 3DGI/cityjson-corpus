# Catalog

This directory holds the canonical benchmark case catalog in
[corpus.json](corpus.json).

Each case records the source kind, primary cost, representation, supported
operations, assertions, and, for generated cases, a profile reference under
`profiles/cases/`.

The generated synthetic cases are materialized by `just generate-data`; the
real-geometry cases stay as catalog entries until their acquisition pipeline is
wired in.

Case narratives live in [cases/](cases/README.md).
