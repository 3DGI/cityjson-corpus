# io_3dbag_jsonl

## Intent

Large real-geometry scan case in a line-oriented feature stream.

## Why This Shape

The same semantic content is split into smaller records. That makes stream
boundaries, decoder overhead, and per-feature allocation visible.

## Performance Signal

This case surfaces:

- record-by-record parsing cost,
- stream framing and iteration overhead,
- small-object allocation churn,
- streaming versus whole-document memory behavior.

## Recommended Use

Use this to compare stream-oriented I/O against monolithic CityJSON input.

