# cjlib-benchmarks

Standalone end-to-end benchmarking for `cjlib`, the C++ and Python bindings, and
the wasm-facing adapter.

The benchmark repo is intentionally separate from `cjlib` so it can:

- pin benchmark datasets and generated cases without polluting the library tree
- build host-language drivers with their own toolchains
- validate roundtrip outputs with `cjval`
- report wrapper overhead relative to the Rust baseline

The benchmark contract is:

- same datasets for every target
- same operations for every target
- same JSON result schema from every driver
- roundtrip outputs must validate with `cjval`

See [`docs/implementation-plan.md`](docs/implementation-plan.md).
