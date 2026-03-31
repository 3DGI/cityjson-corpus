# spec_complete_omnibus

Deterministic synthetic omnibus that covers the broad CityJSON surface as far
as the generator and post-processing pipeline allow.

## Signals

- full-stack parser and serializer integration
- broad allocation patterns
- uncommon-field regressions
- roundtrip correctness across mixed shapes

## Use

Repository-wide correctness fixture for parse, validation, and roundtrip
gating. The existing `serde_cityjson` test data `cityjson_fake_complete` is a
good starting point.
