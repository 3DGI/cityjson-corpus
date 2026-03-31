# io_3dbag_cityjson

Monolithic real-geometry 3DBAG case stored as a whole CityJSON file. This is
not generated from `cjfake`; it is the baseline for sequential I/O, parser
throughput, and whole-document memory behavior on a large external slice.

## Signals

- sequential I/O throughput
- parser throughput on a realistic file
- peak memory under whole-document load
- write amplification for a large output

## Use

Baseline real-geometry I/O case for comparison against layout variants.
