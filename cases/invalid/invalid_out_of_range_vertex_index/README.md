# invalid_out_of_range_vertex_index

Synthetic invalid CityJSON fixture that references a vertex index outside the
available vertex array. The input is valid JSON, but geometry validation
should reject it as an out-of-range boundary reference.

## Signals

- invalid geometry index handling
- semantic validation rejection
- parser error path coverage

## Use

Baseline negative fixture for invalid boundary and vertex-reference checks.
