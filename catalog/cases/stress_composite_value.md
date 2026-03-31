# stress_composite_value

## Intent

Synthetic stress case that mixes composite geometry with heterogeneous
attribute values.

## Why This Shape

This case combines multiple moderate costs rather than one extreme cost. That
makes it useful for observing how the implementation behaves when several
subsystems are active at once.

## Performance Signal

This case surfaces:

- normalization cost across geometry and attributes,
- allocation reuse versus fragmentation,
- intermediate object creation,
- serializer complexity under mixed payloads.

## Recommended Use

Use this as a balanced stress case when you want a realistic mixture rather
than one isolated hot path.

