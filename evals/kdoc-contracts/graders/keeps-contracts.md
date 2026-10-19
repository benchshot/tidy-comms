---
type: llm
weight: 2
---

Judge the code the response returns. The code was pasted, so no file on disk needs editing.

Pass only if all of these hold:
- `trim` keeps a doc comment saying entries are evicted least-recently-used first and that pinned entries are never evicted.
- `restoreIndex` keeps that it restores from the snapshot written by `saveSnapshot` rather than rescanning. The "we deliberately chose this" justification sentence is removed.
- The private `write(key, bytes, attempt)` overload keeps the reason it exists (retries must not re-enter the public method and double-count metrics).
- Every kept or rewritten doc comment is still a `/** */` KDoc, not converted to `//`.
- No code line was changed.
