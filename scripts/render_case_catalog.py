from __future__ import annotations

import argparse

from corpus_cases import CATALOG_PATH, load_case_records, render_catalog_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the derived case catalog.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if catalog/cases.json does not match the current cases/ tree.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_case_records()
    rendered = render_catalog_text(records)

    if args.check:
        if not CATALOG_PATH.exists():
            raise SystemExit(f"missing catalog file: {CATALOG_PATH}")

        current = CATALOG_PATH.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit(
                "catalog/cases.json is out of date; run `uv run python ./scripts/render_case_catalog.py`"
            )

        print(f"catalog is up to date at {CATALOG_PATH}")
        return

    CATALOG_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {CATALOG_PATH}")


if __name__ == "__main__":
    main()
