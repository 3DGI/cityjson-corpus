set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default:
    @just --list

help:
    @just --list

validate-profiles:
    ./scripts/validate_profiles.sh

audit-corpus:
    ./pipelines/audit_corpus.sh

docs-serve:
    uv run mkdocs serve

docs-build:
    uv run mkdocs build
