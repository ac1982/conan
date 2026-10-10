"""Standard-library, offline checks for manifests and materializer guardrails."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("materialize", ROOT / "scripts/materialize.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class HubTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "projects", self.root / "projects")

    def rewrite(self, transform):
        path = self.root / "projects/llm/manifest.json"
        data = json.loads(path.read_text())
        transform(data)
        path.write_text(json.dumps(data))

    def test_manifests_and_hashes(self):
        self.assertEqual({p.name for p in (ROOT / "projects").iterdir()}, {"cyclopts", "mitty", "llm"})
        for name in ("cyclopts", "mitty", "llm"):
            manifest, _ = m.load_manifest(name)
            self.assertEqual(manifest["status"], "reviewed_internal_draft")
            self.assertTrue(manifest["changed_files"])

    def test_tampered_patch_rejected_before_git_or_target_creation(self):
        with (self.root / "projects/llm/fix.patch").open("a") as file:
            file.write("tampered\n")
        with patch.object(m, "git") as git:
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                m.materialize("llm", root=self.root)
            git.assert_not_called()
        self.assertFalse((self.root / ".worktrees").exists())

    def test_tampered_license_rejected(self):
        (self.root / "projects/llm/LICENSE.upstream").write_text("tampered")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            m.load_manifest("llm", self.root)

    def test_invalid_project_and_paths(self):
        for name in ("../llm", "/llm", "--help", "llm/extra"):
            with self.assertRaises(ValueError):
                m.load_manifest(name, self.root)
        for name in ("../a", "/a", ".git/config", "a/.git/config", "a//b", "a\\b", "a/./b"):
            with self.assertRaises(ValueError):
                m.safe_path(name)

    def test_unpinned_base_and_non_https_upstream_rejected(self):
        original = json.loads((self.root / "projects/llm/manifest.json").read_text())
        for field, value in (("base_commit", "main"), ("upstream_url", "file:///repo"),
                             ("upstream_url", "https://user:secret@github.com/a/b.git")):
            data = copy.deepcopy(original)
            data[field] = value
            (self.root / "projects/llm/manifest.json").write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                m.load_manifest("llm", self.root)

    def test_changed_files_must_match(self):
        self.rewrite(lambda data: data.update(changed_files=["unexpected.py"]))
        with self.assertRaisesRegex(ValueError, "paths disagree"):
            m.load_manifest("llm", self.root)

    def test_patch_rejects_unsafe_paths_modes_and_binary(self):
        for data in (b"diff --git a/../x b/../x\n", b"diff --git a/.git/config b/.git/config\n",
                     b"diff --git a/a b/a\nnew file mode 120000\n",
                     b"diff --git a/a b/a\nindex ab..cd 160000\n",
                     b"diff --git a/a b/a\nGIT binary patch\n",
                     b"diff --git a/a b/a\n--- a/a\n+++ b/other\n"):
            with self.assertRaises(ValueError):
                m.patch_paths(data)

    def test_existing_target_is_preserved(self):
        target = m.reserve_target(self.root, "llm")
        marker = target / "keep.txt"
        marker.write_text("keep")
        with patch.object(m, "git") as git:
            with self.assertRaises(FileExistsError):
                m.materialize("llm", root=self.root)
            git.assert_not_called()
        self.assertEqual(marker.read_text(), "keep")

    def test_worktree_and_project_symlinks_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / ".worktrees").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            m.reserve_target(self.root, "llm")
        project = self.root / "projects/llm"
        project.rename(self.root / "moved")
        project.symlink_to(self.root / "moved", target_is_directory=True)
        with self.assertRaises(ValueError):
            m.load_manifest("llm", self.root)

    def test_git_isolated_no_shell_and_no_credentials_in_command(self):
        with patch.dict(os.environ, {"GIT_DIR": "/bad", "GIT_CONFIG_COUNT": "1", "GIT_SSH_COMMAND": "bad"}):
            with patch.object(m.subprocess, "run") as run:
                run.return_value.stdout = "ok\n"
                self.assertEqual(m.git("status"), "ok")
                args, kwargs = run.call_args
                self.assertIsInstance(args[0], list)
                self.assertFalse(kwargs.get("shell", False))
                self.assertNotIn("GIT_DIR", kwargs["env"])
                self.assertNotIn("GIT_CONFIG_COUNT", kwargs["env"])
                self.assertNotIn("GIT_SSH_COMMAND", kwargs["env"])
                self.assertEqual(kwargs["env"]["GIT_CONFIG_GLOBAL"], os.devnull)
                self.assertIn("protocol.allow=never", args[0])
                self.assertIn("core.hooksPath=" + os.devnull, args[0])

    def test_fetch_failure_has_push_guard_already_set(self):
        calls = []

        def fake_git(*args, **kwargs):
            calls.append(args)
            if args[0] == "fetch":
                self.assertIn(("config", "remote.origin.pushurl",
                               "disabled://upstream-submission-is-separate"), calls)
                raise ValueError("fetch failed")
            return ""

        with patch.object(m, "git", side_effect=fake_git):
            with self.assertRaisesRegex(ValueError, "fetch failed"):
                m.materialize("llm", root=self.root)
        self.assertEqual(calls[-1][0], "fetch")

    def test_offline_clone_installs_push_guard_during_creation(self):
        source = self.root / "source"
        source.mkdir()
        with patch.object(m, "git", side_effect=ValueError("clone interrupted")) as git:
            with self.assertRaisesRegex(ValueError, "clone interrupted"):
                m.materialize("llm", source, self.root)
        args, _ = git.call_args
        self.assertEqual(args[0], "clone")
        self.assertIn("remote.origin.pushurl=disabled://upstream-submission-is-separate", args)
        self.assertIn("--config", args)

    def test_failed_materialization_keeps_partial_checkout(self):
        with patch.object(m, "git", side_effect=ValueError("fetch failed")):
            with self.assertRaisesRegex(ValueError, "fetch failed"):
                m.materialize("llm", root=self.root)
        self.assertTrue((self.root / ".worktrees/llm").is_dir())


if __name__ == "__main__":
    unittest.main()
