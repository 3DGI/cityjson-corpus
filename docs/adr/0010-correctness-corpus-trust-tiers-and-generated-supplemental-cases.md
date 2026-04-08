# ADR 0010: Correctness Corpus Trust Tiers and Generated Supplemental Cases

## Status

Accepted.

## Context

The current repository contract is internally inconsistent.

The top-level README and `cases/README.md` both describe the correctness
corpus as checked-in or acquired fixtures that are ready immediately after
clone. The repository state does not match that description:

- `cases/conformance/synthetic/` currently contains generated conformance
  cases.
- `artifacts/correctness-index.json` currently exports those generated
  conformance cases as part of the correctness corpus.

This matters because generator-backed cases are not an independent oracle.
`cjfake` currently depends on the `cityjson-rs` data model, so a model bug can
propagate through generated fixtures into downstream consumers.

The current case contract also cannot express the trust boundary that users
and downstream crates actually need:

- `artifact_mode` says whether the artifact is checked in, generated, or
  acquired.
- `source_kind` says whether the data is synthetic or real.

Neither field says whether a correctness case should be treated as the default
normative oracle or as opt-in supplemental coverage.

One additional issue exists in the current implementation. The case schema
uses `layer: "operation"`, but the correctness index filter in
`scripts/corpus_cases.py` currently checks for `"operations"`. As a result,
operation cases are omitted from `artifacts/correctness-index.json` today.

## Audit

### `spec_complete_omnibus`

Current role:

- generated omnibus case in `cases/conformance/synthetic/`
- assertions: `full_surface_roundtrip`, `no_schema_regressions`
- operations: `parse`, `validate`, `roundtrip`

Overlap with `v2_0`:

- `cases/conformance/v2_0/cityjson_fake_complete/` already has the same
  family, assertions, and operations
- both cases are synthetic full-surface omnibus fixtures

Recommendation:

- remove from the correctness corpus

Reasoning:

- this is the clearest redundancy in the current tree
- keeping both increases maintenance cost without adding an independent oracle
- the checked-in `cityjson_fake_complete` fixture is the better default
  omnibus correctness gate

Replacement:

- none

### `spec_appearance_matrix`

Current role:

- generated appearance-focused conformance case
- assertions: `appearance_preserved`, `theme_dispatch_stable`

Overlap with `v2_0`:

- `appearance_empty` and `appearance_minimal_complete` already cover the
  appearance surface at a basic level
- the current checked-in appearance cases do not cover multi-theme dispatch,
  non-empty material and texture payloads, or default-theme stability

Recommendation:

- minimize into a new checked-in `v2_0` fixture

Reasoning:

- the missing coverage is narrow and easy to hand-author
- multi-theme appearance dispatch is important writer behavior
- this does not need a generator-backed oracle once the interesting surface is
  understood

Concrete follow-up:

- add a checked-in fixture such as `appearance_theme_dispatch`
- include multiple material themes, multiple texture themes, and default-theme
  pointers
- keep the current generated case only until the checked-in replacement exists

### `spec_extensions_feature_stream`

Current role:

- generated interaction case for extensions plus feature streaming
- assertions: `extensions_preserved`, `feature_boundaries_preserved`

Overlap with `v2_0`:

- `extension` covers extension payload preservation
- `cityjsonfeature_minimal_complete` and `cityjsonfeature_root_id_resolves`
  cover feature streaming boundaries and streaming semantics
- no checked-in fixture currently covers the interaction between extensions and
  CityJSONFeature streaming

Recommendation:

- minimize into a new checked-in `v2_0` fixture

Reasoning:

- the interaction is narrow and spec-driven
- a checked-in JSONL fixture is feasible and would be a stronger default oracle
  than a generator-backed case

Concrete follow-up:

- add a checked-in fixture such as `cityjsonfeature_extension_roundtrip`
- keep root-level extension payloads and feature boundaries in the same small
  fixture

### `spec_geometry_matrix`

Current role:

- generated geometry-and-semantics matrix case
- assertions: `geometry_types_preserved`, `boundary_normalization_stable`

Overlap with `v2_0`:

- `v2_0` already contains many focused geometry atoms:
  `geometry_complete_solid`, `geometry_semantics_multisurface`,
  `geometry_semantics_multisolid`, `geometry_instance`,
  `geometry_templates`, and others
- those checked-in cases cover individual shapes and narrow behaviors
- no checked-in fixture currently covers the full cross-product of geometry
  types, LoDs, and semantics in one place

Recommendation:

- keep as a supplemental generated correctness case

Reasoning:

- this is the broadest combinatorial sweep in the current synthetic set
- hand-authoring and reviewing an equivalent checked-in matrix would be costly
  and fragile
- it is useful as opt-in interaction coverage, but it should not pretend to be
  a normative spec atom

Concrete follow-up:

- keep it in the correctness index, but classify it as supplemental
- when it exposes a real bug, add a minimized checked-in regression fixture
  under `v2_0/` instead of promoting the generated matrix to normative status

### `spec_templates_matrix`

Current role:

- generated template-reuse interaction case
- assertions: `instance_count_stable`, `template_reuse_preserved`

Overlap with `v2_0`:

- `geometry_templates` covers template payload parsing
- `geometry_instance` covers geometry instances
- no checked-in fixture currently asserts repeated reuse across many objects or
  instance-count stability across roundtrips

Recommendation:

- minimize into a new checked-in `v2_0` fixture

Reasoning:

- the missing behavior is specific and hand-authorable
- a small checked-in fixture can express template reuse and instance count
  directly without generator coupling

Concrete follow-up:

- add a checked-in fixture such as `geometry_templates_reuse`
- include a small template set referenced by multiple CityObjects
- preserve `instance_count_stable` and `template_reuse_preserved` as explicit
  invariants

## Decision

The correctness corpus should be split by trust tier, not by whether a case is
synthetic.

The default correctness set should be the reviewed, pinned corpus:

- checked-in `v2_0` fixtures
- checked-in invalid fixtures
- checked-in or acquired operation fixtures

Generated correctness cases should remain allowed, but only as supplemental
coverage. They are useful for interaction sweeps and bug discovery, but they
are not the default normative oracle.

Workloads remain benchmark-only. If a workload or supplemental generated case
finds a correctness bug, the fix should be paired with a minimized checked-in
regression fixture under `v2_0/`, `operations/`, or `invalid/`.

## Draft README Changes

The README should describe two correctness tiers instead of claiming that
correctness fixtures are never generated.

Suggested replacement for the root `README.md` correctness section:

> **Correctness testing.** Conformance, invalid, and operation cases define
> invariants that consuming tools must satisfy. The default correctness corpus
> is the reviewed, pinned set of checked-in or acquired fixtures. The
> correctness index may also include explicitly marked supplemental generated
> cases for broader interaction coverage. Downstream tools should treat the
> normative checked-in or acquired corpus as the default oracle and opt into
> supplemental generated cases deliberately.

Suggested addition to `README.md` getting started:

> Checked-in and acquired normative correctness cases are usable immediately
> after cloning. Supplemental generated correctness cases require
> `just generate-data` and are opt-in.

Suggested replacement for the `cases/README.md` subtree description:

> - `conformance/v2_0/` for reviewed, checked-in normative conformance
>   fixtures
> - `conformance/generated/` for supplemental generated conformance coverage
>   when a broad interaction sweep is still useful

If repository path churn is not worth it immediately, the directory may stay
as `conformance/synthetic/` for one release, but the documentation should
still describe those cases as supplemental generated coverage rather than as
the default correctness corpus.

## Draft Catalog Contract Changes

The catalog contract should make the trust boundary machine-readable instead of
forcing downstream crates to guess from path names or `artifact_mode`.

### Case Schema

Add two fields that are required for correctness-layer cases:

- `correctness_class`
  - `normative`
  - `supplemental`
- `oracle_mode`
  - `frozen-fixture`
  - `generator-derived`
  - `upstream-published`

Interpretation:

- `correctness_class` tells downstream tools whether the case belongs in the
  default correctness gate.
- `oracle_mode` tells downstream tools what kind of oracle they are relying
  on.

Examples:

```json
{
  "id": "cityjson_fake_complete",
  "layer": "conformance",
  "correctness_class": "normative",
  "oracle_mode": "frozen-fixture"
}
```

```json
{
  "id": "spec_geometry_matrix",
  "layer": "conformance",
  "correctness_class": "supplemental",
  "oracle_mode": "generator-derived"
}
```

```json
{
  "id": "ops_3dbag_base",
  "layer": "operation",
  "correctness_class": "normative",
  "oracle_mode": "upstream-published"
}
```

### Correctness Index

Keep one derived correctness index, but make the default filter explicit.

Recommended root-level additions:

- `default_correctness_class: "normative"`
- `normative_case_count`
- `supplemental_case_count`

The correctness index should continue to include all correctness cases, but
the default contract for consumers should be:

- use cases where `correctness_class == "normative"` unless the consumer
  explicitly opts into supplemental coverage

The correctness index generation code should also be corrected to include the
schema value `layer: "operation"` instead of filtering on `"operations"`.

### Why Not Use Existing Fields

The current fields are useful but not sufficient:

- `artifact_mode` distinguishes checked-in, generated, and acquired artifacts
  but not normative versus supplemental correctness intent
- `source_kind` distinguishes synthetic versus real data but not trust tier

The proposed fields are therefore additive rather than replacements.

## Consequences

Positive:

- the repository documentation matches the actual corpus
- downstream crates can distinguish default correctness gates from opt-in
  supplemental sweeps without hard-coding path heuristics
- redundant omnibus coverage is removed

## Implementation Note

The corpus reshaping described above has been implemented as of 2026-04-08.

The final corpus split is:

- 44 normative correctness cases
- 1 supplemental generated correctness case

The removed supplemental benchmark-style cases were:

- `spec_complete_omnibus`
- `spec_appearance_matrix`
- `spec_extensions_feature_stream`
- `spec_templates_matrix`

The checked-in normative replacements are:

- `appearance_theme_dispatch`
- `cityjsonfeature_extension_roundtrip`
- `geometry_templates_reuse`

The combinatorial geometry sweep remains in `spec_geometry_matrix` as
supplemental generated coverage.
- interaction-heavy generated cases remain useful without overstating their
  oracle independence

Tradeoffs:

- the case schema and derived indexes need a version bump
- downstream consumers must learn the new correctness metadata
- three current synthetic conformance cases should be replaced with checked-in
  fixtures before the supplemental generated set becomes small and stable

## Migration Plan

1. Fix the `operation` versus `operations` layer mismatch in the correctness
   index pipeline.
2. Remove `spec_complete_omnibus` from the correctness corpus.
3. Add checked-in replacements for:
   - `spec_appearance_matrix`
   - `spec_extensions_feature_stream`
   - `spec_templates_matrix`
4. Reclassify the remaining generated conformance cases as supplemental in the
   case metadata and correctness index.
5. Update the root README, `cases/README.md`, and downstream consumer docs to
   use the normative versus supplemental terminology.
