# io_basisvoorziening_3d_cityjson

Monolithic real-geometry Basisvoorziening 3D case stored as a whole CityJSON
file. This complements the `io_3dbag_cityjson` baseline with a larger
terrain-inclusive Dutch tile from the published 2022 PDOK collection.

## Signals

- sequential I/O throughput on a larger real document
- parser throughput on mixed building-and-terrain geometry
- peak memory under whole-document load
- write amplification for a large output

## Use

Alternative real-geometry I/O baseline for comparisons against the existing
3DBAG case when dataset composition and document size matter.
