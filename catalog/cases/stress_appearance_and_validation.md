# stress_appearance_and_validation

## Intent

Synthetic stress case with heavy appearance metadata and strict write-time
validation.

## Why This Shape

Appearance and validation tend to expose write-path cost more than read-path
cost. The case therefore keeps geometry moderate and concentrates on output
bookkeeping.

## Performance Signal

This case surfaces:

- serializer branching,
- metadata validation cost,
- output-size growth from appearance payloads,
- memory overhead from write-time checks.

## Recommended Use

Use this for serializer and validation work where write-path cost matters.

