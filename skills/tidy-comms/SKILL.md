---
name: tidy-comms
description: Keeps code comments to a minimum, adding them only where a method or block is genuinely complex and needs explaining. Use whenever writing, editing, or reviewing code, when the user asks to tidy, trim, or clean up comments, and when they want a project, branch, or their changes scanned to preview which comments would be removed.
---

# TidyComms

Code should explain itself through clear names and structure. Comments are the exception, not the default.

**Project rules first.** Before tidying, look for a project comment-style file (such as `docs/core/COMMENT-STYLE.md`) or comment rules in `CLAUDE.md` / `AGENTS.md`. Where they conflict with this skill, the project's rules win.

## When writing or editing code

Do not add a comment unless it passes this test: **would a competent developer reading this for the first time misunderstand it, or have to stop and work it out?**

Comment only:
- Methods whose logic is non-obvious: tricky algorithms, math, bit manipulation, concurrency or ordering constraints, performance tricks.
- The *why* behind surprising decisions: workarounds for bugs, platform quirks, deliberate deviations from the obvious approach.
- Hidden constraints or side effects a caller must know about.

Never comment:
- What the code plainly says (`// increment counter`, `// return the result`, `// init view model`).
- Restated method or property names (`/// Gets the user` on `getUser()`).
- Doc tags that repeat the signature: `@param userId the user ID`, `@return the user`, `- Parameter id: The id`. Keep a tag only when it adds something the name and type don't (units, valid ranges, what nil means, thrown errors).
- Section narration (`// Step 1: ...`, `// Now we loop...`).
- Change history or notes to the reviewer (`// added this to fix X`). That belongs in the commit message.
- Design justification (`the SDK does not second-guess the host`, `we deliberately avoid X`). That belongs in the PR description. Cut the justification sentence, not the facts around it: what a term in the name refers to or where a value comes from stays.
- Commented-out code (but see "Ask before removing commented-out API code").

If a comment feels needed because a name is unclear, rename the thing instead.

If a comment only exists to steer callers, enforce it in code instead:
- "Use `cardStyle(...)` instead of applying this directly" / "internal use only" → tighten access control (`private`, `fileprivate`, `internal`).
- "Deprecated, use `newFetch()`" → `@available(*, deprecated, renamed: "newFetch()")` or `@Deprecated`.
- "Must be called on the main thread" → `@MainActor` (Swift) or `@MainThread` (Android).

When writing new code, use the code-level fix and skip the comment. When tidying existing code, remove the comment and *suggest* the code change: access control and annotations can break callers elsewhere, so they need the user's approval.

## How to write the comments that remain

- One to three lines, focused on *why* or *what to watch out for*, not *how*.
- For a complex method, one brief doc comment above it rather than inline comments scattered through the body.
- Match the comment style already used in the file.

## Always keep

- License or copyright headers.
- Tool or compiler directives: `// swiftlint:disable`, `//noinspection`, `// ktlint-disable`, `// @formatter:off`, `// ignore:` (Dart), `// eslint-disable`, `#pragma`.
- Navigation markers: `// MARK:`, `//region` / `//endregion`.
- `TODO`/`FIXME` notes that carry real, actionable information.
- Comments in `strings.xml` and other localization files that give translators context.
- Useful doc comments where generated docs are actually built (below).

## Generated documentation

Doc-comment *style* (`///`, `/** */`, DocC links, `@param`) proves nothing: Xcode, IDE templates and AI tools produce it everywhere. What matters is whether docs are **built**: a `.docc` catalog, `swift-docc-plugin`, a `docbuild` / `generate-documentation` step, Dokka, `dartdoc`, `typedoc`, `jsdoc`, or `jazzy`, or a module listed in `docs_modules` in `.tidycomms.json`.

- **No evidence:** doc comments get no special treatment.
- **Evidence, in the module it covers:** a type- or method-level summary and one short usage example may stay when they say something the signature doesn't. Doc comments that restate a name, type, or default are still removed.
- **Unclear** (such as a public library or SDK with no build step found): ask once per module, not per comment.

## Remove, don't shorten

When cleaning up existing comments, removal is the default. Decide in this order:

1. **Protected** (see "Always keep")? Keep it as is.
2. **Not necessary** by the test above? **Remove it entirely.** Don't shorten it, reword it, or merge several unnecessary comments into one. An unnecessary comment cut down to fewer words is still unnecessary.
3. **Necessary** but bloated, or explains *how* instead of *why*? Rewrite it down to the essential *why*.
4. Otherwise keep it.

A rewrite is never a compromise for a comment you're unsure about. If you can't say what a reader would lose without it, remove it.

**Doc comments that state a contract are necessary.** If a doc comment says something the signature can't (no-op or edge cases, what is preserved, what `null` means, where a value comes from, why a private variant exists), it passes the test. Trim the narration around it; don't delete it. "Evicts least-recently-used entries first; pinned entries are never evicted" on `trim(toBytes:)` stays: the signature says neither.

**Keep the form.** A kept or rewritten doc comment stays a doc comment (`/** */`, `///`). IDE hover and quick-doc read those, not `//`. Never convert one into a line comment.

**Duplicates:** when the same *why* appears in a doc comment and an inline comment, or in two methods' doc comments, keep one copy, preferably inline at the line where the tricky behavior happens, and remove the rest.

**Stale comments:** a comment that contradicts the code (says it clears when the code keeps, wrong limits, wrong order) is a correctness issue, not a style one. Remove or correct it, and report it at the top of the summary. Check a doc comment against the code and comments in its body too: a doc comment that says "retries 3 times" above `maxRetries = 5` is stale, even when you were going to remove it anyway.

## Long doc comments that describe rules

When a doc comment spells out rules, cases, or a contract (lists of cases, "state A vs state B", priority orders), grep the project's docs (`docs/`, `README`, `*.md`) for its key terms before judging it.

- **A doc covers it:** open the section and confirm the anchor exists and every case or rule in the comment is there. Matching key terms is not enough. Only then shrink the comment to a 1–2 line contract (what it returns, its side effects, what the caller must do) plus a pointer to the doc section. Anything the doc doesn't cover stays in the code, trimmed.
- **No doc covers it, and the logic is genuinely complex:** keep a trimmed version in the code and suggest moving the full explanation into docs.
- **Either way**, notes about how this code works (it waits for X to load, it must run before Y, a workaround for a race) stay as a short comment at the line they describe. Docs hold the rules; the code explains its own timing.
- **In the report**, list each comment replaced by a pointer and the section it points to, so the user can check it.

Example: a 35-line KDoc on `resolveExpiry()` lists each expiry case (trial, grace period, revoked, renewed-while-offline...), and `docs/billing/EXPIRY.md` already has an "Expiry cases" section covering the same ones. It becomes:

```kotlin
/**
 * Returns the effective expiry for [subscription] and clears cached entitlements when it has passed.
 * Cases and their priority: docs/billing/EXPIRY.md#expiry-cases
 */
fun resolveExpiry(subscription: Subscription): Instant
```

## Ask before removing commented-out API code

Commented-out code that belongs to an API surface is the one exception to removing without asking. It may be a requirement disabled on purpose, an optional delegate method kept as a reference, or a member other modules still expect. This covers commented-out code:

- Inside a protocol, interface, trait, or abstract class.
- Inside a delegate, data source, listener, callback, or observer, whether it declares one (`PlayerDelegate`) or conforms to one (`extension VC: UITableViewDataSource`).
- That is itself a public or open declaration (`// public func`, `// open var`, `// @objc optional func`).

**Always ask the user** before removing it, in every mode. Show the file and line, the commented-out code, and the type it sits in, then ask keep or delete. Never decide for the user, never count it as a removal until they answer, and don't treat a general "apply everything" as an answer to these. If the project has a `.tidycomms.json`, comments listed under `keep` were already decided: leave them alone without asking again.

## Tidying a file

1. Check for project comment rules, then read the file and classify each comment using "Remove, don't shorten". Check every kept comment against the code it describes.
2. Remove the unnecessary comments and duplicates; rewrite only the necessary ones that are bloated; correct or remove stale ones. Ask about commented-out API code.
3. Do not change any code behavior while tidying.
4. Briefly report, stale comments first, what was removed, rewritten, and kept, plus any rename or access-control change that would remove the need for a kept comment.

## Scanning a project, branch, or changes

When the user asks to scan, audit, or preview comments across a project or directory, or in their changes or branch, **read `references/scan.md` in this skill's directory first** and follow it. Scanning is read-only until the user approves.
