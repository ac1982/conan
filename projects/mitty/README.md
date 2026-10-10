# Propagate non-Error callback rejections

The patch normalizes callback failure values into protocol error markers. Falsey
rejections no longer resolve as successes. A guarded string conversion handles
null-prototype objects and throwing `toString` methods; existing Error metadata is
preserved. Nine regression tests exercise these cases.

The initial unguarded normalization failed on two coercion cases. The included
patch is the revised, reviewed version with the guard, not that initial patch.

## Package

- [Manifest](manifest.json): exact upstream URL, commit, changed files and hashes
- [Reviewed patch](fix.patch)
- [Validation and review](VALIDATION.md)
- [Local upstream PR draft](PR_DRAFT.md)
- [License attribution](ATTRIBUTION.md)

```sh
python3 scripts/materialize.py mitty
```

Run from the hub root. Read the upstream contribution instructions in the generated
checkout before executing tests. This subproject has no upstream PR from this work.
Use an internal hub draft PR for review and the [handoff checklist](../../HANDOFF.md)
for any later upstream submission.
