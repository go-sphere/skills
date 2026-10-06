# Adopting a Legacy Project

A project created before the layout contract has no `.sphere/` directory. Adopt it into the
contract before attempting any normal sync.

## Procedure

1. Inspect the project's earliest template commit.
2. Compare its Git tree against commits from the likely upstream layout.
3. Record a revision **only when exactly one upstream tree matches.**
4. If there is no unique match, **ask the user** for the originating revision. Do not infer a
   convenient base. A wrong base silently corrupts every future three-way merge.
5. Once the revision is confirmed, write the version-1 lock file and follow the normal update flow.

## Identify the Layout Variant

Identifying the variant — `standard`, `simple`, `bun`, or `telegram` — is part of this step. Their
trees differ substantially, so a variant guess is as damaging as a revision guess.

## Version-1 Lock Shape

```json
{
  "schema_version": 1,
  "name": "standard",
  "repository": "https://github.com/go-sphere/sphere-layout.git",
  "ref": "master",
  "upstream_module": "github.com/go-sphere/sphere-layout",
  "base_revision": "full-git-commit-sha"
}
```

Preserve any unknown JSON field — the format is forward-compatible. Layout source repositories
contain no lock file; only generated projects do.
