# LLM validation and known-issue provenance

Reviewed and packaged on 2026-10-10. Baseline:
`05d7ae7dedc524b024ab463b063854e7c43fee01`.
The manifest's patch hash identifies the exact reviewed revision.

## Project verification before packaging

Linux, Python 3.12.14. Pytest used recorded fixtures with network access blocked;
synthetic text and a fake embedding model were used. No live model API was called.

- Final regressions against unchanged production source: 5 failed, 1 passed,
  94 deselected. The pass protects the existing Latin-1 fallback.
- Clean full baseline suite: 1,208 passed, 6 new cases deselected.
- Patched embedding suites: 120 passed.
- Patched full suite: 1,214 passed (`--record-mode none --block-network`).
- Black, Ruff, mypy, Cog generated-document consistency, package build and
  `git diff --check`: passed.
- Independent reviewer reran the failing baseline regressions, 100 CLI embedding
  tests, the 1,214-test offline full suite, changed-file Black/Ruff checks, mypy,
  and whitespace check. Final technical decision: approved, no outstanding changes.

The reviewer inspected but did not repeat the broader Black/Ruff, Cog and build
runs. The OS/Python CI matrix, optional installed-plugin smoke test, live API calls
and full Sphinx HTML documentation build were not run.

## Fresh hub packaging verification

- A new offline clone checked out the exact baseline; `git apply --check --index`
  and patch application succeeded.
- Re-emitted staged diff matched the packaged patch byte-for-byte.
- Python import location was confirmed inside the fresh materialized tree.
- `python -m pytest tests/test_embed.py tests/test_embed_cli.py --record-mode none
  --block-network -q`: 120 passed.
- Staged whitespace check passed; only the two manifest-listed files changed.

Packaging reused an existing test environment; it did not rerun the full suite,
static tools, Cog or package build. Dependencies/build outputs are not included.

## Corrected provenance and overlap

The faulty loop was independently identified and reproduced through source
inspection. Review then found the exact pre-existing report in
[issue #283](https://github.com/simonw/llm/issues/283), including the
[bulk-file reproduction](https://github.com/simonw/llm/issues/283#issuecomment-1725042843)
and [UTF-8-only workaround](https://github.com/simonw/llm/issues/283#issuecomment-1783874602).
The initial novelty assessment was corrected. This is a fix for a known issue,
not a previously unreported bug.

At the 2026-10-10 05:43–05:44 UTC review, the inspected full diffs of
[PR #1559](https://github.com/simonw/llm/pull/1559) and
[PR #1737](https://github.com/simonw/llm/pull/1737) did not change `embed_multi`'s
fallback loop. PR #1559 references the same issue but changes single-item `embed`
and `similar`; PR #1737 changes template, fragment and function-file reads.
[Issue #225](https://github.com/simonw/llm/issues/225) supplies the original fallback
feature context. Review-time non-overlap is limited to the inspected revisions;
refresh policies, open work and indexed searches before upstream submission.
