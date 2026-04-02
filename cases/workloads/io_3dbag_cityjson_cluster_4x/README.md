# io_3dbag_cityjson_cluster_4x

Merged real-geometry 3DBAG workload built from four contiguous published tiles.
This extends the baseline monolithic CityJSON case to a larger, still realistic
whole-document I/O input for memory-growth, cache, and throughput studies.

## Signals

- sequential I/O throughput on a larger real document
- parser throughput beyond the single-tile baseline
- peak memory growth under a realistic 4-tile merged load
- cache behavior under a less cache-friendly working set

## Use

Stress-case real-geometry I/O workload for scaling comparisons against the
single-tile `io_3dbag_cityjson` baseline.
