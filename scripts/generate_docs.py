from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files


ROOT = Path(__file__).resolve().parents[1]


def write_markdown(source: Path, destination: str, replacements: dict[str, str] | None = None) -> None:
    text = source.read_text(encoding="utf-8")
    for old, new in (replacements or {}).items():
        text = text.replace(old, new)

    with mkdocs_gen_files.open(destination, "w") as handle:
        handle.write(text)

    mkdocs_gen_files.set_edit_path(destination, source.relative_to(ROOT).as_posix())


def write_reference_page(
    source: Path,
    destination: str,
    title: str,
    summary: str,
    language: str = "json",
) -> None:
    text = source.read_text(encoding="utf-8").rstrip()
    page = f"# {title}\n\n{summary}\n\n```{language}\n{text}\n```\n"

    with mkdocs_gen_files.open(destination, "w") as handle:
        handle.write(page)

    mkdocs_gen_files.set_edit_path(destination, source.relative_to(ROOT).as_posix())


def main() -> None:
    write_markdown(
        ROOT / "README.md",
        "repository/index.md",
        {
            "docs/index.md": "../index.md",
            "docs/data-generation.md": "../data-generation.md",
            "catalog/corpus.json": "../reference/corpus.md",
            "profiles/cjfake-manifest.schema.json": "../reference/cjfake-manifest-schema.md",
            "docs/adr/0009-cityjson-benchmark-corpus-design.md": "../adr/0009-cityjson-benchmark-corpus-design.md",
        },
    )

    write_markdown(
        ROOT / "catalog/README.md",
        "catalog/index.md",
        {
            "[corpus.json](corpus.json)": "[corpus catalog](../reference/corpus.md)",
            "[cases/](cases/README.md)": "[cases/](cases/index.md)",
        },
    )
    write_markdown(ROOT / "catalog/cases/README.md", "catalog/cases/index.md")

    for source in sorted((ROOT / "catalog/cases").glob("*.md")):
        if source.name == "README.md":
            continue
        write_markdown(source, f"catalog/cases/{source.name}")

    write_markdown(
        ROOT / "profiles/README.md",
        "profiles/index.md",
        {
            "[cjfake-manifest.schema.json](cjfake-manifest.schema.json)": "[CJFake manifest schema](../reference/cjfake-manifest-schema.md)",
            "[cases/](cases/)": "[cases/](cases/index.md)",
        },
    )
    write_markdown(
        ROOT / "profiles/cases/README.md",
        "profiles/cases/index.md",
        {
            "`../cjfake-manifest.schema.json`": "[`../cjfake-manifest.schema.json`](../../reference/cjfake-manifest-schema.md)",
        },
    )

    write_markdown(
        ROOT / "pipelines/README.md",
        "pipelines/index.md",
        {"[`audit_corpus.sh`](audit_corpus.sh)": "[audit_corpus.sh](audit-corpus.md)"},
    )
    write_reference_page(
        ROOT / "pipelines/audit_corpus.sh",
        "pipelines/audit-corpus.md",
        "Audit Corpus Pipeline Script",
        "Shell implementation of the first executable corpus pipeline.",
        language="sh",
    )
    write_markdown(ROOT / "invariants/README.md", "invariants/index.md")
    write_markdown(ROOT / "artifacts/README.md", "artifacts/index.md")

    write_reference_page(
        ROOT / "catalog/corpus.json",
        "reference/corpus.md",
        "Corpus Catalog Reference",
        "Machine-readable benchmark catalog consumed by validation, generation, and benchmark harnesses.",
    )
    write_reference_page(
        ROOT / "profiles/cjfake-manifest.schema.json",
        "reference/cjfake-manifest-schema.md",
        "CJFake Manifest Schema",
        "Machine-readable schema for benchmark generation manifests.",
    )


main()
