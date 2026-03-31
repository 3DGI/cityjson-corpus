# io_3dbag_cityjson

## Intent

Large real-geometry scan case using plain CityJSON.

## Why This Shape

This is the baseline whole-file representation. Keeping the data monolithic
lets us measure the cost of a single large read, a full parse, and a
whole-document write path without layout tricks hiding the cost.

## Performance Signal

This case surfaces:

- sequential I/O throughput,
- parser throughput on a realistic file,
- peak memory under whole-document load,
- write amplification for a large monolithic output.

## Recommended Use

Use this as the baseline real-geometry I/O case and compare it against the
other layout variants.

