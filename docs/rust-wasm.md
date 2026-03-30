# Rust And Wasm Drivers

This worktree owns the Rust baseline driver and the real `wasm32` benchmark
path.

## Rust Baseline

The Rust driver lives in `drivers/rust` and benchmarks `cjlib` directly against
real CityJSON input bytes.

CLI contract:

```text
--operation {probe,summary,roundtrip}
--input PATH
--iterations N
--warmup N
--output PATH
--result-json PATH
[--pretty-output]
```

For `roundtrip`, the driver writes exactly one CityJSON artifact to `--output`.

## Wasm32 Driver

The wasm benchmark path now uses a real `wasm32-unknown-unknown` module:

1. `drivers/wasm/src/lib.rs` exposes a thin `wasm-bindgen` wrapper over
   `cjlib-wasm`
2. `scripts/build_rust_wasm.sh` compiles that crate for
   `wasm32-unknown-unknown`
3. `wasm-bindgen --target nodejs` emits the JS glue and `.wasm` artifact under
   `build/wasm`
4. `drivers/wasm/run_wasm_benchmark.cjs` satisfies the benchmark CLI contract
   and executes the generated module through Node.js

That means `build/bin/cjbench-wasm` now benchmarks the actual JS<->Wasm
boundary instead of a native Rust fallback.

## Portability Notes

This repo only became buildable for `wasm32` after two upstream portability
fixes:

1. `cityjson-rs` no longer hard-rejects non-64-bit targets at compile time
2. `cjlib-wasm` is built with explicit `getrandom` wasm configuration:
   - `ffi/wasm/Cargo.toml` enables `getrandom`'s `wasm_js` feature for
     `target_family = "wasm", target_os = "unknown"`
   - `scripts/build_rust_wasm.sh` passes
     `--cfg getrandom_backend="wasm_js"` through Cargo target config

The resulting benchmark is still Node-specific, not a browser benchmark, but it
is a real `wasm32-unknown-unknown` execution path.

## Build

Run:

```bash
./scripts/build_rust_wasm.sh
```

The script will:

1. build the native Rust baseline driver
2. build the wasm wrapper crate for `wasm32-unknown-unknown`
3. package the wasm artifact with `wasm-bindgen`
4. generate launcher entry points at `build/bin/cjbench-rust` and
   `build/bin/cjbench-wasm`

## Output Schema

Both drivers emit JSON result files with:

- target name
- operation
- input path and byte size
- warmup and iteration counts
- `samples_ns` with one nanosecond sample per measured iteration
- optional output byte size
- probe metrics when `operation=probe`
- summary metrics when `operation=summary` or `roundtrip`
- a portability note that records the benchmark context

## Current Signal

The current full-manifest run shows that the wasm path is materially closer to
Rust on wall time than Python or C++, but it pays a noticeable memory cost on
the largest dataset:

- `summary`: roughly `1.56x` to `3.47x` slower than Rust
- `roundtrip`: roughly `2.33x` to `4.26x` slower than Rust
- worst observed peak RSS:
  `3d_basisvoorziening` `roundtrip` at `4111.60 MiB`
