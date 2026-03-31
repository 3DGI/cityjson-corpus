# Case Fixtures

This directory contains one concrete manifest fixture per `cjfake`-generated
catalog case.

Each file is a one-case manifest that should validate against
`../cjfake-manifest.schema.json` and should be referenced from the matching
entry in `catalog/corpus.json`.

Fixtures currently present:

- `spec_geometry_matrix.json`
- `spec_appearance_matrix.json`
- `spec_templates_matrix.json`
- `spec_extensions_feature_stream.json`
- `spec_complete_omnibus.json`
- `stress_geometry_flattening.json`
- `stress_vertex_transform.json`
- `stress_attribute_tree.json`
- `stress_relation_graph.json`
- `stress_deep_boundary.json`
- `stress_composite_value.json`
- `stress_appearance_and_validation.json`

