"""Filesystem safety regressions; all moves are confined to temporary fixtures."""
from hashlib import sha256
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "reorganize_repository.sh"
MANIFEST = HERE / "reorganization-plan.tsv"


class ReorganizationSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="helix-reorganization-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def run_script(self, *args, ok=True):
        result = subprocess.run(
            ["/bin/bash", str(SCRIPT), "--root", str(self.root), *map(str, args)],
            text=True, capture_output=True,
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def put(self, path, data=b"research contents\x00\xff\n"):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def tiny_plan(self, text="notes/a.md\tdocs/current/a.md\n"):
        return self.put("plan.tsv", text.encode())

    def test_full_manifest_preview_apply_and_undo_preserve_every_byte(self):
        pairs = [line.split("\t") for line in MANIFEST.read_text().splitlines()
                 if line and not line.startswith("#")]
        self.assertEqual(len(pairs), 166)
        for i, (source, _) in enumerate(pairs):
            self.put(source, (str(i) + "\n" + source + "\n").encode() + b"\x00\xff")
        for excluded in ["output/saved/output.npz", "src/output/saved/source_snapshot/a.py",
                         "notes/figures/picture.svg", "arXiv-example/main.tex", ".git/marker",
                         "notes/new_unlisted_note.md", "src/new_unlisted_module.py"]:
            self.put(excluded)
        before = self.snapshot()
        dirs_before = {p for p in self.root.rglob("*") if p.is_dir()}
        self.run_script("--manifest", MANIFEST)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(dirs_before, {p for p in self.root.rglob("*") if p.is_dir()})
        self.run_script("--manifest", MANIFEST, "--apply")
        for source, destination in pairs:
            self.assertFalse((self.root / source).exists())
            self.assertEqual((self.root / destination).read_bytes(), before[source])
        journal, = (self.root / "reorganization-logs").glob("*.tsv")
        after = self.snapshot()
        self.run_script("--undo", journal)
        self.assertEqual(after, self.snapshot())
        self.run_script("--undo", journal, "--apply")
        for source, destination in pairs:
            self.assertEqual((self.root / source).read_bytes(), before[source])
            self.assertFalse((self.root / destination).exists())
        actual = {p: data for p, data in self.snapshot().items()
                  if not p.startswith("reorganization-logs/")}
        self.assertEqual(actual, before)

    def test_collision_preflights_entire_plan_before_any_move(self):
        plan = self.tiny_plan("notes/a.md\tdocs/current/a.md\nnotes/b.md\tdocs/current/b.md\n")
        self.put("notes/a.md"); self.put("notes/b.md")
        self.put("docs/current/b.md", b"existing target")
        before = self.snapshot()
        self.run_script("--manifest", plan, "--apply", ok=False)
        self.assertEqual(before, self.snapshot())

    def test_missing_source_and_duplicate_moves_refused(self):
        plan = self.tiny_plan()
        self.run_script("--manifest", plan, "--apply", ok=False)
        self.put("notes/a.md")
        plan.write_text("notes/a.md\tdocs/a.md\nnotes/a.md\tdocs/b.md\n")
        before = self.snapshot()
        self.run_script("--manifest", plan, "--apply", ok=False)
        self.assertEqual(before, self.snapshot())

    def test_path_escape_outputs_and_symlink_parents_refused(self):
        self.put("notes/a.md")
        for destination in ("../escape.md", "/tmp/escape.md", "src/output/a.md"):
            plan = self.tiny_plan("notes/a.md\t" + destination + "\n")
            before = self.snapshot()
            self.run_script("--manifest", plan, "--apply", ok=False)
            self.assertEqual(before, self.snapshot())
        (self.root / "real").mkdir()
        (self.root / "docs").symlink_to(self.root / "real", target_is_directory=True)
        plan = self.tiny_plan()
        self.run_script("--manifest", plan, "--apply", ok=False)
        self.assertTrue((self.root / "notes/a.md").exists())
        self.assertEqual(list((self.root / "real").iterdir()), [])

    def test_undo_refuses_edited_contents_and_wrong_root(self):
        plan = self.tiny_plan(); self.put("notes/a.md")
        self.run_script("--manifest", plan, "--apply")
        journal, = (self.root / "reorganization-logs").glob("*.tsv")
        self.put("docs/current/a.md", b"later edits must survive")
        before = self.snapshot()
        self.run_script("--undo", journal, "--apply", ok=False)
        self.assertEqual(before, self.snapshot())
        self.put("docs/current/a.md")  # Restore bytes to isolate the root check.
        foreign = self.put("foreign.tsv", journal.read_bytes().replace(
            ("# root:\t" + str(self.root)).encode(), b"# root:\t/somewhere/else"))
        before = self.snapshot()
        result = self.run_script("--undo", foreign, "--apply", ok=False)
        self.assertIn("Journal root does not match", result.stderr)
        self.assertEqual(before, self.snapshot())

    def test_source_symlink_and_dangling_destination_refused(self):
        plan = self.tiny_plan()
        self.put("real.md")
        (self.root / "notes").mkdir()
        (self.root / "notes/a.md").symlink_to(self.root / "real.md")
        self.run_script("--manifest", plan, "--apply", ok=False)
        self.assertTrue((self.root / "notes/a.md").is_symlink())
        plan = self.tiny_plan("src/a.py\tdocs/current/a.py\n")
        self.put("src/a.py")
        (self.root / "docs/current").mkdir(parents=True)
        (self.root / "docs/current/a.py").symlink_to(self.root / "missing.py")
        self.run_script("--manifest", plan, "--apply", ok=False)
        self.assertTrue((self.root / "src/a.py").is_file())
        self.assertTrue((self.root / "docs/current/a.py").is_symlink())

    def test_undo_refuses_existing_original_path(self):
        plan = self.tiny_plan(); self.put("notes/a.md")
        self.run_script("--manifest", plan, "--apply")
        journal, = (self.root / "reorganization-logs").glob("*.tsv")
        self.put("notes/a.md", b"new original-path file must survive")
        before = self.snapshot()
        self.run_script("--undo", journal, "--apply", ok=False)
        self.assertEqual(before, self.snapshot())

    def test_undo_handles_recorded_intent_before_and_after_move(self):
        data = b"same exact contents"
        digest = sha256(data).hexdigest()
        self.put("docs/a.md", data)  # First move completed before interruption.
        self.put("notes/b.md", data)  # Second intent logged, move never started.
        journal = self.put("interrupted.tsv", (
            "# Move journal v1\n# root:\t" + str(self.root) + "\n" +
            digest + "\tnotes/a.md\tdocs/a.md\n" +
            digest + "\tnotes/b.md\tdocs/b.md\n").encode())
        self.run_script("--undo", journal, "--apply")
        self.assertEqual((self.root / "notes/a.md").read_bytes(), data)
        self.assertEqual((self.root / "notes/b.md").read_bytes(), data)
        self.assertFalse((self.root / "docs/a.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
