#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
corpus_path="${repo_dir}/catalog/cases.json"
schema_path="${repo_dir}/profiles/cjfake-manifest.schema.json"
cjfake_cargo="${CJFAKE_CARGO_MANIFEST:-${repo_dir}/../cjfake/Cargo.toml}"

if [[ ! -f "${corpus_path}" ]]; then
  echo "missing corpus catalog: ${corpus_path}" >&2
  exit 1
fi

if [[ ! -f "${schema_path}" ]]; then
  echo "missing profile schema: ${schema_path}" >&2
  exit 1
fi

uv run python "${repo_dir}/scripts/render_case_catalog.py" --check

while IFS=$'\t' read -r case_id profile_relpath; do
  [[ -n "${case_id}" ]] || continue
  [[ -n "${profile_relpath}" ]] || continue

  profile_path="${repo_dir}/${profile_relpath}"
  if [[ ! -f "${profile_path}" ]]; then
    echo "missing profile fixture for ${case_id}: ${profile_relpath}" >&2
    exit 1
  fi

  jq empty "${profile_path}"
  cargo run --quiet --manifest-path "${cjfake_cargo}" -- \
    --manifest "${profile_path}" \
    --schema "${schema_path}" \
    --check-manifest
done < <(
  jq -r '.cases[] | select(.artifact_paths.profile != null) | [.id, .artifact_paths.profile] | @tsv' "${corpus_path}"
)
