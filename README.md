# TidyComms

[![CI](https://github.com/benchshot/tidy-comms/actions/workflows/ci.yml/badge.svg)](https://github.com/benchshot/tidy-comms/actions/workflows/ci.yml)

A [Claude Code](https://claude.com/claude-code) skill that keeps code comments to a minimum.

Claude tends to over-comment: narrating steps, restating method names, leaving notes about what it just changed. TidyComms tells it to let clear names and structure do the explaining, and to comment only where code is genuinely complex or surprising, focusing on *why* rather than *how*.

## What it does

**While writing code**, Claude adds a comment only when a competent developer reading it for the first time would otherwise misunderstand it or have to stop and work it out: tricky algorithms, concurrency constraints, workarounds, hidden side effects.

**On request**, it tidies existing comments, sorting each one into keep, rewrite, or remove, then reports what changed. It never changes code behavior while tidying.

It always keeps license headers, tool directives (`// MARK:`, `// swiftlint:disable`, `// eslint-disable`), actionable TODOs, and doc comments in modules where generated docs are actually built.

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

**Across a whole project, a branch, or just your changes**, it scans the source files and shows what a cleanup would do before touching anything:

```
TidyComms scan: MyApp (84 files)

                 Now      After    Change
Total lines     12,480   11,342   -1,138  (-9.1%)
Comment lines    1,610      472   -1,138  (-70.7%)
Code lines       9,870    9,870        0
```

It follows that with the most affected files and examples of what would go, then asks before applying anything. Commented-out code in a protocol, interface, delegate or public API is never removed automatically: it's listed separately and you decide keep or delete for each one. Bundled scripts (Python 3, no dependencies) do the counting and the editing, so line numbers are exact and what gets applied matches the report you approved. If a file changed since the scan, it's skipped rather than damaged. Claude decides which comments are worth keeping.

**Supported languages:** Swift, Objective-C, Kotlin, Java, Gradle (`.kts`), Dart/Flutter, JavaScript, TypeScript, Python, Ruby, Go, Rust, C, C++, C#, Scala, PHP, SQL, Lua, shell, YAML, TOML, Terraform, CSS/SCSS/Less, and XML/HTML (including Android layouts, manifests and resources). Tool directives such as `swiftlint`, `ktlint`, `//noinspection`, `// MARK:`, `//region` and Dart's `// ignore:` are always kept.

## Install

### With npx

```bash
npx skills add benchshot/tidy-comms -g
```

This is the recommended install: it gives you the short `/tidy-comms` command. Drop `-g` to install into the current project instead of globally. Works with Claude Code and other agents supported by the [skills CLI](https://skills.sh).

### As a Claude Code plugin

In Claude Code (the command becomes `/tidy-comms:tidy-comms`, since plugin skills are namespaced):

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
- "Tidy the comments in my changes" (uncommitted work)
- "Check the comments on my branch before I open a PR" (everything since `main`)
- "Only look at comments I added"

Or invoke it by name: `/tidy-comms` (npx or manual install) or `/tidy-comms:tidy-comms` (plugin install).

## Project settings

An optional `.tidycomms.json` at the project root remembers decisions so scans don't ask twice. TidyComms offers to create it for you when you answer its questions:

```json
{
  "skip": ["Sources/Generated/*"],
  "docs_modules": ["Sources/DesignSystem"],
  "keep": [
    {"file": "Sources/Player/PlayerDelegate.swift", "text": "// func playerDidPause(_ player: Player)"}
  ]
}
```

- `skip`: files to leave out (glob patterns).
- `docs_modules`: modules whose generated docs you publish, if TidyComms can't detect it.
- `keep`: comments you've decided to keep. They're matched by text, so they survive code moving around.

Commit it so your team shares the same decisions.

## Contributing

```bash
cd tests && python3 -m unittest    # scanner and apply script
claude plugin eval .               # skill behavior, with and without the skill installed
```

Tests run in CI on every push. Eval cases live in `evals/`, one folder per scenario. When changing behavior, bump `version` in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` and add a `CHANGELOG.md` entry (CI checks they match). Pushing a `v<version>` tag publishes a GitHub release with those notes.

See [CHANGELOG.md](CHANGELOG.md) for what's changed.

## License

[MIT](LICENSE)
