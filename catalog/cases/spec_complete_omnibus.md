# spec_complete_omnibus

## Intent

Single deterministic fake dataset that covers the full CityJSON surface as far
as the generator and post-processing pipeline allow.

## Why This Shape

This case is intentionally broad. It includes enough of the specification
surface to act as a correctness omnibus, but it is not trying to isolate one
single hot path.

The existing `serde_cityjson` test data `cityjson_fake_complete` is a good
starting point for this case.

## Performance Signal

This case surfaces:

- full-stack parser and serializer integration,
- broad allocation patterns,
- accidental regressions in uncommon fields or combinations,
- roundtrip correctness under mixed object shapes.

## Recommended Use

Use this as the repository-wide correctness fixture. It should gate parse,
validate, and roundtrip behavior, but it should not be used as the primary
performance comparison case.

