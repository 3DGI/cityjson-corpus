#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
release_date="${CORPUS_3DBAG_VERSION:-2025.09.03}"
version_slug="v${release_date//./}"
output_root="${CORPUS_3DBAG_OUTPUT_ROOT:-${repo_dir}/artifacts/acquired/3dbag/${version_slug}}"
tile_id="${CORPUS_3DBAG_TILE_ID:-10-758-50}"
IFS="-" read -r tile_x tile_y tile_z <<<"${tile_id}"
if [[ -z "${tile_x:-}" || -z "${tile_y:-}" || -z "${tile_z:-}" ]]; then
  echo "invalid 3DBAG tile id: ${tile_id}" >&2
  exit 1
fi
download_url="https://data.3dbag.nl/${version_slug}/tiles/${tile_x}/${tile_y}/${tile_z}/${tile_id}.city.json.gz"
output_path="${output_root}/${tile_id}.city.json"
metadata_path="${output_root}/metadata.json"
manifest_path="${output_root}/manifest.json"

for tool in curl gunzip sha256sum jq; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "missing required tool: ${tool}" >&2
    exit 1
  fi
done

mkdir -p "${output_root}"

gzip_path="${output_path}.gz"
curl -fsSL "${download_url}" -o "${gzip_path}"
gunzip -f "${gzip_path}"
jq -n -S \
  --arg dataset "3DBAG" \
  --arg tile_id "${tile_id}" \
  --arg upstream_version "${release_date}" \
  --arg upstream_release_path "${version_slug}" \
  --arg tile_index_url "https://data.3dbag.nl/${version_slug}/tile_index.fgb" \
  --arg download_url "${download_url}" \
  '
  {
    dataset: $dataset,
    tile_id: $tile_id,
    upstream_version: $upstream_version,
    upstream_release_path: $upstream_release_path,
    tile_index_url: $tile_index_url,
    download_url: $download_url
  }
  ' > "${metadata_path}"

checksum="$(sha256sum "${output_path}" | awk '{print $1}')"
byte_size="$(stat -c '%s' "${output_path}")"

jq -S \
  --arg dataset "3DBAG" \
  --arg id "${tile_id}" \
  --arg version "${release_date}" \
  --arg download_url "${download_url}" \
  --arg output_path "artifacts/acquired/3dbag/${version_slug}/${tile_id}.city.json" \
  --arg checksum "${checksum}" \
  --argjson byte_size "${byte_size}" \
  '
  {
    dataset: $dataset,
    id: $id,
    upstream_version: $version,
    download_url: $download_url,
    output: {
      path: $output_path,
      checksum: $checksum,
      byte_size: $byte_size
    }
  }
  ' > "${manifest_path}"

echo "wrote ${output_path}"
echo "wrote ${metadata_path}"
echo "wrote ${manifest_path}"
