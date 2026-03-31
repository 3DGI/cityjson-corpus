# cityjson-benchmarks

Ecosystem-independent benchmark corpus, manifests, generation pipelines, and
correctness fixtures for CityJSON tooling.

This repository defines benchmark inputs for CityJSON software in general. It
is not owned by the `cityjson-rs` ecosystem, even if tools from that ecosystem
are early producers or consumers.

The repository is intentionally split into:

- `docs/` for design notes and repository documentation
- `catalog/` for the canonical corpus manifest and case definitions
- `catalog/cases/` for per-case performance and shape notes
- `profiles/` for corpus-defined manifests and the machine-readable
  `cjfake` schema, first consumed by `cjfake`
- `profiles/cases/` for concrete manifest fixtures tied to catalog cases
- `pipelines/` for corpus build and publication steps
- `invariants/` for correctness assertions
- `artifacts/` for release-ready benchmark outputs

The canonical machine-readable catalog lives at
[catalog/corpus.json](catalog/corpus.json). The manifest contract for
generation lives at [profiles/cjfake-manifest.schema.json](profiles/cjfake-manifest.schema.json),
and the concrete profile fixtures live under [profiles/cases/](profiles/cases/).
Producers such as `cjfake` should adapt to this repository's corpus contract
rather than defining it.
