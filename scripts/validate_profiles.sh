#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
corpus_path="${repo_dir}/catalog/corpus.json"
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

declare -A referenced_profiles=()

while IFS= read -r profile_relpath; do
  [[ -n "${profile_relpath}" ]] || continue
  referenced_profiles["${profile_relpath}"]=1
done < <(jq -r '.cases[] | select(.profile != null) | .profile' "${corpus_path}")

for profile_path in "${repo_dir}"/profiles/cases/*.json; do
  [[ -f "${profile_path}" ]] || continue

  profile_relpath="profiles/cases/$(basename "${profile_path}")"
  if [[ -z "${referenced_profiles[${profile_relpath}]+x}" ]]; then
    echo "profile is not referenced by catalog: ${profile_relpath}" >&2
    exit 1
  fi

  jq empty "${profile_path}"
  cargo run --quiet --manifest-path "${cjfake_cargo}" -- \
    --manifest "${profile_path}" \
    --schema "${schema_path}" \
    --check-manifest
done

for profile_relpath in "${!referenced_profiles[@]}"; do
  if [[ ! -f "${repo_dir}/${profile_relpath}" ]]; then
    echo "catalog references missing profile: ${profile_relpath}" >&2
    exit 1
  fi
done

