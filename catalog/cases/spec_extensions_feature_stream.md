# spec_extensions_feature_stream

## Intent

Small synthetic case that combines extension metadata with feature-stream
packaging.

## Why This Shape

Extensions and feature streams stress boundary handling more than raw model
size. The case should stay small so protocol handling, schema plumbing, and
stream framing stay visible.

## Performance Signal

This case surfaces:

- extension parsing and emission,
- stream framing overhead,
- feature boundary management,
- metadata validation and dispatch cost.

## Recommended Use

Use this as a spec atom for extension-aware read/write paths and for
CityJSONFeature or JSONL packaging behavior.

