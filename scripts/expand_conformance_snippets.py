#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE_ROOT = ROOT / "cases" / "conformance" / "v2_0"

FULL_DOCUMENT_CASES = {
    "cityjson_fake_complete",
    "cityjson_minimal_complete",
}


def base_citymodel() -> dict[str, Any]:
    return {
        "type": "CityJSON",
        "version": "2.0",
        "CityObjects": {},
        "appearance": {},
        "geometry-templates": {
            "templates": [],
            "vertices-templates": [],
        },
        "vertices": [],
    }


def dummy_vertices(count: int) -> list[list[int]]:
    return [[index, 0, 0] for index in range(count)]


def dummy_uv_vertices(count: int) -> list[list[float]]:
    return [[float(index) / 100.0, 0.0] for index in range(count)]


def max_u64_in(value: Any) -> int | None:
    if isinstance(value, list):
        maxima = [candidate for item in value if (candidate := max_u64_in(item)) is not None]
        return max(maxima) if maxima else None
    if isinstance(value, dict):
        maxima = [candidate for item in value.values() if (candidate := max_u64_in(item)) is not None]
        return max(maxima) if maxima else None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def wrap_transform(value: Any) -> dict[str, Any]:
    root = base_citymodel()
    root["transform"] = value
    return root


def wrap_cityobject(value: dict[str, Any]) -> dict[str, Any]:
    root = base_citymodel()
    cityobjects: dict[str, Any] = {"fixture": value}

    for key in ("children", "parents"):
        ids = value.get(key)
        if not isinstance(ids, list):
            continue
        for identifier in ids:
            if isinstance(identifier, str) and identifier not in cityobjects:
                cityobjects[identifier] = {"type": "GenericCityObject"}

    root["CityObjects"] = cityobjects
    return root


def wrap_geometry(value: dict[str, Any]) -> dict[str, Any]:
    vertex_count = 1
    boundary_max = max_u64_in(value.get("boundaries"))
    if boundary_max is not None:
        vertex_count = boundary_max + 1

    root = base_citymodel()
    root["vertices"] = dummy_vertices(vertex_count)
    root["CityObjects"] = {
        "fixture": {
            "type": "GenericCityObject",
            "geometry": [value],
        }
    }

    if "material" in value or "texture" in value:
        appearance: dict[str, Any] = {}

        material_max = max_u64_in(value.get("material"))
        if material_max is not None:
            appearance["materials"] = [
                {"name": f"material-{index}"} for index in range(material_max + 1)
            ]
        elif "texture" in value:
            appearance["materials"] = []

        texture_max = max_u64_in(value.get("texture"))
        if texture_max is not None:
            appearance["textures"] = [
                {
                    "type": "PNG",
                    "image": f"texture-{index}.png",
                }
                for index in range(texture_max + 1)
            ]
            appearance["vertices-texture"] = dummy_uv_vertices(texture_max + 1)
        elif "material" in value:
            appearance["textures"] = []
            appearance["vertices-texture"] = []

        root["appearance"] = appearance

    if value.get("type") == "GeometryInstance":
        root["geometry-templates"] = {
            "templates": [
                {
                    "type": "MultiPoint",
                    "lod": "1",
                    "boundaries": [0],
                }
            ],
            "vertices-templates": [[0.0, 0.0, 0.0]],
        }

    return root


def wrap_appearance(value: dict[str, Any]) -> dict[str, Any]:
    root = base_citymodel()
    root["appearance"] = value
    return root


def wrap_material(value: dict[str, Any]) -> dict[str, Any]:
    return wrap_appearance(
        {
            "materials": [value],
            "textures": [],
            "vertices-texture": [],
        }
    )


def wrap_texture(value: dict[str, Any]) -> dict[str, Any]:
    return wrap_appearance(
        {
            "materials": [],
            "textures": [value],
            "vertices-texture": [],
        }
    )


def wrap_geometry_templates(value: dict[str, Any]) -> dict[str, Any]:
    root = base_citymodel()
    root["geometry-templates"] = value
    return root


def wrap_semantic_minimal(value: dict[str, Any]) -> dict[str, Any]:
    root = base_citymodel()
    root["vertices"] = dummy_vertices(3)
    root["CityObjects"] = {
        "fixture": {
            "type": "GenericCityObject",
            "geometry": [
                {
                    "type": "MultiSurface",
                    "lod": "1",
                    "boundaries": [[[0, 1, 2]]],
                    "semantics": {
                        "surfaces": [value],
                        "values": [0],
                    },
                }
            ],
        }
    }
    return root


def wrap_semantic_extended(value: dict[str, Any]) -> dict[str, Any]:
    root = base_citymodel()
    root["vertices"] = dummy_vertices(3)
    root["CityObjects"] = {
        "fixture": {
            "type": "GenericCityObject",
            "geometry": [
                {
                    "type": "MultiSurface",
                    "lod": "1",
                    "boundaries": [[[0, 1, 2]], [[0, 1, 2]]],
                    "semantics": {
                        "surfaces": [
                            {"type": "WallSurface"},
                            value,
                            {"type": "WallSurface"},
                        ],
                        "values": [0, 1],
                    },
                }
            ],
        }
    }
    return root


def wrap_vertices(value: list[Any]) -> dict[str, Any]:
    root = base_citymodel()
    root["vertices"] = value
    return root


def wrap_metadata(value: dict[str, Any]) -> dict[str, Any]:
    root = base_citymodel()
    root["metadata"] = value
    return root


def wrap_extension(value: dict[str, Any]) -> dict[str, Any]:
    root = base_citymodel()
    root["extensions"] = {"Noise": value}
    return root


def materialize_case(case_id: str, value: Any) -> Any:
    if isinstance(value, dict) and value.get("type") == "CityJSON":
        return value
    if case_id in FULL_DOCUMENT_CASES:
        return value

    if case_id == "geometry_templates":
        return wrap_geometry_templates(value)
    if case_id == "transform":
        return wrap_transform(value)
    if case_id in {"cityobject_complete", "cityobject_extended"}:
        return wrap_cityobject(value)
    if case_id.startswith("geometry_"):
        return wrap_geometry(value)
    if case_id.startswith("appearance_"):
        return wrap_appearance(value)
    if case_id.startswith("material_"):
        return wrap_material(value)
    if case_id.startswith("texture_"):
        return wrap_texture(value)
    if case_id == "semantic_minimal":
        return wrap_semantic_minimal(value)
    if case_id == "semantic_extended":
        return wrap_semantic_extended(value)
    if case_id == "vertices":
        return wrap_vertices(value)
    if case_id.startswith("metadata_"):
        return wrap_metadata(value)
    if case_id == "extension":
        return wrap_extension(value)

    raise SystemExit(f"no materializer for {case_id}")


def main() -> None:
    for path in sorted(CONFORMANCE_ROOT.glob("*/*.city.json")):
        case_id = path.parent.name
        source_text = path.read_text(encoding="utf-8")
        value = json.loads(source_text)
        materialized = materialize_case(case_id, value)
        path.write_text(
            json.dumps(materialized, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
