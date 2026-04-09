# ADR 0010: Correctness Corpus Coverage and Generated Cases

## Status

Accepted.

## Context

The repository needs a single correctness corpus contract that consumers can
use without interpreting extra trust tiers.

Correctness cases are the conformance, invalid, and operation fixtures in the
shared `cases/` tree. Some of them are checked in, some are generated, and
some may be acquired. That difference is already captured by `artifact_mode`
and `artifact_paths`.

An additional trust-tier field is not useful. Consumers already know whether
a case belongs to the correctness corpus by its layer, and they do not need a
second metadata axis for "normative" versus "supplemental".

## Decision

The trust-tier field is removed from the case schema and from case metadata.

The correctness index continues to list the correctness corpus cases, but it
does not split them into normative and supplemental subsets.

Consumers should use:

- `layer` to decide whether a case belongs to correctness coverage
- `artifact_mode` to decide whether the artifact is checked in, generated, or
  acquired
- `source_kind` for provenance only

## Consequences

Positive:

- the case contract is simpler
- the documentation matches how the corpus is actually consumed
- generated cases remain usable without inventing a second trust dimension

Tradeoffs:

- consumers that previously used the removed trust-tier field must switch to
  `layer` and `artifact_mode`
