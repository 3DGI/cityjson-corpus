#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


JsonObject = dict[str, object]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_YEAR = 2022
DEFAULT_TILE_SLUG = "84000_450000"
DEFAULT_API_URL = (
    "https://api.pdok.nl/kadaster/3d-basisvoorziening/ogc/v1/collections/"
    "basisbestand_gebouwen_terreinen/items?f=json&limit=1000"
)


class AcquisitionError(RuntimeError):
    pass


def env_value(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Acquire the pinned Basisvoorziening 3D CityJSON tile."
    )
    parser.add_argument(
        "--api-url",
        default=env_value("CORPUS_BASISVOORZIENING_3D_API_URL", DEFAULT_API_URL),
        help="OGC API items endpoint to query.",
    )
    parser.add_argument(
        "--dataset-year",
        type=int,
        default=int(
            env_value(
                "CORPUS_BASISVOORZIENING_3D_YEAR",
                str(DEFAULT_DATASET_YEAR),
            )
        ),
        help="Target Basisvoorziening 3D release year.",
    )
    parser.add_argument(
        "--tile-slug",
        default=env_value("CORPUS_BASISVOORZIENING_3D_TILE_SLUG", DEFAULT_TILE_SLUG),
        help="Target tile identifier.",
    )
    parser.add_argument(
        "--archive-name",
        default=env_value("CORPUS_BASISVOORZIENING_3D_ARCHIVE_NAME"),
        help="Expected upstream archive name.",
    )
    parser.add_argument(
        "--cityjson-name",
        default=env_value("CORPUS_BASISVOORZIENING_3D_CITYJSON_NAME"),
        help="CityJSON member name inside the archive.",
    )
    parser.add_argument(
        "--output-root",
        default=env_value("CORPUS_BASISVOORZIENING_3D_OUTPUT_ROOT"),
        help="Directory where the acquired artifacts should be written.",
    )
    return parser


def load_json_object(payload: bytes, source: str) -> JsonObject:
    try:
        document = json.loads(payload.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise AcquisitionError(f"{source} is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise AcquisitionError(f"{source} is not valid JSON") from exc

    if not isinstance(document, dict):
        raise AcquisitionError(f"expected a JSON object from {source}")
    return document


def fetch_json(url: str) -> JsonObject:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/geo+json, application/json",
            "User-Agent": "cityjson-corpus/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return load_json_object(response.read(), url)
    except urllib.error.HTTPError as exc:
        raise AcquisitionError(f"failed to fetch {url}: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise AcquisitionError(f"failed to fetch {url}: {exc.reason}") from exc


def get_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise AcquisitionError(f"missing or invalid {label}")
    return value


def get_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AcquisitionError(f"missing or invalid {label}")
    return value


def next_page_url(document: JsonObject, current_url: str) -> str | None:
    raw_links = document.get("links")
    if isinstance(raw_links, list):
        for link in raw_links:
            if not isinstance(link, dict):
                continue
            if link.get("rel") != "next":
                continue
            href = link.get("href")
            if isinstance(href, str) and href:
                return urljoin(current_url, href)

    raw_next = document.get("next")
    if isinstance(raw_next, str) and raw_next:
        return urljoin(current_url, raw_next)
    return None


def find_feature(items_url: str, tile_slug: str, dataset_year: int) -> tuple[JsonObject, str, int]:
    current_url = items_url
    page_number = 0
    while current_url:
        page_number += 1
        document = fetch_json(current_url)
        raw_features = document.get("features")
        if not isinstance(raw_features, list):
            raise AcquisitionError(f"expected features array on page {page_number} from {current_url}")

        for feature in raw_features:
            if not isinstance(feature, dict):
                continue
            raw_properties = feature.get("properties")
            if not isinstance(raw_properties, dict):
                continue

            if str(raw_properties.get("bladnr")) != tile_slug:
                continue
            if get_int(raw_properties.get("jaargang_luchtfoto"), "jaargang_luchtfoto") != dataset_year:
                continue

            download_url = get_string(raw_properties.get("download_link"), "download_link")
            download_size_bytes = get_int(
                raw_properties.get("download_size_bytes"), "download_size_bytes"
            )
            return feature, download_url, download_size_bytes

        current_url = next_page_url(document, current_url)

    raise AcquisitionError(
        f"tile {tile_slug!r} for year {dataset_year} was not found in {items_url}"
    )


def download_file(download_url: str, destination: Path) -> None:
    request = urllib.request.Request(
        download_url,
        headers={"User-Agent": "cityjson-corpus/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    except urllib.error.HTTPError as exc:
        raise AcquisitionError(f"failed to download {download_url}: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise AcquisitionError(f"failed to download {download_url}: {exc.reason}") from exc


def extract_cityjson(archive_path: Path, cityjson_name: str, destination: Path) -> None:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            try:
                with archive.open(cityjson_name) as source, destination.open("wb") as handle:
                    shutil.copyfileobj(source, handle)
            except KeyError as exc:
                raise AcquisitionError(
                    f"{cityjson_name} was not found in {archive_path.name}"
                ) from exc
    except zipfile.BadZipFile as exc:
        raise AcquisitionError(f"{archive_path} is not a valid zip archive") from exc


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stat_size(path: Path) -> int:
    return path.stat().st_size


def json_dump(path: Path, payload: JsonObject) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_outputs_json(output_root: Path, dataset_year: int, cityjson_name: str) -> list[JsonObject]:
    cityjson_path = output_root / cityjson_name
    output_path = f"artifacts/acquired/basisvoorziening-3d/{dataset_year}/{cityjson_name}"
    return [
        {
            "path": output_path,
            "representation": "cityjson",
            "producer": "upstream",
            "derivation": "acquired",
            "validation_role": "canonical",
            "checksum": sha256sum(cityjson_path),
            "byte_size": stat_size(cityjson_path),
            "published": True,
        }
    ]


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    dataset_year = args.dataset_year
    tile_slug = args.tile_slug
    archive_name = (
        args.archive_name
        if args.archive_name is not None
        else f"volledig_{dataset_year}_{tile_slug}.zip"
    )
    cityjson_name = (
        args.cityjson_name
        if args.cityjson_name is not None
        else f"3d_volledig_{tile_slug}.city.json"
    )
    output_root = (
        Path(args.output_root)
        if args.output_root is not None
        else ROOT / "artifacts" / "acquired" / "basisvoorziening-3d" / str(dataset_year)
    )
    metadata_path = output_root / "metadata.json"
    manifest_path = output_root / "manifest.json"
    cityjson_path = output_root / cityjson_name

    output_root.mkdir(parents=True, exist_ok=True)

    _feature, download_url, download_size_bytes = find_feature(args.api_url, tile_slug, dataset_year)

    if not cityjson_path.exists():
        with tempfile.NamedTemporaryFile(
            prefix=f"{cityjson_path.stem}.",
            suffix=".zip",
            dir=output_root,
            delete=False,
        ) as temp_file:
            temp_archive_path = Path(temp_file.name)
        try:
            download_file(download_url, temp_archive_path)
            actual_size = stat_size(temp_archive_path)
            if actual_size != download_size_bytes:
                raise AcquisitionError(
                    "downloaded archive size mismatch: "
                    f"expected {download_size_bytes}, got {actual_size}"
                )
            extract_cityjson(temp_archive_path, cityjson_name, cityjson_path)
        finally:
            temp_archive_path.unlink(missing_ok=True)

    metadata = {
        "dataset": "Basisvoorziening 3D",
        "dataset_year": dataset_year,
        "tile_slug": tile_slug,
        "archive_name": archive_name,
        "cityjson_name": cityjson_name,
        "source_api_url": args.api_url,
        "download_url": download_url,
        "download_size_bytes": download_size_bytes,
    }
    json_dump(metadata_path, metadata)

    manifest = {
        "dataset": "Basisvoorziening 3D",
        "upstream_version": str(dataset_year),
        "tile_slug": tile_slug,
        "case_id": "io_basisvoorziening_3d_cityjson",
        "outputs": build_outputs_json(output_root, dataset_year, cityjson_name),
    }
    json_dump(manifest_path, manifest)

    print(f"wrote {cityjson_path}")
    print(f"wrote {metadata_path}")
    print(f"wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AcquisitionError as exc:
        raise SystemExit(str(exc)) from exc
