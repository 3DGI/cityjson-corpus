# io_3dbag_jsonl

The same real-geometry 3DBAG slice packaged as JSONL. This is a stream-oriented
layout case for record-by-record parsing, framing overhead, and streaming
memory behavior.

## Signals

- record-by-record parsing
- stream framing and iteration overhead
- small-object allocation churn
- streaming versus whole-document memory behavior

## Use

Compare stream-oriented I/O against monolithic CityJSON input.
