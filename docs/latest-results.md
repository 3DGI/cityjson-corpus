# Latest Results

These figures come from `results/latest/summary.md` after running the full
benchmark manifest on 2026-03-30.

The same run also emits `results/latest/summary.csv`, which is the preferred
input for plotting tools and spreadsheet analysis, including the per-run peak
RSS fields.

## High-level Findings

- The Rust baseline stays fastest across every case.
- The Python binding is consistently the most expensive wrapper:
  - roughly `7.42x` to `18.64x` slower than Rust for `summary`
  - roughly `11.85x` to `30.52x` slower than Rust for `roundtrip`
- The C++ binding is materially cheaper than Python but still clearly above the
  Rust baseline:
  - roughly `7.51x` to `18.47x` slower than Rust for `summary`
  - roughly `7.36x` to `18.42x` slower than Rust for `roundtrip`
- The wasm benchmark is now a real `wasm32-unknown-unknown` module executed
  through Node.js, not a native fallback:
  - roughly `1.56x` to `3.47x` slower than Rust for `summary`
  - roughly `2.33x` to `4.26x` slower than Rust for `roundtrip`

## Memory Findings

- Peak RSS is recorded for every case, target, and operation tuple, so timing
  and memory regressions can be inspected together.
- The largest single memory spike in the run is the real wasm32 path on
  `3d_basisvoorziening` `roundtrip`: `4111.60 MiB`.
- Average peak RSS for `roundtrip` across the full manifest:
  - C++: `244.78 MiB`
  - Rust: `261.14 MiB`
  - Python: `262.68 MiB`
  - Wasm: `567.08 MiB`
- The memory story is dominated by the largest dataset:
  - `3dbag` `roundtrip` peak RSS:
    Rust `62.18 MiB`, C++ `70.22 MiB`, Python `89.20 MiB`, Wasm `160.51 MiB`
  - `3d_basisvoorziening` `roundtrip` peak RSS:
    Rust `1994.93 MiB`, C++ `1818.12 MiB`, Python `1837.09 MiB`,
    Wasm `4111.60 MiB`

## Real Dataset Highlights

- `3dbag`
  - Rust `roundtrip`: `58.381 ms`, `62.18 MiB`
  - Python `roundtrip`: `966.772 ms` (`16.56x`), `89.20 MiB`
  - C++ `roundtrip`: `602.961 ms` (`10.33x`), `70.22 MiB`
  - Wasm `roundtrip`: `162.534 ms` (`2.78x`), `160.51 MiB`
- `3d_basisvoorziening`
  - Rust `roundtrip`: `1636.035 ms`, `1994.93 MiB`
  - Python `roundtrip`: `49939.446 ms` (`30.52x`), `1837.09 MiB`
  - C++ `roundtrip`: `30130.733 ms` (`18.42x`), `1818.12 MiB`
  - Wasm `roundtrip`: `6966.936 ms` (`4.26x`), `4111.60 MiB`

## Validation Notes

- The full matrix completed: `9 cases x 4 targets x 3 operations = 108` result
  records.
- Every materialized roundtrip artifact in the benchmark run validated with
  `cjval` (`36` outputs total).
- The source `3d_basisvoorziening` file is invalid according to `cjval` in this
  environment, but the roundtrip outputs produced by all benchmark targets
  validated successfully.
