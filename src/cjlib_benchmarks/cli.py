from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from cjlib_benchmarks.runner import RunSelection, build_targets, prepare_data, run_suite


def parse_csv(value: str | None) -> tuple[str, ...] | None:
    if value is None or value == "":
        return None
    return tuple(item.strip() for item in value.split(",") if item.strip())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cjlib-bench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("prepare-data", "build", "run"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--targets")
        subparser.add_argument("--cases")

    return parser


def selection_from_args(args: argparse.Namespace) -> RunSelection:
    return RunSelection(
        targets=parse_csv(args.targets),
        cases=parse_csv(args.cases),
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    selection = selection_from_args(args)

    try:
        match args.command:
            case "prepare-data":
                prepared = prepare_data(selection)
                json.dump(prepared, sys.stdout, indent=2, sort_keys=True)
                sys.stdout.write("\n")
                return 0
            case "build":
                build_targets(selection)
                return 0
            case "run":
                results_root = run_suite(selection)
                print(results_root)
                return 0
            case _:
                parser.error(f"unsupported command: {args.command}")
    except (
        FileNotFoundError,
        OSError,
        RuntimeError,
        ValueError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
