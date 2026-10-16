#!/usr/bin/env python3
"""Apply an approved TidyComms plan: remove or rewrite the listed comments.

The plan is JSON: {"root": "<project>", "changes": [change, ...]}, where each change
is a block copied from the scan report plus an action:

  {"file": "Sources/API.swift", "start": 42, "end": 42, "kind": "full",
   "text": "    // Build the URL", "action": "remove"}
  {"file": ..., "kind": "trailing", "text": "// call api", "action": "remove"}
  {"file": ..., "kind": "full", "text": ..., "action": "rewrite",
   "replacement": "// Retries once: the CDN drops the first request after a deploy."}

Each comment's text is checked against the file before anything changes, so a file
edited since the scan is skipped and reported rather than damaged.
"""

import argparse
import difflib
import json
import os
import sys
import textwrap
from collections import defaultdict

OPENERS = ("{", "(", "[")


def is_blank(line):
    return not line.strip()


def tidy_gap(lines, i):
    """After removing lines at index i, drop a blank line the removal left dangling."""
    prev = lines[i - 1] if i > 0 else None
    nxt = lines[i] if i < len(lines) else None
    if nxt is not None and is_blank(nxt) and (prev is None or is_blank(prev) or prev.rstrip().endswith(OPENERS)):
        del lines[i]
    elif prev is not None and is_blank(prev) and (nxt is None or nxt.lstrip().startswith(("}", ")", "]"))):
        del lines[i - 1]


def apply_change(lines, change):
    """Apply one change in place. Returns lines removed, or None if the file no longer matches."""
    start, end = change["start"], change["end"]
    if change["kind"] == "trailing":
        if start > len(lines):
            return None
        line = lines[start - 1]
        at = line.rfind(change["text"])
        if at == -1:
            return None
        before, after = line[:at].rstrip(), line[at + len(change["text"]):]
        if change["action"] == "rewrite":
            before += " " + change["replacement"].strip()
        lines[start - 1] = before + after if after.strip() else before
        return 0

    expected = change["text"].split("\n")
    if end > len(lines) or [l.rstrip() for l in lines[start - 1:end]] != [l.rstrip() for l in expected]:
        return None
    if change["action"] == "rewrite":
        original = lines[start - 1]
        indent = original[:len(original) - len(original.lstrip())]
        body = textwrap.dedent(change["replacement"]).strip("\n").split("\n")
        new = [indent + l if l.strip() else "" for l in body]
        lines[start - 1:end] = new
        return (end - start + 1) - len(new)
    del lines[start - 1:end]
    before = len(lines)
    tidy_gap(lines, start - 1)
    return (end - start + 1) + (before - len(lines))


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        data = f.read()
    newline = "\r\n" if "\r\n" in data else "\n"
    ends_with_newline = data.endswith(newline)
    lines = data.split(newline)
    if ends_with_newline:
        lines.pop()
    return lines, newline, ends_with_newline


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan")
    parser.add_argument("--dry-run", action="store_true", help="print the diff without writing files")
    args = parser.parse_args()

    with open(args.plan) as f:
        plan = json.load(f)
    root = os.path.abspath(plan.get("root", "."))

    by_file = defaultdict(list)
    for change in plan["changes"]:
        change.setdefault("action", "remove")
        if change["action"] not in ("remove", "rewrite"):
            sys.exit(f"Unknown action {change['action']!r} in {change.get('file')}")
        if change["action"] == "rewrite" and "replacement" not in change:
            sys.exit(f"Rewrite without replacement in {change.get('file')}:{change['start']}")
        by_file[change.get("file") or change["path"]].append(change)

    removed_total, applied, stale = 0, 0, []
    for rel, changes in sorted(by_file.items()):
        changes.sort(key=lambda c: c["start"])
        for a, b in zip(changes, changes[1:]):
            if b["start"] <= a["end"]:
                sys.exit(f"Overlapping changes in {rel} at lines {a['start']} and {b['start']}")

        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            stale.extend(f"{rel}:{c['start']} (file missing)" for c in changes)
            continue
        lines, newline, ends_with_newline = read(path)
        original = list(lines)
        removed = 0
        for change in reversed(changes):
            result = apply_change(lines, change)
            if result is None:
                stale.append(f"{rel}:{change['start']} (text no longer matches)")
            else:
                removed += result
                applied += 1
        if lines == original:
            continue
        removed_total += removed
        if args.dry_run:
            sys.stdout.writelines(difflib.unified_diff(
                [l + "\n" for l in original], [l + "\n" for l in lines], f"a/{rel}", f"b/{rel}"))
        else:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(newline.join(lines) + (newline if ends_with_newline else ""))
        print(f"{'Would change' if args.dry_run else 'Changed'} {rel}: -{removed} lines", file=sys.stderr)

    print(f"\n{'Would apply' if args.dry_run else 'Applied'} {applied} of {len(plan['changes'])} changes, "
          f"{removed_total} lines removed.", file=sys.stderr)
    if stale:
        print(f"Skipped {len(stale)} because the file changed since the scan:", file=sys.stderr)
        for item in stale:
            print(f"  {item}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
