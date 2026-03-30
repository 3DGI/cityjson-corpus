#!/usr/bin/env python3
"""Benchmark the cjlib Python FFI over real CityJSON inputs.

Result JSON schema:
- language, operation, input, iterations, warmup, pretty_output
- timing_ns: total, per_iteration
- input_bytes, output_bytes
- probe: root_kind, version, has_version
- summary: model_type, counts, and feature flags
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import json
import os
from pathlib import Path
import sys
import time
from typing import Any


def _discover_cjlib_source() -> Path:
    env_root = os.environ.get("CJLIB_ROOT")
    if env_root:
        root = Path(env_root)
    else:
        root = Path(__file__).resolve().parents[2].parent / "cjlib"

    candidate = root / "ffi" / "python" / "src"
    if not candidate.exists():
        raise SystemExit(f"missing cjlib python source path: {candidate}")
    return candidate


sys.path.insert(0, str(_discover_cjlib_source()))

from cjlib import CityModel, Probe, WriteOptions, probe_bytes  # noqa: E402


@dataclass(frozen=True)
class BenchmarkArgs:
    operation: str
    input_path: Path
    iterations: int
    warmup: int
    output_path: Path | None
    pretty_output: bool
    result_json: Path


@dataclass(frozen=True)
class BenchmarkResult:
    language: str
    operation: str
    input: str
    iterations: int
    warmup: int
    pretty_output: bool
    timing_ns: dict[str, int | float]
    samples_ns: list[int]
    input_bytes: int
    output_bytes: int
    probe: dict[str, Any] | None
    summary: dict[str, Any] | None
    output_path: str | None


def parse_args() -> BenchmarkArgs:
    parser = argparse.ArgumentParser(description="Benchmark the cjlib Python FFI")
    parser.add_argument("--operation", choices=("probe", "summary", "roundtrip"), required=True)
    parser.add_argument("--input", dest="input_path", type=Path, required=True)
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument("--warmup", type=int, required=True)
    parser.add_argument("--output", dest="output_path", type=Path)
    parser.add_argument("--pretty-output", action="store_true")
    parser.add_argument("--result-json", dest="result_json", type=Path, required=True)
    namespace = parser.parse_args()
    if namespace.iterations <= 0:
        raise SystemExit("--iterations must be greater than 0")
    if namespace.warmup < 0:
        raise SystemExit("--warmup must be 0 or greater")
    return BenchmarkArgs(
        operation=namespace.operation,
        input_path=namespace.input_path,
        iterations=namespace.iterations,
        warmup=namespace.warmup,
        output_path=namespace.output_path,
        pretty_output=namespace.pretty_output,
        result_json=namespace.result_json,
    )


def _probe_payload(payload: bytes) -> Probe:
    return probe_bytes(payload)


def _summary_payload(model: CityModel) -> dict[str, Any]:
    summary = model.summary()
    return {
        "model_type": summary.model_type.name,
        "version": summary.version.name,
        "cityobject_count": summary.cityobject_count,
        "geometry_count": summary.geometry_count,
        "geometry_template_count": summary.geometry_template_count,
        "vertex_count": summary.vertex_count,
        "template_vertex_count": summary.template_vertex_count,
        "uv_coordinate_count": summary.uv_coordinate_count,
        "semantic_count": summary.semantic_count,
        "material_count": summary.material_count,
        "texture_count": summary.texture_count,
        "extension_count": summary.extension_count,
        "has_metadata": summary.has_metadata,
        "has_transform": summary.has_transform,
        "has_templates": summary.has_templates,
        "has_appearance": summary.has_appearance,
    }


def _probe_data(probe: Probe) -> dict[str, Any]:
    return {
        "root_kind": probe.root_kind.name,
        "version": probe.version.name,
        "has_version": probe.has_version,
    }


def run_benchmark(args: BenchmarkArgs) -> BenchmarkResult:
    if args.operation == "roundtrip" and args.output_path is None:
        raise SystemExit("--output is required for roundtrip")

    payload = args.input_path.read_bytes()

    probe_result: Probe | None = None
    summary_result: dict[str, Any] | None = None
    output_bytes = 0
    last_output: bytes | None = None
    samples_ns: list[int] = []

    for _ in range(args.warmup):
        if args.operation == "probe":
            _probe_payload(payload)
            continue

        model = CityModel.parse_document_bytes(payload)
        try:
            if args.operation == "summary":
                _summary_payload(model)
            else:
                serialized = model.serialize_document(
                    WriteOptions(pretty=args.pretty_output, validate_default_themes=True)
                ).encode("utf-8")
                output_bytes = len(serialized)
                last_output = serialized
        finally:
            model.close()

    for _ in range(args.iterations):
        sample_start = time.perf_counter_ns()
        if args.operation == "probe":
            probe_result = _probe_payload(payload)
        else:
            model = CityModel.parse_document_bytes(payload)
            try:
                summary_result = _summary_payload(model)
                if args.operation == "roundtrip":
                    serialized = model.serialize_document(
                        WriteOptions(pretty=args.pretty_output, validate_default_themes=True)
                    ).encode("utf-8")
                    output_bytes = len(serialized)
                    last_output = serialized
            finally:
                model.close()
        samples_ns.append(time.perf_counter_ns() - sample_start)

    elapsed_ns = sum(samples_ns)

    if args.operation == "roundtrip":
        if last_output is None:
            raise SystemExit("roundtrip produced no output")
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_bytes(last_output)

    if args.operation == "probe":
        probe_payload = _probe_data(probe_result) if probe_result is not None else None
        summary_payload = None
    else:
        probe_payload = None
        summary_payload = summary_result

    return BenchmarkResult(
        language="python",
        operation=args.operation,
        input=str(args.input_path),
        iterations=args.iterations,
        warmup=args.warmup,
        pretty_output=args.pretty_output,
        timing_ns={
            "total": elapsed_ns,
            "per_iteration": elapsed_ns / len(samples_ns),
        },
        samples_ns=samples_ns,
        input_bytes=len(payload),
        output_bytes=output_bytes,
        probe=probe_payload,
        summary=summary_payload,
        output_path=str(args.output_path) if args.output_path is not None else None,
    )


def main() -> int:
    args = parse_args()
    result = run_benchmark(args)
    args.result_json.parent.mkdir(parents=True, exist_ok=True)
    args.result_json.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
