#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dataset_year="${CORPUS_BASISVOORZIENING_3D_YEAR:-2022}"
tile_slug="${CORPUS_BASISVOORZIENING_3D_TILE_SLUG:-84000_450000}"
archive_name="${CORPUS_BASISVOORZIENING_3D_ARCHIVE_NAME:-volledig_${dataset_year}_${tile_slug}.zip}"
cityjson_name="${CORPUS_BASISVOORZIENING_3D_CITYJSON_NAME:-3d_volledig_${tile_slug}.city.json}"
download_url="${CORPUS_BASISVOORZIENING_3D_URL:-https://download.pdok.nl/kadaster/basisvoorziening-3d/v1_0/${dataset_year}/volledig/${archive_name}}"
output_root="${CORPUS_BASISVOORZIENING_3D_OUTPUT_ROOT:-${repo_dir}/artifacts/acquired/basisvoorziening-3d/${dataset_year}}"
cjlib_cargo_manifest="${CORPUS_CJLIB_CARGO_MANIFEST:-${repo_dir}/../cjlib/Cargo.toml}"
metadata_path="${output_root}/metadata.json"
manifest_path="${output_root}/manifest.json"
archive_path="${output_root}/${archive_name}"
cityjson_path="${output_root}/${cityjson_name}"
cityjson_stem="${cityjson_name%.city.json}"

for tool in cargo curl unzip sha256sum jq; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "missing required tool: ${tool}" >&2
    exit 1
  fi
done

if [[ ! -f "${cjlib_cargo_manifest}" ]]; then
  echo "missing cjlib Cargo manifest: ${cjlib_cargo_manifest}" >&2
  exit 1
fi

mkdir -p "${output_root}"

if [[ ! -f "${cityjson_path}" ]]; then
  curl -fsSL "${download_url}" -o "${archive_path}"
  unzip -p "${archive_path}" "${cityjson_name}" > "${cityjson_path}"
  rm -f "${archive_path}"
fi

export_native_formats() {
  local input_json="$1"
  local stem="$2"
  cargo run --quiet --manifest-path "${cjlib_cargo_manifest}" --bin bench_export_formats -- \
    --input "${input_json}" \
    --arrow-file "${output_root}/${stem}.cjarrow" \
    --parquet-file "${output_root}/${stem}.cjparquet"
}

export_native_formats "${cityjson_path}" "${cityjson_stem}"

outputs_json="$(
  {
    printf '%s\t%s\n' "${cityjson_name}" "cityjson"
    printf '%s\t%s\n' "${cityjson_stem}.cjarrow" "cityarrow"
    printf '%s\t%s\n' "${cityjson_stem}.cjparquet" "cityparquet"
  } | while IFS=$'\t' read -r relative_name representation; do
    output_path="${output_root}/${relative_name}"
    jq -n -c \
      --arg path "artifacts/acquired/basisvoorziening-3d/${dataset_year}/${relative_name}" \
      --arg representation "${representation}" \
      --arg checksum "$(sha256sum "${output_path}" | awk '{print $1}')" \
      --argjson byte_size "$(stat -c '%s' "${output_path}")" \
      '{path: $path, representation: $representation, checksum: $checksum, byte_size: $byte_size}'
  done | jq -s -S .
)"

jq -n -S \
  --arg dataset "Basisvoorziening 3D" \
  --arg dataset_year "${dataset_year}" \
  --arg tile_slug "${tile_slug}" \
  --arg archive_name "${archive_name}" \
  --arg cityjson_name "${cityjson_name}" \
  --arg download_url "${download_url}" \
  '
  {
    dataset: $dataset,
    upstream_version: $dataset_year,
    tile_slug: $tile_slug,
    archive_name: $archive_name,
    cityjson_name: $cityjson_name,
    download_url: $download_url
  }
  ' > "${metadata_path}"

jq -n -S \
  --arg dataset "Basisvoorziening 3D" \
  --arg upstream_version "${dataset_year}" \
  --arg tile_slug "${tile_slug}" \
  --arg case_id "io_basisvoorziening_3d_cityjson" \
  --argjson outputs "${outputs_json}" \
  '
  {
    dataset: $dataset,
    upstream_version: $upstream_version,
    tile_slug: $tile_slug,
    case_id: $case_id,
    outputs: $outputs
  }
  ' > "${manifest_path}"

echo "wrote ${cityjson_path}"
echo "wrote ${output_root}/${cityjson_stem}.cjarrow"
echo "wrote ${output_root}/${cityjson_stem}.cjparquet"
echo "wrote ${metadata_path}"
echo "wrote ${manifest_path}"
