---
name: tidy-comms
description: Keeps code comments to a minimum, adding them only where a method or block is genuinely complex and needs explaining. Use whenever writing, editing, or reviewing code, when the user asks to tidy, trim, or clean up comments, and when they want a whole project scanned to preview which comments would be removed.
---

# TidyComms

Code should explain itself through clear names and structure. Comments are the exception, not the default.

## When writing or editing code

Do not add a comment unless it passes this test: **would a competent developer reading this for the first time misunderstand it, or have to stop and work it out?**

Comment only:
- Methods whose logic is non-obvious: tricky algorithms, math, bit manipulation, concurrency or ordering constraints, performance tricks.
- The *why* behind surprising decisions: workarounds for bugs, platform quirks, deliberate deviations from the obvious approach.
- Hidden constraints or side effects a caller must know about.

Never comment:
- What the code plainly says (`// increment counter`, `// return the result`, `// init view model`).
- Restated method or property names (`/// Gets the user` on `getUser()`).
- Doc tags that repeat the signature: `@param userId the user ID`, `@return the user`, `- Parameter id: The id`, `- Returns: The result`. Keep a tag only when it adds something the name and type don't (units, valid ranges, nullability meaning, thrown errors).
- Section narration (`// Step 1: ...`, `// Now we loop...`).
- Change history or notes to the reviewer (`// added this to fix X`, `// updated`). That belongs in the commit message.
- Commented-out code.

If a comment feels needed because a name is unclear, rename the thing instead.

## How to write the comments that remain

- Keep it short: one to three lines, focused on *why* or *what to watch out for*, not *how*.
- For a complex method, place one brief doc comment above it rather than scattering inline comments through the body.
- Match the comment style already used in the file.

## Always keep

- License or copyright headers.
- Tool or compiler directives, such as `// swiftlint:disable`, `//noinspection`, `// ktlint-disable`, `// @formatter:off`, `// ignore:` (Dart), `// eslint-disable`, `#pragma`.
- Navigation markers: `// MARK:`, `//region` / `//endregion`.
- `TODO`/`FIXME` notes that carry real, actionable information.
- Doc comments on public APIs in a library or SDK (Swift packages, Android library modules, published packages), where callers rely on generated docs. App-internal code doesn't get this exemption.
- Comments in Android `strings.xml` (and other localization files) that give translators context.

## Remove, don't shorten

When cleaning up existing comments, removal is the default. Decide in this order:

1. **Is it protected** (see "Always keep")? Keep it as is.
2. **Is it necessary**, by the test above? If not, **remove it entirely**. Do not shorten it, reword it, or condense several unnecessary comments into one. An unnecessary comment cut down to fewer words is still unnecessary.
3. **Only if it is necessary** but bloated, or explains *how* instead of *why*, rewrite it down to the essential *why*.
4. Otherwise keep it.

A rewrite is never a compromise for a comment you're unsure about. If you can't say what a reader would lose without it, remove it.

## When asked to tidy existing comments in a file

1. Read the file and classify each comment using "Remove, don't shorten".
2. Remove the unnecessary comments; rewrite only the necessary ones that are bloated.
3. Do not change any code behavior while tidying.
4. Briefly report what was removed, rewritten, and kept, and point out any spot where a rename would have removed the need for a comment.

## When asked to scan a project

Use this when the user asks to scan, audit, or preview comments across a whole project or directory. Scanning is read-only: report first, change nothing until the user approves.

### 1. Collect

Run the bundled scanner from this skill's directory, writing the report to a temporary location outside the project:

```bash
python3 <skill-dir>/scripts/scan_comments.py <project-root> --out <tmp>/tidycomms-scan.json
```

It prints line totals and writes every comment block to the JSON file with its file, line range, `kind` (`full` for comment-only lines, `trailing` for comments after code), text, and hint `tags`. It uses `git ls-files` when available, skips dependency and build folders, minified files, and files marked as generated.

Tags are hints, not verdicts:
- `shebang`, `directive`, `license`: protected. Always keep.
- `doc`: a doc comment. Keep on public library APIs and genuinely complex methods; otherwise judge like any other comment.
- `todo`: keep only if it carries actionable information.
- `maybe-code`: possibly commented-out code. Confirm by reading it, then remove.

If `python3` is unavailable, fall back to reading files directly and counting by hand.

### 2. Classify

Classify every block that isn't protected using "Remove, don't shorten": **remove**, **rewrite** (only necessary comments; note the shorter line count), or **keep**. Expect most rewrites to be rare; if a large share of blocks lands in rewrite, re-check them, since most should be removals. Read surrounding code when a comment's value depends on context. For a large project, work through it a directory at a time; if subagents are available, split directories across them. Keep the full classification so that applying matches the report exactly.

### 3. Report

Show the numbers first, then the detail:

```
TidyComms scan: <project> (<n> files)

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
  ...

Examples of what would be removed
  APIClient.swift:42      // Build the URL               (says what the code says)
  ProfileView.swift:18    // The user's name             (restates `userName`)
  Cache.swift:88-94       // let old = legacyStore()...  (commented-out code)
  ...
```

- "Now" and "Code lines" come straight from the scanner. "After" is "Now" minus removed lines minus lines saved by rewrites; trailing comments are stripped from their line without removing it.
- Show around ten varied examples of removals and a few rewrites (before → after, with what makes the comment necessary) so the user can judge the call.
- List anything uncertain separately rather than guessing.
- Note where a rename would make a kept comment unnecessary.

End by asking whether to apply all of it, only some files or categories, or nothing.

### 4. Apply (only after approval)

Make exactly the approved changes, file by file. Delete removed full-line comments together with their lines, strip trailing comments while keeping the code, and avoid leaving doubled blank lines behind. Do not touch code. Then rerun the scanner and report the actual before and after totals. If the project has a build or test command, offer to run it.
