# io_3dbag_feature_files

## Intent

Large real-geometry case stored as one feature per file.

## Why This Shape

This layout makes filesystem overhead part of the measurement. It is useful
when the question is not only how fast a parser runs, but how much the storage
layout itself costs.

## Performance Signal

This case surfaces:

- open/close and directory traversal overhead,
- metadata lookup cost,
- random-access versus scan behavior,
- repeated per-file allocation and cleanup.

## Recommended Use

Use this to test storage layouts and file-system heavy corpus access patterns.

