# Native Bindings

This slice benchmarks the Python and C++ wrappers over the shared `cjlib`
FFI.

## Assumptions

- The sibling `cjlib` repository lives at `/home/balazs/Development/cjlib`
- The shared C ABI header already exists at
  `/home/balazs/Development/cjlib/ffi/core/include/cjlib/cjlib.h`
- `cjval` is available on `PATH`

If `CJLIB_ROOT` is set, the build script and C++ driver use that location
instead of the default sibling path.

## Build

Run the native build wrapper from the benchmark repo root:

```bash
./scripts/build_native.sh
```

The script:

- checks the Python benchmark script with `py_compile`
- builds `cjlib-ffi-core` in `release`
- configures and builds the C++ benchmark with CMake
- links the C++ driver against the `release` `cjlib_ffi_core` shared library
- exports `CJLIB_FFI_CORE_LIB` so the Python benchmark loads the same `release`
  shared library
- creates `build/bin/cjbench-python`
- creates `build/bin/cjbench-cpp`
- prints the built C++ executable path and wrapper paths

## Run

The drivers share this CLI contract:

- `--operation {probe,summary,roundtrip}`
- `--input PATH`
- `--iterations N`
- `--warmup N`
- `--output PATH`
- `--pretty-output`
- `--result-json PATH`

Example Python run:

```bash
build/bin/cjbench-python \
  --operation roundtrip \
  --input /home/balazs/Development/serde_cityjson/tests/data/v2_0/cityjson_minimal_complete.city.json \
  --iterations 10 \
  --warmup 2 \
  --output /tmp/cjlib-roundtrip.city.json \
  --result-json /tmp/cjlib-python-result.json
cjval /tmp/cjlib-roundtrip.city.json
```

Example C++ run:

```bash
build/bin/cjbench-cpp \
  --operation roundtrip \
  --input /home/balazs/Development/serde_cityjson/tests/data/v2_0/cityjson_minimal_complete.city.json \
  --iterations 10 \
  --warmup 2 \
  --output /tmp/cjlib-roundtrip.city.json \
  --result-json /tmp/cjlib-cpp-result.json
cjval /tmp/cjlib-roundtrip.city.json
```

## Result JSON

Both drivers emit the same simple result shape:

- `language`
- `operation`
- `input`
- `iterations`
- `warmup`
- `pretty_output`
- `timing_ns.total`
- `timing_ns.per_iteration`
- `samples_ns`
- `input_bytes`
- `output_bytes`
- `probe` for probe runs
- `summary` for summary and roundtrip runs
- `output_path` for roundtrip runs

The schema is intentionally simple so the later trunk orchestrator can merge the
native results with the Rust and wasm runs without translation code.
