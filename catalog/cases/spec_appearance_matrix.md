# spec_appearance_matrix

## Intent

Small synthetic case that exercises materials, textures, and multiple themes
without adding much geometry complexity.

## Why This Shape

Appearance data is easier to measure when the geometry is quiet. The case keeps
the city object graph small so serializer and deserializer overhead around
appearance metadata stays visible.

## Performance Signal

This case surfaces:

- optional-field handling,
- appearance metadata allocation,
- serializer branching,
- object-model size growth from non-geometric payloads.

## Recommended Use

Use this as a spec atom for appearance preservation and for write-path
branching behavior.

