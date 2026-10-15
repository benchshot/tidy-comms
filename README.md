# TidyComms

A [Claude Code](https://claude.com/claude-code) skill that keeps code comments to a minimum.

Claude tends to over-comment: narrating steps, restating method names, leaving notes about what it just changed. TidyComms tells it to let clear names and structure do the explaining, and to comment only where code is genuinely complex or surprising, focusing on *why* rather than *how*.

## What it does

**While writing code**, Claude adds a comment only when a competent developer reading it for the first time would otherwise misunderstand it or have to stop and work it out: tricky algorithms, concurrency constraints, workarounds, hidden side effects.

**On request**, it tidies existing comments, sorting each one into keep, rewrite, or remove, then reports what changed. It never changes code behavior while tidying.

It always keeps license headers, tool directives (`// MARK:`, `// swiftlint:disable`, `// eslint-disable`), actionable TODOs, and public API docs.

### Before

```swift
// Fetch the user
func fetchUser(id: String) async throws -> User {
    // Build the URL
    let url = baseURL.appending(path: "users/\(id)")
    // Make the request
    let (data, _) = try await session.data(from: url)
    // Decode and return the user
    return try decoder.decode(User.self, from: data)
}
```

### After

```swift
func fetchUser(id: String) async throws -> User {
    let url = baseURL.appending(path: "users/\(id)")
    let (data, _) = try await session.data(from: url)
    return try decoder.decode(User.self, from: data)
}
```

**Across a whole project**, it scans every source file and shows what a cleanup would do before touching anything:

```
TidyComms scan: MyApp (84 files)

                 Now      After    Change
Total lines     12,480   11,342   -1,138  (-9.1%)
Comment lines    1,610      472   -1,138  (-70.7%)
Code lines       9,870    9,870        0
```

It follows that with the most affected files and examples of what would go, then asks before applying anything. A bundled script (`scripts/scan_comments.py`, Python 3, no dependencies) handles the counting, so the line numbers are exact; Claude decides which comments are worth keeping.

## Install

### With npx

```bash
npx skills add benchshot/tidy-comms -g
```

Drop `-g` to install into the current project instead of globally. Works with Claude Code and other agents supported by the [skills CLI](https://skills.sh).

### As a Claude Code plugin

In Claude Code:

```
/plugin marketplace add benchshot/tidy-comms
/plugin install tidy-comms@tidy-comms
```

### Manually

Copy the skill folder into your personal skills directory:

```bash
git clone https://github.com/benchshot/tidy-comms.git
mkdir -p ~/.claude/skills
cp -r tidy-comms/skills/tidy-comms ~/.claude/skills/
```

Or into a project's `.claude/skills/` directory to share it with your team.

## Usage

The skill triggers automatically whenever Claude writes, edits, or reviews code. You can also ask for it directly:

- "Tidy the comments in this file"
- "Scan this project for comments TidyComms would remove"

Or invoke it by name: `/tidy-comms` (npx or manual install) or `/tidy-comms:tidy-comms` (plugin install).

## License

[MIT](LICENSE)
