#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
corpus_path="${repo_dir}/catalog/cases.json"
schema_path="${repo_dir}/schemas/cjfake-manifest.schema.json"
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

uv run python "${repo_dir}/scripts/render_case_catalog.py" --check

rm -rf "${output_dir}"
mkdir -p "${output_dir}"

acquired_map_json='{}'
while IFS=$'\t' read -r case_id acquisition_path; do
  [[ -n "${case_id}" ]] || continue
  [[ -n "${acquisition_path}" ]] || continue

  case_acquisition_path="${repo_dir}/${acquisition_path}"
  if [[ ! -f "${case_acquisition_path}" ]]; then
    continue
  fi

  acquired_output_path="$(
    jq -r '
      .outputs[]
      | select(.published == true and .path != null and .representation == "cityjson")
      | .path
    ' "${case_acquisition_path}" | head -n1
  )"

  if [[ -z "${acquired_output_path}" || "${acquired_output_path}" == "null" ]]; then
    continue
  fi

  if [[ "${acquired_output_path}" != /* ]]; then
    acquired_output_path="${repo_dir}/${acquired_output_path}"
  fi

  acquired_map_json="$(
    jq -c --arg case_id "${case_id}" --arg output_path "${acquired_output_path}" \
      '. + {($case_id): $output_path}' <<<"${acquired_map_json}"
  )"
done < <(jq -r '.cases[] | select(.layer == "workload" and .artifact_mode == "acquired" and .artifact_paths.acquisition != null) | [.id, .artifact_paths.acquisition] | @tsv' "${corpus_path}")

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
done < <(jq -r '.cases[] | select(.layer == "workload" and .artifact_paths.profile != null) | [.id, .artifact_paths.profile] | @tsv' "${corpus_path}")

jq -S \
  --arg output_dir "${output_dir}" \
  --arg corpus_path "catalog/cases.json" \
  --arg schema_path "schemas/cjfake-manifest.schema.json" \
  --arg cjfake_cargo "${cjfake_cargo}" \
  --argjson acquired_map "${acquired_map_json}" \
  '
  {
    version: .version,
    purpose: .purpose,
    case_count: (
      [.cases[]
       | select(.layer == "workload")
       | select(
           .artifact_paths.profile != null
           or (.artifact_paths.profile == null and (.artifact_mode != "acquired" or ($acquired_map[.id] != null)))
         )]
      | length
    ),
    catalog_case_count: (.cases | length),
    catalog: $corpus_path,
    generator: {
      tool: "cjfake",
      cargo_manifest: $cjfake_cargo,
      manifest_schema: $schema_path
    },
    output_dir: $output_dir,
    generated_cases: [
      .cases[]
      | select(.layer == "workload")
      | select(.artifact_paths.profile != null)
      | {
          id,
          layer,
          family,
          source_kind,
          artifact_mode,
          primary_cost,
          representation,
          scale,
          operations,
          assertions,
          artifact_paths,
          documentation,
          invariants,
          output: ($output_dir + "/" + .id + ".city.json")
        }
    ],
    other_cases: [
      .cases[]
      | select(.layer == "workload")
      | select(.artifact_paths.profile == null)
      | select(.artifact_mode != "acquired" or ($acquired_map[.id] != null))
      | {
          id,
          layer,
          family,
          source_kind,
          artifact_mode,
          primary_cost,
          representation,
          scale,
          operations,
          assertions,
          artifact_paths,
          documentation,
          output: ($acquired_map[.id] // null)
        }
    ]
  }
  ' "${corpus_path}" > "${index_path}"

echo "wrote ${output_dir}"
echo "wrote ${index_path}"
