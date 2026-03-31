# Profiles

This directory holds the manifests and input profiles used to build benchmark
cases.

The profile model belongs to this repository. `cjfake` is the first generator
expected to consume these profiles, but the profiles should stay benchmark- and
CityJSON-oriented rather than encode `cjfake`-internal assumptions.

The machine-readable contract for `cjfake` manifests is
[cjfake-manifest.schema.json](cjfake-manifest.schema.json). Any manifest in
this directory should validate against it.

Use profiles when a case is generated rather than checked in as a
ready-made artifact.

Expected profile families:

- synthetic profiles for `cjfake`-driven generation
- real-geometry augmentation profiles where `cjfake` adds non-geometric
  benchmark surfaces
- shared profile fragments if multiple cases reuse the same shape controls

Profiles should stay descriptive. They define how to produce a case, not the
benchmark result of running that case.
