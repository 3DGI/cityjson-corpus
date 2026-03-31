#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
corpus_path="${repo_dir}/catalog/corpus.json"
schema_path="${repo_dir}/profiles/cjfake-manifest.schema.json"
cjfake_cargo="${CJFAKE_CARGO_MANIFEST:-${repo_dir}/../cjfake/Cargo.toml}"
output_dir="${CORPUS_GENERATED_DIR:-${repo_dir}/artifacts/generated}"
index_path="${CORPUS_BENCHMARK_INDEX_PATH:-${repo_dir}/artifacts/benchmark-index.json}"

for tool in jq cargo; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "missing required tool: ${tool}" >&2
    exit 1
  fi
done

if [[ ! -f "${corpus_path}" ]]; then
  echo "missing corpus catalog: ${corpus_path}" >&2
  exit 1
fi

if [[ ! -f "${schema_path}" ]]; then
  echo "missing manifest schema: ${schema_path}" >&2
  exit 1
fi

if [[ ! -f "${cjfake_cargo}" ]]; then
  echo "missing cjfake Cargo manifest: ${cjfake_cargo}" >&2
  exit 1
fi

rm -rf "${output_dir}"
mkdir -p "${output_dir}"

while IFS=$'\t' read -r case_id profile_path; do
  [[ -n "${case_id}" ]] || continue
  [[ -n "${profile_path}" ]] || continue

  case_profile_path="${repo_dir}/${profile_path}"
  if [[ ! -f "${case_profile_path}" ]]; then
    echo "missing profile fixture for ${case_id}: ${profile_path}" >&2
    exit 1
  fi

  cargo run --quiet --manifest-path "${cjfake_cargo}" -- \
    --manifest "${case_profile_path}" \
    --schema "${schema_path}" \
    --output "${output_dir}/${case_id}.city.json"
done < <(jq -r '.cases[] | select(.profile != null) | [.id, .profile] | @tsv' "${corpus_path}")

jq -S \
  --arg output_dir "${output_dir}" \
  --arg corpus_path "catalog/corpus.json" \
  --arg schema_path "profiles/cjfake-manifest.schema.json" \
  --arg cjfake_cargo "${cjfake_cargo}" \
  '
  {
    version: .version,
    purpose: .purpose,
    case_count: (.cases | length),
    corpus: $corpus_path,
    generator: {
      tool: "cjfake",
      cargo_manifest: $cjfake_cargo,
      manifest_schema: $schema_path
    },
    invariants: {
      path: "invariants/corpus.json",
      case_count: (.cases | length),
      positive_case_count: ([.cases[] | select(.profile != null)] | length),
      negative_case_count: ([.cases[] | select(.profile == null)] | length)
    },
    output_dir: $output_dir,
    synthetic_cases: [
      .cases[]
      | select(.profile != null)
      | {
          id,
          family,
          source_kind,
          primary_cost,
          representation,
          scale,
          operations,
          assertions,
          profile,
          documentation,
          output: ($output_dir + "/" + .id + ".city.json")
        }
    ],
    external_cases: [
      .cases[]
      | select(.profile == null)
      | {
          id,
          family,
          source_kind,
          primary_cost,
          representation,
          scale,
          operations,
          assertions,
          documentation
        }
    ]
  }
  ' "${corpus_path}" > "${index_path}"

echo "wrote ${output_dir}"
echo "wrote ${index_path}"
