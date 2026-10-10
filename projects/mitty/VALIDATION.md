# Mitty validation

Reviewed and packaged on 2026-10-10. Baseline:
`08bf0d226fe9d7a2a1665ca189acf4b8db66d52e`.
The manifest identifies the final guarded patch, not the earlier unguarded revision.

## Project verification before packaging

- Original upstream source with all nine proposed tests: 8 failed, 1 passed.
- Initial unguarded conversion plus those tests: 2 timed out, 7 passed, with
  2 unhandled rejections. This exposed the need to guard string conversion.
- Final guarded patch: all nine regression tests passed.
- Full suite and coverage: 234 passed across 9 files; 100% statements (473/473),
  branches (368/368), and lines (471/471); 98.8% functions (83/84).
- Lint, formatting check, typecheck, ESM/IIFE/declaration build and whitespace
  checks passed on the final patch.
- Independent reviewer implemented and verified the guard revision; no remaining
  blocking issue was reported. This was a review-driven revision, not an unchanged
  patch approved by a fully separate final implementer.

Checks exercised the local Node/Vitest environment. Other runtime and browser
matrices were not verified. Passing local tests are not an upstream CI result.

## Fresh hub packaging verification

- A new offline clone checked out the exact baseline; `git apply --check --index`
  and patch application succeeded.
- Re-emitted staged diff matched the packaged patch byte-for-byte.
- `npm test` in the materialized tree: 234 tests passed across 9 files.
- Staged whitespace check passed; only the two manifest-listed files changed.

The fresh run reused existing local development dependencies through an ignored
checkout-only link. No dependencies or build output are included in this hub.
Packaging did not repeat coverage, lint, format, typecheck or build.

## Scope and overlap

Review inspected the then-complete issue/PR collection and related protocol and
serialization changes. No duplicate falsey callback-rejection fix was found.
An existing [PR #4 comment](https://github.com/jcubic/mitty/pull/4#discussion_r4126796638)
warns about a different string-conversion path; this patch does not change that path.
The [RO/RPC callback-result contract](https://github.com/jcubic/rorpc/blob/master/SPEC.md#74-callback-result--client-to-host)
requires an error marker for callback failure. Refresh upstream context and policies
before submission; later or unpublished work may differ.
