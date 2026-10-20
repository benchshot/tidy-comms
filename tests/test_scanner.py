import json
import os
import unittest

from helpers import FIXTURES, TempProject, by_path, scan

EXPECTED = {
    "ios/Sample.swift": ((22, 9, 10, 3), [
        (1, 4, "full", ["license", "header"]),
        (8, 8, "full", ["directive"]),
        (10, 10, "full", ["doc"]),
        (12, 12, "full", []),
        (13, 13, "trailing", []),
        (15, 16, "full", []),
        (20, 20, "full", ["maybe-code"]),
        (21, 21, "trailing", []),
    ]),
    "ios/Player.swift": ((17, 10, 4, 3), [
        (3, 3, "full", ["maybe-code", "api"]),
        (8, 8, "full", ["maybe-code"]),
        (14, 14, "full", ["maybe-code", "api"]),
        (17, 17, "full", ["maybe-code", "api"]),
    ]),
    "android/app/src/main/java/Repo.kt": ((17, 4, 12, 1), [
        (3, 3, "full", ["directive"]),
        (4, 8, "full", ["doc"]),
        (9, 9, "trailing", []),
        (10, 11, "full", []),
        (12, 12, "trailing", []),
        (13, 13, "full", ["directive"]),
        (14, 14, "full", ["directive"]),
        (15, 15, "full", ["directive"]),
        (17, 17, "full", ["directive"]),
    ]),
    "android/app/src/main/java/UserRepository.kt": ((10, 7, 2, 1), [
        (3, 3, "full", ["maybe-code", "api"]),
        (8, 8, "full", ["maybe-code"]),
    ]),
    "android/app/src/main/res/layout/activity_main.xml": ((9, 5, 4, 0), [
        (2, 2, "full", []),
        (5, 7, "full", ["maybe-code"]),
        (8, 8, "trailing", []),
    ]),
    "flutter/main.dart": ((3, 1, 2, 0), [
        (1, 1, "full", ["directive", "header"]),
        (2, 2, "full", ["header"]),
        (3, 3, "trailing", ["directive"]),
    ]),
    "scripts/tool.py": ((8, 5, 2, 1), [
        (1, 1, "full", ["shebang"]),
        (2, 2, "full", ["header"]),
        (3, 3, "trailing", ["directive"]),
        (7, 7, "trailing", []),
    ]),
}


class ScannerFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = scan(FIXTURES)
        cls.files = by_path(cls.report)

    def test_finds_expected_files(self):
        self.assertEqual(sorted(self.files), sorted(EXPECTED))

    def test_line_counts(self):
        for path, (counts, _) in EXPECTED.items():
            with self.subTest(path=path):
                f = self.files[path]
                self.assertEqual((f["lines"], f["code"], f["comment"], f["blank"]), counts)

    def test_blocks_and_tags(self):
        for path, (_, blocks) in EXPECTED.items():
            with self.subTest(path=path):
                actual = [(b["start"], b["end"], b["kind"], b["tags"]) for b in self.files[path]["blocks"]]
                self.assertEqual(actual, blocks)

    def test_skips_generated_files(self):
        self.assertEqual(self.report["summary"]["skipped_generated"], 1)
        self.assertNotIn("ios/Generated.swift", self.files)

    def test_api_blocks_carry_their_enclosing_declaration(self):
        player = self.files["ios/Player.swift"]["blocks"]
        self.assertEqual(player[0]["context"], "public protocol PlayerDelegate: AnyObject {")
        self.assertEqual(player[1].get("context"), None)
        self.assertNotIn("context", player[3])

    def test_comment_markers_inside_strings_are_code(self):
        texts = [b["text"] for b in self.files["ios/Sample.swift"]["blocks"]]
        self.assertFalse(any("not // a comment" in t or "inside a string" in t for t in texts))

    def test_no_docs_evidence(self):
        self.assertEqual(self.report["summary"]["docs_evidence"], [])


class DocsEvidence(TempProject):
    def test_reports_each_kind_of_evidence(self):
        self.write("Sources/DesignSystem/DesignSystem.docc/DesignSystem.md", "# DesignSystem\n")
        self.write("Package.swift", '.package(url: "https://github.com/apple/swift-docc-plugin", from: "1.0.0")\n')
        self.write("android/build.gradle.kts", 'plugins { id("org.jetbrains.dokka") }\n')
        self.write(".github/workflows/docs.yml", "run: xcodebuild docbuild -scheme App\n")
        evidence = scan(self.root)["summary"]["docs_evidence"]
        self.assertEqual(evidence, [
            "Sources/DesignSystem/DesignSystem.docc: DocC catalog",
            ".github/workflows/docs.yml: docbuild",
            "Package.swift: swift-docc-plugin",
            "android/build.gradle.kts: dokka",
        ])


class Config(TempProject):
    def write_config(self, config):
        self.write(".tidycomms.json", json.dumps(config))

    def test_skip_globs(self):
        self.write_config({"skip": ["android/*", "flutter/*"]})
        report = scan(self.root)
        self.assertEqual(sorted(by_path(report)), ["ios/Player.swift", "ios/Sample.swift", "scripts/tool.py"])
        self.assertEqual(report["summary"]["skipped_by_config"], 4)

    def test_keep_matches_text_in_a_file_or_anywhere(self):
        self.write_config({"keep": [
            {"file": "ios/Player.swift", "text": "// func playerDidPause(_ player: Player)"},
            {"text": "  # Import things  "},
        ]})
        report = scan(self.root)
        files = by_path(report)
        self.assertIn("kept", files["ios/Player.swift"]["blocks"][0]["tags"])
        self.assertNotIn("kept", files["ios/Player.swift"]["blocks"][1]["tags"])
        self.assertIn("kept", files["scripts/tool.py"]["blocks"][1]["tags"])
        self.assertEqual(report["summary"]["kept_by_config"], 2)

    def test_docs_modules(self):
        self.write_config({"docs_modules": ["Sources/DesignSystem"]})
        evidence = scan(self.root)["summary"]["docs_evidence"]
        self.assertEqual(evidence, ["Sources/DesignSystem: listed in .tidycomms.json"])


class ChangedScope(TempProject):
    def setUp(self):
        super().setUp()
        self.init_git()

    def add_comment_to_sample(self):
        text = self.read("ios/Sample.swift").replace(
            "    let s = ", "    // New comment\n    let s = ")
        self.write("ios/Sample.swift", text)

    def test_changed_limits_to_modified_and_untracked_files(self):
        self.add_comment_to_sample()
        self.write("ios/New.swift", "// Brand new\nlet x = 1\n")
        report = scan(self.root, "--changed")
        self.assertEqual(sorted(by_path(report)), ["ios/New.swift", "ios/Sample.swift"])
        self.assertEqual(report["summary"]["scope"], "uncommitted changes")

    def test_changed_lines_keeps_only_comments_on_changed_lines(self):
        self.add_comment_to_sample()
        files = by_path(scan(self.root, "--changed", "--changed-lines"))
        blocks = files["ios/Sample.swift"]["blocks"]
        self.assertEqual([(b["start"], b["text"].strip()) for b in blocks], [(14, "// New comment")])

    def test_since_includes_committed_branch_work(self):
        self.git("checkout", "-qb", "feature")
        self.add_comment_to_sample()
        self.git("commit", "-qam", "comment")
        self.write("flutter/main.dart", self.read("flutter/main.dart") + "// uncommitted\n")
        files = by_path(scan(self.root, "--since", "main"))
        self.assertEqual(sorted(files), ["flutter/main.dart", "ios/Sample.swift"])

    def test_changed_lines_requires_a_scope(self):
        with self.assertRaises(Exception):
            scan(self.root, "--changed-lines")


if __name__ == "__main__":
    unittest.main()
