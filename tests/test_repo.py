import json
import os
import re
import unittest

from helpers import REPO, SKILL


def read(*parts):
    with open(os.path.join(REPO, *parts)) as f:
        return f.read()


class RepoConsistency(unittest.TestCase):
    def test_versions_match(self):
        plugin = json.loads(read(".claude-plugin", "plugin.json"))["version"]
        marketplace = json.loads(read(".claude-plugin", "marketplace.json"))["plugins"][0]["version"]
        changelog = re.search(r"^## \[(\d+\.\d+\.\d+)\]", read("CHANGELOG.md"), re.M).group(1)
        self.assertEqual(plugin, marketplace, "plugin.json and marketplace.json versions differ")
        self.assertEqual(plugin, changelog, "newest CHANGELOG.md entry doesn't match plugin.json")

    def test_skill_frontmatter(self):
        skill = read("skills", "tidy-comms", "SKILL.md")
        self.assertRegex(skill, r"^---\nname: tidy-comms\ndescription: .+\n---\n")

    def test_referenced_files_exist(self):
        for doc in ("SKILL.md", os.path.join("references", "scan.md")):
            text = read("skills", "tidy-comms", doc)
            for ref in set(re.findall(r"(?:`|python3 )((?:scripts|references)/[\w./-]+?\.\w+)", text)):
                with self.subTest(doc=doc, ref=ref):
                    self.assertTrue(os.path.isfile(os.path.join(SKILL, ref)), f"{doc} mentions missing {ref}")


if __name__ == "__main__":
    unittest.main()
