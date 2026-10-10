# Local upstream PR draft

This is a reviewable handoff draft, not a submitted upstream PR. The internal hub
PR should link this document. The submitting agent must refresh upstream context
and adapt the final title/body. All issue links below identify the upstream project.

---

Honor the first successful encoding in embed-multi --files

Addresses the known upstream issue [simonw/llm#283](https://github.com/simonw/llm/issues/283), where `embed-multi --files` corrupts non-ASCII UTF-8 text unless `--encoding utf-8` is explicitly supplied.

`llm embed-multi --files` currently keeps trying encodings after a successful decode. With the default UTF-8/Latin-1 sequence, Latin-1 replaces correctly decoded UTF-8 text, so non-ASCII text is corrupted before it reaches the embedding model and when `--store` saves it.

For example, a UTF-8 file containing `Café résumé` reaches the model and is stored as `CafÃ© rÃ©sumÃ©`, even though the command succeeds. The documentation says Latin-1 should be a fallback only when UTF-8 raises an encoding error.

This stops the loop after the first successful decode. Regression coverage checks the default encodings, explicit encoding priority in both orders, failure of an earlier encoding, the Latin-1 fallback, and UTF-16. Each case checks both the model input and stored content.

Related: [simonw/llm#1559](https://github.com/simonw/llm/pull/1559) also references [simonw/llm#283](https://github.com/simonw/llm/issues/283), but its current diff changes the single-item `embed` and `similar` commands. This patch addresses the `embed-multi --files` path from the original report. [simonw/llm#1737](https://github.com/simonw/llm/pull/1737) covers template, fragment, and function file reads.

Validation on Linux / Python 3.12.14:
- Five new cases fail on the unchanged implementation; all six pass with the fix.
- Embeddings suites: 120 passed.
- Full suite: 1,214 passed with `--record-mode none --block-network`.
- Black, Ruff, mypy, Cog generated-documentation checks, package build, and `git diff --check` passed.

The OS/Python CI matrix and optional plugin-installation smoke test were not run. No live model APIs were called. Developed with OpenAI Codex assistance.
