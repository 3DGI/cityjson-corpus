#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
release_date="${CORPUS_3DBAG_VERSION:-2025.09.03}"
version_slug="v${release_date//./}"
output_root="${CORPUS_3DBAG_OUTPUT_ROOT:-${repo_dir}/artifacts/acquired/3dbag/${version_slug}}"
base_tile_id="${CORPUS_3DBAG_TILE_ID:-10-758-50}"
cluster_tile_ids_raw="${CORPUS_3DBAG_CLUSTER_TILE_IDS:-10-756-48 10-756-50 10-758-48}"
cluster_output_name="${CORPUS_3DBAG_CLUSTER_OUTPUT_NAME:-cluster_4x.city.json}"
ops_root_id="${CORPUS_3DBAG_OPS_ROOT_ID:-NL.IMBAG.Pand.0928100000037540}"
cjio_spec="${CORPUS_CJIO_SPEC:-cjio==0.10.1}"
python="${CORPUS_PYTHON:-python3}"
artifact_helper="${repo_dir}/scripts/cityjson_artifacts.py"
metadata_path="${output_root}/metadata.json"
manifest_path="${output_root}/manifest.json"
export PYTHONHASHSEED="${CORPUS_PYTHONHASHSEED:-0}"

for tool in curl gunzip jq uvx "${python}"; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "missing required tool: ${tool}" >&2
    exit 1
  fi
done

mkdir -p "${output_root}"

read -r -a cluster_tile_ids <<<"${cluster_tile_ids_raw}"
if [[ "${#cluster_tile_ids[@]}" -eq 0 ]]; then
  echo "cluster tile list is empty" >&2
  exit 1
fi

download_tile() {
  local tile_id="$1"
  local tile_x tile_y tile_z download_url output_path gzip_path

  IFS="-" read -r tile_x tile_y tile_z <<<"${tile_id}"
  if [[ -z "${tile_x:-}" || -z "${tile_y:-}" || -z "${tile_z:-}" ]]; then
    echo "invalid 3DBAG tile id: ${tile_id}" >&2
    exit 1
  fi

  output_path="${output_root}/${tile_id}.city.json"
  if [[ -f "${output_path}" ]]; then
    return
  fi

  download_url="https://data.3dbag.nl/${version_slug}/tiles/${tile_x}/${tile_y}/${tile_z}/${tile_id}.city.json.gz"
  gzip_path="${output_path}.gz"
  curl -fsSL "${download_url}" -o "${gzip_path}"
  gunzip -f "${gzip_path}"
}

download_tile "${base_tile_id}"
for tile_id in "${cluster_tile_ids[@]}"; do
  download_tile "${tile_id}"
done

base_output_name="${base_tile_id}.city.json"
base_output_path="${output_root}/${base_output_name}"
cluster_output_path="${output_root}/${cluster_output_name}"
jsonl_output_name="${base_tile_id}.city.jsonl"
jsonl_output_path="${output_root}/${jsonl_output_name}"
feature_files_output_name="${base_tile_id}.feature-files"
feature_files_output_path="${output_root}/${feature_files_output_name}"
ops_output_name="ops_3dbag.city.json"
ops_output_path="${output_root}/${ops_output_name}"

merge_args=("${base_output_path}")
for tile_id in "${cluster_tile_ids[@]}"; do
  merge_args+=(merge "${output_root}/${tile_id}.city.json")
done
merge_args+=(save "${cluster_output_path}")
uvx --from "${cjio_spec}" cjio "${merge_args[@]}"
uvx --from "${cjio_spec}" cjio "${base_output_path}" export jsonl "${jsonl_output_path}"
"${python}" "${artifact_helper}" split-feature-files "${jsonl_output_path}" "${feature_files_output_path}"
uvx --from "${cjio_spec}" cjio "${base_output_path}" subset --id "${ops_root_id}" save "${ops_output_path}"

tile_urls_json="$(
  {
    printf '%s\n' "${base_tile_id}"
    printf '%s\n' "${cluster_tile_ids[@]}"
  } | while IFS= read -r tile_id; do
    IFS="-" read -r tile_x tile_y tile_z <<<"${tile_id}"
    jq -n -c \
      --arg tile_id "${tile_id}" \
      --arg download_url "https://data.3dbag.nl/${version_slug}/tiles/${tile_x}/${tile_y}/${tile_z}/${tile_id}.city.json.gz" \
      '{tile_id: $tile_id, download_url: $download_url}'
  done | jq -s -S .
)"

cluster_derived_from_json="$(
  {
    printf '%s\n' "artifacts/acquired/3dbag/${version_slug}/${base_output_name}"
    for tile_id in "${cluster_tile_ids[@]}"; do
      printf '%s\n' "artifacts/acquired/3dbag/${version_slug}/${tile_id}.city.json"
    done
  } | jq -R . | jq -c -s .
)"
base_derived_from_json="$(jq -cn --arg path "artifacts/acquired/3dbag/${version_slug}/${base_output_name}" '[$path]')"
jsonl_derived_from_json="$(jq -cn --arg path "artifacts/acquired/3dbag/${version_slug}/${jsonl_output_name}" '[$path]')"

outputs_json="$(
  {
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${base_output_name}" "cityjson" "upstream" "acquired" "canonical" '["io_3dbag_cityjson"]' "[]"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${cluster_output_name}" "cityjson" "cjio" "merged" "benchmark-only" '["io_3dbag_cityjson_cluster_4x"]' "${cluster_derived_from_json}"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${jsonl_output_name}" "jsonl" "cjio" "exported" "benchmark-only" '["io_3dbag_jsonl"]' "${base_derived_from_json}"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${feature_files_output_name}" "feature-files" "cityjson-corpus" "materialized" "benchmark-only" '["io_3dbag_feature_files"]' "${jsonl_derived_from_json}"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "${ops_output_name}" "cityjson" "cjio" "subset" "canonical" '["ops_3dbag"]' "${base_derived_from_json}"
  } | while IFS=$'\t' read -r relative_name representation producer derivation validation_role case_ids_json derived_from_json; do
    output_path="${output_root}/${relative_name}"
    descriptor_json="$("${python}" "${artifact_helper}" describe --representation "${representation}" "${output_path}")"
    jq -n -c \
      --arg path "artifacts/acquired/3dbag/${version_slug}/${relative_name}" \
      --arg representation "${representation}" \
      --arg producer "${producer}" \
      --arg derivation "${derivation}" \
      --arg validation_role "${validation_role}" \
      --argjson case_ids "${case_ids_json}" \
      --argjson derived_from "${derived_from_json}" \
      --argjson descriptor "${descriptor_json}" \
      '
      $descriptor
      + {
          path: $path,
          representation: $representation,
          producer: $producer,
          derivation: $derivation,
          validation_role: $validation_role,
          case_ids: $case_ids,
          published: true
        }
      + (if $derived_from | length > 0 then {derived_from: $derived_from} else {} end)
      '
  done | jq -s -S .
)"

jq -n -S \
  --arg dataset "3DBAG" \
  --arg base_tile_id "${base_tile_id}" \
  --arg upstream_version "${release_date}" \
  --arg upstream_release_path "${version_slug}" \
  --arg tile_index_url "https://data.3dbag.nl/${version_slug}/tile_index.fgb" \
  --arg cluster_output_name "${cluster_output_name}" \
  --arg ops_root_id "${ops_root_id}" \
  --argjson cluster_tile_ids "$(printf '%s\n' "${cluster_tile_ids[@]}" | jq -R . | jq -s .)" \
  --argjson tile_urls "${tile_urls_json}" \
  '
  {
    dataset: $dataset,
    upstream_version: $upstream_version,
    upstream_release_path: $upstream_release_path,
    tile_index_url: $tile_index_url,
    base_tile_id: $base_tile_id,
    cluster_tile_ids: $cluster_tile_ids,
    cluster_output_name: $cluster_output_name,
    ops_root_id: $ops_root_id,
    downloads: $tile_urls
  }
  ' > "${metadata_path}"

jq -n -S \
  --arg dataset "3DBAG" \
  --arg upstream_version "${release_date}" \
  --arg base_tile_id "${base_tile_id}" \
  --arg cluster_output_name "${cluster_output_name}" \
  --arg ops_root_id "${ops_root_id}" \
  --argjson cluster_tile_ids "$(printf '%s\n' "${cluster_tile_ids[@]}" | jq -R . | jq -s .)" \
  --argjson outputs "${outputs_json}" \
  '
  {
    version: 1,
    dataset: $dataset,
    upstream_version: $upstream_version,
    base_tile_id: $base_tile_id,
    cluster_output_name: $cluster_output_name,
    cluster_tile_ids: $cluster_tile_ids,
    ops_root_id: $ops_root_id,
    outputs: $outputs
  }
  ' > "${manifest_path}"

echo "wrote ${base_output_path}"
for tile_id in "${cluster_tile_ids[@]}"; do
  echo "wrote ${output_root}/${tile_id}.city.json"
done
echo "wrote ${cluster_output_path}"
echo "wrote ${jsonl_output_path}"
echo "wrote ${feature_files_output_path}"
echo "wrote ${ops_output_path}"
echo "wrote ${metadata_path}"
echo "wrote ${manifest_path}"
