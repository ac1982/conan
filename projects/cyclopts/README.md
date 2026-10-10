# Preserve symlinked configuration filenames

The patch keeps the requested configuration symlink's filename during lookup and
resolves the selected target for cache identity. It avoids silently ignoring a valid
config, reporting it missing, or loading an unrelated same-named target neighbor.

Nine regression cases cover lookup options, conflicting filenames, CLI defaults,
target modification and equal-size/equal-mtime symlink retargeting. Independent
review approved the final patch without a remaining blocker.

## Package

- [Manifest](manifest.json): exact upstream URL, commit, changed files and hashes
- [Reviewed patch](fix.patch)
- [Validation and review](VALIDATION.md)
- [Local upstream PR draft](PR_DRAFT.md)
- [License attribution](ATTRIBUTION.md)

```sh
python3 scripts/materialize.py cyclopts
```

Run from the hub root. Read the upstream contribution instructions in the generated
checkout before executing tests. This subproject has no upstream PR from this work.
Use an internal hub draft PR for review and the [handoff checklist](../../HANDOFF.md)
for any later upstream submission.
