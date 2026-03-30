# Latest Results

These figures come from `results/latest/summary.md` after running the full
benchmark manifest on 2026-03-30.

## High-level Findings

- The Rust baseline stays fastest across every case.
- The Python binding is consistently the most expensive wrapper:
  - roughly `7.4x` to `17.6x` slower than Rust for `summary`
  - roughly `11.3x` to `29.1x` slower than Rust for `roundtrip`
- The C++ binding is materially cheaper than Python but still clearly above the
  Rust baseline:
  - roughly `7.4x` to `17.5x` slower than Rust for `summary`
  - roughly `6.9x` to `17.5x` slower than Rust for `roundtrip`
- The current `cjlib-wasm` benchmark is a native host-side fallback because the
  upstream stack cannot compile to `wasm32` today.
  Even with that limitation, the narrower adapter stayed much closer to Rust:
  - roughly `1.4x` to `3.0x` slower than Rust for `summary`
  - roughly `2.2x` to `3.4x` slower than Rust for `roundtrip`

## Real Dataset Highlights

- `3dbag`
  - Rust `roundtrip`: `56.649 ms`
  - Python `roundtrip`: `953.876 ms` (`16.84x`)
  - C++ `roundtrip`: `587.824 ms` (`10.38x`)
  - Wasm-adapter `roundtrip`: `124.397 ms` (`2.20x`)
- `3d_basisvoorziening`
  - Rust `roundtrip`: `1665.759 ms`
  - Python `roundtrip`: `48471.406 ms` (`29.10x`)
  - C++ `roundtrip`: `29192.315 ms` (`17.52x`)
  - Wasm-adapter `roundtrip`: `5718.450 ms` (`3.43x`)

## Validation Notes

- Every materialized roundtrip artifact in the benchmark run validated with
  `cjval`.
- The source `3d_basisvoorziening` file is invalid according to `cjval` in this
  environment, but the compact roundtrip outputs produced by all benchmark
  targets validated successfully.
