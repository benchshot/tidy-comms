---
name: tidy-comms
description: Keeps code comments to a minimum, adding them only where a method or block is genuinely complex and needs explaining. Use whenever writing, editing, or reviewing code, and when the user asks to tidy, trim, or clean up comments.
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
- Tool or compiler directives (`// swiftlint:disable`, `// eslint-disable`, `#pragma`, `// MARK:` and similar navigation markers).
- `TODO`/`FIXME` notes that carry real, actionable information.
- Doc comments on public APIs in a library or SDK, where callers rely on generated docs.

## When asked to tidy existing comments

1. Read the file and classify each comment as keep, rewrite (too long or explains *how* instead of *why*), or remove.
2. Remove redundant comments; tighten the ones worth keeping.
3. Do not change any code behavior while tidying.
4. Briefly report what was removed, rewritten, and kept, and point out any spot where a rename would have removed the need for a comment.
