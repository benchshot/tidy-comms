---
type: llm
weight: 2
---

Judge the code the response returns. The code was pasted, so no file on disk needs editing.

The updated file must still contain:
- The copyright header.
- `// MARK: - ImageCache`.
- A comment in `insert(_:for:)` explaining *why* the image is decoded before insertion. It may be tightened, but the reason (avoiding decompression on the main thread) must survive.

The code itself must be unchanged apart from comments. Fail if any code line was altered, added, or removed.
