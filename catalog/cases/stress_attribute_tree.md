# stress_attribute_tree

## Intent

Synthetic stress case with deep and heterogeneous nested attributes.

## Why This Shape

Attribute recursion and mixed map/list/scalar nodes create allocation churn
that is easy to underestimate in shallow cases. The geometry should stay
minimal so the attribute tree remains the dominant cost.

## Performance Signal

This case surfaces:

- recursive conversion cost,
- hash map and vector growth,
- short-lived allocation churn,
- serializer cost for deeply nested non-geometric data.

## Recommended Use

Use this when you want to see how attribute-heavy payloads behave in memory
and during de/serialization.

