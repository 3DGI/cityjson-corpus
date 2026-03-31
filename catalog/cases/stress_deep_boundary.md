# stress_deep_boundary

## Intent

Synthetic stress case with deeply nested geometry boundary arrays.

## Why This Shape

Boundary-heavy geometry exercises recursion, nested container handling, and
stack or heap pressure in ways that simpler shapes do not. The geometry should
be awkward on purpose.

## Performance Signal

This case surfaces:

- boundary parsing cost,
- recursive descent overhead,
- nested vector allocation and copy cost,
- error-path sensitivity for malformed or deep nesting.

## Recommended Use

Use this to test deep geometry boundary handling and normalization cost.

