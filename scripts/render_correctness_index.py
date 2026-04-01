from __future__ import annotations

import argparse

from corpus_cases import (
    CORRECTNESS_INDEX_PATH,
    load_case_records,
    render_correctness_index_text,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the derived correctness case index."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if artifacts/correctness-index.json does not match the current cases/ tree.",
    )
    args = parser.parse_args()

    records = load_case_records()
    rendered = render_correctness_index_text(records)

    if args.check:
        if not CORRECTNESS_INDEX_PATH.exists():
            raise SystemExit(
                f"missing correctness index file: {CORRECTNESS_INDEX_PATH}"
            )

        current = CORRECTNESS_INDEX_PATH.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit(
                "artifacts/correctness-index.json is out of date; run "
                "`uv run python ./scripts/render_correctness_index.py`"
            )

        print(f"correctness index is up to date at {CORRECTNESS_INDEX_PATH}")
        return

    CORRECTNESS_INDEX_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {CORRECTNESS_INDEX_PATH}")


if __name__ == "__main__":
    main()
