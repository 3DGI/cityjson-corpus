#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
release_date="${CORPUS_3DBAG_VERSION:-2025.09.03}"
version_slug="v${release_date//./}"
output_root="${CORPUS_3DBAG_OUTPUT_ROOT:-${repo_dir}/artifacts/acquired/3dbag/${version_slug}}"
base_tile_id="${CORPUS_3DBAG_TILE_ID:-10-758-50}"
cluster_tile_ids_raw="${CORPUS_3DBAG_CLUSTER_TILE_IDS:-10-756-48 10-756-50 10-758-48}"
cluster_output_name="${CORPUS_3DBAG_CLUSTER_OUTPUT_NAME:-cluster_4x.city.json}"
metadata_path="${output_root}/metadata.json"
manifest_path="${output_root}/manifest.json"

for tool in curl gunzip sha256sum jq uvx; do
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

cluster_output_path="${output_root}/${cluster_output_name}"
merge_args=("${output_root}/${base_tile_id}.city.json")
for tile_id in "${cluster_tile_ids[@]}"; do
  merge_args+=(merge "${output_root}/${tile_id}.city.json")
done
merge_args+=(save "${cluster_output_path}")
uvx --from cjio cjio "${merge_args[@]}"

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
    printf '%s\n' "artifacts/acquired/3dbag/${version_slug}/${base_tile_id}.city.json"
    for tile_id in "${cluster_tile_ids[@]}"; do
      printf '%s\n' "artifacts/acquired/3dbag/${version_slug}/${tile_id}.city.json"
    done
  } | jq -R . | jq -c -s .
)"

outputs_json="$(
  {
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "${base_tile_id}.city.json" "cityjson" "upstream" "acquired" "canonical" "[]"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "${cluster_output_name}" "cityjson" "cjio" "merged" "benchmark-only" "${cluster_derived_from_json}"
  } | while IFS=$'\t' read -r relative_name representation producer derivation validation_role derived_from_json; do
    output_path="${output_root}/${relative_name}"
    jq -n -c \
      --arg path "artifacts/acquired/3dbag/${version_slug}/${relative_name}" \
      --arg representation "${representation}" \
      --arg producer "${producer}" \
      --arg derivation "${derivation}" \
      --arg validation_role "${validation_role}" \
      --arg checksum "$(sha256sum "${output_path}" | awk '{print $1}')" \
      --argjson byte_size "$(stat -c '%s' "${output_path}")" \
      --argjson derived_from "${derived_from_json}" \
      '
      {
        path: $path,
        representation: $representation,
        producer: $producer,
        derivation: $derivation,
        validation_role: $validation_role,
        checksum: $checksum,
        byte_size: $byte_size,
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
    downloads: $tile_urls
  }
  ' > "${metadata_path}"

jq -n -S \
  --arg dataset "3DBAG" \
  --arg upstream_version "${release_date}" \
  --arg base_tile_id "${base_tile_id}" \
  --arg cluster_case_id "io_3dbag_cityjson_cluster_4x" \
  --arg cluster_output_name "${cluster_output_name}" \
  --argjson cluster_tile_ids "$(printf '%s\n' "${cluster_tile_ids[@]}" | jq -R . | jq -s .)" \
  --argjson outputs "${outputs_json}" \
  '
  {
    dataset: $dataset,
    upstream_version: $upstream_version,
    base_tile_id: $base_tile_id,
    cluster_case_id: $cluster_case_id,
    cluster_output_name: $cluster_output_name,
    cluster_tile_ids: $cluster_tile_ids,
    outputs: $outputs
  }
  ' > "${manifest_path}"

echo "wrote ${output_root}/${base_tile_id}.city.json"
for tile_id in "${cluster_tile_ids[@]}"; do
  echo "wrote ${output_root}/${tile_id}.city.json"
done
echo "wrote ${cluster_output_path}"
echo "wrote ${metadata_path}"
echo "wrote ${manifest_path}"
