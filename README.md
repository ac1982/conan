# Conan: OSS contribution hub

A central workspace for reviewed contributions to independent open-source projects.
Each project is a compact, patch-based subproject with an exact upstream commit,
reviewed patch, license attribution, validation summary, and local PR draft.

## Projects

- [Cyclopts](projects/cyclopts/README.md): preserve symlinked configuration filenames
- [Mitty](projects/mitty/README.md): propagate non-Error callback rejections safely
- [LLM](projects/llm/README.md): honor the first successful file encoding

## Why patches rather than vendored trees?

Only the contribution and its provenance belong in this repository. Entire upstream
repositories, dependencies, virtual environments, build artifacts and large raw logs
are deliberately excluded. Each manifest pins a 40-character upstream commit and
SHA-256 hashes for its patch and upstream license. Materialized upstream checkouts
live in ignored `.worktrees/` directories; they are independent Git repositories,
not Git submodules or Git worktrees attached to this hub.

## Validate and materialize

Requirements: Python 3.10+ and Git. Hub validation uses only the Python standard library.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/materialize.py cyclopts --check
python3 scripts/materialize.py cyclopts
python3 scripts/materialize.py mitty
python3 scripts/materialize.py llm
```

Materialization fetches the exact pinned commit from the manifest's public HTTPS
upstream, checks it out detached, checks the patch, and applies it to the index and
working tree. It does not install dependencies, run project code, run checkout hooks,
recurse into submodules, use Git LFS filters, or submit anything upstream. Upstream
push URLs are disabled on the generated checkouts as an accidental-push guard.
Inspect the source and follow each upstream project's contribution instructions
before installing dependencies or executing its tests.

For offline use with an existing local clone containing the pinned commit:

```sh
python3 scripts/materialize.py llm --source-repo /path/to/local/llm
```

That path is an example supplied by the operator; no machine-specific source paths
are stored in the manifests. Offline mode clones committed objects without hardlinks
and ignores uncommitted changes. It does not fetch. Existing target checkouts and
symlinked worktree directories are refused. Failed partial checkouts are retained
for inspection rather than deleted automatically. Inspect and move/remove one
manually before retrying. Do not add `.worktrees/` to the hub.

## Internal draft PR workflow

1. Work on a branch in `ac1982/conan`, such as
   `contributions/2026-10-10-reviewed-fixes`.
2. Update only the relevant project's patch, manifest hashes, draft and validation.
3. Run the offline hub checks and recheck patch application at the pinned commit.
4. Open a **draft PR in this hub** for review; link the relevant subproject folders.
5. Hand the reviewed package to the separate upstream-submission agent using
   [HANDOFF.md](HANDOFF.md). Internal approval is not an upstream submission.

No upstream PR has been created by this work. Upstream submission remains a separate
handoff. There are no fork-creation, upstream-push, merge, or PR-submission actions in
the tooling. The checked-in drafts are text artifacts, not published upstream PRs.

CI runs only offline metadata and materializer guardrail tests. It does not fetch or
execute the three upstream projects. Historical project test results are distinguished
from hub packaging checks in [VALIDATION.md](VALIDATION.md).

See [LICENSES.md](LICENSES.md) for upstream license scope.
