# io_3dbag_feature_files

The same real-geometry 3DBAG slice split into one file per feature. This is a
filesystem-heavy layout case for open/close overhead, metadata lookup, and
random-access behavior.

## Signals

- open/close and directory traversal overhead
- metadata lookup cost
- random access versus scan behavior
- repeated per-file allocation and cleanup

## Use

Test storage layouts and filesystem-heavy corpus access patterns.
