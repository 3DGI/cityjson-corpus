#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUST_MANIFEST="${ROOT_DIR}/drivers/rust/Cargo.toml"
WASM_MANIFEST="${ROOT_DIR}/drivers/wasm/Cargo.toml"
BUILD_BIN_DIR="${ROOT_DIR}/build/bin"
BUILD_WASM_DIR="${ROOT_DIR}/build/wasm"
WASM_TARGET="wasm32-unknown-unknown"
WASM_ARTIFACT="${ROOT_DIR}/drivers/wasm/target/${WASM_TARGET}/release/cjlib_benchmark_wasm_driver.wasm"
WASM_RUSTFLAGS='target.wasm32-unknown-unknown.rustflags=["--cfg=getrandom_backend=\"wasm_js\""]'

if ! command -v cargo >/dev/null 2>&1; then
  echo "cargo is required" >&2
  exit 1
fi
if ! command -v wasm-bindgen >/dev/null 2>&1; then
  echo "wasm-bindgen is required" >&2
  exit 1
fi
if ! command -v node >/dev/null 2>&1; then
  echo "node is required" >&2
  exit 1
fi

cargo build --release --manifest-path "${RUST_MANIFEST}"
cargo build --release --target "${WASM_TARGET}" --manifest-path "${WASM_MANIFEST}" --config "${WASM_RUSTFLAGS}"

mkdir -p "${BUILD_BIN_DIR}"
mkdir -p "${BUILD_WASM_DIR}"
wasm-bindgen --target nodejs --out-dir "${BUILD_WASM_DIR}" --out-name cjbench_wasm "${WASM_ARTIFACT}"
cat > "${BUILD_BIN_DIR}/cjbench-rust" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "${ROOT_DIR}/drivers/rust/target/release/cjlib-benchmark-rust-driver" "\$@"
EOF
cat > "${BUILD_BIN_DIR}/cjbench-wasm" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec node "${ROOT_DIR}/drivers/wasm/run_wasm_benchmark.cjs" "\$@"
EOF
chmod +x "${BUILD_BIN_DIR}/cjbench-rust" "${BUILD_BIN_DIR}/cjbench-wasm"
