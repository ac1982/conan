#!/usr/bin/env python3
"""Fetch a pinned upstream tree and apply a hash-checked patch; never run it."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"[a-z][a-z0-9-]*\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
UPSTREAM = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git\Z")


def safe_path(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_./-]+", value):
        raise ValueError("Invalid relative path")
    parts = value.split("/")
    if any(p in ("", ".", "..", ".git") for p in parts):
        raise ValueError("Unsafe relative path")
    if PurePosixPath(value).is_absolute():
        raise ValueError("Absolute path not allowed")
    return value


def local_file(root, relative):
    path = root / safe_path(relative)
    # Reject symlink components, including a symlinked project directory.
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlinked hub files are not allowed")
    if not path.is_file():
        raise ValueError("Required hub file is missing")
    return path


def patch_paths(data):
    paths = []
    for line in data.decode("utf-8").splitlines():
        if line.startswith("diff --git "):
            match = re.fullmatch(r"diff --git a/([A-Za-z0-9_./-]+) b/([A-Za-z0-9_./-]+)", line)
            if not match or match[1] != match[2]:
                raise ValueError("Unsupported patch paths or rename")
            path = safe_path(match[1])
            if path in paths:
                raise ValueError("Duplicate patch file")
            paths.append(path)
        elif line.startswith(("new file mode ", "deleted file mode ", "old mode ", "new mode ")):
            if line.rsplit(" ", 1)[-1] not in ("100644", "100755"):
                raise ValueError("Only regular file modes are supported")
        elif line.startswith("index "):
            words = line.split()
            if len(words) == 3 and words[-1] not in ("100644", "100755"):
                raise ValueError("Only regular file modes are supported")
        elif line.startswith(("GIT binary patch", "Binary files ", "rename from ", "rename to ", "copy from ", "copy to ")):
            raise ValueError("Only regular text patches are supported")
        elif line.startswith(("--- ", "+++ ")):
            marker = line[4:]
            if marker != "/dev/null":
                prefix = "a/" if line.startswith("--- ") else "b/"
                if not marker.startswith(prefix) or not paths or safe_path(marker[2:]) != paths[-1]:
                    raise ValueError("Patch marker path disagrees with diff header")
    if not paths:
        raise ValueError("Patch has no files")
    return paths


def load_manifest(project, root=ROOT):
    if not SLUG.fullmatch(project):
        raise ValueError("Invalid project name")
    manifest_file = local_file(root, f"projects/{project}/manifest.json")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("project") != project:
        raise ValueError("Invalid manifest identity/version")
    if not UPSTREAM.fullmatch(manifest.get("upstream_url", "")):
        raise ValueError("Only public GitHub HTTPS upstream URLs are supported")
    if not SHA.fullmatch(manifest.get("base_commit", "")):
        raise ValueError("The upstream base must be a full commit hash")
    for key in ("patch", "license"):
        item = manifest[key]
        if not DIGEST.fullmatch(item.get("sha256", "")):
            raise ValueError("Invalid file hash")
        path = local_file(root, f"projects/{project}/{safe_path(item['file'])}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"{key} hash mismatch")
    patch = local_file(root, f"projects/{project}/{manifest['patch']['file']}")
    actual_paths = patch_paths(patch.read_bytes())
    if actual_paths != manifest.get("changed_files"):
        raise ValueError("Patch paths disagree with manifest")
    return manifest, patch


def git_env():
    # Ignore inherited repository selectors, config injection, hooks and filters.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1")
    return env


def git(*args, cwd=None, allow_file=False):
    command = ["git", "-c", f"core.hooksPath={os.devnull}", "-c", "core.fsmonitor=false",
               "-c", "submodule.recurse=false", "-c", "protocol.allow=never",
               "-c", "protocol.https.allow=always"]
    if allow_file:
        command += ["-c", "protocol.file.allow=always"]
    result = subprocess.run(command + list(args), cwd=cwd, env=git_env(),
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True)
    return result.stdout.strip()


def reserve_target(root, project):
    parent = root / ".worktrees"
    if parent.is_symlink():
        raise ValueError("Refusing a symlinked worktree directory")
    parent.mkdir(exist_ok=True)
    if parent.is_symlink() or parent.resolve().parent != root.resolve():
        raise ValueError("Worktree directory must be inside the hub")
    target = parent / project
    # Atomic exclusive creation: existing checkouts are never overwritten/deleted.
    target.mkdir(exist_ok=False)
    return target


def materialize(project, source_repo=None, root=ROOT):
    manifest, patch = load_manifest(project, root)
    source = None
    if source_repo is not None:
        source = Path(source_repo).resolve(strict=True)
        if not source.is_dir():
            raise ValueError("The offline source must be a local repository directory")
    target = reserve_target(root, project)
    try:
        if source is None:
            # Empty templates avoid inherited template hooks. No submodules/LFS filters.
            git("init", "--template=", str(target))
            git("remote", "add", "origin", manifest["upstream_url"], cwd=target)
            git("config", "remote.origin.pushurl", "disabled://upstream-submission-is-separate", cwd=target)
            git("fetch", "--no-tags", "--depth=1", "origin", manifest["base_commit"], cwd=target)
        else:
            # Offline reuse copies committed Git objects, not the source working tree.
            git("clone", "--template=", "--no-checkout", "--no-hardlinks", "--no-tags",
                "--config", "remote.origin.pushurl=disabled://upstream-submission-is-separate",
                "--", str(source), str(target), allow_file=True)
            git("remote", "set-url", "origin", manifest["upstream_url"], cwd=target)
        git("config", "remote.origin.pushurl", "disabled://upstream-submission-is-separate", cwd=target)
        git("checkout", "--detach", manifest["base_commit"], cwd=target)
        if git("rev-parse", "HEAD", cwd=target) != manifest["base_commit"]:
            raise ValueError("Checked-out commit disagrees with manifest")
        git("apply", "--check", "--index", str(patch), cwd=target)
        git("apply", "--index", str(patch), cwd=target)
        actual = git("diff", "--cached", "--name-only", "-z", cwd=target).split("\0")
        if sorted(p for p in actual if p) != sorted(manifest["changed_files"]):
            raise ValueError("Applied paths disagree with manifest")
        git("diff", "--cached", "--check", cwd=target)
        return target
    except Exception:
        # Preserve partial output for inspection. Never recursively remove user files.
        print(f"Materialization failed; inspect the partial checkout at {target} before retrying.", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("--source-repo", help="Offline local clone containing the pinned commit")
    parser.add_argument("--check", action="store_true", help="Validate metadata only; no Git/network/writes")
    args = parser.parse_args()
    try:
        if args.check:
            load_manifest(args.project)
            print(f"{args.project}: manifest, patch and license verified")
        else:
            target = materialize(args.project, args.source_repo)
            print(f"Prepared {target}; patch staged, dependencies and project code not executed.")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(exc.stderr.strip(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
