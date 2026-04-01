from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from corpus_cases import (
    ACQUISITION_SCHEMA_PATH,
    CATALOG_PATH,
    CASE_SCHEMA_PATH,
    CORRECTNESS_INDEX_PATH,
    INVARIANTS_SCHEMA_PATH,
    PROFILE_SCHEMA_PATH,
    ROOT,
    load_case_records,
    load_json_object,
    render_catalog_text,
    render_correctness_index_text,
)


def load_schema(path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_document(validator: Draft202012Validator, path) -> dict[str, object]:
    payload = load_json_object(path)
    validator.validate(payload)
    return payload


def validate_jsonish_file(path) -> None:
    text = path.read_text(encoding="utf-8")
    try:
        json.loads(text)
        return
    except json.JSONDecodeError:
        for line in text.splitlines():
            if line.strip():
                json.loads(line)


def validate_profile_fixture(
    validator: Draft202012Validator, case_id: str, profile_path
) -> None:
    payload = validate_document(validator, profile_path)
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 1:
        raise SystemExit(
            f"profile fixture must contain exactly one case: {profile_path}"
        )

    profile_case = cases[0]
    if not isinstance(profile_case, dict):
        raise SystemExit(f"profile fixture must contain object entries: {profile_path}")

    profile_case_id = profile_case.get("id")
    if profile_case_id != case_id:
        raise SystemExit(
            f"profile fixture id mismatch in {profile_path}: {profile_case_id} != {case_id}"
        )


def validate_acquisition_fixture(
    validator: Draft202012Validator, case_id: str, acquisition_path
) -> None:
    payload = validate_document(validator, acquisition_path)
    if payload.get("id") != case_id:
        raise SystemExit(
            f"acquisition id mismatch in {acquisition_path}: {payload.get('id')} != {case_id}"
        )


def validate_tree() -> None:
    case_schema = load_schema(CASE_SCHEMA_PATH)
    invariants_schema = load_schema(INVARIANTS_SCHEMA_PATH)
    profile_schema = load_schema(PROFILE_SCHEMA_PATH)
    acquisition_schema = load_schema(ACQUISITION_SCHEMA_PATH)
    case_validator = Draft202012Validator(case_schema)
    invariants_validator = Draft202012Validator(invariants_schema)
    profile_validator = Draft202012Validator(profile_schema)
    acquisition_validator = Draft202012Validator(acquisition_schema)

    seen_ids: set[str] = set()
    records = load_case_records()

    for record in records:
        case_payload = validate_document(case_validator, record.case_path)
        invariants_payload = validate_document(
            invariants_validator, record.invariants_path
        )

        case_id = case_payload["id"]
        if case_id in seen_ids:
            raise SystemExit(f"duplicate case id in case layout: {case_id}")
        seen_ids.add(case_id)

        if invariants_payload["id"] != case_id:
            raise SystemExit(
                f"case/invariants id mismatch in {record.case_dir}: {case_id} != {invariants_payload['id']}"
            )

        artifact_paths = record.artifact_paths
        source_name = artifact_paths.get("source")
        if isinstance(source_name, str):
            source_file = ROOT / source_name
            if not source_file.exists():
                raise SystemExit(f"missing case source file: {source_file}")

            if source_file.suffix not in {".json", ".jsonl"}:
                raise SystemExit(f"unsupported case source extension: {source_file}")

            validate_jsonish_file(source_file)

        profile_name = artifact_paths.get("profile")
        if isinstance(profile_name, str):
            profile_file = ROOT / profile_name
            if not profile_file.exists():
                raise SystemExit(f"missing case profile file: {profile_file}")
            validate_profile_fixture(profile_validator, case_id, profile_file)

        acquisition_name = artifact_paths.get("acquisition")
        if isinstance(acquisition_name, str):
            acquisition_file = ROOT / acquisition_name
            if not acquisition_file.exists():
                raise SystemExit(f"missing case acquisition file: {acquisition_file}")
            validate_acquisition_fixture(
                acquisition_validator, case_id, acquisition_file
            )

        documentation_path = case_payload.get("documentation")
        if isinstance(documentation_path, str):
            doc_path = ROOT / documentation_path
            if not doc_path.exists():
                raise SystemExit(f"missing case documentation file: {doc_path}")

    expected_catalog = render_catalog_text(records)
    if not CATALOG_PATH.exists():
        raise SystemExit(f"missing catalog file: {CATALOG_PATH}")

    current_catalog = CATALOG_PATH.read_text(encoding="utf-8")
    if current_catalog != expected_catalog:
        raise SystemExit(
            "catalog/cases.json is out of date; run `uv run python ./scripts/render_case_catalog.py`"
        )

    expected_correctness_index = render_correctness_index_text(records)
    if not CORRECTNESS_INDEX_PATH.exists():
        raise SystemExit(f"missing correctness index file: {CORRECTNESS_INDEX_PATH}")

    current_correctness_index = CORRECTNESS_INDEX_PATH.read_text(encoding="utf-8")
    if current_correctness_index != expected_correctness_index:
        raise SystemExit(
            "artifacts/correctness-index.json is out of date; run "
            "`uv run python ./scripts/render_correctness_index.py`"
        )


def main() -> None:
    validate_tree()
    print(f"validated shared case layout under {ROOT / 'cases'}")


if __name__ == "__main__":
    main()
