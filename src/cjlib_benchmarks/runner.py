from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import statistics
import subprocess
from cjlib_benchmarks.model import CaseConfig, Manifest, OperationName, TargetConfig


REPO_ROOT = Path(__file__).resolve().parents[2]
OPERATIONS: tuple[OperationName, ...] = ("probe", "summary", "roundtrip")


@dataclass(frozen=True)
class RunSelection:
    targets: tuple[str, ...] | None = None
    cases: tuple[str, ...] | None = None


def load_manifest() -> Manifest:
    return Manifest.load(REPO_ROOT / "benchmarks" / "manifest.json")


def run_checked(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_case_input(case: CaseConfig) -> Path:
    if case.kind == "real":
        if case.source_path is None:
            raise ValueError(f"real case {case.identifier} is missing source_path")
        input_path = Path(case.source_path)
        if not input_path.exists():
            raise FileNotFoundError(f"missing real dataset for {case.identifier}: {input_path}")
        return input_path

    if case.kind != "synthetic":
        raise ValueError(f"unsupported case kind for {case.identifier}: {case.kind}")
    if case.profile_path is None or case.seed is None:
        raise ValueError(f"synthetic case {case.identifier} is missing profile_path or seed")

    output_path = REPO_ROOT / "data" / "generated" / f"{case.identifier}.city.json"
    if output_path.exists():
        return output_path

    ensure_directory(output_path.parent)
    profile_path = REPO_ROOT / case.profile_path
    command = [
        "cargo",
        "run",
        "--manifest-path",
        str(REPO_ROOT / "tools" / "cjfake-profile-gen" / "Cargo.toml"),
        "--",
        str(profile_path),
        str(case.seed),
        str(output_path),
    ]
    run_checked(command, cwd=REPO_ROOT)
    validate_cityjson(output_path)
    return output_path


def validate_cityjson(path: Path) -> None:
    run_checked(["cjval", "-q", str(path)], cwd=REPO_ROOT)


def prepare_data(selection: RunSelection) -> dict[str, str]:
    manifest = load_manifest()
    prepared: dict[str, str] = {}
    for case in select_cases(manifest, selection):
        prepared[case.identifier] = str(resolve_case_input(case))
    return prepared


def build_targets(selection: RunSelection) -> None:
    selected_targets = selection.targets or tuple(target.identifier for target in load_manifest().targets)
    wants_native = any(target in {"python", "cpp"} for target in selected_targets)
    wants_rust_wasm = any(target in {"rust", "wasm"} for target in selected_targets)

    if wants_native:
        run_checked([str(REPO_ROOT / "scripts" / "build_native.sh")], cwd=REPO_ROOT)
    if wants_rust_wasm:
        run_checked([str(REPO_ROOT / "scripts" / "build_rust_wasm.sh")], cwd=REPO_ROOT)


def select_targets(manifest: Manifest, selection: RunSelection) -> tuple[TargetConfig, ...]:
    if selection.targets is None:
        return manifest.targets
    wanted = set(selection.targets)
    return tuple(target for target in manifest.targets if target.identifier in wanted)


def select_cases(manifest: Manifest, selection: RunSelection) -> tuple[CaseConfig, ...]:
    if selection.cases is None:
        return manifest.cases
    wanted = set(selection.cases)
    return tuple(case for case in manifest.cases if case.identifier in wanted)


def result_median_ms(payload: dict[str, Any]) -> float:
    return statistics.median(payload["samples_ns"]) / 1_000_000.0


def run_suite(selection: RunSelection) -> Path:
    manifest = load_manifest()
    build_targets(selection)

    results_root = REPO_ROOT / "results" / "latest"
    raw_dir = results_root / "raw"
    outputs_dir = results_root / "outputs"
    ensure_directory(raw_dir)
    ensure_directory(outputs_dir)

    aggregated: list[dict[str, Any]] = []

    for case in select_cases(manifest, selection):
        input_path = resolve_case_input(case)
        for target in select_targets(manifest, selection):
            for operation in OPERATIONS:
                output_path = outputs_dir / case.identifier / f"{target.identifier}.city.json"
                result_json = raw_dir / f"{case.identifier}__{target.identifier}__{operation}.json"
                ensure_directory(output_path.parent)
                ensure_directory(result_json.parent)

                command = [
                    *target.command,
                    "--operation",
                    operation,
                    "--input",
                    str(input_path),
                    "--iterations",
                    str(manifest.defaults.iterations_for(operation)),
                    "--warmup",
                    str(manifest.defaults.warmup_iterations),
                    "--output",
                    str(output_path),
                    "--result-json",
                    str(result_json),
                ]
                if operation == "roundtrip":
                    command.append("--pretty-output")

                run_checked(command, cwd=REPO_ROOT)
                payload = json.loads(result_json.read_text(encoding="utf-8"))
                payload["case_id"] = case.identifier
                payload["case_description"] = case.description
                payload["target"] = target.identifier
                payload["operation"] = operation
                payload["input_path"] = str(input_path)
                payload["median_ms"] = result_median_ms(payload)
                if operation == "roundtrip":
                    validate_cityjson(output_path)
                    payload["validation"] = {
                        "tool": "cjval",
                        "ok": True,
                        "output_path": str(output_path),
                    }
                result_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
                aggregated.append(payload)

    summary_json = results_root / "summary.json"
    summary_md = results_root / "summary.md"
    summary_payload = build_summary(aggregated)
    summary_json.write_text(json.dumps(summary_payload, indent=2, sort_keys=True), encoding="utf-8")
    summary_md.write_text(render_summary_markdown(summary_payload), encoding="utf-8")
    return results_root


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    baseline: dict[tuple[str, str], float] = {}
    for item in results:
        key = (item["case_id"], item["operation"])
        if item["target"] == "rust":
            baseline[key] = item["median_ms"]

    enriched: list[dict[str, Any]] = []
    for item in results:
        key = (item["case_id"], item["operation"])
        rust_median = baseline.get(key)
        overhead_ratio = None
        overhead_percent = None
        if rust_median is not None and rust_median > 0:
            overhead_ratio = item["median_ms"] / rust_median
            overhead_percent = ((item["median_ms"] - rust_median) / rust_median) * 100.0

        enriched.append(
            {
                **item,
                "rust_baseline_ms": rust_median,
                "overhead_ratio_vs_rust": overhead_ratio,
                "overhead_percent_vs_rust": overhead_percent,
            }
        )

    return {
        "repo": str(REPO_ROOT),
        "results": enriched,
    }


def render_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Benchmark Summary",
        "",
        "| Case | Operation | Target | Median ms | Ratio vs Rust | Valid |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for item in summary["results"]:
        ratio = item["overhead_ratio_vs_rust"]
        ratio_text = f"{ratio:.2f}x" if ratio is not None else "n/a"
        valid = item.get("validation", {}).get("ok", "")
        valid_text = "yes" if valid is True else ""
        lines.append(
            f"| {item['case_id']} | {item['operation']} | {item['target']} | "
            f"{item['median_ms']:.3f} | {ratio_text} | {valid_text} |"
        )
    lines.append("")
    return "\n".join(lines)
