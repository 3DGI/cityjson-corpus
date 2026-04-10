from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import mkdocs_gen_files
import mkdocs_gen_files.editor as mkdocs_editor
from mkdocs.config import load_config as load_mkdocs_config

SCRIPT_DIR = Path(__file__).resolve().parent
CORPUS_CASES_PATH = SCRIPT_DIR / "corpus_cases.py"
DOCS_CONFIG_PATH = SCRIPT_DIR.parent / "properdocs.yml"


def configure_mkdocs_gen_files() -> None:
    if not DOCS_CONFIG_PATH.exists():
        return

    def load_properdocs_config(config_file=None, *, config_file_path=None, **kwargs):
        if config_file is None and config_file_path is None:
            config_file = str(DOCS_CONFIG_PATH)
        return load_mkdocs_config(
            config_file, config_file_path=config_file_path, **kwargs
        )

    mkdocs_editor.load_config = load_properdocs_config


def load_corpus_cases_module():
    spec = importlib.util.spec_from_file_location("corpus_cases", CORPUS_CASES_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"failed to load corpus_cases module from {CORPUS_CASES_PATH}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("corpus_cases", module)
    spec.loader.exec_module(module)
    return module


corpus_cases = load_corpus_cases_module()
ROOT = corpus_cases.ROOT
humanize_case_id = corpus_cases.humanize_case_id
load_case_records = corpus_cases.load_case_records
repo_relative = corpus_cases.repo_relative
configure_mkdocs_gen_files()


CASE_ROOT = ROOT / "cases"
CJFAKE_SCHEMA_SOURCE = (
    ROOT.parent / "cjfake" / "src" / "data" / "cjfake-manifest.schema.json"
)
CJFAKE_SCHEMA_PAGE = "reference/cjfake-manifest-schema.md"
CJFAKE_SCHEMA_LINK = (
    "https://github.com/3DGI/cjfake/blob/main/src/data/cjfake-manifest.schema.json"
)


def write_markdown(
    source: Path, destination: str, replacements: dict[str, str] | None = None
) -> None:
    text = source.read_text(encoding="utf-8")
    for old, new in (replacements or {}).items():
        text = text.replace(old, new)

    with mkdocs_gen_files.open(destination, "w") as handle:
        handle.write(text)

    mkdocs_gen_files.set_edit_path(destination, source.relative_to(ROOT).as_posix())


def write_generated_markdown(destination: str, text: str, edit_path: Path) -> None:
    with mkdocs_gen_files.open(destination, "w") as handle:
        handle.write(text)

    try:
        edit_target = edit_path.relative_to(ROOT).as_posix()
    except ValueError:
        return

    mkdocs_gen_files.set_edit_path(destination, edit_target)


def write_reference_page(
    source: Path,
    destination: str,
    title: str,
    summary: str,
    language: str = "json",
) -> None:
    text = source.read_text(encoding="utf-8").rstrip()
    page = f"# {title}\n\n{summary}\n\n```{language}\n{text}\n```\n"
    write_generated_markdown(destination, page, source)


def strip_title(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def summary_from_text(text: str) -> str:
    for chunk in text.split("\n\n"):
        summary = " ".join(line.strip() for line in chunk.splitlines() if line.strip())
        if summary:
            return summary
    return ""


def case_page_path(case_dir: Path) -> str:
    relative_dir = case_dir.relative_to(CASE_ROOT).as_posix()
    return f"cases/{relative_dir}.md"


def load_optional_json(path: Path | None) -> dict[str, object] | None:
    if path is None or not path.exists():
        return None

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None
    return payload


def render_json_block(title: str, payload: dict[str, object] | None) -> str:
    if payload is None:
        return ""

    rendered = json.dumps(payload, indent=2, sort_keys=True)
    return f"## {title}\n\n```json\n{rendered}\n```\n"


def build_case_page(record) -> str:
    title = humanize_case_id(record.case_id)
    parts = [f"# {title}", ""]

    if record.readme_path is not None:
        readme_text = strip_title(record.readme_path.read_text(encoding="utf-8"))
        if readme_text:
            parts.extend([readme_text, ""])
    elif isinstance(record.case_data.get("description"), str):
        parts.extend([str(record.case_data["description"]), ""])

    contract_lines = [
        "## Contract",
        "",
        f"- `id`: `{record.case_id}`",
        f"- `layer`: `{record.case_data['layer']}`",
        f"- `family`: `{record.case_data['family']}`",
        f"- `artifact_mode`: `{record.case_data['artifact_mode']}`",
        f"- `source_kind`: `{record.case_data['source_kind']}`",
        f"- `representation`: `{record.case_data['representation']}`",
    ]
    contract_lines.append(f"- `path`: `{repo_relative(record.case_dir)}`")
    contract_lines.append("")
    parts.extend(contract_lines)

    artifact_lines = []
    for key, value in sorted(record.artifact_paths.items()):
        artifact_lines.append(f"- `{key}`: `{value}`")

    if artifact_lines:
        parts.extend(["## Artifacts", "", *artifact_lines, ""])

    parts.append(render_json_block("case.json", record.case_data).rstrip())
    parts.append("")
    parts.append(render_json_block("invariants.json", record.invariants_data).rstrip())
    parts.append("")

    profile_payload = (
        load_optional_json(ROOT / record.artifact_paths["profile"])
        if "profile" in record.artifact_paths
        else None
    )
    acquisition_payload = (
        load_optional_json(ROOT / record.artifact_paths["acquisition"])
        if "acquisition" in record.artifact_paths
        else None
    )

    if profile_payload is not None:
        parts.append(render_json_block("profile.json", profile_payload).rstrip())
        parts.append("")

    if acquisition_payload is not None:
        parts.append(
            render_json_block("acquisition.json", acquisition_payload).rstrip()
        )
        parts.append("")

    return "\n".join(part for part in parts if part is not None).rstrip() + "\n"


def build_layer_index(title: str, records: list, index_path: str) -> str:
    parent = Path(index_path).parent
    parts = [f"# {title}", ""]

    for record in sorted(records, key=lambda item: item.case_id):
        case_summary = ""
        if record.readme_path is not None:
            case_summary = summary_from_text(
                strip_title(record.readme_path.read_text(encoding="utf-8"))
            )
        elif isinstance(record.case_data.get("description"), str):
            case_summary = str(record.case_data["description"])
        elif record.invariants_data.get("checks"):
            first_check = record.invariants_data["checks"][0]
            if isinstance(first_check, dict) and isinstance(
                first_check.get("description"), str
            ):
                case_summary = str(first_check["description"])

        link_path = Path(case_page_path(record.case_dir)).relative_to(parent).as_posix()
        parts.append(f"- [{record.case_id}]({link_path})")
        if case_summary:
            parts.append(f"  {case_summary}")

    parts.append("")
    return "\n".join(parts)


def main() -> None:
    records = load_case_records()

    write_markdown(
        ROOT / "README.md",
        "repository/index.md",
        {
            "docs/index.md": "../index.md",
            "catalog/cases.json": "../reference/cases.md",
            CJFAKE_SCHEMA_LINK: f"../{CJFAKE_SCHEMA_PAGE}",
            "cases/README.md": "../cases/index.md",
            "schemas/README.md": "../schemas/index.md",
            "docs/data-generation.md": "../data-generation.md",
            "docs/adr/0009-cityjson-benchmark-corpus-design.md": "../adr/0009-cityjson-benchmark-corpus-design.md",
        },
    )

    write_markdown(
        ROOT / "catalog" / "README.md",
        "catalog/index.md",
        {
            "[cases.json](cases.json)": "[cases.json](../reference/cases.md)",
            "[`cases/`](../cases/README.md)": "[`cases/`](../cases/index.md)",
        },
    )

    write_markdown(
        ROOT / "cases" / "README.md",
        "cases/index.md",
        {
            "`catalog/cases.json`": "[`catalog/cases.json`](../reference/cases.md)",
            "[`schemas/README.md`](../schemas/README.md)": "[`schemas/index.md`](../schemas/index.md)",
        },
    )
    write_markdown(
        ROOT / "schemas" / "README.md",
        "schemas/index.md",
        {
            "[case.schema.json](case.schema.json)": "[case.schema.json](../reference/case-schema.md)",
            "[invariants.schema.json](invariants.schema.json)": "[invariants.schema.json](../reference/invariants-schema.md)",
            "[acquisition.schema.json](acquisition.schema.json)": "[acquisition.schema.json](../reference/acquisition-schema.md)",
            f"[cjfake-manifest.schema.json]({CJFAKE_SCHEMA_LINK})": f"[cjfake-manifest.schema.json](../{CJFAKE_SCHEMA_PAGE})",
            "[`cases/`](../cases/README.md)": "[`cases/`](../cases/index.md)",
        },
    )
    write_markdown(ROOT / "pipelines" / "README.md", "pipelines/index.md")
    write_markdown(ROOT / "artifacts" / "README.md", "artifacts/index.md")

    grouped_records: dict[str, list] = {
        "conformance": [],
        "operation": [],
        "workload": [],
        "invalid": [],
    }

    for record in records:
        grouped_records[str(record.case_data["layer"])].append(record)
        page_path = case_page_path(record.case_dir)
        write_generated_markdown(page_path, build_case_page(record), record.case_path)

    write_generated_markdown(
        "cases/conformance/index.md",
        build_layer_index(
            "Conformance Cases",
            grouped_records["conformance"],
            "cases/conformance/index.md",
        ),
        ROOT / "cases" / "README.md",
    )
    write_generated_markdown(
        "cases/operations/index.md",
        build_layer_index(
            "Operation Cases", grouped_records["operation"], "cases/operations/index.md"
        ),
        ROOT / "cases" / "README.md",
    )
    write_generated_markdown(
        "cases/workloads/index.md",
        build_layer_index(
            "Workload Cases", grouped_records["workload"], "cases/workloads/index.md"
        ),
        ROOT / "cases" / "README.md",
    )
    write_generated_markdown(
        "cases/invalid/index.md",
        build_layer_index(
            "Invalid Cases", grouped_records["invalid"], "cases/invalid/index.md"
        ),
        ROOT / "cases" / "README.md",
    )

    write_reference_page(
        ROOT / "catalog" / "cases.json",
        "reference/cases.md",
        "Derived Case Catalog",
        "Machine-readable case index rendered from the canonical cases/ tree.",
    )
    write_reference_page(
        CJFAKE_SCHEMA_SOURCE,
        CJFAKE_SCHEMA_PAGE,
        "CJFake Manifest Schema",
        "Machine-readable schema for benchmark generation manifests.",
    )
    write_reference_page(
        ROOT / "schemas" / "case.schema.json",
        "reference/case-schema.md",
        "Case Schema",
        "Machine-readable schema for per-case metadata contracts.",
    )
    write_reference_page(
        ROOT / "schemas" / "invariants.schema.json",
        "reference/invariants-schema.md",
        "Invariants Schema",
        "Machine-readable schema for per-case invariants.",
    )
    write_reference_page(
        ROOT / "schemas" / "acquisition.schema.json",
        "reference/acquisition-schema.md",
        "Acquisition Schema",
        "Machine-readable schema for per-case real-data acquisition metadata.",
    )


main()
