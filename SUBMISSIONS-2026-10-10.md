# Upstream submission handoff — 2026-10-10

The three patches packaged at `fb9a731` were independently reviewed and submitted upstream. Their submitted diffs match the manifest patch hashes byte-for-byte. The original author was preserved and each PR discloses AI assistance and the independent verification.

| Project | Upstream PR | Submitted commit | Target/base |
| --- | --- | --- | --- |
| Cyclopts | https://github.com/BrianPugh/cyclopts/pull/995 | `1ebe2f64b4c4cdfa01f534b70b182fd9bfd603bf` | `main`, `0b06f0f781f7b97fc6e75d1ef7673cabd1dca23d` |
| LLM | https://github.com/simonw/llm/pull/1750 | `04fdfd8d3136a8912af27fa9fc6c463d004060ca` | `main`, `05d7ae7dedc524b024ab463b063854e7c43fee01` |
| Mitty | https://github.com/jcubic/mitty/pull/5 | `0d223204f3463b91e1102b52bf5bb33e24bc94ff` | `master`, `08bf0d226fe9d7a2a1665ca189acf4b8db66d52e` |

## Independent checks

All three upstream tips still matched the pinned bases immediately before submission. Contribution rules, templates, repository/owner defaults, and all-state PR/issue collections were refreshed. No duplicate matching fix was found in the checked public work. This does not establish the absence of unpublished work.

- Cyclopts: unchanged source failed 6 of the 9 symlink cases; all 9 pass with the patch. Full suite with `--run-slow`: 3,692 passed, 211 skipped, 24 snapshots passed. All applicable pre-commit checks (including Ruff/Pyright) and the Sphinx HTML build with `-W` passed. Related #371/#864 and #993 do not fix this symlink-basename behavior.
- LLM: unchanged source failed 5 of the 6 encoding cases; all 6 pass with the patch. Full offline suite: 1,214 passed with `--record-mode none --block-network`. Black, Ruff, mypy, Cog and package build passed. This fixes the existing issue https://github.com/simonw/llm/issues/283; current #1559/#1737 diffs do not fix this bulk-file loop.
- Mitty: unchanged source failed 8 of the 9 callback cases; all 9 pass with the patch. Full coverage run: 234 passed; statements/branches/lines 100%, functions 98.8%. Lint, formatting, typecheck and build passed. The existing #4 review about `report_failure` covers a separate conversion path.

Environment: Linux arm64, Python 3.12.15, Node 24.21.0. Cyclopts used `TERM=xterm` with `NO_COLOR` unset. Other OS/Python/browser matrices, skipped tests, and the optional LLM plugin-install smoke test were not run. No live model API calls were made.

## Follow-up

At the first post-submission check on 2026-10-10 (Asia/Singapore), all three PRs were open with no review threads. Their Actions were `action_required`, awaiting maintainer approval; this is not a CI pass or a merge. Continue on these same PRs if changes are requested. Do not open duplicate submissions or self-merge.

This handoff is an internal record and is not an additional upstream contribution. The original manifests and validation reports remain historical descriptions of the reviewed package.
