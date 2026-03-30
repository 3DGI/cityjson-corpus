# Latest Results

These figures come from `results/latest/summary.md` after running the full
benchmark manifest on 2026-03-30.

The same run also emits `results/latest/summary.csv`, which is the preferred
input for plotting tools and spreadsheet analysis, including the per-run peak
RSS fields.

## High-level Findings

- The Rust baseline stays fastest across every case.
- The native benchmark harness now builds and loads the `release`
  `cjlib-ffi-core` shared library for both Python and C++, instead of relying
  on debug leftovers.
- With that fix in place, the native FFI overhead is small on this machine:
  - Python is roughly `0.93x` to `1.15x` of Rust for `summary`
  - Python is roughly `1.02x` to `1.14x` of Rust for `roundtrip`
  - C++ is roughly `0.95x` to `1.17x` of Rust for `summary`
  - C++ is roughly `0.99x` to `1.09x` of Rust for `roundtrip`
- The wasm benchmark is now a real `wasm32-unknown-unknown` module executed
  through Node.js, not a native fallback:
  - roughly `1.42x` to `3.13x` slower than Rust for `summary`
  - roughly `2.02x` to `4.17x` slower than Rust for `roundtrip`

## Memory Findings

- Peak RSS is recorded for every case, target, and operation tuple, so timing
  and memory regressions can be inspected together.
- The largest single memory spike in the run is the real wasm32 path on
  `3d_basisvoorziening` `roundtrip`: `4110.94 MiB`.
- Average peak RSS for `roundtrip` across the full manifest:
  - C++: `245.69 MiB`
  - Rust: `261.71 MiB`
  - Python: `256.49 MiB`
  - Wasm: `567.78 MiB`
- The memory story is dominated by the largest dataset:
  - `3dbag` `roundtrip` peak RSS:
    Rust `60.46 MiB`, C++ `68.14 MiB`, Python `82.87 MiB`, Wasm `160.30 MiB`
  - `3d_basisvoorziening` `roundtrip` peak RSS:
    Rust `1995.10 MiB`, C++ `1816.97 MiB`, Python `1828.14 MiB`,
    Wasm `4110.94 MiB`

## Real Dataset Highlights

- `3dbag`
  - Rust `roundtrip`: `59.690 ms`, `60.46 MiB`
  - Python `roundtrip`: `63.180 ms` (`1.06x`), `82.87 MiB`
  - C++ `roundtrip`: `61.834 ms` (`1.04x`), `68.14 MiB`
  - Wasm `roundtrip`: `151.420 ms` (`2.54x`), `160.30 MiB`
- `3d_basisvoorziening`
  - Rust `roundtrip`: `1690.771 ms`, `1995.10 MiB`
  - Python `roundtrip`: `1871.080 ms` (`1.11x`), `1828.14 MiB`
  - C++ `roundtrip`: `1758.243 ms` (`1.04x`), `1816.97 MiB`
  - Wasm `roundtrip`: `6506.655 ms` (`3.85x`), `4110.94 MiB`

## Validation Notes

- The full matrix completed: `9 cases x 4 targets x 3 operations = 108` result
  records.
- Every materialized roundtrip artifact in the benchmark run validated with
  `cjval` (`36` outputs total).
- The source `3d_basisvoorziening` file is invalid according to `cjval` in this
  environment, but the roundtrip outputs produced by all benchmark targets
  validated successfully.
