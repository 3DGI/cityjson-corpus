from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


JsonObject = dict[str, object]

ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = ROOT / "cases"
CATALOG_PATH = ROOT / "catalog" / "cases.json"
CASE_SCHEMA_PATH = ROOT / "schemas" / "case.schema.json"
INVARIANTS_SCHEMA_PATH = ROOT / "schemas" / "invariants.schema.json"
ACQUISITION_SCHEMA_PATH = ROOT / "schemas" / "acquisition.schema.json"
PROFILE_SCHEMA_PATH = ROOT / "profiles" / "cjfake-manifest.schema.json"


@dataclass(frozen=True)
class CaseRecord:
    case_dir: Path
    case_path: Path
    invariants_path: Path
    case_data: JsonObject
    invariants_data: JsonObject
    readme_path: Path | None

    @property
    def case_id(self) -> str:
        value = self.case_data["id"]
        return str(value)

    @property
    def artifact_paths(self) -> dict[str, str]:
        raw_paths = self.case_data.get("artifact_paths", {})
        if not isinstance(raw_paths, dict):
            return {}

        artifact_paths: dict[str, str] = {}
        for key, value in raw_paths.items():
            if isinstance(key, str) and isinstance(value, str):
                artifact_paths[key] = value
        return artifact_paths


def load_json_object(path: Path) -> JsonObject:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"expected JSON object in {path}")
    return payload


def repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_case_records(case_root: Path = CASE_ROOT) -> list[CaseRecord]:
    records: list[CaseRecord] = []
    for case_path in sorted(case_root.rglob("case.json")):
        case_dir = case_path.parent
        invariants_path = case_dir / "invariants.json"
        readme_path = case_dir / "README.md"
        if not invariants_path.exists():
            raise SystemExit(f"missing invariants file: {invariants_path}")

        record = CaseRecord(
            case_dir=case_dir,
            case_path=case_path,
            invariants_path=invariants_path,
            case_data=load_json_object(case_path),
            invariants_data=load_json_object(invariants_path),
            readme_path=readme_path if readme_path.exists() else None,
        )
        records.append(record)

    if not records:
        raise SystemExit(f"no case.json files found under {case_root}")

    return records


def humanize_case_id(case_id: str) -> str:
    words = case_id.replace("_", " ").split()
    return " ".join(word.capitalize() for word in words)


def build_catalog_case(record: CaseRecord) -> JsonObject:
    entry = dict(record.case_data)
    entry["path"] = repo_relative(record.case_dir)
    entry["case"] = repo_relative(record.case_path)
    entry["invariants"] = repo_relative(record.invariants_path)

    if record.readme_path is not None:
        entry["documentation"] = repo_relative(record.readme_path)

    return entry


def build_catalog_document(records: list[CaseRecord]) -> JsonObject:
    cases = [build_catalog_case(record) for record in sorted(records, key=lambda item: item.case_id)]
    return {
        "version": 1,
        "purpose": "Derived case index for the shared CityJSON corpus. Source of truth lives under cases/.",
        "cases": cases,
    }


def render_catalog_text(records: list[CaseRecord]) -> str:
    document = build_catalog_document(records)
    return json.dumps(document, indent=2, sort_keys=True) + "\n"
