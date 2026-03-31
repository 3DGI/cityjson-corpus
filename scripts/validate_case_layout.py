from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CASE_SCHEMA_PATH = ROOT / "schemas" / "case.schema.json"
INVARIANTS_SCHEMA_PATH = ROOT / "schemas" / "invariants.schema.json"
CASE_ROOT = ROOT / "cases"


def load_schema(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_document(validator: Draft202012Validator, path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validator.validate(payload)


def validate_jsonish_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    try:
        json.loads(text)
        return
    except json.JSONDecodeError:
        for line in text.splitlines():
            if line.strip():
                json.loads(line)


def validate_tree(case_root: Path) -> None:
    case_schema = load_schema(CASE_SCHEMA_PATH)
    invariants_schema = load_schema(INVARIANTS_SCHEMA_PATH)
    case_validator = Draft202012Validator(case_schema)
    invariants_validator = Draft202012Validator(invariants_schema)

    seen_ids: set[str] = set()

    for case_file in sorted(case_root.rglob("case.json")):
        case_dir = case_file.parent
        invariants_file = case_dir / "invariants.json"
        if not invariants_file.exists():
            raise SystemExit(f"missing invariants file: {invariants_file}")

        validate_document(case_validator, case_file)
        validate_document(invariants_validator, invariants_file)

        case_payload = json.loads(case_file.read_text(encoding="utf-8"))
        invariants_payload = json.loads(invariants_file.read_text(encoding="utf-8"))

        case_id = case_payload["id"]
        if case_id in seen_ids:
            raise SystemExit(f"duplicate case id in case layout: {case_id}")
        seen_ids.add(case_id)

        if invariants_payload["id"] != case_id:
            raise SystemExit(
                f"case/invariants id mismatch in {case_dir}: {case_id} != {invariants_payload['id']}"
            )

        source_name = case_payload["artifact_paths"]["source"]
        source_file = case_dir / source_name
        if not source_file.exists():
            raise SystemExit(f"missing case source file: {source_file}")

        if source_file.suffix not in {".json", ".jsonl"}:
            raise SystemExit(f"unsupported case source extension: {source_file}")

        validate_jsonish_file(source_file)

    if not seen_ids:
        raise SystemExit(f"no case.json files found under {case_root}")


def main() -> None:
    validate_tree(CASE_ROOT)
    print(f"validated shared case layout under {CASE_ROOT}")


if __name__ == "__main__":
    main()
