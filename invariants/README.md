# Invariants

This directory holds correctness assertions for benchmark cases.

These assertions make the corpus useful for regression testing, not just
performance measurement.

Examples include:

- expected object and geometry counts
- hierarchy preservation
- semantic-surface preservation
- roundtrip equivalence checks
- layout conversion expectations

Keep invariants close to the benchmark cases they validate, but separate from
the case catalog so correctness rules can evolve without redefining the case
identity.

