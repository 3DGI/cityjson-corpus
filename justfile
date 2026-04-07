set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

_default:
    @just --list

# Format Python files with ruff.
fmt:
    uvx --from ruff ruff format .

# Lint Python, validate the case tree and catalog sync, and check profile fixtures.
lint:
    uvx --from ruff ruff check .
    uv run python ./scripts/validate_case_layout.py
    ./scripts/validate_profiles.sh

# Rewrite catalog/cases.json and artifacts/correctness-index.json from cases/.
sync-catalog:
    uv run python ./scripts/render_case_catalog.py
    uv run python ./scripts/render_correctness_index.py

# Materialize synthetic workloads into artifacts/generated/ and write artifacts/benchmark-index.json.
generate-data:
    ./scripts/generate_data.sh

# Download the published 3DBAG slice (CityJSON, cityarrow, cityparquet) into artifacts/acquired/.
acquire-3dbag:
    ./scripts/acquire_3dbag.sh

# Start a local MkDocs dev server.
docs-serve:
    uv run mkdocs serve

# Build the MkDocs site.
docs-build:
    uv run mkdocs build
