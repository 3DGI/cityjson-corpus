#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_root="${CORPUS_3DBAG_OUTPUT_ROOT:-${repo_dir}/artifacts/acquired/3dbag/v20231008}"
tile_id="${CORPUS_3DBAG_TILE_ID:-10-356-724}"
version="${CORPUS_3DBAG_VERSION:-v20231008}"
tile_path="${tile_id//[-]//}"
download_url="https://data.3dbag.nl/${version}/tiles/${tile_path}/${tile_id}.city.json.gz"
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
curl -fsSL "https://data.3dbag.nl/${version}/metadata.json" -o "${metadata_path}"

checksum="$(sha256sum "${output_path}" | awk '{print $1}')"
byte_size="$(stat -c '%s' "${output_path}")"

jq -S \
  --arg dataset "3DBAG" \
  --arg id "${tile_id}" \
  --arg version "${version}" \
  --arg download_url "${download_url}" \
  --arg output_path "artifacts/acquired/3dbag/v20231008/${tile_id}.city.json" \
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
