# Artifacts

This directory is for built benchmark outputs that are suitable for release,
distribution, or pinning in downstream benchmark runs.

Examples:

- generated CityJSON benchmark fixtures
- sourced `3DBAG` benchmark subsets
- alternate layout exports such as `jsonl` or `feature-files`
- checksums or release metadata

Do not treat this directory as the source of truth for case design. The source
of truth is the combination of the catalog, profiles, and pipelines that can
reproduce these artifacts.
