from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.cityjson_artifacts import (
    ArtifactError,
    describe_artifact,
    sha256_directory,
    split_feature_files,
)


HEADER = {
    "type": "CityJSON",
    "version": "2.0",
    "CityObjects": {},
    "vertices": [],
    "metadata": {
        "referenceSystem": "https://example.com/crs",
        "geographicalExtent": [0, 0, 0, 10, 10, 10],
    },
}
FEATURE = {
    "type": "CityJSONFeature",
    "id": "building-a",
    "CityObjects": {
        "building-a": {
            "type": "Building",
            "children": ["building-a-part"],
            "attributes": {"name": "A"},
            "geometry": [{"type": "MultiSurface", "lod": "0", "boundaries": []}],
        },
        "building-a-part": {
            "type": "BuildingPart",
            "parents": ["building-a"],
            "geometry": [
                {
                    "type": "Solid",
                    "lod": "2.2",
                    "boundaries": [],
                    "semantics": {"surfaces": [{"type": "RoofSurface"}]},
                }
            ],
        },
    },
    "vertices": [[0, 0, 0], [1, 0, 0]],
}


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def write_jsonl(path: Path, *payloads: object) -> None:
    path.write_text(
        "".join(json.dumps(payload) + "\n" for payload in payloads),
        encoding="utf-8",
    )


class DescribeArtifactTest(unittest.TestCase):
    def test_cityjson_summary_counts_root_objects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.city.json"
            document = dict(HEADER)
            document["CityObjects"] = FEATURE["CityObjects"]
            document["vertices"] = FEATURE["vertices"]
            write_json(path, document)

            summary = describe_artifact(path, "cityjson")["summary"]

        self.assertEqual(summary["feature_count"], 1)
        self.assertEqual(summary["cityobject_count"], 2)
        self.assertEqual(
            summary["cityobject_types"], {"Building": 1, "BuildingPart": 1}
        )
        self.assertEqual(summary["vertex_count"], 2)
        self.assertEqual(summary["geometry_types"], ["MultiSurface", "Solid"])
        self.assertEqual(summary["lods"], ["0", "2.2"])
        self.assertEqual(summary["semantic_surface_types"], ["RoofSurface"])
        self.assertEqual(summary["attribute_keys"], ["name"])

    def test_jsonl_summary_aggregates_feature_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.city.jsonl"
            second_feature = dict(FEATURE)
            second_feature["id"] = "building-b"
            write_jsonl(path, HEADER, FEATURE, second_feature)

            summary = describe_artifact(path, "jsonl")["summary"]

        self.assertEqual(summary["feature_count"], 2)
        self.assertEqual(summary["cityobject_count"], 4)
        self.assertEqual(summary["vertex_count"], 4)

    def test_jsonl_rejects_missing_metadata_header(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.city.jsonl"
            write_jsonl(path, FEATURE)

            with self.assertRaisesRegex(ArtifactError, "CityJSON object"):
                describe_artifact(path, "jsonl")


class SplitFeatureFilesTest(unittest.TestCase):
    def test_split_writes_metadata_and_feature_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sample.city.jsonl"
            destination = root / "feature-files"
            write_jsonl(source, HEADER, FEATURE)

            split_feature_files(source, destination)
            summary = describe_artifact(destination, "feature-files")["summary"]

            self.assertTrue((destination / "metadata.json").exists())
            self.assertTrue(
                (destination / "features" / "building-a.city.jsonl").exists()
            )
            self.assertEqual(summary["feature_count"], 1)
            self.assertEqual(summary["cityobject_count"], 2)

    def test_split_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sample.city.jsonl"
            write_jsonl(source, HEADER, FEATURE, FEATURE)

            with self.assertRaisesRegex(ArtifactError, "duplicate feature id"):
                split_feature_files(source, root / "feature-files")

    def test_split_rejects_unsafe_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sample.city.jsonl"
            feature = dict(FEATURE)
            feature["id"] = "../outside"
            write_jsonl(source, HEADER, feature)

            with self.assertRaisesRegex(ArtifactError, "unsafe feature id"):
                split_feature_files(source, root / "feature-files")

    def test_directory_hash_is_deterministic(self) -> None:
        with (
            tempfile.TemporaryDirectory() as first_dir,
            tempfile.TemporaryDirectory() as second_dir,
        ):
            first = Path(first_dir)
            second = Path(second_dir)
            (first / "nested").mkdir()
            (second / "nested").mkdir()
            (first / "nested" / "b").write_text("two", encoding="utf-8")
            (first / "a").write_text("one", encoding="utf-8")
            (second / "a").write_text("one", encoding="utf-8")
            (second / "nested" / "b").write_text("two", encoding="utf-8")

            self.assertEqual(sha256_directory(first), sha256_directory(second))


if __name__ == "__main__":
    unittest.main()
