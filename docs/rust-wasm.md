# Rust And Wasm Drivers

This worktree owns the Rust baseline driver and the wasm-oriented adapter
driver.

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

## Wasm Adapter

The current `cjlib` wasm layer is benchmarked through a native Rust CLI in
`drivers/wasm`. This is a deliberate fallback, not a claim that the repo
currently produces a browser or Node-loadable `.wasm` artifact.

The reason is upstream and concrete:

- `cityjson-rs` hard-fails compilation on non-64-bit targets
- `wasm32-*` therefore cannot build today
- the benchmark still exercises the narrower `cjlib-wasm` adapter surface so we
  can measure wrapper cost and catch semantic regressions

## Blocker Evidence

The blocker is reproducible with the current sources:

1. `/home/balazs/Development/cityjson-rs/src/backend/default/vertex.rs` contains:
   `#[cfg(not(target_pointer_width = "64"))] compile_error!("This crate only supports 64-bit platforms");`
2. Attempting the original `wasm32-unknown-unknown` packaging path failed with:
   `error: This crate only supports 64-bit platforms`
3. That failure was hit while building the benchmark-side wasm wrapper, so the
   Node and browser packaging path is not currently viable without upstream
   portability work in `cityjson-rs`

The adapter driver implements:

- `probe`
- `summary`
- `roundtrip`

`roundtrip` writes exactly one CityJSON artifact to `--output`.

## Build

Run:

```bash
./scripts/build_rust_wasm.sh
```

The script will:

1. build the Rust driver
2. build the wasm-adapter driver
3. generate launcher entry points at `build/bin/cjbench-rust` and
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
- a portability note on the wasm-adapter result to make the `wasm32` blocker
  explicit in reports
