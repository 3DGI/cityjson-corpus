# spec_extensions_feature_stream

Deterministic synthetic feature-stream case (`seed 1004`) with 4 `Building`/
`Bridge` city objects, `MultiSurface` geometry at LoD 2, attributes enabled,
and semantics enabled. Materials, textures, and templates are disabled so the
extension-aware packaging path stays focused.

## Signals

- extension parsing and emission
- stream framing overhead
- feature boundary management
- metadata validation and dispatch

## Use

Spec atom for extension-aware read/write paths and CityJSONFeature or JSONL
packaging.
