set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default:
    @just --list

help:
    @just --list

validate-profiles:
    ./scripts/validate_profiles.sh

validate-cases:
    uv run python ./scripts/validate_case_layout.py

sync-catalog:
    uv run python ./scripts/render_case_catalog.py
    uv run python ./scripts/render_correctness_index.py

generate-data:
    ./scripts/generate_data.sh

acquire-3dbag:
    ./scripts/acquire_3dbag.sh

audit-corpus:
    ./pipelines/audit_corpus.sh

bootstrap-cases:
    uv run python ./scripts/bootstrap_case_layout.py
    uv run python ./scripts/render_case_catalog.py
    uv run python ./scripts/render_correctness_index.py

docs-serve:
    uv run mkdocs serve

docs-build:
    uv run mkdocs build
