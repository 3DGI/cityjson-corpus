# Independent Use

You can use this corpus without using the current CityJSON tools.
The repo gives you the files, the metadata, and the expected behavior.

## Reusable Parts

- `catalog/cases.json`: full case index.
- `artifacts/correctness-index.json`: correctness cases.
- `artifacts/benchmark-index.json`: workload artifacts.
- `schemas/`: metadata contract.
- `cases/` and `artifacts/`: the actual files.

## Typical Uses

- a new parser or validator in another language;
- a database import pipeline;
- a viewer or tiling service;
- a converter between CityJSON and another format;
- a QA tool that checks acceptance and rejection behavior;
- a benchmark harness that wants realistic and synthetic workload inputs.

## Integration Flow

Use this flow:

1. Read `catalog/cases.json` to discover the available cases.
2. Pick the layer you need:
   - correctness work: `conformance`, `invalid`, `operation`;
   - performance work: `workload`.
3. Read each case's `artifact_mode` and `artifact_paths`.
4. Materialize the needed files:
   - checked-in files are already in the repo;
   - generated files come from `just generate-data`;
   - acquired files come from the acquisition commands.
5. Read `invariants.json` to understand the expected behavior.

## Limits

- Some acquired artifacts have upstream licenses. Check `acquisition.json`
  before redistributing them.
- Some generated cases need local tool dependencies to materialize their files.
- Benchmark-only derived artifacts are useful for performance work, but they
  are not the canonical correctness input for the same case.

## Next Pages

- [Catalog Overview](catalog/index.md)
- [Case Layout](cases/index.md)
- [Artifacts](artifacts/index.md)
- [Schemas](schemas/index.md)
