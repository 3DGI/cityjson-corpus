#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
corpus_path="${repo_dir}/catalog/cases.json"
schema_path="${CJFAKE_MANIFEST_SCHEMA:-${repo_dir}/../cityjson-fake/src/data/cityjson-fake-manifest.schema.json}"
schema_ref="${CJFAKE_MANIFEST_SCHEMA_REF:-https://github.com/3DGI/cityjson-fake/blob/main/src/data/cityjson-fake-manifest.schema.json}"
cityjson_fake_cargo="${CJFAKE_CARGO_MANIFEST:-${repo_dir}/../cityjson-fake/Cargo.toml}"
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

if [[ ! -f "${cityjson_fake_cargo}" ]]; then
  echo "missing cityjson-fake Cargo manifest: ${cityjson_fake_cargo}" >&2
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

  acquired_outputs_json="$(
    jq -c '
      [
        .outputs[]
        | select(.published == true and .path != null)
      ]
    ' "${case_acquisition_path}"
  )"

  if [[ -z "${acquired_outputs_json}" || "${acquired_outputs_json}" == "[]" ]]; then
    continue
  fi

  acquired_case_json="$(
    jq -c --arg repo_dir "${repo_dir}" '
      . as $outputs
      | {
          canonical_artifact: (
            (
              $outputs
              | map(select(.validation_role == "canonical"))
              | .[0].path
            ) as $canonical_path
            | if $canonical_path == null then
                null
              elif ($canonical_path | startswith("/")) then
                $canonical_path
              else
                ($repo_dir + "/" + $canonical_path)
              end
          ),
          artifacts: (
            $outputs
            | map(
                (
                  . + {
                    path: (
                      if (.path | startswith("/")) then
                        .path
                      else
                        ($repo_dir + "/" + .path)
                      end
                    )
                  }
                )
                + (
                  if (.derived_from // [] | length) > 0 then
                    {
                      derived_from: (
                        .derived_from
                        | map(
                            if startswith("/") then
                              .
                            else
                              ($repo_dir + "/" + .)
                            end
                          )
                      )
                    }
                  else
                    {}
                  end
                )
              )
          )
        }
    ' <<<"${acquired_outputs_json}"
  )"

  acquired_map_json="$(
    jq -c --arg case_id "${case_id}" --argjson case_artifacts "${acquired_case_json}" \
      '. + {($case_id): $case_artifacts}' <<<"${acquired_map_json}"
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

  cargo run --quiet --manifest-path "${cityjson_fake_cargo}" -- \
    --manifest "${case_profile_path}" \
    --schema "${schema_path}" \
    --output "${output_dir}/${case_id}.city.json"
done < <(jq -r '.cases[] | select(.layer == "workload" and .artifact_paths.profile != null) | [.id, .artifact_paths.profile] | @tsv' "${corpus_path}")

jq -S \
  --arg output_dir "${output_dir}" \
  --arg repo_dir "${repo_dir}" \
  --arg corpus_path "catalog/cases.json" \
  --arg schema_path "${schema_ref}" \
  --arg cityjson_fake_cargo "${cityjson_fake_cargo}" \
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
           or (.artifact_paths.profile == null and (.artifact_mode != "acquired" or (($acquired_map[.id].artifacts // []) | length > 0)))
         )]
      | length
    ),
    catalog_case_count: (.cases | length),
    catalog: $corpus_path,
    generator: {
      tool: "cityjson-fake",
      cargo_manifest: $cityjson_fake_cargo,
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
          representation,
          assertions,
          artifact_paths,
          documentation,
          invariants,
          canonical_artifact: ($output_dir + "/" + .id + ".city.json"),
          artifacts: [
            {
              representation,
              producer: "cityjson-fake",
              derivation: "materialized",
              derived_from: [($repo_dir + "/" + .artifact_paths.profile)],
              validation_role: "canonical",
              path: ($output_dir + "/" + .id + ".city.json")
            }
          ]
        }
    ],
    other_cases: [
      .cases[]
      | select(.layer == "workload")
      | select(.artifact_paths.profile == null)
      | select(.artifact_mode != "acquired" or (($acquired_map[.id].artifacts // []) | length > 0))
      | {
          id,
          layer,
          family,
          source_kind,
          artifact_mode,
          representation,
          assertions,
          artifact_paths,
          documentation,
          canonical_artifact: ($acquired_map[.id].canonical_artifact // null),
          artifacts: ($acquired_map[.id].artifacts // [])
        }
    ]
  }
  ' "${corpus_path}" > "${index_path}"

echo "wrote ${output_dir}"
echo "wrote ${index_path}"
