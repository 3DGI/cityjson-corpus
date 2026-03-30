#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cjlib_root="${CJLIB_ROOT:-/home/balazs/Development/cjlib}"
build_root="${repo_root}/build/native"
bin_root="${repo_root}/build/bin"

mkdir -p "${build_root}"
mkdir -p "${bin_root}"

python3 -m py_compile "${repo_root}/drivers/python/benchmark.py"

cmake \
  -S "${repo_root}/drivers/cpp" \
  -B "${build_root}/cpp" \
  -DCJLIB_ROOT="${cjlib_root}"
cmake --build "${build_root}/cpp"

cat >"${bin_root}/cjbench-python" <<EOF
#!/usr/bin/env bash
set -euo pipefail

script_dir="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
repo_root="\$(cd "\${script_dir}/../.." && pwd)"
cjlib_root="\${CJLIB_ROOT:-${cjlib_root}}"
export CJLIB_ROOT="\${cjlib_root}"
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
