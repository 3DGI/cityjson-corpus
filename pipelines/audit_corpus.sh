#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
catalog_path="${repo_dir}/catalog/corpus.json"
schema_path="${repo_dir}/profiles/cjfake-manifest.schema.json"
validator="${repo_dir}/scripts/validate_profiles.sh"
output_path="${CORPUS_AUDIT_PATH:-${repo_dir}/artifacts/corpus-audit.json}"

if [[ ! -f "${catalog_path}" ]]; then
  echo "missing corpus catalog: ${catalog_path}" >&2
  exit 1
fi

if [[ ! -f "${schema_path}" ]]; then
  echo "missing profile schema: ${schema_path}" >&2
  exit 1
fi

if [[ ! -x "${validator}" ]]; then
  echo "missing profile validator: ${validator}" >&2
  exit 1
fi

"${validator}"

mkdir -p "$(dirname "${output_path}")"

tmp_summary="$(mktemp)"
trap 'rm -f "${tmp_summary}"' EXIT

jq -S '
  def count_by(field):
    reduce .cases[] as $case ({};
      .[$case[field]] = ((.[ $case[field] ] // 0) + 1)
    );

  {
    corpus: {
      version: .version,
      purpose: .purpose,
      case_count: (.cases | length)
    },
    coverage: {
      cases_by_source_kind: (count_by("source_kind")),
      cases_by_primary_cost: (count_by("primary_cost")),
      cases_by_family: (count_by("family")),
      profile_case_count: ([.cases[] | select(.profile != null)] | length),
      unprofiled_case_count: ([.cases[] | select(.profile == null)] | length)
    },
    profile_fixtures: [
      .cases[]
      | select(.profile != null)
      | {
          id,
          profile,
          family,
          source_kind,
          primary_cost
        }
    ],
    unprofiled_cases: [
      .cases[]
      | select(.profile == null)
      | {
          id,
          family,
          source_kind,
          primary_cost,
          representation
        }
    ]
  }
' "${catalog_path}" > "${tmp_summary}"

while IFS=$'\t' read -r case_id profile_path; do
  [[ -n "${case_id}" ]] || continue
  [[ -n "${profile_path}" ]] || continue

  case_profile_path="${repo_dir}/${profile_path}"
  if [[ ! -f "${case_profile_path}" ]]; then
    echo "missing profile fixture for ${case_id}: ${profile_path}" >&2
    exit 1
  fi

  jq -e --arg case_id "${case_id}" '
    (.cases | length == 1) and (.cases[0].id == $case_id)
  ' "${case_profile_path}" >/dev/null
done < <(jq -r '.cases[] | select(.profile != null) | [.id, .profile] | @tsv' "${catalog_path}")

mv "${tmp_summary}" "${output_path}"
echo "wrote ${output_path}"
