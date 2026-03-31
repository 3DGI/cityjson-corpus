# spec_templates_matrix

## Intent

Small synthetic case with geometry templates and repeated instances.

## Why This Shape

Templates compress repeated geometry into a small shared definition plus many
instances. That shape is useful because it separates repeated-shape handling
from raw geometry size.

## Performance Signal

This case surfaces:

- template lookup cost,
- instance expansion or indirection cost,
- memory reuse versus duplication,
- serializer behavior when many objects share one geometry source.

## Recommended Use

Use this as a spec atom for template support and for repeated-instance memory
behavior.

