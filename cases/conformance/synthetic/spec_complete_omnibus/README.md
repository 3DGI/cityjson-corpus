# spec_complete_omnibus

Deterministic synthetic omnibus case (`seed 1005`) with 6 `Building`/`Bridge`
city objects, the full geometry matrix, LoDs 0-3, 8-16 vertices in
`[-500, 500]`, geometry hierarchies with 1-2 children, materials and textures
enabled, geometry templates enabled, attributes enabled with nesting depth 3,
and semantics enabled for the full surface set.

## Signals

- full-stack parser and serializer integration
- broad allocation patterns
- uncommon-field regressions
- roundtrip correctness across mixed shapes

## Use

Repository-wide correctness fixture for parse, validation, and roundtrip
gating. The existing `serde_cityjson` test data `cityjson_fake_complete` serves
as a starting point.
