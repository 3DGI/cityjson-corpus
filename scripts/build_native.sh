#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cjlib_root="${CJLIB_ROOT:-/home/balazs/Development/cjlib}"
build_root="${repo_root}/build/native"
bin_root="${repo_root}/build/bin"

mkdir -p "${build_root}"
mkdir -p "${bin_root}"

python3 -m py_compile "${repo_root}/drivers/python/benchmark.py"

if [[ "$(uname -s)" == "Darwin" ]]; then
  cjlib_ffi_core_shared_lib="${cjlib_root}/target/release/libcjlib_ffi_core.dylib"
elif [[ "$(uname -s)" == "Linux" ]]; then
  cjlib_ffi_core_shared_lib="${cjlib_root}/target/release/libcjlib_ffi_core.so"
else
  cjlib_ffi_core_shared_lib="${cjlib_root}/target/release/cjlib_ffi_core.dll"
fi

cargo build --release --manifest-path "${cjlib_root}/ffi/core/Cargo.toml"

cmake \
  -S "${repo_root}/drivers/cpp" \
  -B "${build_root}/cpp" \
  -DCJLIB_ROOT="${cjlib_root}" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCJLIB_FFI_CORE_SHARED_LIB="${cjlib_ffi_core_shared_lib}"
cmake --build "${build_root}/cpp" --config Release

cat >"${bin_root}/cjbench-python" <<EOF
#!/usr/bin/env bash
set -euo pipefail

script_dir="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
repo_root="\$(cd "\${script_dir}/../.." && pwd)"
cjlib_root="\${CJLIB_ROOT:-${cjlib_root}}"
export CJLIB_ROOT="\${cjlib_root}"
export CJLIB_FFI_CORE_LIB="${cjlib_ffi_core_shared_lib}"
export PYTHONPATH="\${cjlib_root}/ffi/python/src\${PYTHONPATH:+:\${PYTHONPATH}}"
exec python3 "\${repo_root}/drivers/python/benchmark.py" "\$@"
EOF

cat >"${bin_root}/cjbench-cpp" <<EOF
#!/usr/bin/env bash
set -euo pipefail

script_dir="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
repo_root="\$(cd "\${script_dir}/../.." && pwd)"
exec "\${repo_root}/build/native/cpp/cjlib_native_benchmark" "\$@"
EOF

chmod +x "${bin_root}/cjbench-python" "${bin_root}/cjbench-cpp"

printf '%s\n' "${build_root}/cpp/cjlib_native_benchmark"
printf '%s\n' "${bin_root}/cjbench-python"
printf '%s\n' "${bin_root}/cjbench-cpp"
