#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
validator="${repo_dir}/scripts/validate_profiles.sh"
case_validator="${repo_dir}/scripts/validate_case_layout.py"
output_path="${CORPUS_AUDIT_PATH:-${repo_dir}/artifacts/corpus-audit.json}"

if [[ ! -x "${validator}" ]]; then
  echo "missing profile validator: ${validator}" >&2
  exit 1
fi

"${validator}"
uv run python "${case_validator}"
CORPUS_AUDIT_PATH="${output_path}" uv run python "${repo_dir}/scripts/build_audit_summary.py"
