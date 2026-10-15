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

The skill triggers automatically whenever Claude writes, edits, or reviews code. To tidy an existing file, ask Claude to "tidy the comments in this file" or invoke it directly:

- `/tidy-comms:tidy-comms` when installed as a plugin
- `/tidy-comms` when installed manually

## License

[MIT](LICENSE)
