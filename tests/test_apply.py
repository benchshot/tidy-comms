import unittest

from helpers import TempProject, apply, by_path, scan

PROTECTED = {"license", "directive", "shebang", "doc"}

SAMPLE_AFTER = '''//
//  Sample.swift
//  Copyright (c) 2026 Example. All rights reserved.
//

import Foundation

// MARK: - Fetching

/// Fetches the user.
func fetchUser(id: String) -> String {
    let url = "https://example.com/users/\\(id)"
    let s = "not // a comment"
    let multi = """
    // inside a string
    """
    return url + s + multi
}
'''


class Apply(TempProject):
    def plan_for(self, path, keep_tags=PROTECTED, **overrides):
        blocks = by_path(scan(self.root))[path]["blocks"]
        changes = [dict(b, file=path, action="remove") for b in blocks if not keep_tags & set(b["tags"])]
        return {"root": self.root, "changes": changes, **overrides}

    def test_removes_unprotected_comments(self):
        result = apply(self.plan_for("ios/Sample.swift"))
        self.assertEqual(self.read("ios/Sample.swift"), SAMPLE_AFTER)
        self.assertIn("Applied 5 of 5 changes, 4 lines removed.", result.stderr)

    def test_scan_after_apply_matches_reported_savings(self):
        before = by_path(scan(self.root))["ios/Sample.swift"]["lines"]
        apply(self.plan_for("ios/Sample.swift"))
        after = by_path(scan(self.root))["ios/Sample.swift"]["lines"]
        self.assertEqual(before - after, 4)

    def test_dry_run_changes_nothing(self):
        original = self.read("ios/Sample.swift")
        result = apply(self.plan_for("ios/Sample.swift"), "--dry-run")
        self.assertEqual(self.read("ios/Sample.swift"), original)
        self.assertIn("-    // Build the URL", result.stdout)
        self.assertIn("Would apply 5 of 5 changes", result.stderr)

    def test_skips_changes_when_file_changed_since_scan(self):
        plan = self.plan_for("ios/Sample.swift")
        self.write("ios/Sample.swift", self.read("ios/Sample.swift").replace("// Build the URL", "// Edited"))
        result = apply(plan)
        self.assertIn("// Edited", self.read("ios/Sample.swift"))
        self.assertNotIn("// trailing note", self.read("ios/Sample.swift"))
        self.assertIn("Skipped 1", result.stderr)
        self.assertIn("ios/Sample.swift:12 (text no longer matches)", result.stderr)

    def test_rewrite_keeps_indentation(self):
        plan = self.plan_for("ios/Sample.swift")
        plan["changes"] = [dict(c, action="rewrite", replacement="// Shorter.")
                           for c in plan["changes"] if c["start"] == 15]
        apply(plan)
        lines = self.read("ios/Sample.swift").splitlines()
        self.assertEqual(lines[14], "    // Shorter.")
        self.assertEqual(lines[15], '    let multi = """')

    def test_strips_trailing_comment_mid_line(self):
        self.write("a.kt", "val x = 1 /* a /* b */ c */ + 2\n")
        apply(self.plan_for("a.kt"))
        self.assertEqual(self.read("a.kt"), "val x = 1 + 2\n")

    def test_removes_xml_comments(self):
        path = "android/app/src/main/res/layout/activity_main.xml"
        apply(self.plan_for(path))
        self.assertEqual(self.read(path), '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:text="a &lt;!-- not --&gt;">
    <TextView android:text="hi" />
</LinearLayout>
''')

    def test_collapses_blank_lines_left_behind(self):
        self.write("b.swift", "// Header note\n\nimport UIKit\n\n// Between\n\nlet a = 1\n"
                              "func f() {\n    // Opening\n\n    let b = 2\n\n    // Closing\n}\n")
        apply(self.plan_for("b.swift"))
        self.assertEqual(self.read("b.swift"),
                         "import UIKit\n\nlet a = 1\nfunc f() {\n    let b = 2\n}\n")

    def test_preserves_crlf_and_missing_final_newline(self):
        self.write("c.swift", "// Remove\r\nlet a = 1 // also\r\nlet b = 2")
        apply(self.plan_for("c.swift"))
        self.assertEqual(self.read("c.swift"), "let a = 1\r\nlet b = 2")

    def test_rejects_overlapping_changes(self):
        plan = self.plan_for("ios/Sample.swift")
        plan["changes"].append(dict(plan["changes"][0]))
        with self.assertRaises(Exception):
            apply(plan)


if __name__ == "__main__":
    unittest.main()
