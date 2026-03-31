# Profiles

This directory holds the input profiles used to build benchmark cases.

Use profiles when a case is generated or derived rather than checked in as a
ready-made artifact.

Expected profile families:

- synthetic profiles for `cjfake`-driven generation
- derived profiles for `3DBAG` reshaping and enrichment
- shared profile fragments if multiple cases reuse the same shape controls

Profiles should stay descriptive. They define how to produce a case, not the
benchmark result of running that case.

