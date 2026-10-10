# Cyclopts validation

Reviewed and packaged on 2026-10-10. Baseline:
`0b06f0f781f7b97fc6e75d1ef7673cabd1dca23d`.
The manifest's patch hash identifies the exact reviewed revision.

## Project verification before packaging

Linux, Python 3.12.14, project test/all extras installed:

- Untouched production source plus final symlink regressions: 6 failed, 3 passed,
  22 deselected. Expected failures establish the bug, not a passing baseline suite.
- Configuration suite: 135 passed.
- Full suite: 3,691 passed, 199 skipped, 13 deselected; 24 snapshots passed.
- Repository-wide pre-commit: all applicable checks passed, including Ruff and
  Pyright; no-file hooks skipped. `git diff --check` passed.
- Independent reviewer reran baseline regressions and the 135-test config suite,
  checked 11 additional edge cases, and approved without blocking changes.

The full suite and full lint runs were not independently repeated by the reviewer.
The checks used `TERM=xterm` with `NO_COLOR` unset for the Rich terminal tests.
Other Python versions/operating systems were not tested; unavailable platform/shell
cases and the repository's default slow-test exclusions remain unverified.

## Fresh hub packaging verification

- A new offline clone checked out the exact baseline; `git apply --check --index`
  and patch application succeeded.
- Re-emitted staged diff matched the packaged patch byte-for-byte.
- Python import location was confirmed inside the fresh materialized tree.
- `python -m pytest tests/config -q`: 135 passed.
- Staged whitespace check passed; only the three manifest-listed files changed.

The fresh packaging run reused an existing test environment without copying it into
this repository. It did not rerun the full project suite or all pre-commit hooks.

## Scope and overlap

Source inspection preceded issue/PR searching. Review-time indexed searches found
no matching symlink-basename fix; related configuration work was inspected and
considered distinct. Search cannot prove absence of later, unindexed or unpublished
work. Refresh upstream checks and contribution policies before submission.
