set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

_default:
    @just --list

# Format Python files with ruff.
fmt:
    uvx --from ruff ruff format .

# Lint Python, validate the case tree and catalog sync, and run cjval.
lint:
    @echo "{{BOLD}}Linting Python files...{{NORMAL}}"
    @uvx --from ruff ruff check .
    @echo "{{BOLD}}Validating case tree...{{NORMAL}}"
    @uv run python ./scripts/validate_case_layout.py
    just cjval

# Run cjval on all conformance cases.
cjval:
    @echo "{{BOLD}}Running cjval on conformance cases...{{NORMAL}}"
    @status=0; while IFS= read -r -d '' file; do basename="$(basename "$file")"; output="$(cjval -q -e schemas/cityjson/noise.ext.json "$file" 2>&1)"; printf "%s %s\n" "$output" "$basename"; case "$output" in *"❌ File is invalid"*) status=1 ;; esac; done < <(find cases/conformance/v2_0 -type f -name '*.city.json' -print0); exit "$status"

# Rewrite catalog/cases.json and artifacts/correctness-index.json from cases/.
sync-catalog:
    uv run python ./scripts/render_case_catalog.py
    uv run python ./scripts/render_correctness_index.py

# Materialize synthetic workloads into artifacts/generated/ and write artifacts/benchmark-index.json.
generate-data:
    ./scripts/generate_data.sh
    just _cjval-generated

[private]
_cjval-generated:
    @echo "{{BOLD}}Running cjval on generated workload cases...{{NORMAL}}"
    @status=0; while IFS= read -r -d '' file; do basename="$(basename "$file")"; output="$(cjval -q "$file" 2>&1)"; printf "%s %s\n" "$output" "$basename"; case "$output" in *"❌ File is invalid"*) status=1 ;; esac; done < <(find artifacts/generated -type f -name '*.city.json' -print0); exit "$status"

# Download the published 3DBAG slice (CityJSON, cityjson-arrow, cityjson-parquet) into artifacts/acquired/.
acquire-3dbag:
    ./scripts/acquire_3dbag.sh

# Download the published Basisvoorziening 3D tile (CityJSON, cityjson-arrow, cityjson-parquet) into artifacts/acquired/.
acquire-basisvoorziening-3d:
    ./scripts/acquire_basisvoorziening_3d.sh

# Remove generated workload data, acquired artifacts, derived indexes, generated docs pages, and the built site.
clean:
    rm -rf artifacts/generated
    rm -rf artifacts/acquired
    rm -f artifacts/benchmark-index.json
    rm -f artifacts/correctness-index.json
    rm -f catalog/cases.json
    rm -rf docs/artifacts docs/cases docs/catalog docs/pipelines docs/reference docs/repository docs/schemas
    rm -rf site

# Start a local ProperDocs dev server.
docs-serve:
    uv run properdocs serve -o

# Build the MkDocs site.
docs-build:
    uv run properdocs build
