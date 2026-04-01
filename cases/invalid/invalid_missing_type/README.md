# invalid_missing_type

Synthetic invalid CityJSON fixture that omits the top-level `type` marker.
The input is syntactically valid JSON but must be rejected before any geometry
traversal or roundtrip operations.

## Signals

- missing top-level contract fields
- schema-level rejection
- parser error path coverage

## Use

Baseline negative fixture for validation and rejection handling.
