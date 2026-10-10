# Local upstream PR draft

This is a reviewable handoff draft, not a submitted upstream PR. The internal hub
PR should link this document. The submitting agent must refresh upstream context
and adapt the final title/body. All issue links below identify the upstream project.

---

# Title

fix: propagate non-Error callback rejections

# Body

## Problem

A callback that rejects with `undefined`, `null`, `false`, `0`, or `''` can silently resolve as `undefined` on the host. The client sends the raw rejection reason, and the host checks `error` by truthiness. A truthy string rejects, but does not arrive as an `Error`.

## Change

Normalize non-Error callback failures before sending the reply so they travel as protocol error markers. Guard string conversion and fall back to `Error('Callback failed')` if conversion throws, including for null-prototype objects. Existing `Error` instances retain their name, message, stack, and code.

The change is limited to callback failure handling. Nine tests cover the rejection values, conversion failures, and existing Error metadata. Eight fail on the original implementation; all nine pass with the fix.

## Validation

- `npm test`: 234 tests pass
- `npm run coverage`: 234 tests pass; 100% statement, branch, and line coverage
- `npm run lint`, `npm run format:check`, `npm run typecheck`, and `npm run build`: pass
- `git diff --check`: pass

AI disclosure: The patch, tests, and this description were prepared with OpenAI AI assistance. All listed checks were run against the final patch.
