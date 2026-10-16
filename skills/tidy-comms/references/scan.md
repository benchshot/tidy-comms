# Scanning a project, branch, or changes

Report first, change nothing until the user approves. The rules for what to remove, rewrite, keep, or ask about are in `SKILL.md`; this file covers the workflow. Paths below are relative to the skill's directory.

## 1. Collect

Run the scanner, writing its report to a temporary location outside the project:

```bash
python3 scripts/scan_comments.py <project-root> --out <tmp>/tidycomms-scan.json
```

Choose the scope from the request:

| Request | Flags |
|---|---|
| "scan the project" | none |
| "my changes", "what I haven't committed" | `--changed` |
| "my branch", "before my PR" | `--since main` (or the base branch the user names) |
| "only the comments I added" | add `--changed-lines` to either of the above |

With `--changed-lines`, line totals still cover whole files, but only comments on changed lines are listed, so report on those comments rather than whole-file totals.

The scanner uses `git ls-files` when available and skips dependency and build folders, minified files, and generated files. Its JSON lists every comment block with `file`, `start`, `end`, `kind` (`full` for comment-only lines, `trailing` for comments after code), `text`, and hint `tags`. The summary includes `docs_evidence` (see "Generated documentation" in `SKILL.md`).

Tags are hints, not verdicts:
- `shebang`, `directive`, `license`: protected. Always keep.
- `kept`: listed under `keep` in `.tidycomms.json`. The user already decided; keep it and don't ask again.
- `doc`: judge with "Generated documentation", using `docs_evidence`.
- `todo`: keep only if it carries actionable information.
- `maybe-code`: possibly commented-out code. Confirm by reading it, then remove.
- `api`: commented-out code in a protocol, interface, delegate, or public declaration (`context` holds the enclosing declaration). Confirm by reading it, then list it under "Needs your decision". Also catch API cases the tag missed.

If `python3` is unavailable, read the files directly and count by hand.

## 2. Classify

Classify every block that isn't protected or kept: **remove**, **rewrite** (necessary comments only; note the shorter line count), or **keep**, following "Remove, don't shorten". Rewrites should be rare; if many blocks land there, re-check them, since most should be removals. Read surrounding code when a comment's value depends on context. For a large project, work a directory at a time; if subagents are available, split directories across them.

Keep the classification as a plan (step 5) so applying matches the report exactly.

## 3. Report

Numbers first, then detail:

```
TidyComms scan: <project> (<n> files, <scope>)

                 Now      After    Change
Total lines     12,480   11,342   -1,138  (-9.1%)
Comment lines    1,610      472   -1,138  (-70.7%)
Code lines       9,870    9,870        0

Remove:   1,031 lines in 412 blocks, plus 64 trailing comments
Rewrite:    107 lines saved across 38 blocks
Keep:       472 lines (58 protected, 96 doc, 21 TODO, 297 explain complex code)

Most affected files
  Sources/Networking/APIClient.swift     -142
  Sources/Views/ProfileView.swift         -98

Examples of what would be removed
  APIClient.swift:42      // Build the URL               (says what the code says)
  ProfileView.swift:18    // The user's name             (restates `userName`)
  Cache.swift:88-94       // let old = legacyStore()...  (commented-out code)

Needs your decision: commented-out API code (not counted above)
  PlayerDelegate.swift:12   // func playerDidPause(_ player: Player)
                            in: public protocol PlayerDelegate
  UserRepository.kt:8       // suspend fun users(): List<User>
                            in: interface UserRepository

Suggested code changes (not applied)
  CardStyle.swift:14      make `CardStyleModifier` private (replaces "use cardStyle() instead")
```

- "Now" and "Code lines" come from the scanner. "After" is "Now" minus removed lines minus lines saved by rewrites. Trailing comments are stripped from their line without removing it.
- Show around ten varied removal examples and a few rewrites (before → after, with what makes the comment necessary).
- List anything uncertain separately rather than guessing.
- Note renames that would make a kept comment unnecessary.

End by asking whether to apply all of it, only some files or categories, or nothing, and separately ask keep or delete for each "Needs your decision" item.

## 4. Remember decisions

When the user answers "Needs your decision" items, skips folders, or names modules whose docs are published, offer to record it in `.tidycomms.json` at the project root so later scans don't ask again. Create or update it only with their approval:

```json
{
  "skip": ["Sources/Generated/*", "**/Legacy/*"],
  "docs_modules": ["Sources/DesignSystem"],
  "keep": [
    {"file": "Sources/Player/PlayerDelegate.swift", "text": "// func playerDidPause(_ player: Player)"}
  ]
}
```

- `skip`: glob patterns of files to leave out.
- `docs_modules`: modules whose generated docs are published, when the scanner can't detect it.
- `keep`: comments the user chose to keep, matched by text (whitespace-insensitive), so they survive line shifts. Omit `file` to match the text in any file.

## 5. Apply (only after approval)

Write the approved changes to a plan file outside the project. Each change is a block copied unchanged from the scan JSON (`start`, `end`, `kind`, `text`) plus `file` and an `action`:

```json
{
  "root": "<project-root>",
  "changes": [
    {"file": "Sources/API.swift", "start": 42, "end": 42, "kind": "full", "text": "    // Build the URL", "action": "remove"},
    {"file": "Sources/API.swift", "start": 57, "end": 57, "kind": "trailing", "text": "// call api", "action": "remove"},
    {"file": "Sources/Cache.swift", "start": 10, "end": 13, "kind": "full", "text": "...", "action": "rewrite",
     "replacement": "// Evicts oldest first: the server rejects batches over 50."}
  ]
}
```

Include only approved changes, and "Needs your decision" items only where the user chose delete. Write `replacement` without indentation; the script indents it to match.

Preview, then apply:

```bash
python3 scripts/apply_plan.py <tmp>/tidycomms-plan.json --dry-run
python3 scripts/apply_plan.py <tmp>/tidycomms-plan.json
```

The script removes full-line comments with their lines, strips trailing comments while keeping the code, tidies blank lines left behind, and preserves line endings. It checks each comment's text before changing anything: if a file was edited since the scan, that change is skipped and listed. Report skipped items to the user and offer to rescan them.

Afterwards, rerun the scanner with the same flags and report the actual before and after totals. If the project has a build or test command, offer to run it.
