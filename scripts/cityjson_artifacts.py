#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


JsonObject = dict[str, object]
Representation = Literal["cityjson", "jsonl", "feature-files"]


class ArtifactError(RuntimeError):
    pass


@dataclass
class SummaryAccumulator:
    cityjson_version: str | None = None
    reference_system: str | None = None
    geographical_extent: list[object] | None = None
    feature_count: int = 0
    cityobject_count: int = 0
    cityobject_types: Counter[str] = field(default_factory=Counter)
    vertex_count: int = 0
    geometry_types: set[str] = field(default_factory=set)
    lods: set[str | int | float] = field(default_factory=set)
    semantic_surface_types: set[str] = field(default_factory=set)
    attribute_keys: set[str] = field(default_factory=set)

    def add_metadata(self, document: JsonObject) -> None:
        version = document.get("version")
        if isinstance(version, str):
            self.cityjson_version = version

        metadata = document.get("metadata")
        if not isinstance(metadata, dict):
            return

        reference_system = metadata.get("referenceSystem")
        if isinstance(reference_system, str):
            self.reference_system = reference_system

        geographical_extent = metadata.get("geographicalExtent")
        if isinstance(geographical_extent, list):
            self.geographical_extent = geographical_extent

    def add_cityobjects(self, document: JsonObject, *, count_roots: bool) -> None:
        cityobjects = require_mapping(document, "CityObjects")
        vertices = require_list(document, "vertices")
        self.cityobject_count += len(cityobjects)
        self.vertex_count += len(vertices)

        if count_roots:
            self.feature_count += sum(
                1
                for cityobject in cityobjects.values()
                if is_root_cityobject(cityobject)
            )

        for cityobject in cityobjects.values():
            if not isinstance(cityobject, dict):
                raise ArtifactError("CityObjects entries must be JSON objects")

            cityobject_type = cityobject.get("type")
            if isinstance(cityobject_type, str):
                self.cityobject_types[cityobject_type] += 1

            attributes = cityobject.get("attributes")
            if isinstance(attributes, dict):
                self.attribute_keys.update(
                    key for key in attributes if isinstance(key, str)
                )

            geometries = cityobject.get("geometry", [])
            if not isinstance(geometries, list):
                raise ArtifactError("CityObject geometry must be an array")
            for geometry in geometries:
                self.add_geometry(geometry)

    def add_geometry(self, geometry: object) -> None:
        if not isinstance(geometry, dict):
            raise ArtifactError("geometry entries must be JSON objects")

        geometry_type = geometry.get("type")
        if isinstance(geometry_type, str):
            self.geometry_types.add(geometry_type)

        lod = geometry.get("lod")
        if isinstance(lod, str | int | float) and not isinstance(lod, bool):
            self.lods.add(lod)

        semantics = geometry.get("semantics")
        if not isinstance(semantics, dict):
            return

        surfaces = semantics.get("surfaces")
        if not isinstance(surfaces, list):
            return
        for surface in surfaces:
            if not isinstance(surface, dict):
                continue
            surface_type = surface.get("type")
            if isinstance(surface_type, str):
                self.semantic_surface_types.add(surface_type)

    def as_json(self) -> JsonObject:
        return {
            "cityjson_version": self.cityjson_version,
            "reference_system": self.reference_system,
            "geographical_extent": self.geographical_extent,
            "feature_count": self.feature_count,
            "cityobject_count": self.cityobject_count,
            "cityobject_types": dict(sorted(self.cityobject_types.items())),
            "vertex_count": self.vertex_count,
            "geometry_types": sorted(self.geometry_types),
            "lods": sorted(self.lods, key=lambda item: (str(type(item)), str(item))),
            "semantic_surface_types": sorted(self.semantic_surface_types),
            "attribute_keys": sorted(self.attribute_keys),
        }


def require_mapping(document: JsonObject, key: str) -> dict[str, object]:
    value = document.get(key)
    if not isinstance(value, dict):
        raise ArtifactError(f"{key} must be a JSON object")
    return value


def require_list(document: JsonObject, key: str) -> list[object]:
    value = document.get(key)
    if not isinstance(value, list):
        raise ArtifactError(f"{key} must be an array")
    return value


def is_root_cityobject(cityobject: object) -> bool:
    if not isinstance(cityobject, dict):
        raise ArtifactError("CityObjects entries must be JSON objects")
    parents = cityobject.get("parents")
    return not isinstance(parents, list) or len(parents) == 0


def load_json_object(text: str, source: str) -> JsonObject:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ArtifactError(f"{source} is not valid JSON") from exc
    if not isinstance(document, dict):
        raise ArtifactError(f"{source} must contain a JSON object")
    return document


def load_json_file(path: Path) -> JsonObject:
    try:
        return load_json_object(path.read_text(encoding="utf-8"), str(path))
    except UnicodeDecodeError as exc:
        raise ArtifactError(f"{path} is not valid UTF-8") from exc


def require_document_type(
    document: JsonObject, expected_type: str, source: str
) -> None:
    if document.get("type") != expected_type:
        raise ArtifactError(f"{source} must contain a {expected_type} object")


def add_feature(
    accumulator: SummaryAccumulator, document: JsonObject, source: str
) -> str:
    require_document_type(document, "CityJSONFeature", source)
    feature_id = document.get("id")
    if not isinstance(feature_id, str) or not feature_id:
        raise ArtifactError(f"{source} has a missing or invalid feature id")
    accumulator.feature_count += 1
    accumulator.add_cityobjects(document, count_roots=False)
    return feature_id


def iter_jsonl_objects(path: Path) -> list[tuple[int, JsonObject, str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ArtifactError(f"{path} is not valid UTF-8") from exc

    objects: list[tuple[int, JsonObject, str]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        source = f"{path}:{line_number}"
        objects.append((line_number, load_json_object(line, source), line))
    return objects


def summarize_cityjson(path: Path) -> JsonObject:
    document = load_json_file(path)
    require_document_type(document, "CityJSON", str(path))
    accumulator = SummaryAccumulator()
    accumulator.add_metadata(document)
    accumulator.add_cityobjects(document, count_roots=True)
    return accumulator.as_json()


def summarize_jsonl(path: Path) -> JsonObject:
    objects = iter_jsonl_objects(path)
    if not objects:
        raise ArtifactError(f"{path} is empty")

    _, header, _ = objects[0]
    require_document_type(header, "CityJSON", f"{path}:1")
    accumulator = SummaryAccumulator()
    accumulator.add_metadata(header)
    for line_number, feature, _ in objects[1:]:
        add_feature(accumulator, feature, f"{path}:{line_number}")
    return accumulator.as_json()


def feature_file_paths(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.city.jsonl") if path.is_file())


def summarize_feature_files(root: Path) -> JsonObject:
    metadata_path = root / "metadata.json"
    metadata = load_json_file(metadata_path)
    require_document_type(metadata, "CityJSON", str(metadata_path))
    accumulator = SummaryAccumulator()
    accumulator.add_metadata(metadata)

    for feature_path in feature_file_paths(root):
        objects = iter_jsonl_objects(feature_path)
        if len(objects) != 1:
            raise ArtifactError(
                f"{feature_path} must contain exactly one feature object"
            )
        line_number, feature, _ = objects[0]
        add_feature(accumulator, feature, f"{feature_path}:{line_number}")
    return accumulator.as_json()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def directory_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def sha256_directory(root: Path) -> str:
    digest = hashlib.sha256()
    for path in directory_files(root):
        relative_path = path.relative_to(root).as_posix().encode()
        digest.update(len(relative_path).to_bytes(8, "big"))
        digest.update(relative_path)
        digest.update(path.stat().st_size.to_bytes(8, "big"))
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def directory_size(root: Path) -> int:
    return sum(path.stat().st_size for path in directory_files(root))


def describe_artifact(path: Path, representation: Representation) -> JsonObject:
    if representation == "cityjson":
        return {
            "checksum": sha256_file(path),
            "byte_size": path.stat().st_size,
            "summary": summarize_cityjson(path),
        }
    if representation == "jsonl":
        return {
            "checksum": sha256_file(path),
            "byte_size": path.stat().st_size,
            "summary": summarize_jsonl(path),
        }
    return {
        "checksum": sha256_directory(path),
        "byte_size": directory_size(path),
        "summary": summarize_feature_files(path),
    }


def validate_feature_filename(feature_id: str) -> str:
    if (
        feature_id in {".", ".."}
        or Path(feature_id).name != feature_id
        or "/" in feature_id
        or "\\" in feature_id
    ):
        raise ArtifactError(f"unsafe feature id for filename: {feature_id!r}")
    return feature_id


def split_feature_files(source: Path, destination: Path) -> None:
    objects = iter_jsonl_objects(source)
    if not objects:
        raise ArtifactError(f"{source} is empty")

    _, metadata, metadata_line = objects[0]
    require_document_type(metadata, "CityJSON", f"{source}:1")

    features: list[tuple[str, str]] = []
    seen_ids: set[str] = set()
    accumulator = SummaryAccumulator()
    for line_number, feature, line in objects[1:]:
        feature_id = validate_feature_filename(
            add_feature(accumulator, feature, f"{source}:{line_number}")
        )
        if feature_id in seen_ids:
            raise ArtifactError(f"duplicate feature id: {feature_id}")
        seen_ids.add(feature_id)
        features.append((feature_id, line))

    if destination.exists():
        shutil.rmtree(destination)
    features_dir = destination / "features"
    features_dir.mkdir(parents=True)
    (destination / "metadata.json").write_text(metadata_line + "\n", encoding="utf-8")
    for feature_id, line in features:
        (features_dir / f"{feature_id}.city.jsonl").write_text(
            line + "\n", encoding="utf-8"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Describe and materialize CityJSON corpus artifacts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    describe_parser = subparsers.add_parser(
        "describe", help="Print checksum, byte size, and summary JSON."
    )
    describe_parser.add_argument(
        "--representation",
        required=True,
        choices=("cityjson", "jsonl", "feature-files"),
    )
    describe_parser.add_argument("path", type=Path)

    split_parser = subparsers.add_parser(
        "split-feature-files", help="Split a JSONL stream into one file per feature."
    )
    split_parser.add_argument("source", type=Path)
    split_parser.add_argument("destination", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "describe":
        payload = describe_artifact(args.path, args.representation)
        print(json.dumps(payload, sort_keys=True))
        return 0

    split_feature_files(args.source, args.destination)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ArtifactError as exc:
        raise SystemExit(str(exc)) from exc
