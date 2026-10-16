import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(REPO, "skills", "tidy-comms")
SCAN = os.path.join(SKILL, "scripts", "scan_comments.py")
APPLY = os.path.join(SKILL, "scripts", "apply_plan.py")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "project")


def run(script, *args, cwd=None):
    return subprocess.run([sys.executable, script, *args], capture_output=True, text=True, check=True, cwd=cwd)


def scan(root, *args):
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "scan.json")
        run(SCAN, root, "--out", out, *args)
        with open(out) as f:
            return json.load(f)


def apply(plan, *args):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "plan.json")
        with open(path, "w") as f:
            json.dump(plan, f)
        return run(APPLY, path, *args)


def by_path(report):
    return {f["path"]: f for f in report["files"]}


class TempProject(unittest.TestCase):
    """Gives each test a scratch copy of the fixture project (outside any git repo)."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        shutil.copytree(FIXTURES, self.root, dirs_exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.root, rel), newline="") as f:
            return f.read()

    def git(self, *args):
        subprocess.run(["git", "-C", self.root, *args], capture_output=True, check=True)

    def init_git(self):
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "test")
        self.git("add", "-A")
        self.git("commit", "-qm", "initial")
