# io_3dbag_jsonl

Large real-geometry scan case in a line-oriented feature stream.

## Signals

- record-by-record parsing
- stream framing and iteration overhead
- small-object allocation churn
- streaming versus whole-document memory behavior

## Use

Compare stream-oriented I/O against monolithic CityJSON input.
