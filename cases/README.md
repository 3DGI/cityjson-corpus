# Cases

This directory is the source of truth for the shared corpus.

Every case lives in its own folder. That folder tells you:

- what the case is;
- what result is expected;
- where the artifact comes from.

## Case Folder Layout

A case folder usually looks like this:

```text
cases/<layer>/<group>/<case-id>/
  case.json
  invariants.json
  README.md            # optional
  <source file>        # for checked-in cases
  profile.json         # for generated cases
  acquisition.json     # for acquired cases
```

Files mean:

- `case.json`: stable metadata for the case.
- `invariants.json`: expected acceptance, rejection, or preservation checks.
- `README.md`: short notes for people reading the repo.
- source file: the checked-in artifact, if the case stores its bytes in git.
- `profile.json`: generator input for a case that is built later.
- `acquisition.json`: description of an external published source.

The meaning of controlled values such as `layer`, `artifact_mode`,
`representation`, and `status` is documented in
[`schemas/README.md`](../schemas/README.md).

## Corpus Layers

The main subtrees are:

- `conformance/v2_0/`: checked-in valid fixtures.
- `conformance/synthetic/`: generated valid fixtures.
- `operations/`: medium cases for common tasks on realistic data.
- `workloads/`: larger performance cases, both synthetic and real data.
- `invalid/`: deliberately broken fixtures.

## Correctness And Performance

Conformance, invalid, and operation cases form the correctness corpus.

Use them when you need to check whether software accepts, rejects, or preserves
the right things.

Workload cases are for performance work. Use them when you want to compare file
layout, throughput, or memory behavior.

`catalog/cases.json` is the derived index of all cases.
`artifacts/correctness-index.json` is the derived index of correctness cases.

## How To Change A Case

1. Create or edit the case folder under the right subtree.
2. Keep `case.json` and `invariants.json` in sync with each other.
3. Add the right artifact source:
   - checked-in file,
   - `profile.json`,
   - or `acquisition.json`.
4. Add `README.md` when the case needs a short human explanation.
5. Run:
   - `just sync-catalog`
   - `just generate-data` when needed
   - `just docs-build`
   - `just lint`

## How To Remove A Case

1. Delete the case folder.
2. Run `just clean` to remove generated docs pages.
3. Rebuild with `just docs-build`.

Do not edit `catalog/cases.json` by hand. Rebuild it from the case tree.
