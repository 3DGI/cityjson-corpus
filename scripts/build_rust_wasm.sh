#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUST_MANIFEST="${ROOT_DIR}/drivers/rust/Cargo.toml"
WASM_MANIFEST="${ROOT_DIR}/drivers/wasm/Cargo.toml"
BUILD_BIN_DIR="${ROOT_DIR}/build/bin"

if ! command -v cargo >/dev/null 2>&1; then
  echo "cargo is required" >&2
  exit 1
fi

cargo build --release --manifest-path "${RUST_MANIFEST}"
cargo build --release --manifest-path "${WASM_MANIFEST}"

mkdir -p "${BUILD_BIN_DIR}"
cat > "${BUILD_BIN_DIR}/cjbench-rust" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "${ROOT_DIR}/drivers/rust/target/release/cjlib-benchmark-rust-driver" "\$@"
EOF
cat > "${BUILD_BIN_DIR}/cjbench-wasm" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "${ROOT_DIR}/drivers/wasm/target/release/cjlib-benchmark-wasm-driver" "\$@"
EOF
chmod +x "${BUILD_BIN_DIR}/cjbench-rust" "${BUILD_BIN_DIR}/cjbench-wasm"
