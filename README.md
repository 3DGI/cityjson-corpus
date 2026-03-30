# cjlib-benchmarks

Standalone end-to-end benchmarking for `cjlib`, the C++ and Python bindings, and
the wasm-facing adapter.

The benchmark repo is intentionally separate from `cjlib` so it can:

- pin benchmark datasets and generated cases without polluting the library tree
- build host-language drivers with their own toolchains
- validate roundtrip outputs with `cjval`
- report wrapper overhead relative to the Rust baseline
- capture per-run peak RSS so timing and memory regressions can be compared

The wasm benchmark target is a real `wasm32-unknown-unknown` module packaged
with `wasm-bindgen` and executed through Node.js. The benchmark therefore
measures an actual JS<->Wasm boundary, not a native Rust fallback.

The benchmark contract is:

- same datasets for every target
- same operations for every target
- same JSON result schema from every driver
- roundtrip outputs must validate with `cjval`
- each benchmark run also emits `results/latest/summary.csv` for plotting

See [`docs/implementation-plan.md`](docs/implementation-plan.md).

## Prerequisites

- `cargo`
- `node`
- `wasm-bindgen`
- `cjval`

## Driver Contract

Every target driver must be exposed through one of these stable entry points:

- `build/bin/cjbench-rust`
- `build/bin/cjbench-python`
- `build/bin/cjbench-cpp`
- `build/bin/cjbench-wasm`

Each driver must accept:

```text
--operation {probe,summary,roundtrip}
--input PATH
--iterations N
--warmup N
--output PATH
--pretty-output
--result-json PATH
```

The benchmark orchestrator assumes those paths and arguments.

## Output Artifacts

Each run writes a self-contained result bundle under `results/latest/`:

- `summary.json`
- `summary.md`
- `summary.csv`
- `raw/*.json`
- `outputs/**/*.city.json`

The orchestrator also records peak resident set size for each target run and
threads that metric through the raw result JSON, Markdown summary, and CSV
export.
