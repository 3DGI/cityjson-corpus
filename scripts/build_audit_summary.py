from __future__ import annotations

import json
import os
from pathlib import Path

from corpus_cases import JsonObject, load_case_records, repo_relative


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "artifacts" / "corpus-audit.json"


def count_by(records: list, field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = record.case_data.get(field)
        if not isinstance(value, str):
            continue
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_negative_fixture_summary(records: list) -> list[JsonObject]:
    fixtures: list[JsonObject] = []
    for record in records:
        kind = record.invariants_data.get("kind")
        if kind != "negative":
            continue

        expected_result = record.invariants_data.get("expected_result")
        source_path = record.artifact_paths.get("source")

        fixture_summary: JsonObject = {
            "id": record.case_id,
            "invariants": repo_relative(record.invariants_path),
        }
        if isinstance(source_path, str):
            fixture_summary["fixture"] = source_path
        if isinstance(expected_result, str):
            fixture_summary["expected_result"] = expected_result
        fixtures.append(fixture_summary)

    return fixtures


def build_profile_fixture_summary(records: list) -> list[JsonObject]:
    fixtures: list[JsonObject] = []
    for record in records:
        profile_path = record.artifact_paths.get("profile")
        if not isinstance(profile_path, str):
            continue

        fixtures.append(
            {
                "id": record.case_id,
                "profile": profile_path,
                "family": record.case_data["family"],
                "source_kind": record.case_data["source_kind"],
                "primary_cost": record.case_data["primary_cost"],
                "layer": record.case_data["layer"],
            }
        )

    return fixtures


def build_unmaterialized_case_summary(records: list) -> list[JsonObject]:
    cases: list[JsonObject] = []
    for record in records:
        artifact_mode = record.case_data.get("artifact_mode")
        if artifact_mode == "generated":
            continue

        cases.append(
            {
                "id": record.case_id,
                "layer": record.case_data["layer"],
                "family": record.case_data["family"],
                "source_kind": record.case_data["source_kind"],
                "primary_cost": record.case_data["primary_cost"],
                "representation": record.case_data["representation"],
                "artifact_mode": artifact_mode,
            }
        )

    return cases


def main() -> None:
    records = load_case_records()
    output_path = Path(os.environ.get("CORPUS_AUDIT_PATH", DEFAULT_OUTPUT_PATH))
    output: JsonObject = {
        "corpus": {
            "version": 1,
            "case_count": len(records),
        },
        "coverage": {
            "cases_by_layer": count_by(records, "layer"),
            "cases_by_source_kind": count_by(records, "source_kind"),
            "cases_by_primary_cost": count_by(records, "primary_cost"),
            "cases_by_family": count_by(records, "family"),
            "cases_by_artifact_mode": count_by(records, "artifact_mode"),
            "profile_case_count": len(build_profile_fixture_summary(records)),
            "negative_case_count": len(build_negative_fixture_summary(records)),
        },
        "negative_fixtures": build_negative_fixture_summary(records),
        "profile_fixtures": build_profile_fixture_summary(records),
        "unmaterialized_cases": build_unmaterialized_case_summary(records),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
