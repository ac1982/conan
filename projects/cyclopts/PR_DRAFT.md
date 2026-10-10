# Local upstream PR draft

This is a reviewable handoff draft, not a submitted upstream PR. The internal hub
PR should link this document. The submitting agent must refresh upstream context
and adapt the final title/body. All issue links below identify the upstream project.

---

Title: fix(config): preserve symlinked configuration filenames

## Problem

A config file symlink can be ignored when its target has a different name and lives in another directory. With the defaults, Cyclopts silently uses an empty config; with `must_exist=True`, it raises `FileNotFoundError`. If the target directory contains a file with the symlink's original name, Cyclopts reads that unrelated file instead.

Minimal reproduction:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from cyclopts.config import Json

with TemporaryDirectory() as directory:
    root = Path(directory)
    target = root / "settings" / "stored.json"
    target.parent.mkdir()
    target.write_text('{"port": 8123}')
    link = root / "config.json"
    link.symlink_to(target)
    print(Json(link).config)
```

Before: `{}`. After: `{'port': 8123}`.

## Change

`ConfigFromFile.config` currently resolves the whole path, then reconstructs candidates using the original filename. Resolve only the containing directory so lookup retains the requested symlink filename. Resolve the selected candidate separately in `FileCacheKey` to preserve cache invalidation when a symlink is retargeted, including equal-size/equal-mtime targets.

Regressions cover required/optional files, parent search on/off, conflicting neighboring filenames, actual CLI defaults, target modification, and symlink retargeting. The existing relative-path and parent-search behavior covered by [BrianPugh/cyclopts#370](https://github.com/BrianPugh/cyclopts/issues/370) and [BrianPugh/cyclopts#864](https://github.com/BrianPugh/cyclopts/issues/864) remains tested.

## Verification

Python 3.12.14 on Linux, with all extras installed; base `0b06f0f781f7b97fc6e75d1ef7673cabd1dca23d`.

- New symlink tests against untouched source: **6 failed, 3 passed, 22 deselected**. The passing cases protect existing parent-search and cache behavior.
- `python -m pytest tests/config -q`: **135 passed**.
- `python -m pytest -q`: **3,691 passed, 199 skipped, 13 deselected; 24 snapshots passed**. The repository's default slow-test exclusions were retained.
- `pre-commit run --all-files`: **all applicable checks passed**, including Ruff and Pyright; no-file hooks skipped.
- `git diff --check`: passed.

Pytest ran with `TERM=xterm` and `NO_COLOR` unset because the runner's inherited dumb-terminal setting overrides Rich's configured console width. Checks on other Python versions and operating systems remain for CI.

AI assistance: An OpenAI coding agent identified the bug, implemented the fix, wrote the tests and this description, and ran the checks above. A separate agent reviewed the patch and independently reproduced the baseline failure and passing configuration tests.
