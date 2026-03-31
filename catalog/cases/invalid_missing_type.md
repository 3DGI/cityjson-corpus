# invalid_missing_type

Synthetic invalid CityJSON fixture that omits the top-level `type` marker.
The input is intentionally syntactically valid JSON, but it should be rejected
before any geometry traversal or roundtrip path runs.

## Signals

- missing top-level contract fields
- schema-level rejection
- parser error path coverage

## Use

Baseline negative fixture for validation and rejection handling.
