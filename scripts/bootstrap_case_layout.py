from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CONFORMANCE_ROOT = Path(
    os.environ.get(
        "SERDE_CITYJSON_CONFORMANCE_ROOT",
        ROOT.parent / "serde_cityjson" / "tests" / "data" / "v2_0",
    )
)
SOURCE_INVALID_ROOT = Path(os.environ.get("CITYJSON_BENCHMARKS_INVALID_ROOT", ROOT / "invalid"))
OUTPUT_CONFORMANCE_ROOT = ROOT / "cases" / "conformance" / "v2_0"
OUTPUT_INVALID_ROOT = ROOT / "cases" / "invalid"


CHECK_DESCRIPTIONS = {
    "roundtrip_stable": "The fixture roundtrips without loss.",
    "feature_boundaries_preserved": "Feature boundaries remain stable during streaming.",
    "full_surface_roundtrip": "The full fixture surface roundtrips without loss.",
    "no_schema_regressions": "The fixture does not regress schema coverage.",
    "geometry_surface_preserved": "Geometry stays stable across parse and roundtrip.",
    "appearance_preserved": "Appearance data stays stable across parse and roundtrip.",
    "material_payload_preserved": "Material payloads stay stable across parse and roundtrip.",
    "texture_payload_preserved": "Texture payloads stay stable across parse and roundtrip.",
    "semantic_surface_preserved": "Semantic surfaces stay stable across parse and roundtrip.",
    "metadata_payload_preserved": "Metadata stays stable across parse and roundtrip.",
    "cityobject_structure_preserved": "CityObject structure stays stable across parse and roundtrip.",
    "extension_payload_preserved": "Extension payloads stay stable across parse and roundtrip.",
    "transform_applied_correctly": "Transforms are applied in the expected order and scale.",
    "vertex_indices_preserved": "Vertex indexing stays stable across parse and roundtrip.",
    "rejects_missing_top_level_type": "A CityJSON document without the top-level type marker is rejected.",
    "rejects_out_of_range_vertex_index": "A boundary that references a missing vertex index is rejected.",
}


def humanize(name: str) -> str:
    return name.replace("_", " ")


def case_id_from_name(name: str) -> str:
    for suffix in (".city.jsonl", ".city.json", ".json"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return Path(name).stem


def operations_for(case_id: str, representation: str, negative: bool) -> list[str]:
    if negative:
        return ["parse", "validate"]
    if case_id == "cityjsonfeature_minimal_complete" or representation == "cityjsonfeature":
        return ["parse", "stream_iteration", "serialize"]
    if case_id == "cityjson_fake_complete":
        return ["parse", "validate", "roundtrip"]
    if case_id.startswith("geometry_"):
        return ["parse", "geometry_validation", "roundtrip"]
    if case_id.startswith("appearance_") or case_id.startswith("material_") or case_id.startswith("texture_"):
        return ["parse", "serialize", "roundtrip"]
    if case_id.startswith("semantic_"):
        return ["parse", "roundtrip", "semantic_resolution"]
    if case_id.startswith("metadata_"):
        return ["parse", "validate", "roundtrip"]
    if case_id.startswith("cityobject_"):
        return ["parse", "attribute_lookup", "roundtrip"]
    if case_id == "extension":
        return ["parse", "extension_validation", "roundtrip"]
    if case_id == "transform":
        return ["parse", "roundtrip", "vertex_transform"]
    if case_id == "vertices":
        return ["parse", "roundtrip", "vertex_indexing"]
    return ["parse", "roundtrip"]


def assertions_for(case_id: str, negative: bool) -> list[str]:
    if negative:
        return {
            "invalid_missing_type": ["rejects_missing_top_level_type"],
            "invalid_out_of_range_vertex_index": ["rejects_out_of_range_vertex_index"],
        }[case_id]

    if case_id == "cityjson_fake_complete":
        return ["full_surface_roundtrip", "no_schema_regressions"]
    if case_id == "cityjsonfeature_minimal_complete":
        return ["feature_boundaries_preserved"]
    if case_id.startswith("geometry_"):
        return ["geometry_surface_preserved"]
    if case_id.startswith("appearance_"):
        return ["appearance_preserved"]
    if case_id.startswith("material_"):
        return ["material_payload_preserved"]
    if case_id.startswith("texture_"):
        return ["texture_payload_preserved"]
    if case_id.startswith("semantic_"):
        return ["semantic_surface_preserved"]
    if case_id.startswith("metadata_"):
        return ["metadata_payload_preserved"]
    if case_id.startswith("cityobject_"):
        return ["cityobject_structure_preserved"]
    if case_id == "extension":
        return ["extension_payload_preserved"]
    if case_id == "transform":
        return ["transform_applied_correctly"]
    if case_id == "vertices":
        return ["vertex_indices_preserved"]
    return ["roundtrip_stable"]


def check_descriptions(case_id: str, assertions: list[str]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    for assertion in assertions:
        checks.append(
            {
                "id": assertion,
                "description": CHECK_DESCRIPTIONS.get(
                    assertion,
                    f"{humanize(assertion)} remains stable across parse and roundtrip.",
                ),
            }
        )
    return checks


def source_representation(source_path: Path) -> str:
    return "cityjsonfeature" if source_path.name.endswith(".jsonl") else "cityjson"


def case_family(case_id: str, negative: bool) -> str:
    if negative:
        return "invalid"
    if case_id == "cityjson_fake_complete":
        return "omnibus"
    return "spec_atom"


def primary_cost(case_id: str, representation: str, negative: bool) -> str:
    if negative:
        return "deserialize"
    if representation == "cityjsonfeature":
        return "io"
    if case_id.startswith("appearance_") or case_id.startswith("material_") or case_id.startswith("texture_"):
        return "serialize"
    return "deserialize"


def secondary_costs(case_id: str, representation: str, negative: bool) -> list[str]:
    if negative:
        return ["validate"]
    if representation == "cityjsonfeature":
        return ["deserialize", "serialize"]
    if case_id.startswith("appearance_") or case_id.startswith("material_") or case_id.startswith("texture_"):
        return ["deserialize"]
    return ["serialize"]


def case_dict(case_id: str, source_name: str, source_path: Path, negative: bool) -> dict[str, object]:
    representation = source_representation(source_path)
    assertions = assertions_for(case_id, negative)
    case = {
        "version": 1,
        "id": case_id,
        "layer": "invalid" if negative else "conformance",
        "family": case_family(case_id, negative),
        "source_kind": "synthetic-controlled",
        "cityjson_version": "2.0",
        "representation": representation,
        "artifact_mode": "checked-in",
        "artifact_paths": {
            "source": source_name,
        },
        "primary_cost": primary_cost(case_id, representation, negative),
        "secondary_costs": secondary_costs(case_id, representation, negative),
        "geometry_validity": "dummy",
        "scale": "tiny",
        "operations": operations_for(case_id, representation, negative),
        "assertions": assertions,
    }

    if not negative:
        case["description"] = f"{humanize(case_id)} conformance fixture migrated from serde_cityjson."

    return case


def invariants_dict(case_id: str, source_name: str, negative: bool) -> dict[str, object]:
    assertions = assertions_for(case_id, negative)
    invariants: dict[str, object] = {
        "version": 1,
        "id": case_id,
        "kind": "negative" if negative else "positive",
        "checks": check_descriptions(case_id, assertions),
    }

    if negative:
        invariants["fixture"] = source_name
        invariants["expected_result"] = "reject"

    return invariants


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def emit_case(case_id: str, source_path: Path, output_root: Path, negative: bool) -> None:
    source_name = source_path.name
    case_dir = output_root / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, case_dir / source_name)
    write_json(case_dir / "case.json", case_dict(case_id, source_name, source_path, negative))
    write_json(case_dir / "invariants.json", invariants_dict(case_id, source_name, negative))


def bootstrap_conformance_cases() -> int:
    if not SOURCE_CONFORMANCE_ROOT.exists():
        raise SystemExit(f"missing conformance source root: {SOURCE_CONFORMANCE_ROOT}")

    OUTPUT_CONFORMANCE_ROOT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT_CONFORMANCE_ROOT.exists():
        shutil.rmtree(OUTPUT_CONFORMANCE_ROOT)
    OUTPUT_CONFORMANCE_ROOT.mkdir(parents=True, exist_ok=True)

    emitted = 0
    for source_path in sorted(SOURCE_CONFORMANCE_ROOT.iterdir()):
        if source_path.name == "schemas" or not source_path.is_file():
            continue
        if source_path.suffix not in {".json", ".jsonl"}:
            continue
        emit_case(case_id_from_name(source_path.name), source_path, OUTPUT_CONFORMANCE_ROOT, negative=False)
        emitted += 1
    return emitted


def bootstrap_invalid_cases() -> int:
    if not SOURCE_INVALID_ROOT.exists():
        raise SystemExit(f"missing invalid source root: {SOURCE_INVALID_ROOT}")

    OUTPUT_INVALID_ROOT.mkdir(parents=True, exist_ok=True)
    emitted = 0
    for source_path in sorted(SOURCE_INVALID_ROOT.glob("*.json")):
        emit_case(case_id_from_name(source_path.name), source_path, OUTPUT_INVALID_ROOT, negative=True)
        emitted += 1
    return emitted


def main() -> None:
    conformance_count = bootstrap_conformance_cases()
    invalid_count = bootstrap_invalid_cases()
    print(f"wrote {conformance_count} conformance cases")
    print(f"wrote {invalid_count} invalid cases")


if __name__ == "__main__":
    main()
