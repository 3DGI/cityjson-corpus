# Catalog

This directory holds the canonical benchmark case catalog.

Put case definitions here when a case needs to be named, classified, and
versioned independently from the tool that generates it.

The catalog is where each case should declare:

- source kind: `synthetic-controlled`, `real-geometry`, or
  `real-geometry-enriched`
- primary system cost: `io`, `allocation`, `memory`, `deserialize`, or
  `serialize`
- secondary costs
- representation and layout
- supported operations and correctness assertions

The intent is to make the benchmark corpus explicit and reusable across
`cjfake`, `cjindex`, `serde_cityjson`, and other consumers.

