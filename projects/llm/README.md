# Honor the first successful encoding in embed-multi --files

The one-line production fix stops the fallback-encoding loop after its first
successful decode. UTF-8 text is no longer overwritten by a later Latin-1 decode;
six regression cases check both embedding-model input and stored text.

This independently rediscovered code path addresses the already reported
[upstream issue #283](https://github.com/simonw/llm/issues/283), not a newly unreported
bug. Review found the exact report in its comments and corrected the original
novelty claim. The report's [bulk-file reproduction](https://github.com/simonw/llm/issues/283#issuecomment-1725042843)
and [UTF-8-only workaround](https://github.com/simonw/llm/issues/283#issuecomment-1783874602)
match this failure.

As of the 2026-10-10 review, [PR #1559](https://github.com/simonw/llm/pull/1559)
changed single-item `embed`/`similar`, while [PR #1737](https://github.com/simonw/llm/pull/1737)
changed template, fragment and function-file reads. Neither inspected diff changed
the bulk-embedding loop. Refresh these checks before upstream submission.

## Package

- [Manifest](manifest.json): exact upstream URL, commit, changed files and hashes
- [Reviewed patch](fix.patch)
- [Validation and review](VALIDATION.md)
- [Local upstream PR draft](PR_DRAFT.md)
- [License attribution](ATTRIBUTION.md)

```sh
python3 scripts/materialize.py llm
```

Run from the hub root. Read the upstream contribution instructions in the generated
checkout before executing tests. This subproject has no upstream PR from this work.
Use an internal hub draft PR for review and the [handoff checklist](../../HANDOFF.md)
for any later upstream submission.
