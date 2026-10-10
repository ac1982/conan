# Handoff to upstream submission

This repository is the internal review destination. Do not treat an internal hub PR
or technical approval as an upstream PR, merge approval, or permission to publish
new upstream messages. The separate submitting agent owns that workflow.

For each selected subproject:

1. Read its manifest, attribution, validation summary and `PR_DRAFT.md`.
2. Verify the patch and license hashes with `scripts/materialize.py PROJECT --check`.
3. Refresh upstream contribution/AI policies and all-state issue/PR overlap checks.
   Confirm the destination and submission authorization before external mutations.
4. Materialize the pinned tree and inspect `git diff --cached`. The patch is staged;
   it has not been committed. Run upstream checks in an appropriate isolated setup.
5. If upstream has moved, port on a separate working branch, rerun the relevant tests
   and review the final diff. Do not silently change the baseline or validation claims.
6. Adapt the local PR draft and provide truthful AI-assistance disclosure. Preserve
   known-issue provenance and link related upstream work with qualified URLs.
7. Record any later upstream submission URL and exact submitted commit here through
   a separate internal branch/draft PR. Do not claim submission before it is verified.

## LLM provenance requirement

This fixes the reported `embed-multi --files` behavior in
[simonw/llm issue #283](https://github.com/simonw/llm/issues/283). The faulty code path
was independently identified and reproduced before review found the prior report;
this is **not a previously unreported bug**.

At review on 2026-10-10, the inspected diffs of
[PR #1559](https://github.com/simonw/llm/pull/1559) and
[PR #1737](https://github.com/simonw/llm/pull/1737) did not fix this bulk-embedding loop.
PR #1559 targets single-item `embed`/`similar`; PR #1737 targets template, fragment
and function-file reads. Recheck both immediately before any upstream submission:
indexed search and an observation-time diff cannot rule out later/unpublished work.
