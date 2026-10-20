# Changelog

All notable changes to TidyComms. Versions match `version` in `.claude-plugin/plugin.json`.

## [Unreleased]

### Fixed
- Doc comments that state a contract (edge cases, what `null` means, where a value comes from, why a private overload exists) are trimmed, not deleted.
- Kept doc comments stay doc comments; they are no longer converted to `//`.
- Cutting design justification no longer takes the facts next to it.
- A doc comment that contradicts the code or comments in its body is reported as stale.
- SDKs with no docs build count as unclear for generated docs, so the skill asks.
- A long doc comment is shrunk to a doc pointer only after the linked section is confirmed to exist and cover every rule in it. Notes about the code's own timing stay at the line they describe, and pointer replacements are listed in the report.

### Added
- `kdoc-contracts` eval.
- File header comments are always kept. The scanner tags every comment block above a file's first line of code as `header` and treats it as protected, not just headers that mention a license.

## [1.5.0] - 2026-10-16

### Added
- `apply_plan.py` applies an approved scan in one pass. It checks each comment's text before changing a file, so files edited since the scan are skipped and reported instead of damaged. It also tidies leftover blank lines and preserves line endings.
- Scan only your changes: `--changed` (uncommitted work), `--since <ref>` (a branch), and `--changed-lines` (only comments on changed lines).
- Optional `.tidycomms.json` per project: `skip` globs, `docs_modules`, and `keep` decisions, so later scans don't ask about the same comment again.
- Test suite for the scanner and apply script, run in CI on every push.
- Eval suite (`claude plugin eval`) covering removal vs. shortening, commented-out API code, writing new code, Android KDoc, and access-control suggestions.

### Changed
- The scan workflow moved to `references/scan.md` and loads only when scanning. The part of the skill that loads on every coding task is about 40% smaller.

## [1.4.0] - 2026-10-15

### Changed
- Doc comments are judged by whether generated docs are actually built (DocC catalog, `swift-docc-plugin`, `docbuild`, Dokka, and others), not by doc-comment style. The scanner reports this as `docs_evidence`.

## [1.3.1] - 2026-10-15

### Added
- Comments that only steer callers ("use X instead", "deprecated", "main thread only") are replaced by suggested access control or annotations.

## [1.3.0] - 2026-10-15

### Added
- Commented-out code in protocols, interfaces, delegates, and public declarations is never removed without asking. The scanner tags it `api`, with the enclosing declaration.

## [1.2.0] - 2026-10-15

### Added
- Android and Flutter support: XML layouts, manifests and resources; `//noinspection`, `ktlint`, `@formatter`, `//region`, and Dart `// ignore:` directives.
- Correct handling of nested block comments in Swift, Kotlin, Dart, Rust, and Scala.
- Doc tags that repeat the signature (`@param userId the user id`) are removed.

## [1.1.1] - 2026-10-15

### Changed
- Unnecessary comments are removed outright instead of being shortened.

## [1.1.0] - 2026-10-14

### Added
- Project scan mode with a before/after line report, powered by `scan_comments.py`.

## [1.0.0] - 2026-10-14

### Added
- First release: the TidyComms skill, Claude Code plugin and marketplace manifests, and npx install support.
