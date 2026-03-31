#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
catalog_path="${repo_dir}/catalog/corpus.json"
schema_path="${repo_dir}/profiles/cjfake-manifest.schema.json"
invariants_path="${repo_dir}/invariants/corpus.json"
validator="${repo_dir}/scripts/validate_profiles.sh"
case_validator="${repo_dir}/scripts/validate_case_layout.py"
output_path="${CORPUS_AUDIT_PATH:-${repo_dir}/artifacts/corpus-audit.json}"

if [[ ! -f "${catalog_path}" ]]; then
  echo "missing corpus catalog: ${catalog_path}" >&2
  exit 1
fi

if [[ ! -f "${schema_path}" ]]; then
  echo "missing profile schema: ${schema_path}" >&2
  exit 1
fi

if [[ ! -f "${invariants_path}" ]]; then
  echo "missing corpus invariants: ${invariants_path}" >&2
  exit 1
fi

if [[ ! -x "${validator}" ]]; then
  echo "missing profile validator: ${validator}" >&2
  exit 1
fi

"${validator}"
uv run python "${case_validator}"

jq empty "${invariants_path}"

check_duplicate_ids() {
  local file_path="$1"
  local label="$2"

  local duplicates
  duplicates="$(jq -r '.cases | group_by(.id) | map(select(length > 1) | .[0].id)[]?' "${file_path}")"
  if [[ -n "${duplicates}" ]]; then
    echo "duplicate case ids in ${label}: ${duplicates}" >&2
    exit 1
  fi
}

check_duplicate_ids "${catalog_path}" "catalog"
check_duplicate_ids "${invariants_path}" "invariants"

catalog_ids_file="$(mktemp)"
invariants_ids_file="$(mktemp)"
tmp_summary="$(mktemp)"
trap 'rm -f "${catalog_ids_file}" "${invariants_ids_file}" "${tmp_summary}"' EXIT

jq -r '.cases[].id' "${catalog_path}" | sort > "${catalog_ids_file}"
jq -r '.cases[].id' "${invariants_path}" | sort > "${invariants_ids_file}"

if ! diff -u "${catalog_ids_file}" "${invariants_ids_file}" >/dev/null; then
  echo "catalog case ids do not match invariants case ids" >&2
  diff -u "${catalog_ids_file}" "${invariants_ids_file}" >&2 || true
  exit 1
fi

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

while IFS=$'\t' read -r case_id kind fixture expected_result; do
  [[ -n "${case_id}" ]] || continue

  if [[ "${kind}" == "negative" ]]; then
    fixture_path="${repo_dir}/${fixture}"
    if [[ ! -f "${fixture_path}" ]]; then
      echo "missing invalid fixture for ${case_id}: ${fixture}" >&2
      exit 1
    fi

    jq empty "${fixture_path}"
  fi
done < <(jq -r '.cases[] | [.id, .kind, (.fixture // ""), (.expected_result // "")] | @tsv' "${invariants_path}")

mkdir -p "$(dirname "${output_path}")"

jq -S \
  --slurpfile invariants "${invariants_path}" \
  '
  def count_by(field):
    reduce .cases[] as $case ({};
      .[$case[field]] = ((.[ $case[field] ] // 0) + 1)
    );

  ($invariants[0]) as $invariants_doc
  |
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
    invariants: {
      case_count: ($invariants_doc.cases | length),
      positive_case_count: ([$invariants_doc.cases[] | select(.kind == "positive")] | length),
      negative_case_count: ([$invariants_doc.cases[] | select(.kind == "negative")] | length),
      negative_fixtures: [
        $invariants_doc.cases[]
        | select(.kind == "negative")
        | {
            id,
            fixture,
            expected_result
          }
      ]
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
mv "${tmp_summary}" "${output_path}"
echo "wrote ${output_path}"
