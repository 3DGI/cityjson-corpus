set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default:
    @just --list

help:
    @just --list

validate-profiles:
    ./scripts/validate_profiles.sh

validate-cases:
    uv run python ./scripts/validate_case_layout.py

generate-data:
    ./scripts/generate_data.sh

audit-corpus:
    ./pipelines/audit_corpus.sh

bootstrap-cases:
    uv run python ./scripts/bootstrap_case_layout.py

docs-serve:
    uv run mkdocs serve

docs-build:
    uv run mkdocs build
